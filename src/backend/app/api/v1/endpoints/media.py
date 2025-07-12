"""
Media endpoints
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api import deps
from app.models.models import User

router = APIRouter()


@router.post("/upload")
async def upload_media(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    file: UploadFile = File(...),
) -> Any:
    """
    Upload media file
    """
    # TODO: Implement media upload
    return {"filename": file.filename, "size": file.size}
