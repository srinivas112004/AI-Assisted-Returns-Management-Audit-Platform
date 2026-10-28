from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.entities import ReturnShipment, ReturnRequest, ReturnAuthorization
from app.services.audit_service import log_event

def create_return_shipment(
    db: Session,
    rma_number_str: str,
    carrier: str = "UPS",
    tracking_number: Optional[str] = None,
    destination_warehouse: str = "WH-CENTRAL-01"
) -> ReturnShipment:
    rma = db.query(ReturnRequest).filter(ReturnRequest.rma_number == rma_number_str).first()
    if not rma:
        raise HTTPException(status_code=404, detail="ReturnRequest not found")

    if not rma.authorization:
        raise HTTPException(status_code=400, detail="Cannot create shipment for unauthorized return.")

    shipment_count = db.query(ReturnShipment).count() + 1
    shipment_id = f"RTS-2026-{shipment_count:06d}"
    
    if not tracking_number:
        tracking_number = f"1Z{carrier[:2].upper()}9999{shipment_count:06d}"

    now = datetime.now(timezone.utc)
    shipment = ReturnShipment(
        shipment_id=shipment_id,
        return_request_id=rma.id,
        return_authorization_id=rma.authorization.id,
        carrier=carrier,
        tracking_number=tracking_number,
        status="IN_TRANSIT",
        shipped_date=now,
        destination_warehouse=destination_warehouse
    )
    db.add(shipment)

    rma.status = "IN_TRANSIT"
    db.commit()
    db.refresh(shipment)
    db.refresh(rma)

    log_event(
        db,
        entity_type="ReturnShipment",
        entity_id=shipment.shipment_id,
        event_type="SHIPPED",
        actor="logistics_system",
        new_state=shipment.status,
        reason=f"Carrier {carrier}, Tracking {tracking_number}"
    )

    return shipment


def receive_shipment(
    db: Session,
    shipment_id_str: str,
    receiver_id: str = "WAREHOUSE_STATION_01"
) -> ReturnShipment:
    shipment = db.query(ReturnShipment).filter(ReturnShipment.shipment_id == shipment_id_str).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="ReturnShipment not found")

    if shipment.status == "DELIVERED":
        return shipment # Already received

    now = datetime.now(timezone.utc)
    prev_status = shipment.status
    shipment.status = "DELIVERED"
    shipment.received_date = now

    rma = db.query(ReturnRequest).filter(ReturnRequest.id == shipment.return_request_id).first()
    if rma:
        rma.status = "RECEIVED"

    db.commit()
    db.refresh(shipment)

    log_event(
        db,
        entity_type="ReturnShipment",
        entity_id=shipment.shipment_id,
        event_type="RECEIVED",
        actor=receiver_id,
        previous_state=prev_status,
        new_state=shipment.status,
        reason="Package delivered to warehouse intake dock"
    )

    return shipment
