from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.entities import Inspection, ReturnShipment, ReturnLine, ReturnRequest
from app.rules.inspection import evaluate_inspection_outcome
from app.services.audit_service import log_event

def record_inspection(
    db: Session,
    shipment_id_str: str,
    return_line_id_str: str,
    inspected_quantity: int,
    item_condition: str,
    packaging_condition: str,
    damage_type: str = "NONE",
    missing_components: Optional[str] = None,
    notes: Optional[str] = None,
    inspector_id: str = "INSPECTOR_QA_01",
    allow_unreceived_override: bool = False
) -> Inspection:
    shipment = db.query(ReturnShipment).filter(ReturnShipment.shipment_id == shipment_id_str).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="ReturnShipment not found")

    return_line = db.query(ReturnLine).filter(ReturnLine.return_line_id == return_line_id_str).first()
    if not return_line:
        raise HTTPException(status_code=404, detail="ReturnLine not found")

    # Invariant: Shipment must be delivered/received before inspection
    if shipment.status != "DELIVERED" and not allow_unreceived_override:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot inspect unreceived goods. Shipment status is '{shipment.status}'. Documented exception required."
        )

    # Invariant: Inspected quantity cannot exceed approved quantity
    if inspected_quantity <= 0:
        raise HTTPException(status_code=400, detail="Inspected quantity must be > 0.")

    # Evaluate outcome deterministically
    is_received = (shipment.status == "DELIVERED")
    result, recommended_disp, apply_fee = evaluate_inspection_outcome(
        item_condition=item_condition,
        packaging_condition=packaging_condition,
        damage_type=damage_type,
        is_received=is_received
    )

    ins_count = db.query(Inspection).count() + 1
    inspection_id = f"INS-2026-{ins_count:06d}"

    now = datetime.now(timezone.utc)
    inspection = Inspection(
        inspection_id=inspection_id,
        return_shipment_id=shipment.id,
        return_line_id=return_line.id,
        inspected_quantity=inspected_quantity,
        item_condition=item_condition,
        packaging_condition=packaging_condition,
        result=result,
        damage_type=damage_type,
        missing_components=missing_components,
        notes=notes,
        inspector_id=inspector_id,
        inspection_timestamp=now,
        recommended_disposition=recommended_disp
    )
    db.add(inspection)

    # Update RMA status to INSPECTED
    rma = db.query(ReturnRequest).filter(ReturnRequest.id == return_line.return_request_id).first()
    if rma:
        rma.status = "INSPECTED"

    db.commit()
    db.refresh(inspection)

    log_event(
        db,
        entity_type="Inspection",
        entity_id=inspection.inspection_id,
        event_type="INSPECTED",
        actor=inspector_id,
        new_state=result,
        reason=f"Recommended disposition: {recommended_disp}, Item Condition: {item_condition}"
    )

    return inspection

