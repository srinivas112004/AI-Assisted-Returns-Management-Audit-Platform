from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.entities import InventoryDisposition, InventoryMovement

router = APIRouter()

@router.get("")
def list_dispositions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    disposition_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(InventoryDisposition)
    if disposition_type:
        query = query.filter(InventoryDisposition.disposition_type == disposition_type)

    total = query.count()
    items = query.order_by(InventoryDisposition.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": d.id,
                "disposition_id": d.disposition_id,
                "return_line_id": d.return_line.return_line_id if d.return_line else None,
                "product_name": d.return_line.product.name if (d.return_line and d.return_line.product) else None,
                "inspection_id": d.inspection.inspection_id if d.inspection else None,
                "disposition_type": d.disposition_type,
                "quantity": d.quantity,
                "warehouse_location": d.warehouse_location,
                "status": d.status,
                "technician_id": d.technician_id,
                "notes": d.notes,
                "date": d.disposition_date.isoformat()
            }
            for d in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
    }

@router.get("/movements")
def list_movements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    movement_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(InventoryMovement)
    if movement_type:
        query = query.filter(InventoryMovement.movement_type == movement_type)

    total = query.count()
    items = query.order_by(InventoryMovement.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": m.id,
                "movement_id": m.movement_id,
                "product_sku": m.product.sku if m.product else None,
                "product_name": m.product.name if m.product else None,
                "movement_type": m.movement_type,
                "quantity": m.quantity,
                "from_location": m.from_location,
                "to_location": m.to_location,
                "reference_id": m.reference_id,
                "timestamp": m.timestamp.isoformat()
            }
            for m in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
    }
