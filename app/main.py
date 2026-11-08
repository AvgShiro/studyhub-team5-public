"""Entry point. Run:  uvicorn app.main:app --reload --port 8000"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import select

from app.auth import admin_only, hash_password
from app.database import Base, SessionLocal, engine
from app.models import User
from app.routes import gdpr, login, users


def seed_test_users() -> None:
    """Create the same test accounts as the mock API (development only)."""
    with SessionLocal() as db:
        if db.scalar(select(User).limit(1)):
            return
        db.add_all([
            User(email="student@th-deg.de", name="Test Student", role="student",
                 password_hash=hash_password("test123")),
            User(email="admin@th-deg.de", name="Test Admin", role="admin",
                 password_hash=hash_password("admin123")),
        ])
        db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    seed_test_users()
    yield


app = FastAPI(title="StudyHub Team 5 - Identity API", lifespan=lifespan)
app.include_router(login.router)
app.include_router(users.router)
app.include_router(gdpr.router)


@app.get("/admin/ping", tags=["admin"])
def admin_ping(user: User = Depends(admin_only)):
    """Example of a role-protected endpoint (Team 4's admin features)."""
    return {"ok": True, "admin": user.name}
