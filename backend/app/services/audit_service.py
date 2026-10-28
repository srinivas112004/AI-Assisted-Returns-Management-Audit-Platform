from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.entities import ReturnEvent

def log_event(
    db: Session,
    entity_type: str,
    entity_id: str,
    event_type: str,
    actor: str,
    previous_state: Optional[str] = None,
    new_state: Optional[str] = None,
    reason: Optional[str] = None,
    timestamp: Optional[datetime] = None
) -> ReturnEvent:
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    # Generate sequential event id if needed
    count = db.query(ReturnEvent).count() + 1
    event_id = f"EVT-2026-{count:06d}"

    evt = ReturnEvent(
        event_id=event_id,
        entity_type=entity_type,
        entity_id=entity_id,
        event_type=event_type,
        previous_state=previous_state,
        new_state=new_state,
        actor=actor,
        reason=reason,
        timestamp=timestamp
    )
    db.add(evt)
    db.commit()
    db.refresh(evt)
    return evt

