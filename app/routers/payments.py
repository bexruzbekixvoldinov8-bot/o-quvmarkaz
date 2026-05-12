from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database.db import get_db
from app.models.models import Payment, User, RoleEnum
from app.auth import require_role

router = APIRouter()

class PaymentCreate(BaseModel):
    student_id: int
    amount: float
    month: str
    method: str = "cash"
    note: Optional[str] = None

@router.post("/")
def add_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.reception, RoleEnum.director))
):
    payment = Payment(
        student_id=data.student_id,
        center_id=current_user.center_id,
        amount=data.amount,
        month=data.month,
        method=data.method,
        note=data.note
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return {"id": payment.id, "amount": payment.amount, "month": payment.month}

@router.get("/")
def list_payments(
    month: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.reception, RoleEnum.director))
):
    q = db.query(Payment).filter(Payment.center_id == current_user.center_id)
    if month:
        q = q.filter(Payment.month == month)
    payments = q.all()
    return [{"id": p.id, "student_id": p.student_id, "amount": p.amount, "month": p.month, "method": p.method} for p in payments]

@router.get("/debts")
def student_debts(
    month: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.reception, RoleEnum.director))
):
    """Students who haven't paid this month"""
    all_students = db.query(User).filter(
        User.center_id == current_user.center_id,
        User.role == RoleEnum.student,
        User.is_active == True
    ).all()
    paid_ids = {
        p.student_id for p in db.query(Payment).filter(
            Payment.center_id == current_user.center_id,
            Payment.month == month
        ).all()
    }
    debtors = [{"id": s.id, "full_name": s.full_name, "phone": s.phone}
               for s in all_students if s.id not in paid_ids]
    return {"month": month, "debtors": debtors, "count": len(debtors)}
