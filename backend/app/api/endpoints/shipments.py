from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.entities import ReturnShipment, ReturnRequest, Inspection
from app.schemas.models import ReceiveShipmentRequest, InspectShipmentRequest
from app.services.shipment_service import receive_shipment
from app.services.inspection_service import record_inspection

router = APIRouter()

@router.get("")
def list_shipments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    carrier: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ReturnShipment)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (ReturnShipment.shipment_id.ilike(search_filter)) |
            (ReturnShipment.tracking_number.ilike(search_filter))
        )
    if status:
        query = query.filter(ReturnShipment.status == status)
    if carrier:
        query = query.filter(ReturnShipment.carrier == carrier)

    total = query.count()
    items = query.order_by(ReturnShipment.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": s.id,
                "shipment_id": s.shipment_id,
                "rma_number": s.return_request.rma_number if s.return_request else None,
                "carrier": s.carrier,
                "tracking_number": s.tracking_number,
                "status": s.status,
                "shipped_date": s.shipped_date.isoformat() if s.shipped_date else None,
                "received_date": s.received_date.isoformat() if s.received_date else None,
                "destination_warehouse": s.destination_warehouse,
                "inspections_count": len(s.inspections),
                "created_at": s.created_at.isoformat()
            }
            for s in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
    }


@router.post("/{shipment_id}/receive")
def receive_shipment_endpoint(shipment_id: str, req: ReceiveShipmentRequest, db: Session = Depends(get_db)):
    if shipment_id.isdigit():
        shipment = db.query(ReturnShipment).filter(ReturnShipment.id == int(shipment_id)).first()
        ship_id_str = shipment.shipment_id if shipment else None
    else:
        ship_id_str = shipment_id

    if not ship_id_str:
        raise HTTPException(status_code=404, detail="Shipment not found")

    shipped = receive_shipment(db, ship_id_str, receiver_id=req.receiver_id)
    return {
        "message": "Shipment marked received at warehouse.",
        "shipment_id": shipped.shipment_id,
        "status": shipped.status,
        "received_date": shipped.received_date.isoformat() if shipped.received_date else None
    }


@router.post("/{shipment_id}/inspect")
def inspect_shipment_endpoint(shipment_id: str, req: InspectShipmentRequest, db: Session = Depends(get_db)):
    if shipment_id.isdigit():
        shipment = db.query(ReturnShipment).filter(ReturnShipment.id == int(shipment_id)).first()
        ship_id_str = shipment.shipment_id if shipment else None
    else:
        ship_id_str = shipment_id

    if not ship_id_str:
        raise HTTPException(status_code=404, detail="Shipment not found")

    insp = record_inspection(
        db=db,
        shipment_id_str=ship_id_str,
        return_line_id_str=req.return_line_id,
        inspected_quantity=req.inspected_quantity,
        item_condition=req.item_condition,
        packaging_condition=req.packaging_condition,
        damage_type=req.damage_type,
        missing_components=req.missing_components,
        notes=req.notes,
        inspector_id=req.inspector_id,
        allow_unreceived_override=req.allow_unreceived_override
    )
    return {
        "message": "Inspection recorded successfully.",
        "inspection_id": insp.inspection_id,
        "result": insp.result,
        "recommended_disposition": insp.recommended_disposition
    }

