from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.entities import Inspection

router = APIRouter()

@router.get("")
def list_inspections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    result: Optional[str] = None,
    disposition: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Inspection)
    if result:
        query = query.filter(Inspection.result == result)
    if disposition:
        query = query.filter(Inspection.recommended_disposition == disposition)

    total = query.count()
    items = query.order_by(Inspection.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": i.id,
                "inspection_id": i.inspection_id,
                "shipment_id": i.shipment.shipment_id if i.shipment else None,
                "return_line_id": i.return_line.return_line_id if i.return_line else None,
                "product_name": i.return_line.product.name if (i.return_line and i.return_line.product) else None,
                "inspected_quantity": i.inspected_quantity,
                "item_condition": i.item_condition,
                "packaging_condition": i.packaging_condition,
                "result": i.result,
                "damage_type": i.damage_type,
                "missing_components": i.missing_components,
                "notes": i.notes,
                "inspector_id": i.inspector_id,
                "recommended_disposition": i.recommended_disposition,
                "timestamp": i.inspection_timestamp.isoformat()
            }
            for i in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
    }

