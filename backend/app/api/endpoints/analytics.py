from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.analytics.evaluation import evaluate_platform_metrics
from app.models.entities import ReturnRequest, ReturnLine, Product, InventoryDisposition, Refund

router = APIRouter()

@router.get("/overview")
def get_analytics_overview(db: Session = Depends(get_db)):
    metrics = evaluate_platform_metrics(db)

    # Returns by Reason category
    reasons = db.query(ReturnRequest.reason_category, func.count(ReturnRequest.id)).group_by(ReturnRequest.reason_category).all()
    reasons_breakdown = [{"category": r[0], "count": r[1]} for r in reasons]

    # Returns by Product Category
    cat_query = db.query(Product.category, func.count(ReturnLine.id)).join(ReturnLine, ReturnLine.product_id == Product.id).group_by(Product.category).all()
    categories_breakdown = [{"category": c[0], "count": c[1]} for c in cat_query]

    # Returns by Channel
    channel_query = db.query(ReturnRequest.channel, func.count(ReturnRequest.id)).group_by(ReturnRequest.channel).all()
    channels_breakdown = [{"channel": ch[0], "count": ch[1]} for ch in channel_query]

    # Financial breakdown
    total_refunds = float(db.query(func.coalesce(func.sum(Refund.net_refund_amount), 0)).scalar())
    total_restock_fees = float(db.query(func.coalesce(func.sum(Refund.restocking_fee_deducted), 0)).scalar())

    return {
        "evaluation_metrics": metrics,
        "reasons_breakdown": reasons_breakdown,
        "categories_breakdown": categories_breakdown,
        "channels_breakdown": channels_breakdown,
        "financials": {
            "total_refunded_usd": total_refunds,
            "total_restocking_fees_recovered_usd": total_restock_fees
        }
    }

@router.get("/anomalies")
def get_anomaly_analytics(db: Session = Depends(get_db)):
    metrics = evaluate_platform_metrics(db)
    return {
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1_score": metrics["f1_score"],
        "total_anomalies": metrics["total_anomalies"],
        "detected_anomalies": metrics["detected_anomalies"],
        "false_positives": metrics["false_positives"],
        "detection_rate_by_issue_type": metrics["detection_rate_by_issue_type"]
    }

