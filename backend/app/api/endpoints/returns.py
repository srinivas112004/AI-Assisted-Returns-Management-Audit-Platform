from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from app.db.session import get_db
from app.models.entities import (
    ReturnRequest, ReturnLine, ReturnAuthorization, ReturnShipment,
    Inspection, Refund, InventoryDisposition, ReturnEvent, Order, Customer, Product
)
from app.schemas.models import (
    ReturnRequestCreate, AuthorizeReturnRequest, CreateShipmentRequest,
    ProcessRefundRequest, ExecuteDispositionRequest, LineOverrideRequest
)
from app.services.return_service import (
    create_return_request, evaluate_return_request, authorize_return, apply_line_override
)
from app.services.shipment_service import create_return_shipment
from app.services.refund_service import process_refund
from app.services.disposition_service import execute_inventory_disposition

router = APIRouter()

@router.get("")
def list_returns(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    eligibility: Optional[str] = None,
    channel: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ReturnRequest)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (ReturnRequest.rma_number.ilike(search_filter)) |
            (ReturnRequest.reason_category.ilike(search_filter))
        )
    if status:
        query = query.filter(ReturnRequest.status == status)
    if eligibility:
        query = query.filter(ReturnRequest.overall_eligibility == eligibility)
    if channel:
        query = query.filter(ReturnRequest.channel == channel)

    total = query.count()
    items = query.order_by(ReturnRequest.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": r.id,
                "rma_number": r.rma_number,
                "order_id": r.order.order_id if r.order else None,
                "customer_id": r.customer.customer_id if r.customer else None,
                "customer_name": f"{r.customer.first_name} {r.customer.last_name}" if r.customer else None,
                "status": r.status,
                "overall_eligibility": r.overall_eligibility,
                "requested_date": r.requested_date.isoformat(),
                "channel": r.channel,
                "reason_category": r.reason_category,
                "lines_count": len(r.lines),
                "has_authorization": r.authorization is not None,
                "shipments_count": len(r.shipments),
                "refunds_count": len(r.refunds)
            }
            for r in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
    }


@router.post("")
def submit_return(req: ReturnRequestCreate, db: Session = Depends(get_db)):
    rma = create_return_request(
        db=db,
        order_id_str=req.order_id,
        customer_id_str=req.customer_id,
        reason_category=req.reason_category,
        channel=req.channel,
        lines_data=[line.model_dump() for line in req.lines],
        customer_comments=req.customer_comments
    )
    return {
        "message": "Return request submitted and evaluated successfully.",
        "rma_number": rma.rma_number,
        "overall_eligibility": rma.overall_eligibility,
        "status": rma.status
    }


