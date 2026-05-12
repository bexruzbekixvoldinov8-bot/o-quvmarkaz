from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database.db import get_db
from app.models.models import User, Group, Attendance, Grade, RoleEnum
from app.auth import require_role

router = APIRouter()

class AttendanceMark(BaseModel):
    student_id: int
    group_id: int
    date: str
    status: str = "present"

class GradeCreate(BaseModel):
    student_id: int
    group_id: int
    score: float
    type: str = "baho"
    comment: Optional[str] = None

@router.get("/my-groups")
def my_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.teacher))
):
    groups = db.query(Group).filter(Group.teacher_id == current_user.id, Group.is_active == True).all()
    return [{"id": g.id, "name": g.name, "course": g.course, "schedule": g.schedule} for g in groups]

@router.post("/attendance")
def mark_attendance(
    data: AttendanceMark,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.teacher))
):
    existing = db.query(Attendance).filter(
        Attendance.student_id == data.student_id,
        Attendance.group_id == data.group_id,
        Attendance.date == data.date
    ).first()
    if existing:
        existing.status = data.status
        db.commit()
        return {"detail": "Davomat yangilandi"}
    att = Attendance(
        student_id=data.student_id,
        group_id=data.group_id,
        date=data.date,
        status=data.status,
        marked_by=current_user.id
    )
    db.add(att)
    db.commit()
    return {"detail": "Davomat belgilandi"}

@router.get("/attendance/{group_id}")
def get_attendance(
    group_id: int,
    date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.teacher, RoleEnum.director))
):
    q = db.query(Attendance).filter(Attendance.group_id == group_id)
    if date:
        q = q.filter(Attendance.date == date)
    records = q.all()
    return [{"student_id": r.student_id, "date": r.date, "status": r.status} for r in records]

@router.post("/grade")
def add_grade(
    data: GradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.teacher))
):
    grade = Grade(
        student_id=data.student_id,
        teacher_id=current_user.id,
        group_id=data.group_id,
        score=data.score,
        type=data.type,
        comment=data.comment
    )
    db.add(grade)
    db.commit()
    return {"detail": "Baho qo'shildi", "score": data.score}

@router.get("/grades/{group_id}")
def get_grades(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.teacher, RoleEnum.director))
):
    grades = db.query(Grade).filter(Grade.group_id == group_id).all()
    return [{"student_id": g.student_id, "score": g.score, "type": g.type, "comment": g.comment} for g in grades]
