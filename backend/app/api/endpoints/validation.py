from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.validators.engine import run_validation_suite

router = APIRouter()

@router.get("/report")
def get_validation_report(db: Session = Depends(get_db)):
    report = run_validation_suite(db)
    return report
