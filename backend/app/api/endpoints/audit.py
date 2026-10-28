from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.entities import ReturnEvent

router = APIRouter()

@router.get("")
def list_audit_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    event_type: Optional[str] = None,
    actor: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ReturnEvent)
    if entity_type:
        query = query.filter(ReturnEvent.entity_type == entity_type)
    if entity_id:
        query = query.filter(ReturnEvent.entity_id == entity_id)
    if event_type:
        query = query.filter(ReturnEvent.event_type == event_type)
    if actor:
        query = query.filter(ReturnEvent.actor.ilike(f"%{actor}%"))

    total = query.count()
    items = query.order_by(ReturnEvent.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": e.id,
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
            for e in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
    }

