from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.entities import (
    ReturnRequest, ReturnLine, ReturnAuthorization, Order, OrderLine, Customer, Product, ReturnPolicy
)
from app.rules.eligibility import evaluate_line_eligibility
from app.rules.refund import calculate_line_refund
from app.services.audit_service import log_event

def create_return_request(
    db: Session,
    order_id_str: str,
    customer_id_str: str,
    reason_category: str,
    channel: str,
    lines_data: List[Dict[str, Any]],
    customer_comments: Optional[str] = None,
    requested_date: Optional[datetime] = None
) -> ReturnRequest:
    if requested_date is None:
        requested_date = datetime.now(timezone.utc)

    # 1. Validate Order and Customer
    order = db.query(Order).filter(Order.order_id == order_id_str).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{order_id_str}' not found.")

    customer = db.query(Customer).filter(Customer.customer_id == customer_id_str).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id_str}' not found.")

    if order.customer_id != customer.id:
        raise HTTPException(status_code=400, detail="Order does not belong to specified customer.")

    # 2. Generate RMA number
    rma_count = db.query(ReturnRequest).count() + 1
    rma_number = f"RMA-2026-{rma_count:06d}"

    rma = ReturnRequest(
        rma_number=rma_number,
        order_id=order.id,
        customer_id=customer.id,
        status="SUBMITTED",
        overall_eligibility="PENDING_REVIEW",
        requested_date=requested_date,
        channel=channel,
        reason_category=reason_category,
        customer_comments=customer_comments
    )
    db.add(rma)
    db.flush()

    line_idx = 1
    for item in lines_data:
        order_line_id = item["order_line_id"]
        req_qty = int(item["requested_quantity"])

        ol = db.query(OrderLine).filter(OrderLine.id == order_line_id).first()
        if not ol or ol.order_id != order.id:
            raise HTTPException(status_code=400, detail=f"Invalid OrderLine {order_line_id} for order {order_id_str}")

        return_line_id = f"RMAL-{rma_number}-{line_idx:02d}"
        
        # Initial line creation
        r_line = ReturnLine(
            return_line_id=return_line_id,
            return_request_id=rma.id,
            order_line_id=ol.id,
            product_id=ol.product_id,
            requested_quantity=req_qty,
            eligible_quantity=0,
            approved_quantity=0,
            rejected_quantity=0,
            eligibility_status="PENDING_REVIEW",
            estimated_refund_amount=Decimal("0.00"),
            actual_refund_amount=Decimal("0.00"),
            disposition_status="PENDING"
        )
        db.add(r_line)
        line_idx += 1

    db.commit()
    db.refresh(rma)

    log_event(
        db,
        entity_type="ReturnRequest",
        entity_id=rma.rma_number,
        event_type="CREATED",
        actor=f"customer:{customer.customer_id}",
        new_state=rma.status,
        reason="Initial return submission"
    )

    # Immediately evaluate eligibility
    return evaluate_return_request(db, rma.id)


def evaluate_return_request(db: Session, rma_id: int) -> ReturnRequest:
    rma = db.query(ReturnRequest).filter(ReturnRequest.id == rma_id).first()
    if not rma:
        raise HTTPException(status_code=404, detail="ReturnRequest not found")

    order = db.query(Order).filter(Order.id == rma.order_id).first()
    
    total_lines = len(rma.lines)
    eligible_count = 0
    rejected_count = 0

    for r_line in rma.lines:
        ol = db.query(OrderLine).filter(OrderLine.id == r_line.order_line_id).first()
        prod = db.query(Product).filter(Product.id == ol.product_id).first()

        # Find applicable policy
        policy = db.query(ReturnPolicy).filter(
            ReturnPolicy.category == prod.category,
            ReturnPolicy.is_active == True
        ).first()

        window_days = policy.return_window_days if policy else prod.default_return_window_days
        policy_code = policy.policy_code if policy else "POL-STD-30"
        restock_fee_pct = policy.restocking_fee_percent if policy else Decimal("0.00")

        eval_res = evaluate_line_eligibility(
            product_category=prod.category,
            product_is_returnable=prod.is_returnable,
            order_delivery_date=order.delivery_date,
            request_date=rma.requested_date,
            purchased_quantity=ol.quantity,
            already_returned_quantity=ol.returned_quantity,
            requested_quantity=r_line.requested_quantity,
            policy_window_days=window_days,
            policy_code=policy_code,
            override_approved=r_line.override_approved
        )

        r_line.eligible_quantity = eval_res.eligible_quantity
        r_line.rejected_quantity = eval_res.rejected_quantity
        r_line.policy_code_applied = eval_res.policy_code
        r_line.ineligibility_reason = eval_res.ineligibility_reason
        
        if eval_res.is_eligible:
            r_line.eligibility_status = "OVERRIDDEN" if r_line.override_approved else "ELIGIBLE"
            eligible_count += 1
            # Estimate refund
            calc = calculate_line_refund(
                unit_price=ol.unit_price,
                purchased_quantity=ol.quantity,
                return_quantity=eval_res.eligible_quantity,
                allocated_discount=ol.allocated_discount,
                line_tax=ol.line_tax,
                restocking_fee_percent=restock_fee_pct,
                apply_restocking_fee=False
            )
            r_line.estimated_refund_amount = calc.net_refund_amount
        else:
            r_line.eligibility_status = "INELIGIBLE"
            r_line.estimated_refund_amount = Decimal("0.00")
            rejected_count += 1

    # Update overall eligibility
    if eligible_count == total_lines:
        rma.overall_eligibility = "FULLY_ELIGIBLE"
        rma.status = "ELIGIBLE"
    elif eligible_count > 0:
        rma.overall_eligibility = "PARTIALLY_ELIGIBLE"
        rma.status = "PARTIALLY_ELIGIBLE"
    else:
        rma.overall_eligibility = "INELIGIBLE"
        rma.status = "REJECTED"

    db.commit()
    db.refresh(rma)

    log_event(
        db,
        entity_type="ReturnRequest",
        entity_id=rma.rma_number,
        event_type="ELIGIBILITY_EVALUATED",
        actor="rules_engine",
        new_state=rma.overall_eligibility,
        reason=f"Eligible lines: {eligible_count}/{total_lines}"
    )

    return rma


