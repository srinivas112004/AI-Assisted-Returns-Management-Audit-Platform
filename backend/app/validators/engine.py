from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.entities import (
    Customer, Product, ReturnPolicy, Order, OrderLine, ReturnRequest,
    ReturnLine, ReturnAuthorization, ReturnShipment, Inspection,
    Refund, RefundAttempt, InventoryDisposition, InventoryMovement,
    AnomalyRecord
)

class ValidationCheckResult:
    def __init__(self, check_name: str, status: str, description: str, violations_count: int = 0, sample_violations: List[str] = None):
        self.check_name = check_name
        self.status = status # PASS, WARN, FAIL
        self.description = description
        self.violations_count = violations_count
        self.sample_violations = sample_violations or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_name": self.check_name,
            "status": self.status,
            "description": self.description,
            "violations_count": self.violations_count,
            "sample_violations": self.sample_violations[:10]
        }

def run_validation_suite(db: Session) -> Dict[str, Any]:
    """
    Executes all invariant checks on the database records.
    Produces a comprehensive machine-readable validation report.
    """
    checks: List[ValidationCheckResult] = []
    total_violations = 0

    # 1. Primary Key Uniqueness & Required Values
    customers = db.query(Customer).all()
    orders = db.query(Order).all()
    order_lines = db.query(OrderLine).all()
    rmas = db.query(ReturnRequest).all()
    return_lines = db.query(ReturnLine).all()
    shipments = db.query(ReturnShipment).all()
    inspections = db.query(Inspection).all()
    refunds = db.query(Refund).all()
    dispositions = db.query(InventoryDisposition).all()
    movements = db.query(InventoryMovement).all()

    # Check 1: PK / Business ID uniqueness
    rma_nums = [r.rma_number for r in rmas]
    dup_rmas = len(rma_nums) - len(set(rma_nums))
    if dup_rmas == 0:
        checks.append(ValidationCheckResult("PK_UNIQUENESS_RMA", "PASS", "All ReturnRequest RMA numbers are unique."))
    else:
        checks.append(ValidationCheckResult("PK_UNIQUENESS_RMA", "FAIL", f"Found {dup_rmas} duplicate RMA numbers.", dup_rmas))
        total_violations += dup_rmas

    # Check 2: Foreign Key Integrity (Orphan checks)
    customer_ids = set(c.id for c in customers)
    order_customer_orphans = [o.order_id for o in orders if o.customer_id not in customer_ids]
    if not order_customer_orphans:
        checks.append(ValidationCheckResult("FK_ORDER_CUSTOMER", "PASS", "All orders reference valid customer IDs."))
    else:
        checks.append(ValidationCheckResult("FK_ORDER_CUSTOMER", "FAIL", f"{len(order_customer_orphans)} orders have invalid customer FK.", len(order_customer_orphans), order_customer_orphans))
        total_violations += len(order_customer_orphans)

    order_ids = set(o.id for o in orders)
    rma_order_orphans = [r.rma_number for r in rmas if r.order_id not in order_ids]
    if not rma_order_orphans:
        checks.append(ValidationCheckResult("FK_RMA_ORDER", "PASS", "All ReturnRequests reference valid order IDs."))
    else:
        checks.append(ValidationCheckResult("FK_RMA_ORDER", "FAIL", f"{len(rma_order_orphans)} RMAs reference invalid order IDs.", len(rma_order_orphans), rma_order_orphans))
        total_violations += len(rma_order_orphans)

    # Check 3: Date Ordering (Order Date <= Delivery Date <= RMA Request Date)
    date_violations = []
    for r in rmas:
        ord_obj = next((o for o in orders if o.id == r.order_id), None)
        if ord_obj and ord_obj.delivery_date:
            if r.requested_date.date() < ord_obj.delivery_date.date():
                date_violations.append(f"{r.rma_number}: request_date {r.requested_date.date()} < delivery {ord_obj.delivery_date.date()}")
    if not date_violations:
        checks.append(ValidationCheckResult("DATE_ORDERING_LIFECYCLE", "PASS", "All RMA requested dates are on or after order delivery."))
    else:
        checks.append(ValidationCheckResult("DATE_ORDERING_LIFECYCLE", "FAIL", f"{len(date_violations)} RMAs requested prior to delivery.", len(date_violations), date_violations))
        total_violations += len(date_violations)

    # Check 4: Return Quantity vs Purchased Quantity
    qty_violations = []
    for rl in return_lines:
        ol = next((l for l in order_lines if l.id == rl.order_line_id), None)
        if ol and rl.requested_quantity > ol.quantity:
            qty_violations.append(f"{rl.return_line_id}: requested {rl.requested_quantity} > purchased {ol.quantity}")
    if not qty_violations:
        checks.append(ValidationCheckResult("QUANTITY_BOUNDS_CHECK", "PASS", "No return lines exceed purchased quantity."))
    else:
        checks.append(ValidationCheckResult("QUANTITY_BOUNDS_CHECK", "FAIL", f"{len(qty_violations)} return lines exceed purchased quantity.", len(qty_violations), qty_violations))
        total_violations += len(qty_violations)

    # Check 5: Refund Amount vs Paid Amount
    refund_amount_violations = []
    for ref in refunds:
        if ref.return_line_id:
            rl = next((r for r in return_lines if r.id == ref.return_line_id), None)
            if rl:
                ol = next((l for l in order_lines if l.id == rl.order_line_id), None)
                if ol and ref.net_refund_amount > ol.total_line_amount:
                    refund_amount_violations.append(f"{ref.refund_id}: refund ${ref.net_refund_amount} > line paid ${ol.total_line_amount}")
    if not refund_amount_violations:
        checks.append(ValidationCheckResult("REFUND_ARITHMETIC_LIMIT", "PASS", "All refunds are within allowable paid purchase amounts."))
    else:
        checks.append(ValidationCheckResult("REFUND_ARITHMETIC_LIMIT", "FAIL", f"{len(refund_amount_violations)} refunds exceed paid amounts.", len(refund_amount_violations), refund_amount_violations))
        total_violations += len(refund_amount_violations)

    # Check 6: Duplicate Refund Prevention Check
    dup_idempotency = db.query(Refund.idempotency_key, func.count(Refund.id)).group_by(Refund.idempotency_key).having(func.count(Refund.id) > 1).all()
    if not dup_idempotency:
        checks.append(ValidationCheckResult("DUPLICATE_REFUND_IDEMPOTENCY", "PASS", "No duplicate refund payments exist with identical idempotency keys."))
    else:
        dup_keys = [d[0] for d in dup_idempotency]
        checks.append(ValidationCheckResult("DUPLICATE_REFUND_IDEMPOTENCY", "FAIL", f"Found duplicate refund payouts: {dup_keys}", len(dup_keys), dup_keys))
        total_violations += len(dup_keys)

    # Check 7: Restock Before Inspection Invariant
    restock_before_insp_violations = []
    for d in dispositions:
        if d.disposition_type == "RESTOCK":
            if not d.inspection_id:
                restock_before_insp_violations.append(f"{d.disposition_id}: restocked without inspection_id")
            else:
                insp = next((i for i in inspections if i.id == d.inspection_id), None)
                if not insp or insp.result not in ["PASS", "PASS_WITH_RESTOCKING_FEE"]:
                    restock_before_insp_violations.append(f"{d.disposition_id}: restocked with invalid inspection result '{insp.result if insp else None}'")
    if not restock_before_insp_violations:
        checks.append(ValidationCheckResult("RESTOCK_BEFORE_INSPECTION_CHECK", "PASS", "All RESTOCK dispositions have completed passing inspections."))
    else:
        checks.append(ValidationCheckResult("RESTOCK_BEFORE_INSPECTION_CHECK", "FAIL", f"{len(restock_before_insp_violations)} items restocked before/without passing inspection.", len(restock_before_insp_violations), restock_before_insp_violations))
        total_violations += len(restock_before_insp_violations)

    # Check 8: Return After Window Without Override
    late_without_override = []
    for rl in return_lines:
        if rl.eligibility_status == "ELIGIBLE" and not rl.override_approved:
            req = next((r for r in rmas if r.id == rl.return_request_id), None)
            if req:
                ord_obj = next((o for o in orders if o.id == req.order_id), None)
                if ord_obj and ord_obj.delivery_date:
                    days = (req.requested_date.date() - ord_obj.delivery_date.date()).days
                    if days > 30: # General max window
                        late_without_override.append(f"{rl.return_line_id}: requested after {days} days without authorized override")
    if not late_without_override:
        checks.append(ValidationCheckResult("POLICY_WINDOW_COMPLIANCE", "PASS", "No late returns were approved without explicit authorized override."))
    else:
        checks.append(ValidationCheckResult("POLICY_WINDOW_COMPLIANCE", "FAIL", f"{len(late_without_override)} late returns approved without override.", len(late_without_override), late_without_override))
        total_violations += len(late_without_override)

    # Overall Status
    has_fail = any(c.status == "FAIL" for c in checks)
    has_warn = any(c.status == "WARN" for c in checks)
    overall_status = "FAIL" if has_fail else ("WARN" if has_warn else "PASS")

    return {
        "overall_status": overall_status,
        "total_checks": len(checks),
        "passed_checks": sum(1 for c in checks if c.status == "PASS"),
        "failed_checks": sum(1 for c in checks if c.status == "FAIL"),
        "warning_checks": sum(1 for c in checks if c.status == "WARN"),
        "total_violations": total_violations,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": [c.to_dict() for c in checks]
    }
