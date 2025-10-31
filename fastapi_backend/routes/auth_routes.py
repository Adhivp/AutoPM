"""
Authentication routes for registration, login, and user management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import get_db
from models.user import User, UserRole
from services import auth_service
from utils.jwt_handler import verify_token

router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth2 scheme for JWT token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Pydantic models for request/response validation
class UserRegister(BaseModel):
    """User registration request model"""
    email: EmailStr
    password: str
    full_name: str
    role: Optional[UserRole] = UserRole.MEMBER


class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model (without sensitive data)"""
    id: int
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response model"""
    access_token: str
    token_type: str


# Dependency to get current user from JWT token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        token: JWT token from Authorization header
        db: Database session
    
    Returns:
        User object
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    
    user = auth_service.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


# Dependency to check if user has admin role
async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensure current user has admin role
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User object if admin
    
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Args:
        user_data: User registration data
        db: Database session
    
    Returns:
        Created user object (without password)
    """
    user = auth_service.register_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=user_data.role
    )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login user and return JWT access token
    
    Args:
        form_data: OAuth2 password request form (username=email, password)
        db: Database session
    
    Returns:
        JWT access token and token type
    """
    # OAuth2PasswordRequestForm uses 'username' field, but we use it for email
    token_data = auth_service.login_user(db, form_data.username, form_data.password)
    return token_data


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Args:
        current_user: Current authenticated user from token
    
    Returns:
        Current user object
    """
    return current_user


@router.get("/verify")
async def verify_token_endpoint(current_user: User = Depends(get_current_user)):
    """
    Verify if the provided token is valid
    
    Args:
        current_user: Current authenticated user from token
    
    Returns:
        Success message with user email
    """
    return {
        "message": "Token is valid",
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value
    }
