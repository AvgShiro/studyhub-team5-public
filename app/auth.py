"""Passwords, tokens and role checks. Keep all security code in this file."""
import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

# CHANGE THIS in real use (set TEAM5_SECRET). The default is for development only.
SECRET = os.getenv("TEAM5_SECRET", "dev-only-secret-change-me-please-32bytes")
ALGORITHM = "HS256"
TOKEN_HOURS = 8


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Return {"user_id": int, "role": str} or raise jwt.PyJWTError."""
    data = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    return {"user_id": int(data["sub"]), "role": data["role"]}


def current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    """Read 'Authorization: Bearer <token>' and return the User row."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    try:
        info = decode_token(authorization.removeprefix("Bearer "))
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.get(User, info["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="Unknown user")
    return user


def admin_only(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user
