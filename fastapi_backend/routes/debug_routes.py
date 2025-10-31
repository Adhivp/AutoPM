"""Debug routes (development only)

Provides a quick endpoint to check password hashing/verification for a given user.
DO NOT enable this in production.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from utils.password import hash_password, verify_password

router = APIRouter(prefix="/debug", tags=["Debug"])


class VerifyRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/verify-password")
def verify_password_endpoint(req: VerifyRequest, db: Session = Depends(get_db)):
    """Return stored hash, computed hash and whether they match for debugging."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stored = user.hashed_password
    computed = hash_password(req.password)
    matches = verify_password(req.password, stored)

    return {
        "email": user.email,
        "stored_hashed_password": stored,
        "computed_hashed_password": computed,
        "matches": matches,
        "is_active": bool(user.is_active)
    }
