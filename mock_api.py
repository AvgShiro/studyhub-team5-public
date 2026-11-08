"""StudyHub Team 5 - MOCK Auth/Identity API.

Everything here is FAKE on purpose: fixed users, fake tokens, data in memory.
Purpose: let Teams 1, 2, 3, 4 and 6 build against the agreed URLs and JSON
shapes today. Later we replace the inside (real database, hashed passwords,
JWT) WITHOUT changing the URLs or response shapes.

Run:  uvicorn mock_api:app --reload --port 8000
Docs: http://localhost:8000/docs
"""
from enum import Enum
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="StudyHub Team 5 - Mock Identity API")


# ---------- The contract (agree on these with the other teams) ----------
class Role(str, Enum):
    student = "student"
    admin = "admin"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    token: str
    user_id: int          # integer for now; change only if all teams agree
    role: Role


class User(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: Role


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)


# ---------- Fake data (in memory) ----------
USERS = {
    1: {"user_id": 1, "name": "Test Student", "email": "student@th-deg.de",
        "role": "student", "password": "test123"},
    2: {"user_id": 2, "name": "Test Admin", "email": "admin@th-deg.de",
        "role": "admin", "password": "admin123"},
}


# ---------- Helpers ----------
def public(user: dict) -> User:
    """Strip the password before returning a user."""
    return User(**{k: v for k, v in user.items() if k != "password"})


def current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    """Read 'Authorization: Bearer mock-token-<id>' and return the user."""
    if not authorization or not authorization.startswith("Bearer mock-token-"):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    try:
        uid = int(authorization.removeprefix("Bearer mock-token-"))
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = USERS.get(uid)
    if not user:
        raise HTTPException(status_code=401, detail="Unknown user")
    return user


def admin_only(user: dict = Depends(current_user)) -> dict:
    if user["role"] != Role.admin.value:
        raise HTTPException(status_code=403, detail="Admins only")
    return user


# ---------- Endpoints ----------
@app.post("/auth/login", response_model=LoginResponse)
def login(body: LoginRequest):
    for u in USERS.values():
        if u["email"] == body.email and u["password"] == body.password:
            return LoginResponse(token=f"mock-token-{u['user_id']}",
                                 user_id=u["user_id"], role=u["role"])
    raise HTTPException(status_code=401, detail="Wrong email or password")


@app.get("/users/me", response_model=User)
def me(user: dict = Depends(current_user)):
    return public(user)


@app.patch("/users/me", response_model=User)
def update_me(body: ProfileUpdate, user: dict = Depends(current_user)):
    if body.name is not None:
        user["name"] = body.name
    return public(user)


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, _: dict = Depends(current_user)):
    """Other teams look up a user by ID (e.g. Team 2 showing a group member)."""
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found")
    return public(USERS[user_id])


@app.get("/admin/ping")
def admin_ping(user: dict = Depends(admin_only)):
    """Example of a role-protected endpoint (Team 4's admin features)."""
    return {"ok": True, "admin": user["name"]}


# ---------- GDPR stubs ----------
@app.get("/users/me/export")
def export_me(user: dict = Depends(current_user)):
    """Real version will also collect data from Teams 1-4 and 6."""
    return {"profile": public(user).model_dump(), "reservations": [],
            "groups": [], "notification_settings": {}, "ratings": []}


@app.delete("/users/me", status_code=204)
def delete_me(user: dict = Depends(current_user)):
    """Real version will ask every team to delete or anonymize first."""
    USERS.pop(user["user_id"], None)
