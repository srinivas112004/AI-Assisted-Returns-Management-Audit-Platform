from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.entities import ReturnLine, RefundAttempt, AnomalyRecord, ReturnEvent

router = APIRouter()

@router.get("")
def list_exceptions(
    db: Session = Depends(get_db)
):
    # 1. Overridden Exceptions
    overridden_lines = db.query(ReturnLine).filter(ReturnLine.override_approved == True).all()
    overrides_data = [
        {
            "id": l.id,
            "type": "POLICY_OVERRIDE",
            "business_id": l.return_line_id,
            "policy_code": l.policy_code_applied,
            "override_by": l.override_by,
            "override_reason": l.override_reason,
            "requested_quantity": l.requested_quantity,
            "eligible_quantity": l.eligible_quantity,
            "date": l.created_at.isoformat()
        }
        for l in overridden_lines
    ]

    # 2. Blocked Duplicate Payments
    blocked_attempts = db.query(RefundAttempt).filter(RefundAttempt.outcome == "BLOCKED_DUPLICATE").all()
    blocked_data = [
        {
            "id": a.id,
            "type": "BLOCKED_DUPLICATE_PAYMENT",
            "business_id": a.idempotency_key,
            "rma_number": a.return_request.rma_number if a.return_request else None,
            "requested_amount": float(a.requested_amount),
            "reason": a.reason,
            "date": a.attempt_timestamp.isoformat()
        }
        for a in blocked_attempts
    ]

    # 3. Ground Truth & Monitored Anomalies
    anomalies = db.query(AnomalyRecord).all()
    anomalies_data = [
        {
            "id": ar.id,
            "type": "ANOMALY_MONITOR",
            "business_id": ar.anomaly_id,
            "issue_type": ar.issue_type,
            "affected_entity": ar.affected_entity,
            "affected_business_id": ar.affected_business_id,
            "severity": ar.severity,
            "rationale": ar.rationale,
            "expected_decision": ar.expected_business_decision,
            "detected": ar.detected,
            "date": ar.created_at.isoformat()
        }
        for ar in anomalies
    ]

    # 4. Rejected Return Lines
    rejected_lines = db.query(ReturnLine).filter(ReturnLine.eligibility_status == "INELIGIBLE").limit(20).all()
    rejected_data = [
        {
            "id": rl.id,
            "type": "REJECTED_RETURN",
            "business_id": rl.return_line_id,
            "policy_code": rl.policy_code_applied,
            "reason": rl.ineligibility_reason,
            "requested_quantity": rl.requested_quantity,
            "date": rl.created_at.isoformat()
        }
        for rl in rejected_lines
    ]

    return {
        "summary": {
            "overrides_count": len(overrides_data),
            "blocked_duplicates_count": len(blocked_data),
            "anomalies_count": len(anomalies_data),
            "rejected_lines_count": len(rejected_data)
        },
        "overrides": overrides_data,
        "blocked_duplicates": blocked_data,
        "anomalies": anomalies_data,
        "rejected_returns": rejected_data
    }

