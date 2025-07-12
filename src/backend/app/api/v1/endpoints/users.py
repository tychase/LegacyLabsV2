"""
User endpoints
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_user
from app.models.models import User
from app.schemas import user as user_schema

router = APIRouter()


@router.get("/me", response_model=user_schema.User)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user
    """
    return current_user


@router.put("/me", response_model=user_schema.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: user_schema.UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update current user
    """
    user = crud_user.user.update(db, db_obj=current_user, obj_in=user_in)
    return user
