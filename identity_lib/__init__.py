"""Functions other teams import instead of touching our database.

    from identity_lib import verify_token, get_user
    info = verify_token(token)       # {"user_id": 3, "role": "student"}
    user = get_user(3)               # {"user_id": 3, "name": ..., ...} or None

This is the stable surface: we may change app/ freely, but these function
names, arguments and return shapes only change after agreeing with the teams.
"""
import jwt

from app.auth import decode_token
from app.database import SessionLocal
from app.models import User
from app.schemas import UserOut


def verify_token(token: str) -> dict | None:
    """Return {"user_id": int, "role": str}, or None if invalid/expired."""
    try:
        return decode_token(token)
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


def get_user(user_id: int) -> dict | None:
    """Return the public user data as a dict, or None if there is no such user."""
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if not user:
            return None
        return UserOut.model_validate(user).model_dump(mode="json")
