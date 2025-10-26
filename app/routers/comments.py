from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, dependencies, models
from ..db import get_db

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=schemas.CommentRead)
def create_comment(
    comment_in: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    return crud.create_comment(db, comment_in, current_user.id)

@router.get("/", response_model=list[schemas.CommentRead])
def read_comments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    return crud.get_comments(db, skip=skip, limit=limit)

@router.get("/{comment_id}", response_model=schemas.CommentRead)
def read_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    comment = crud.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(404, "Comment not found")
    return comment

@router.put("/{comment_id}", response_model=schemas.CommentRead)
def update_comment(
    comment_id: int,
    comment_update: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    comment = dependencies.check_comment_ownership(comment_id, db, current_user)
    updated_comment = crud.update_comment(db, comment_id, comment_update.get('text', comment.text))
    if not updated_comment:
        raise HTTPException(404, "Comment not found")
    return updated_comment

@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    comment = dependencies.check_comment_ownership(comment_id, db, current_user)
    success = crud.delete_comment(db, comment_id)
    if not success:
        raise HTTPException(404, "Comment not found")
    return {"message": "Comment deleted successfully"}
