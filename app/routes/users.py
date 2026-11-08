from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import current_user
from app.database import get_db
from app.models import User
from app.schemas import ProfileUpdate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


# "/me" must come before "/{user_id}" or "me" would be read as an ID.
@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user


@router.patch("/me", response_model=UserOut)
def update_me(body: ProfileUpdate, user: User = Depends(current_user),
              db: Session = Depends(get_db)):
    if body.name is not None:
        user.name = body.name
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, _: User = Depends(current_user),
             db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
