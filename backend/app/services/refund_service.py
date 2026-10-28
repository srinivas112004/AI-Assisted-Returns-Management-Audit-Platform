from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.models.entities import Refund, RefundAttempt, ReturnRequest, ReturnLine, OrderLine, Order, ReturnPolicy, Product
from app.rules.refund import calculate_line_refund, quantize
from app.services.audit_service import log_event

def process_refund(
    db: Session,
    rma_number_str: str,
    idempotency_key: str,
    return_line_id_str: Optional[str] = None,
    refund_method: str = "ORIGINAL_PAYMENT",
    apply_restocking_fee: bool = False,
    override_max_amount: Optional[Decimal] = None
) -> Dict[str, Any]:
    """
    Executes a safe, idempotent refund calculation and issuance.
    Strictly prevents duplicate payments and overlimit payouts.
    """
    now = datetime.now(timezone.utc)
    
    # 1. Idempotency Check
    existing_refund = db.query(Refund).filter(Refund.idempotency_key == idempotency_key).first()
    if existing_refund:
        # Record duplicate attempt
        attempt = RefundAttempt(
            refund_id=existing_refund.id,
            return_request_id=existing_refund.return_request_id,
            idempotency_key=idempotency_key,
            attempt_timestamp=now,
            requested_amount=existing_refund.net_refund_amount,
            outcome="BLOCKED_DUPLICATE",
            reason=f"Blocked duplicate attempt with existing idempotency key '{idempotency_key}'"
        )
        db.add(attempt)
        db.commit()

        log_event(
            db,
            entity_type="Refund",
            entity_id=existing_refund.refund_id,
            event_type="REFUND_BLOCKED",
            actor="payment_guard",
            reason=f"Blocked repeated attempt with idempotency key '{idempotency_key}'"
        )

        return {
            "status": "BLOCKED_DUPLICATE",
            "message": "Duplicate refund request blocked by idempotency safeguard.",
            "refund": existing_refund,
            "blocked": True
        }

    # 2. Look up RMA
    rma = db.query(ReturnRequest).filter(ReturnRequest.rma_number == rma_number_str).first()
    if not rma:
        raise HTTPException(status_code=404, detail="ReturnRequest not found")

    target_lines = rma.lines
    if return_line_id_str:
        target_lines = [l for l in rma.lines if l.return_line_id == return_line_id_str]
        if not target_lines:
            raise HTTPException(status_code=404, detail="ReturnLine not found in this RMA")

    total_net_refund = Decimal("0.00")
    total_base = Decimal("0.00")
    total_tax = Decimal("0.00")
    total_restock = Decimal("0.00")
    refunded_return_line_id = None

    for r_line in target_lines:
        if r_line.approved_quantity <= 0:
            continue

        refunded_return_line_id = r_line.id
        ol = db.query(OrderLine).filter(OrderLine.id == r_line.order_line_id).first()
        prod = db.query(Product).filter(Product.id == ol.product_id).first()
        policy = db.query(ReturnPolicy).filter(
            ReturnPolicy.category == prod.category,
            ReturnPolicy.is_active == True
        ).first()

        restock_fee_pct = policy.restocking_fee_percent if policy else Decimal("0.00")

        # Sum past completed refunds for this line
        prev_refunds = db.query(func.coalesce(func.sum(Refund.net_refund_amount), 0)).filter(
            Refund.return_line_id == r_line.id,
            Refund.status == "COMPLETED"
        ).scalar()
        prev_refunded_dec = Decimal(str(prev_refunds))

        calc = calculate_line_refund(
            unit_price=ol.unit_price,
            purchased_quantity=ol.quantity,
            return_quantity=r_line.approved_quantity,
            allocated_discount=ol.allocated_discount,
            line_tax=ol.line_tax,
            restocking_fee_percent=restock_fee_pct,
            previously_refunded_amount=prev_refunded_dec,
            apply_restocking_fee=apply_restocking_fee
        )

        if not calc.is_valid:
            # Overlimit attempt detected
            attempt = RefundAttempt(
                refund_id=None,
                return_request_id=rma.id,
                idempotency_key=idempotency_key,
                attempt_timestamp=now,
                requested_amount=calc.net_refund_amount,
                outcome="REJECTED_OVERLIMIT",
                reason=calc.error_message or "Refund exceeds allowable paid limit."
            )
            db.add(attempt)
            db.commit()

            raise HTTPException(
                status_code=400,
                detail=f"Refund rejected: {calc.error_message}"
            )

        total_base += calc.base_unit_refund
        total_tax += calc.tax_refund
        total_restock += calc.restocking_fee_deducted
        total_net_refund += calc.net_refund_amount

    if total_net_refund <= Decimal("0.00"):
        raise HTTPException(status_code=400, detail="Calculated refundable balance is $0.00.")

    # 3. Create Refund record
    ref_count = db.query(Refund).count() + 1
    refund_id = f"REF-2026-{ref_count:06d}"
    gateway_ref = f"GATEWAY-SIM-{ref_count:06d}-{idempotency_key[:8]}"

    refund = Refund(
        refund_id=refund_id,
        return_request_id=rma.id,
        return_line_id=refunded_return_line_id if len(target_lines) == 1 else None,
        idempotency_key=idempotency_key,
        refund_method=refund_method,
        base_unit_refund=quantize(total_base),
        tax_refund=quantize(total_tax),
        shipping_refund=Decimal("0.00"),
        restocking_fee_deducted=quantize(total_restock),
        net_refund_amount=quantize(total_net_refund),
        status="COMPLETED",
        processed_at=now,
        gateway_reference=gateway_ref
    )
    db.add(refund)
    db.flush()

    # Record successful attempt
    attempt = RefundAttempt(
        refund_id=refund.id,
        return_request_id=rma.id,
        idempotency_key=idempotency_key,
        attempt_timestamp=now,
        requested_amount=quantize(total_net_refund),
        outcome="SUCCESS",
        reason="Refund processed successfully"
    )
    db.add(attempt)

    # Update line actual_refund_amount and RMA status
    for r_line in target_lines:
        r_line.actual_refund_amount += quantize(total_net_refund)
    rma.status = "COMPLETED"

    db.commit()
    db.refresh(refund)
    db.refresh(rma)

    log_event(
        db,
        entity_type="Refund",
        entity_id=refund.refund_id,
        event_type="REFUND_COMPLETED",
        actor="refund_engine",
        new_state=refund.status,
        reason=f"Refund of ${refund.net_refund_amount} issued via {refund_method}"
    )

    return {
        "status": "COMPLETED",
        "message": "Refund processed successfully.",
        "refund": refund,
        "blocked": False
    }
