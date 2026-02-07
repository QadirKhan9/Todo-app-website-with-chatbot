from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from sqlmodel import Session
from src.auth.middleware import get_current_user, verify_user_owns_resource
from src.models.user_model import User, UserRead
from src.database import get_session
from src.services.auth_service import get_user_by_id
import uuid


router = APIRouter()


@router.get("/{user_id}/profile", response_model=UserRead)
async def get_profile(user_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_session)):
    # Verify that the current user is accessing their own profile
    verify_user_owns_resource(current_user, user_id)

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    user = get_user_by_id(user_uuid, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/{user_id}/profile", response_model=UserRead)
async def update_profile(user_id: str, user_update: dict, current_user: dict = Depends(get_current_user), db: Session = Depends(get_session)):
    # Verify that the current user is updating their own profile
    verify_user_owns_resource(current_user, user_id)

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    user = get_user_by_id(user_uuid, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update user fields based on user_update
    for field, value in user_update.items():
        if hasattr(user, field):
            setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user