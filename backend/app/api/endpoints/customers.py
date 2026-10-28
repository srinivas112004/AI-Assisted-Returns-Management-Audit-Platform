from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.entities import Customer

router = APIRouter()

@router.get("")
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    segment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Customer)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Customer.customer_id.ilike(search_filter)) |
            (Customer.first_name.ilike(search_filter)) |
            (Customer.last_name.ilike(search_filter)) |
            (Customer.email.ilike(search_filter))
        )
    if segment:
        query = query.filter(Customer.segment == segment)

    total = query.count()
    items = query.order_by(Customer.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": [
            {
                "id": c.id,
                "customer_id": c.customer_id,
                "name": f"{c.first_name} {c.last_name}",
                "email": c.email,
                "phone": c.phone,
                "segment": c.segment,
                "risk_score": c.risk_score,
                "orders_count": len(c.orders),
                "created_at": c.created_at.isoformat()
            }
            for c in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
    }
