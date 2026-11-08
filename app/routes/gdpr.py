from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import current_user
from app.database import get_db
from app.gdpr_hooks import DELETERS, EXPORTERS
from app.models import User
from app.schemas import UserOut

router = APIRouter(prefix="/users/me", tags=["gdpr"])


@router.get("/export")
def export_me(user: User = Depends(current_user)):
    """Our own data plus whatever every registered team exports."""
    data = {"profile": UserOut.model_validate(user).model_dump(mode="json")}
    for name, exporter in EXPORTERS.items():
        data[name] = exporter(user.id)
    return data


@router.delete("", status_code=204)
def delete_me(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Ask every team to delete/anonymise first, then delete the user last."""
    for deleter in DELETERS.values():
        deleter(user.id)
    db.delete(user)
    db.commit()
