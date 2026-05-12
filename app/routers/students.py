from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.models import User, Enrollment, Attendance, Grade, Payment, Bonus, RoleEnum
from app.auth import require_role

router = APIRouter()

@router.get("/my-profile")
def my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.student))
):
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()
    group_ids = [e.group_id for e in enrollments]
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "groups": group_ids
    }

@router.get("/my-attendance")
def my_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.student))
):
    records = db.query(Attendance).filter(Attendance.student_id == current_user.id).all()
    total = len(records)
    present = len([r for r in records if r.status == "present"])
    percent = round((present / total * 100), 1) if total > 0 else 0
    return {
        "total": total,
        "present": present,
        "percent": percent,
        "records": [{"date": r.date, "status": r.status, "group_id": r.group_id} for r in records]
    }

@router.get("/my-grades")
def my_grades(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.student))
):
    grades = db.query(Grade).filter(Grade.student_id == current_user.id).all()
    return [{"score": g.score, "type": g.type, "comment": g.comment, "group_id": g.group_id} for g in grades]

@router.get("/my-payments")
def my_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.student))
):
    payments = db.query(Payment).filter(Payment.student_id == current_user.id).all()
    return [{"amount": p.amount, "month": p.month, "method": p.method, "paid_at": str(p.paid_at)} for p in payments]

@router.get("/my-rating")
def my_rating(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.student))
):
    bonuses = db.query(Bonus).filter(Bonus.user_id == current_user.id).all()
    total_bonus  = sum(b.amount for b in bonuses if b.type == "bonus")
    total_jarima = sum(b.amount for b in bonuses if b.type == "jarima")
    rating = total_bonus - total_jarima
    return {"total_bonus": total_bonus, "total_jarima": total_jarima, "net_rating": rating}

@router.get("/all")
def all_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.director, RoleEnum.reception))
):
    students = db.query(User).filter(
        User.center_id == current_user.center_id,
        User.role == RoleEnum.student
    ).all()
    return [{"id": s.id, "full_name": s.full_name, "phone": s.phone, "is_active": s.is_active} for s in students]
