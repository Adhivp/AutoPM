"""
Authentication service for user registration, login, and token management
"""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User, UserRole
from utils.password import hash_password, verify_password
from utils.jwt_handler import create_access_token


def register_user(db: Session, email: str, password: str, full_name: str, role: UserRole = UserRole.MEMBER) -> User:
    """
    Register a new user
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
        full_name: User's full name
        role: User role (default: MEMBER)
    
    Returns:
        Created user object
    
    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    hashed_password = hash_password(password)
    new_user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        role=role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
    
    Returns:
        User object if authentication successful, None otherwise
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    if not user.is_active:
        return None
    
    return user


def login_user(db: Session, email: str, password: str) -> dict:
    """
    Login user and generate JWT token
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
    
    Returns:
        Dictionary with access_token and token_type
    
    Raises:
        HTTPException: If authentication fails
    """
    user = authenticate_user(db, email, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token with user information
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Get user by ID
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get user by email
    
    Args:
        db: Database session
        email: User email
    
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()
