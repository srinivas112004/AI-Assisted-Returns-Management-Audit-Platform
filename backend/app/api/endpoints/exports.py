import io
import json
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import (
    Customer, Product, ReturnPolicy, Order, OrderLine, ReturnRequest,
    ReturnLine, ReturnAuthorization, ReturnShipment, Inspection,
    Refund, RefundAttempt, InventoryDisposition, InventoryMovement,
    ReturnEvent, AnomalyRecord
)

router = APIRouter()

MODEL_MAP = {
    "customers": Customer,
    "products": Product,
    "return_policies": ReturnPolicy,
    "orders": Order,
    "order_lines": OrderLine,
    "return_requests": ReturnRequest,
    "return_lines": ReturnLine,
    "return_authorizations": ReturnAuthorization,
    "return_shipments": ReturnShipment,
    "inspections": Inspection,
    "refunds": Refund,
    "refund_attempts": RefundAttempt,
    "inventory_dispositions": InventoryDisposition,
    "inventory_movements": InventoryMovement,
    "return_events": ReturnEvent,
    "ground_truth": AnomalyRecord
}

def get_entity_dataframe(entity_name: str, db: Session) -> pd.DataFrame:
    model_cls = MODEL_MAP.get(entity_name.lower())
    if not model_cls:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown entity '{entity_name}'. Available: {list(MODEL_MAP.keys())}"
        )
    
    rows = [
        {col.name: getattr(item, col.name) for col in item.__table__.columns}
        for item in db.query(model_cls).all()
    ]
    df = pd.DataFrame(rows)
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str)
    return df

@router.get("/{entity}.csv")
def export_entity_csv(entity: str, db: Session = Depends(get_db)):
    df = get_entity_dataframe(entity, db)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    
    response = Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={entity}.csv"}
    )
    return response

@router.get("/{entity}.json")
def export_entity_json(entity: str, db: Session = Depends(get_db)):
    df = get_entity_dataframe(entity, db)
    json_str = df.to_json(orient="records", indent=2)
    
    response = Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={entity}.json"}
    )
    return response
