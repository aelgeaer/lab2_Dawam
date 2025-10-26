# routers/users.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, dependencies, crud, models
from app.db import get_db

router = APIRouter(tags=["users"])

@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Create user. Email must be unique.
    """
    # Only admins can create users via this endpoint
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(400, "Email already registered")
        
    user = crud.create_user_with_password(db, user_in)
    return user

@router.get("/", response_model=List[schemas.UserRead])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Get list of users (pagination via skip/limit).
    """
    # Only admins can list all users
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return crud.get_users(db, skip=skip, limit=limit)

@router.get("/me", response_model=schemas.UserRead)
def get_current_user_info(
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Get current user information"""
    return current_user

@router.get("/{user_id}", response_model=schemas.UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    # Users can see their own profile, admins can see any profile
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Update user. Partial update supported.
    """
    # Users can update their own profile, admins can update any profile
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
        
    # Only admins can change verification status
    if user_update.is_verified_author is not None and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change verification status"
        )

    # Check email uniqueness (if email is being changed)
    if user_update.email and user_update.email != user.email:
        other_user = crud.get_user_by_email(db, user_update.email)
        if other_user:
            raise HTTPException(400, "Email already registered")

    # Apply changes to fields that are NOT None
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Delete user. Related records (news, comments) will be cascade deleted.
    """
    # Users can delete their own account, admins can delete any account
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
