from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import verify_admin_key
from app.db.session import get_db
from app.schemas.models import DataGenerationRequest
from app.generator.generate import generate_dataset

router = APIRouter()

@router.post("/generate-data")
def trigger_data_generation(
    req: DataGenerationRequest,
    is_admin: bool = Depends(verify_admin_key),
    db: Session = Depends(get_db)
):
    if req.profile not in ["starter", "full"]:
        raise HTTPException(status_code=400, detail="Profile must be 'starter' or 'full'.")

    # Execute generator
    res = generate_dataset(profile=req.profile, seed=req.seed, export_files=True, save_to_db=True)
    return {
        "message": f"Successfully generated dataset with profile '{req.profile}' and seed {req.seed}.",
        "summary": res
    }

