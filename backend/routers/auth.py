from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import (
    create_token, get_current_user, hash_password, verify_password,
)
from database import get_db
from models import User
from schemas import LoginIn, SignupIn, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["Auth"])

MAX_FAILED_ATTEMPTS = 5
LOCK_MINUTES = 15


@router.post("/signup", response_model=UserOut, status_code=201)
def signup(data: SignupIn, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter(User.email == email).first():  # R5.2
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    user = db.query(User).filter(User.email == data.email.lower()).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.locked_until and user.locked_until > now:  # R5.5
        raise HTTPException(
            status_code=423,
            detail="Account locked. Try again in 15 minutes.",
        )

    if not verify_password(data.password, user.password_hash):
        user.failed_attempts += 1
        if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = now + timedelta(minutes=LOCK_MINUTES)
            user.failed_attempts = 0
            db.commit()
            raise HTTPException(
                status_code=423,
                detail="Account locked. Try again in 15 minutes.",
            )
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user.failed_attempts = 0  # success resets the counter
    user.locked_until = None
    db.commit()
    return TokenOut(access_token=create_token(user.id))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user