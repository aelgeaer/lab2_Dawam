from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models, schemas, auth
from .config import settings
from fastapi import HTTPException
from typing import List, Optional

# User CRUD operations
def create_user_with_password(db: Session, user_in: schemas.UserCreate) -> models.User:
    password_hash = auth.get_password_hash(user_in.password) if user_in.password else None
    user = models.User(
        name=user_in.name,
        email=user_in.email,
        password_hash=password_hash,
        avatar=user_in.avatar,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_or_create_user_from_github(db: Session, github_user) -> models.User:
    user = db.query(models.User).filter(models.User.github_id == github_user.id).first()
    if user:
        return user
    
    # Check if email already exists
    if github_user.email:
        existing_user = db.query(models.User).filter(models.User.email == github_user.email).first()
        if existing_user:
            # Link GitHub account to existing user
            existing_user.github_id = github_user.id
            db.commit()
            db.refresh(existing_user)
            return existing_user
    
    # Create new user
    user = models.User(
        name=github_user.display_name or github_user.email,
        email=github_user.email,
        github_id=github_user.id,
        avatar=github_user.picture,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if not user or not user.password_hash:
        return None
    if not auth.verify_password(password, user.password_hash):
        return None
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()
    
def get_user_by_github_id(db: Session, github_id: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.github_id == github_id).first()

# Refresh Token operations
def create_refresh_token(db: Session, user_id: int, token: str, user_agent: str):
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = models.RefreshToken(
        user_id=user_id,
        token=token,
        user_agent=user_agent,
        expires_at=expires_at
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token

def get_refresh_token(db: Session, token: str) -> Optional[models.RefreshToken]:
    return db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()

def update_refresh_token(db: Session, old_token: str, new_token: str, user_agent: str):
    refresh_token = get_refresh_token(db, old_token)
    if refresh_token:
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token.token = new_token
        refresh_token.user_agent = user_agent
        refresh_token.expires_at = expires_at
        db.commit()
        db.refresh(refresh_token)
    return refresh_token

def delete_refresh_token(db: Session, token: str):
    refresh_token = get_refresh_token(db, token)
    if refresh_token:
        db.delete(refresh_token)
        db.commit()
        return True
    return False

def get_user_sessions(db: Session, user_id: int) -> List[models.RefreshToken]:
    return db.query(models.RefreshToken).filter(
        models.RefreshToken.user_id == user_id,
        models.RefreshToken.expires_at > datetime.utcnow()
    ).all()

# News CRUD operations
def create_news(db: Session, news_in: schemas.NewsCreate, author_id: int):
    news = models.News(
        title=news_in.title,
        content=news_in.content,
        author_id=author_id,
        cover=news_in.cover
    )
    db.add(news)
    db.commit()
    db.refresh(news)
    return news

def get_news(db: Session, skip: int = 0, limit: int = 100) -> List[models.News]:
    return db.query(models.News).offset(skip).limit(limit).all()

def get_news_by_id(db: Session, news_id: int) -> Optional[models.News]:
    return db.query(models.News).filter(models.News.id == news_id).first()

def update_news(db: Session, news_id: int, news_update: schemas.NewsCreate):
    news = get_news_by_id(db, news_id)
    if not news:
        return None
    
    for field, value in news_update.dict(exclude_unset=True).items():
        setattr(news, field, value)
    
    db.commit()
    db.refresh(news)
    return news

def delete_news(db: Session, news_id: int):
    news = get_news_by_id(db, news_id)
    if not news:
        return False
    db.delete(news)
    db.commit()
    return True

# Comment CRUD operations
def create_comment(db: Session, comment_in: schemas.CommentCreate, author_id: int):
    # Check if news exists
    news = get_news_by_id(db, comment_in.news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    comment = models.Comment(
        text=comment_in.text,
        news_id=comment_in.news_id,
        author_id=author_id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def get_comments(db: Session, skip: int = 0, limit: int = 100) -> List[models.Comment]:
    return db.query(models.Comment).offset(skip).limit(limit).all()

def get_comment_by_id(db: Session, comment_id: int) -> Optional[models.Comment]:
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

def update_comment(db: Session, comment_id: int, text: str):
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        return None
    comment.text = text
    db.commit()
    db.refresh(comment)
    return comment

def delete_comment(db: Session, comment_id: int):
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        return False
    db.delete(comment)
    db.commit()
    return True

def get_comments_by_news(db: Session, news_id: int, skip: int = 0, limit: int = 100) -> List[models.Comment]:
    return db.query(models.Comment)\
        .filter(models.Comment.news_id == news_id)\
        .order_by(models.Comment.published_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
