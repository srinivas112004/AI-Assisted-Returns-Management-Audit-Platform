from fastapi import Header, HTTPException, Security
from app.core.config import settings

def verify_admin_key(x_admin_key: str = Header(None, alias="X-Admin-Key")):
    if not x_admin_key or x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Invalid or missing administrator credentials (X-Admin-Key)."
        )
    return True

