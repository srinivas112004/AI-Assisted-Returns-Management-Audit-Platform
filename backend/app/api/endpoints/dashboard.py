from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from app.db.session import get_db
from app.models.entities import (
    Order, ReturnRequest, ReturnLine, ReturnShipment, Inspection, Refund,
    RefundAttempt, InventoryDisposition, AnomalyRecord
)
from app.validators.engine import run_validation_suite

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_orders = db.query(Order).count()
    total_rmas = db.query(ReturnRequest).count()
    return_rate = round((total_rmas / total_orders * 100), 2) if total_orders > 0 else 0.0

    eligible_rmas = db.query(ReturnRequest).filter(ReturnRequest.overall_eligibility.in_(["FULLY_ELIGIBLE", "PARTIALLY_ELIGIBLE"])).count()
    rejected_rmas = db.query(ReturnRequest).filter(ReturnRequest.overall_eligibility == "INELIGIBLE").count()
    pending_review = db.query(ReturnRequest).filter(ReturnRequest.overall_eligibility == "PENDING_REVIEW").count()

    # Shipments received awaiting inspection
    total_delivered_shipments = db.query(ReturnShipment).filter(ReturnShipment.status == "DELIVERED").count()
    inspected_count = db.query(Inspection).count()
    pending_inspections = max(0, total_delivered_shipments - inspected_count)

    total_refund_sum = db.query(func.coalesce(func.sum(Refund.net_refund_amount), 0)).scalar()
    refund_amount = float(total_refund_sum)

    blocked_duplicates = db.query(RefundAttempt).filter(RefundAttempt.outcome == "BLOCKED_DUPLICATE").count()

    # Disposition breakdown
    dispositions = db.query(InventoryDisposition.disposition_type, func.sum(InventoryDisposition.quantity)).group_by(InventoryDisposition.disposition_type).all()
    disp_breakdown = {dtype: int(qty) for dtype, qty in dispositions}
    for dt in ["RESTOCK", "REFURBISH", "QUARANTINE", "SCRAP"]:
        disp_breakdown.setdefault(dt, 0)

    # Anomalies
    total_anomalies = db.query(AnomalyRecord).count()
    detected_anomalies = db.query(AnomalyRecord).filter(AnomalyRecord.detected == True).count()

    # Validation summary
    val_rep = run_validation_suite(db)
    pass_rate = round(val_rep["passed_checks"] / val_rep["total_checks"] * 100, 1) if val_rep["total_checks"] > 0 else 100.0

    # Recent activity
    recent_rmas = [
        {
            "id": r.id,
            "rma_number": r.rma_number,
            "order_id": r.order.order_id if r.order else None,
            "customer_name": f"{r.customer.first_name} {r.customer.last_name}" if r.customer else None,
            "status": r.status,
            "overall_eligibility": r.overall_eligibility,
            "requested_date": r.requested_date.isoformat(),
        }
        for r in db.query(ReturnRequest).order_by(ReturnRequest.id.desc()).limit(5).all()
    ]

    return {
        "cards": {
            "total_orders": total_orders,
            "return_requests": total_rmas,
            "return_rate_percent": return_rate,
            "eligible_requests": eligible_rmas,
            "rejected_requests": rejected_rmas,
            "pending_review_requests": pending_review,
            "pending_inspections": pending_inspections,
            "refund_amount": refund_amount,
            "blocked_duplicate_refunds": blocked_duplicates,
            "detected_anomalies": detected_anomalies,
            "total_anomalies": total_anomalies,
            "validation_pass_rate": pass_rate,
            "validation_overall_status": val_rep["overall_status"],
        },
        "disposition_breakdown": disp_breakdown,
        "recent_returns": recent_rmas,
    }

