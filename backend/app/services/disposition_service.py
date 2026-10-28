from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.models.entities import (
    InventoryDisposition, InventoryMovement, ReturnLine, Inspection, ReturnShipment, Product
)
from app.rules.disposition import validate_disposition_action
from app.services.audit_service import log_event

def execute_inventory_disposition(
    db: Session,
    return_line_id_str: str,
    disposition_type: str, # RESTOCK, REFURBISH, QUARANTINE, SCRAP
    quantity: int,
    warehouse_location: str = "WH-BIN-A12",
    technician_id: str = "TECH_DISP_01",
    notes: Optional[str] = None
) -> InventoryDisposition:
    r_line = db.query(ReturnLine).filter(ReturnLine.return_line_id == return_line_id_str).first()
    if not r_line:
        raise HTTPException(status_code=404, detail="ReturnLine not found")

    # Find the inspection associated with this return line
    inspection = db.query(Inspection).filter(Inspection.return_line_id == r_line.id).first()
    shipment = None
    if inspection:
        shipment = db.query(ReturnShipment).filter(ReturnShipment.id == inspection.return_shipment_id).first()

    shipment_status = shipment.status if shipment else "UNKNOWN"
    inspection_id = inspection.id if inspection else None
    inspection_result = inspection.result if inspection else None

    # Calculate already disposed quantity for this return line
    already_disposed = db.query(func.coalesce(func.sum(InventoryDisposition.quantity), 0)).filter(
        InventoryDisposition.return_line_id == r_line.id,
        InventoryDisposition.status == "COMPLETED"
    ).scalar()

    # Business rule validation
    validation = validate_disposition_action(
        disposition_type=disposition_type,
        inspection_id=inspection_id,
        inspection_result=inspection_result,
        shipment_status=shipment_status,
        already_disposed_quantity=already_disposed,
        line_approved_quantity=r_line.approved_quantity,
        disposition_quantity=quantity
    )

    if not validation.is_valid:
        raise HTTPException(status_code=400, detail=validation.error_message)

    disp_count = db.query(InventoryDisposition).count() + 1
    disposition_id = f"DISP-2026-{disp_count:06d}"

    now = datetime.now(timezone.utc)
    disp = InventoryDisposition(
        disposition_id=disposition_id,
        return_line_id=r_line.id,
        inspection_id=inspection_id,
        disposition_type=disposition_type,
        quantity=quantity,
        warehouse_location=warehouse_location,
        disposition_date=now,
        technician_id=technician_id,
        notes=notes,
        status="COMPLETED"
    )
    db.add(disp)
    db.flush()

    # Movement audit log
    mov_count = db.query(InventoryMovement).count() + 1
    movement_id = f"MOV-2026-{mov_count:06d}"
    movement_type_map = {
        "RESTOCK": "INBOUND_RESTOCK",
        "REFURBISH": "REFURBISH_TRANSFER",
        "QUARANTINE": "QUARANTINE_HOLD",
        "SCRAP": "SCRAP_WRITE_OFF",
    }
    mov_type = movement_type_map.get(disposition_type, "INBOUND_RESTOCK")

    movement = InventoryMovement(
        movement_id=movement_id,
        product_id=r_line.product_id,
        inventory_disposition_id=disp.id,
        movement_type=mov_type,
        quantity=quantity,
        from_location="RETURNS_INSPECTION_BAY",
        to_location=warehouse_location,
        reference_id=disp.disposition_id,
        timestamp=now
    )
    db.add(movement)

    # Update line disposition status
    new_total_disposed = already_disposed + quantity
    if new_total_disposed >= r_line.approved_quantity:
        # Check if split
        all_disps = db.query(InventoryDisposition).filter(InventoryDisposition.return_line_id == r_line.id).all()
        types = set(d.disposition_type for d in all_disps)
        if len(types) > 1:
            r_line.disposition_status = "SPLIT"
        else:
            r_line.disposition_status = disposition_type
    else:
        r_line.disposition_status = "SPLIT"

    db.commit()
    db.refresh(disp)
    db.refresh(r_line)

    log_event(
        db,
        entity_type="InventoryDisposition",
        entity_id=disp.disposition_id,
        event_type="DISPOSITION_DECIDED",
        actor=technician_id,
        new_state=disposition_type,
        reason=f"Executed disposition {disposition_type} for qty {quantity} to {warehouse_location}"
    )

    return disp