@router.get("/{return_id}")
def get_return_lifecycle(return_id: str, db: Session = Depends(get_db)):
    if return_id.isdigit():
        rma = db.query(ReturnRequest).filter(ReturnRequest.id == int(return_id)).first()
    else:
        rma = db.query(ReturnRequest).filter(ReturnRequest.rma_number == return_id).first()

    if not rma:
        raise HTTPException(status_code=404, detail="ReturnRequest not found")

    lines_detail = []
    for rl in rma.lines:
        p = rl.product
        insps = [
            {
                "inspection_id": i.inspection_id,
                "item_condition": i.item_condition,
                "packaging_condition": i.packaging_condition,
                "result": i.result,
                "damage_type": i.damage_type,
                "recommended_disposition": i.recommended_disposition,
                "inspector_id": i.inspector_id,
                "timestamp": i.inspection_timestamp.isoformat()
            }
            for i in rl.inspections
        ]
        disps = [
            {
                "disposition_id": d.disposition_id,
                "disposition_type": d.disposition_type,
                "quantity": d.quantity,
                "warehouse_location": d.warehouse_location,
                "status": d.status,
                "date": d.disposition_date.isoformat()
            }
            for d in rl.dispositions
        ]
        lines_detail.append({
            "id": rl.id,
            "return_line_id": rl.return_line_id,
            "product_id": p.id if p else None,
            "sku": p.sku if p else None,
            "name": p.name if p else None,
            "category": p.category if p else None,
            "requested_quantity": rl.requested_quantity,
            "eligible_quantity": rl.eligible_quantity,
            "approved_quantity": rl.approved_quantity,
            "rejected_quantity": rl.rejected_quantity,
            "eligibility_status": rl.eligibility_status,
            "ineligibility_reason": rl.ineligibility_reason,
            "policy_code_applied": rl.policy_code_applied,
            "override_approved": rl.override_approved,
            "override_reason": rl.override_reason,
            "override_by": rl.override_by,
            "estimated_refund_amount": float(rl.estimated_refund_amount),
            "actual_refund_amount": float(rl.actual_refund_amount),
            "disposition_status": rl.disposition_status,
            "inspections": insps,
            "dispositions": disps
        })

    shipments_data = [
        {
            "id": s.id,
            "shipment_id": s.shipment_id,
            "carrier": s.carrier,
            "tracking_number": s.tracking_number,
            "status": s.status,
            "shipped_date": s.shipped_date.isoformat() if s.shipped_date else None,
            "received_date": s.received_date.isoformat() if s.received_date else None,
            "destination_warehouse": s.destination_warehouse,
            "inspections_count": len(s.inspections)
        }
        for s in rma.shipments
    ]

    refunds_data = [
        {
            "id": rf.id,
            "refund_id": rf.refund_id,
            "idempotency_key": rf.idempotency_key,
            "refund_method": rf.refund_method,
            "base_unit_refund": float(rf.base_unit_refund),
            "tax_refund": float(rf.tax_refund),
            "restocking_fee_deducted": float(rf.restocking_fee_deducted),
            "net_refund_amount": float(rf.net_refund_amount),
            "status": rf.status,
            "processed_at": rf.processed_at.isoformat(),
            "gateway_reference": rf.gateway_reference
        }
        for rf in rma.refunds
    ]

    # Fetch audit events for this RMA
    events = db.query(ReturnEvent).filter(
        (ReturnEvent.entity_id == rma.rma_number) |
        (ReturnEvent.entity_id.in_([l.return_line_id for l in rma.lines])) |
        (ReturnEvent.entity_id.in_([s.shipment_id for s in rma.shipments])) |
        (ReturnEvent.entity_id.in_([rf.refund_id for rf in rma.refunds]))
    ).order_by(ReturnEvent.id.asc()).all()

    audit_timeline = [
        {
            "event_id": e.event_id,
            "entity_type": e.entity_type,
            "entity_id": e.entity_id,
            "event_type": e.event_type,
            "previous_state": e.previous_state,
            "new_state": e.new_state,
            "actor": e.actor,
            "reason": e.reason,
            "timestamp": e.timestamp.isoformat()
        }
        for e in events
    ]

    return {
        "id": rma.id,
        "rma_number": rma.rma_number,
        "status": rma.status,
        "overall_eligibility": rma.overall_eligibility,
        "requested_date": rma.requested_date.isoformat(),
        "channel": rma.channel,
        "reason_category": rma.reason_category,
        "customer_comments": rma.customer_comments,
        "order": {
            "order_id": rma.order.order_id,
            "order_date": rma.order.order_date.isoformat(),
            "delivery_date": rma.order.delivery_date.isoformat() if rma.order.delivery_date else None,
            "total_amount": float(rma.order.total_amount)
        } if rma.order else None,
        "customer": {
            "customer_id": rma.customer.customer_id,
            "name": f"{rma.customer.first_name} {rma.customer.last_name}",
            "email": rma.customer.email,
            "segment": rma.customer.segment
        } if rma.customer else None,
        "authorization": {
            "authorization_number": rma.authorization.authorization_number,
            "authorized_date": rma.authorization.authorized_date.isoformat(),
            "authorized_by": rma.authorization.authorized_by,
            "authorized_quantity": rma.authorization.authorized_quantity,
            "status": rma.authorization.status,
            "valid_until": rma.authorization.valid_until.isoformat()
        } if rma.authorization else None,
        "lines": lines_detail,
        "shipments": shipments_data,
        "refunds": refunds_data,
        "audit_timeline": audit_timeline
    }


