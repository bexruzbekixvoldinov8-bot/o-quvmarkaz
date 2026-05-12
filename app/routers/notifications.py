from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database.db import get_db
from app.models.models import Notification, User, RoleEnum
from app.auth import require_role, get_current_user

router = APIRouter()

class NotifCreate(BaseModel):
    user_id: Optional[int] = None
    title: str
    message: str
    type: str = "info"

@router.post("/send")
def send_notification(
    data: NotifCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.director, RoleEnum.reception))
):
    notif = Notification(
        center_id=current_user.center_id,
        user_id=data.user_id,
        title=data.title,
        message=data.message,
        type=data.type
    )
    db.add(notif)
    db.commit()
    return {"detail": "Bildirishnoma yuborildi"}

@router.get("/my")
def my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifs = db.query(Notification).filter(
        (Notification.user_id == current_user.id) |
        (Notification.center_id == current_user.center_id)
    ).order_by(Notification.created_at.desc()).limit(20).all()
    return [{"id": n.id, "title": n.title, "message": n.message, "type": n.type, "is_read": n.is_read} for n in notifs]

@router.patch("/read/{notif_id}")
def mark_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"detail": "O'qildi"}
