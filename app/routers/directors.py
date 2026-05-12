from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database.db import get_db
from app.models.models import User, Center, Bonus, Payment, RoleEnum
from app.auth import get_current_user, require_role, hash_password

router = APIRouter()

class BonusCreate(BaseModel):
    user_id: int
    amount: float
    reason: str
    type: str = "bonus"  # bonus / jarima

@router.get("/dashboard")
def director_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.director, RoleEnum.superadmin))
):
    cid = current_user.center_id
    teachers = db.query(User).filter(User.center_id == cid, User.role == RoleEnum.teacher).count()
    students = db.query(User).filter(User.center_id == cid, User.role == RoleEnum.student).count()
    total_income = db.query(Payment).filter(Payment.center_id == cid).all()
    income_sum = sum(p.amount for p in total_income)
    center = db.query(Center).filter(Center.id == cid).first()
    return {
        "center_name": center.name if center else "",
        "teachers": teachers,
        "students": students,
        "total_income": income_sum,
    }

@router.get("/teachers")
def list_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.director, RoleEnum.superadmin))
):
    teachers = db.query(User).filter(
        User.center_id == current_user.center_id,
        User.role == RoleEnum.teacher
    ).all()
    return [{"id": t.id, "full_name": t.full_name, "phone": t.phone, "is_active": t.is_active} for t in teachers]

@router.delete("/teachers/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.director))
):
    teacher = db.query(User).filter(User.id == teacher_id, User.center_id == current_user.center_id).first()
    if not teacher:
        raise HTTPException(404, "O'qituvchi topilmadi")
    teacher.is_active = False
    db.commit()
    return {"detail": "O'qituvchi o'chirildi"}

@router.post("/bonus")
def give_bonus(
    data: BonusCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.director))
):
    bonus = Bonus(user_id=data.user_id, amount=data.amount, reason=data.reason, type=data.type)
    db.add(bonus)
    db.commit()
    return {"detail": f"{data.type} berildi", "amount": data.amount}

@router.get("/bonuses")
def list_bonuses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.director))
):
    bonuses = db.query(Bonus).all()
    return [{"id": b.id, "user_id": b.user_id, "amount": b.amount, "reason": b.reason, "type": b.type} for b in bonuses]

@router.get("/report")
def monthly_report(
    month: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.director))
):
    payments = db.query(Payment).filter(
        Payment.center_id == current_user.center_id,
        Payment.month == month
    ).all()
    total = sum(p.amount for p in payments)
    return {"month": month, "total_income": total, "payment_count": len(payments)}
