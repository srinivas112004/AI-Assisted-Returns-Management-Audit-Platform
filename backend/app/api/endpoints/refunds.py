from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.entities import Refund, RefundAttempt

router = APIRouter()

@router.get("")
def list_refunds(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    method: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Refund)
    if status:
        query = query.filter(Refund.status == status)
    if method:
        query = query.filter(Refund.refund_method == method)

    total = query.count()
    items = query.order_by(Refund.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": r.id,
                "refund_id": r.refund_id,
                "rma_number": r.return_request.rma_number if r.return_request else None,
                "return_line_id": r.return_line.return_line_id if r.return_line else None,
                "idempotency_key": r.idempotency_key,
                "refund_method": r.refund_method,
                "base_unit_refund": float(r.base_unit_refund),
                "tax_refund": float(r.tax_refund),
                "shipping_refund": float(r.shipping_refund),
                "restocking_fee_deducted": float(r.restocking_fee_deducted),
                "net_refund_amount": float(r.net_refund_amount),
                "status": r.status,
                "processed_at": r.processed_at.isoformat(),
                "gateway_reference": r.gateway_reference
            }
            for r in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
    }

@router.get("/attempts")
def list_refund_attempts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    outcome: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(RefundAttempt)
    if outcome:
        query = query.filter(RefundAttempt.outcome == outcome)

    total = query.count()
    items = query.order_by(RefundAttempt.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": a.id,
                "refund_id": a.refund.refund_id if a.refund else None,
                "rma_number": a.return_request.rma_number if a.return_request else None,
                "idempotency_key": a.idempotency_key,
                "requested_amount": float(a.requested_amount),
                "outcome": a.outcome,
                "reason": a.reason,
                "timestamp": a.attempt_timestamp.isoformat()
            }
            for a in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
    }
