from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, dependencies, models
from ..db import get_db

router = APIRouter(prefix="/news", tags=["news"])

@router.post("/", response_model=schemas.NewsRead)
def create_news(
    news_in: schemas.NewsCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user),
    verified_author: models.User = Depends(dependencies.require_verified_author)
):
    return crud.create_news(db, news_in, current_user.id)

@router.get("/", response_model=list[schemas.NewsRead])
def read_news(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    return crud.get_news(db, skip=skip, limit=limit)

@router.get("/{news_id}", response_model=schemas.NewsRead)
def read_news_item(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    news = crud.get_news_by_id(db, news_id)
    if not news:
        raise HTTPException(404, "News not found")
    return news

@router.put("/{news_id}", response_model=schemas.NewsRead)
def update_news(
    news_id: int,
    news_update: schemas.NewsCreate,
    db: Session = Depends(get_db),
    news: models.News = Depends(dependencies.check_news_ownership)
):
    updated_news = crud.update_news(db, news_id, news_update)
    if not updated_news:
        raise HTTPException(404, "News not found")
    return updated_news

@router.delete("/{news_id}")
def delete_news(
    news_id: int,
    db: Session = Depends(get_db),
    news: models.News = Depends(dependencies.check_news_ownership)
):
    success = crud.delete_news(db, news_id)
    if not success:
        raise HTTPException(404, "News not found")
    return {"message": "News deleted successfully"}
