from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_sso.sso.github import GithubSSO
from sqlalchemy.orm import Session
from app import schemas, crud, dependencies, models
from app.db import get_db
from app.config import settings

router = APIRouter(tags=["authentication"])

github_sso = GithubSSO(
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    redirect_uri="http://localhost:8000/auth/github/callback",
    allow_insecure_http=True,
    scope=["user:email", "read:user"]
)

@router.post("/register", response_model=schemas.Token)
def register(
    user_in: schemas.UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user with email and password"""
    try:
        # Check if user already exists
        if crud.get_user_by_email(db, user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = crud.create_user_with_password(db, user_in)
        
        # Create tokens
        access_token = dependencies.create_access_token(data={"user_id": user.id})
        refresh_token = dependencies.create_refresh_token(data={"user_id": user.id})
        
        # Store refresh token
        user_agent = request.headers.get("user-agent", "")
        crud.create_refresh_token(db, user.id, refresh_token, user_agent)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/login", response_model=schemas.Token)
def login(
    user_in: schemas.UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    try:
        user = crud.authenticate_user(db, user_in.email, user_in.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create tokens
        access_token = dependencies.create_access_token(data={"user_id": user.id})
        refresh_token = dependencies.create_refresh_token(data={"user_id": user.id})
        
        # Store refresh token
        user_agent = request.headers.get("user-agent", "")
        crud.create_refresh_token(db, user.id, refresh_token, user_agent)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/refresh", response_model=schemas.Token)
def refresh_token(
    refresh_request: schemas.RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    try:
        token_data = dependencies.verify_token(refresh_request.refresh_token)
        if not token_data or token_data.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = token_data.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify refresh token exists in database
        refresh_token_obj = crud.get_refresh_token(db, refresh_request.refresh_token)
        if not refresh_token_obj or refresh_token_obj.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired or invalid"
            )
        
        # Create new tokens
        access_token = dependencies.create_access_token(data={"user_id": user_id})
        new_refresh_token = dependencies.create_refresh_token(data={"user_id": user_id})
        
        # Update refresh token in database
        user_agent = request.headers.get("user-agent", "")
        crud.update_refresh_token(db, refresh_request.refresh_token, new_refresh_token, user_agent)
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.post("/logout")
def logout(
    refresh_request: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Logout by invalidating refresh token"""
    try:
        crud.delete_refresh_token(db, refresh_request.refresh_token)
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Logout failed: {str(e)}"
        )

@router.get("/sessions", response_model=list[schemas.SessionInfo])
def get_my_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Get active sessions for current user"""
    try:
        return crud.get_user_sessions(db, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get sessions: {str(e)}"
        )

@router.get("/github")
async def github_auth():
    """Initiate GitHub OAuth flow"""
    return await github_sso.get_login_redirect()

@router.get("/github/callback", response_model=schemas.Token)
async def github_callback(request: Request, db: Session = Depends(get_db)):
    """GitHub OAuth callback"""
    try:
        user_info = await github_sso.verify_and_process(request)
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Authentication failed")
        
        # Find or create user
        user = db.query(models.User).filter(models.User.github_id == user_info.id).first()
        if not user:
            # Check if email already exists
            if user_info.email:
                existing_user = db.query(models.User).filter(models.User.email == user_info.email).first()
                if existing_user:
                    # Link GitHub account to existing user
                    existing_user.github_id = user_info.id
                    db.commit()
                    user = existing_user
            
            if not user:
                # Create new user
                user = models.User(
                    name=user_info.display_name or user_info.email or f"user_{user_info.id}",
                    email=user_info.email or f"{user_info.id}@github.user",
                    github_id=user_info.id,
                    avatar=user_info.picture,
                    is_verified_author=True  # Auto-verify GitHub users
                )
                db.add(user)
                db.commit()
                db.refresh(user)
        
        # Create tokens
        access_token = dependencies.create_access_token(data={"user_id": user.id})
        refresh_token = dependencies.create_refresh_token(data={"user_id": user.id})
        
        # Store refresh token
        user_agent = request.headers.get("user-agent", "")
        crud.create_refresh_token(db, user.id, refresh_token, user_agent)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")
