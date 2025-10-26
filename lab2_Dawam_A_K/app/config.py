from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://qqjdpd:password@localhost:5432/news_db"
    SECRET_KEY: str = "your-super-secret-key-change-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # GitHub OAuth
    GITHUB_CLIENT_ID: str = "Ov23li4nuQiNClfapRab"
    GITHUB_CLIENT_SECRET: str = "9eb460ab220f586604072e01c9d2fb497fb549fe"
    
    class Config:
        env_file = ".env"

settings = Settings()