def apply_line_override(
    db: Session,
    return_line_id_str: str,
    override_by: str,
    override_reason: str
) -> ReturnLine:
    r_line = db.query(ReturnLine).filter(ReturnLine.return_line_id == return_line_id_str).first()
    if not r_line:
        raise HTTPException(status_code=404, detail="ReturnLine not found")

    r_line.override_approved = True
    r_line.override_by = override_by
    r_line.override_reason = override_reason

    db.commit()
    db.refresh(r_line)

    log_event(
        db,
        entity_type="ReturnLine",
        entity_id=r_line.return_line_id,
        event_type="EXCEPTION_OVERRIDDEN",
        actor=override_by,
        reason=override_reason
    )

    # Re-evaluate parent RMA
    evaluate_return_request(db, r_line.return_request_id)
    db.refresh(r_line)
    return r_line


def authorize_return(
    db: Session,
    rma_number_str: str,
    authorized_by: str = "SYSTEM_POLICY_ENGINE",
    validity_days: int = 14
) -> ReturnAuthorization:
    rma = db.query(ReturnRequest).filter(ReturnRequest.rma_number == rma_number_str).first()
    if not rma:
        raise HTTPException(status_code=404, detail="ReturnRequest not found")

    if rma.authorization:
        raise HTTPException(status_code=400, detail="ReturnRequest is already authorized.")

    if rma.overall_eligibility not in ["FULLY_ELIGIBLE", "PARTIALLY_ELIGIBLE"]:
        raise HTTPException(status_code=400, detail="Cannot authorize an ineligible return request.")

    total_authorized_qty = 0
    for r_line in rma.lines:
        if r_line.eligible_quantity > 0:
            r_line.approved_quantity = r_line.eligible_quantity
            total_authorized_qty += r_line.approved_quantity
            
            # Reserve in order line
            ol = db.query(OrderLine).filter(OrderLine.id == r_line.order_line_id).first()
            if ol:
                ol.returned_quantity += r_line.approved_quantity
        else:
            r_line.approved_quantity = 0

    if total_authorized_qty <= 0:
        raise HTTPException(status_code=400, detail="No eligible items to authorize.")

    auth_count = db.query(ReturnAuthorization).count() + 1
    auth_number = f"RMA-AUTH-2026-{auth_count:06d}"

    now = datetime.now(timezone.utc)
    auth = ReturnAuthorization(
        authorization_number=auth_number,
        return_request_id=rma.id,
        authorized_date=now,
        authorized_by=authorized_by,
        authorized_quantity=total_authorized_qty,
        status="ISSUED",
        valid_until=now + timedelta(days=validity_days),
        notes="Standard automated authorization"
    )
    db.add(auth)

    prev_status = rma.status
    rma.status = "AUTHORIZED"

    db.commit()
    db.refresh(auth)
    db.refresh(rma)

    log_event(
        db,
        entity_type="ReturnRequest",
        entity_id=rma.rma_number,
        event_type="AUTHORIZED",
        actor=authorized_by,
        previous_state=prev_status,
        new_state=rma.status,
        reason=f"Issued authorization {auth.authorization_number} for {total_authorized_qty} units"
    )

    return auth