@router.post("/{return_id}/evaluate")
def reevaluate_return(return_id: str, db: Session = Depends(get_db)):
    if return_id.isdigit():
        rma = db.query(ReturnRequest).filter(ReturnRequest.id == int(return_id)).first()
    else:
        rma = db.query(ReturnRequest).filter(ReturnRequest.rma_number == return_id).first()

    if not rma:
        raise HTTPException(status_code=404, detail="ReturnRequest not found")

    updated_rma = evaluate_return_request(db, rma.id)
    return {
        "message": "Return evaluated successfully.",
        "overall_eligibility": updated_rma.overall_eligibility,
        "status": updated_rma.status
    }


@router.post("/{return_id}/authorize")
def authorize_return_endpoint(return_id: str, req: AuthorizeReturnRequest, db: Session = Depends(get_db)):
    if return_id.isdigit():
        rma = db.query(ReturnRequest).filter(ReturnRequest.id == int(return_id)).first()
        rma_num = rma.rma_number if rma else None
    else:
        rma_num = return_id

    if not rma_num:
        raise HTTPException(status_code=404, detail="ReturnRequest not found")

    auth = authorize_return(
        db=db,
        rma_number_str=rma_num,
        authorized_by=req.authorized_by,
        validity_days=req.validity_days
    )
    return {
        "message": "Return authorized successfully.",
        "authorization_number": auth.authorization_number,
        "authorized_quantity": auth.authorized_quantity,
        "valid_until": auth.valid_until.isoformat()
    }


@router.post("/{return_id}/override-line")
def override_line_endpoint(return_id: str, req: LineOverrideRequest, return_line_id: str = Query(...), db: Session = Depends(get_db)):
    line = apply_line_override(
        db=db,
        return_line_id_str=return_line_id,
        override_by=req.override_by,
        override_reason=req.override_reason
    )
    return {
        "message": "Line override successfully approved and evaluated.",
        "return_line_id": line.return_line_id,
        "eligibility_status": line.eligibility_status,
        "eligible_quantity": line.eligible_quantity
    }


@router.post("/{return_id}/shipments")
def create_shipment_endpoint(return_id: str, req: CreateShipmentRequest, db: Session = Depends(get_db)):
    if return_id.isdigit():
        rma = db.query(ReturnRequest).filter(ReturnRequest.id == int(return_id)).first()
        rma_num = rma.rma_number if rma else None
    else:
        rma_num = return_id

    if not rma_num:
        raise HTTPException(status_code=404, detail="ReturnRequest not found")

    shipment = create_return_shipment(
        db=db,
        rma_number_str=rma_num,
        carrier=req.carrier,
        tracking_number=req.tracking_number,
        destination_warehouse=req.destination_warehouse
    )
    return {
        "message": "Return shipment created.",
        "shipment_id": shipment.shipment_id,
        "tracking_number": shipment.tracking_number,
        "status": shipment.status
    }


@router.post("/{return_id}/refund")
def process_refund_endpoint(return_id: str, req: ProcessRefundRequest, db: Session = Depends(get_db)):
    if return_id.isdigit():
        rma = db.query(ReturnRequest).filter(ReturnRequest.id == int(return_id)).first()
        rma_num = rma.rma_number if rma else None
    else:
        rma_num = return_id

    if not rma_num:
        raise HTTPException(status_code=404, detail="ReturnRequest not found")

    result = process_refund(
        db=db,
        rma_number_str=rma_num,
        idempotency_key=req.idempotency_key,
        return_line_id_str=req.return_line_id,
        refund_method=req.refund_method,
        apply_restocking_fee=req.apply_restocking_fee
    )
    return {
        "status": result["status"],
        "message": result["message"],
        "blocked": result["blocked"],
        "refund_id": result["refund"].refund_id if result.get("refund") else None,
        "net_refund_amount": float(result["refund"].net_refund_amount) if result.get("refund") else 0.0
    }


@router.post("/{return_id}/disposition")
def execute_disposition_endpoint(return_id: str, req: ExecuteDispositionRequest, db: Session = Depends(get_db)):
    disp = execute_inventory_disposition(
        db=db,
        return_line_id_str=req.return_line_id,
        disposition_type=req.disposition_type,
        quantity=req.quantity,
        warehouse_location=req.warehouse_location,
        technician_id=req.technician_id,
        notes=req.notes
    )
    return {
        "message": "Inventory disposition executed successfully.",
        "disposition_id": disp.disposition_id,
        "disposition_type": disp.disposition_type,
        "quantity": disp.quantity,
        "status": disp.status
    }

