from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from ..db.session import get_db
from ..db.models import User
from ..utils.auth import auth_service, user_manager
from ..utils.logger import api_logger

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_info: dict

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime

# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        user_data = auth_service.get_current_user(token)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database to ensure they still exist and are active
        user = db.query(User).filter(User.user_id == user_data["user_id"]).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Optional authentication dependency (for endpoints that work with or without auth)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Create new user
        hashed_password = auth_service.get_password_hash(user_data.password)
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role="analyst",  # Default role
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        api_logger.info(f"New user registered: {user_data.username}")
        
        return UserResponse(
            user_id=new_user.user_id,
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            is_active=new_user.is_active,
            created_at=new_user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token"""
    try:
        # Find user in database
        user = db.query(User).filter(User.username == login_data.username).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not auth_service.verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        token_data = {
            "sub": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
        
        access_token = auth_service.create_access_token(token_data)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        api_logger.info(f"User logged in: {user.username}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60,
            user_info={
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )

@router.post("/logout")
async def logout_user(
    current_user: dict = Depends(get_current_user)
):
    """Logout user (client should discard token)"""
    api_logger.info(f"User logged out: {current_user['username']}")
    return {"message": "Successfully logged out"}

@router.post("/refresh")
async def refresh_token(
    current_user: dict = Depends(get_current_user)
):
    """Refresh access token"""
    try:
        # Create new token with same user data
        token_data = {
            "sub": current_user["user_id"],
            "username": current_user["username"],
            "email": current_user.get("email"),
            "role": current_user["role"]
        }
        
        new_token = auth_service.create_access_token(token_data)
        
        return Token(
            access_token=new_token,
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60,
            user_info=current_user
        )
        
    except Exception as e:
        api_logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )
