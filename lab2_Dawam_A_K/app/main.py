# main.py
from fastapi import FastAPI
from app.db import engine, Base
from app.routers import users, news, comments, auth

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="News API - lab2_Dawam_A_K",
    version="2.0.0",
    description="API for news with authentication and authorization"
)

# Include routers
app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users")
app.include_router(news.router, prefix="/news")
app.include_router(comments.router, prefix="/comments")

@app.get("/")
def read_root():
    return {"message": "News API with Auth is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
