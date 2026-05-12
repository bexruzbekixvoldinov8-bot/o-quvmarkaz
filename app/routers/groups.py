from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database.db import get_db
from app.models.models import User, Group, Enrollment, RoleEnum
from app.auth import require_role

router = APIRouter()

class GroupCreate(BaseModel):
    name: str
    course: str
    schedule: str
    price: float
    teacher_id: Optional[int] = None

class EnrollStudent(BaseModel):
    student_id: int
    group_id: int

@router.post("/")
def create_group(
    data: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.director, RoleEnum.reception))
):
    group = Group(
        name=data.name,
        center_id=current_user.center_id,
        teacher_id=data.teacher_id,
        course=data.course,
        schedule=data.schedule,
        price=data.price
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return {"id": group.id, "name": group.name}

@router.get("/")
def list_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.director, RoleEnum.reception, RoleEnum.teacher))
):
    groups = db.query(Group).filter(
        Group.center_id == current_user.center_id,
        Group.is_active == True
    ).all()
    return [{"id": g.id, "name": g.name, "course": g.course, "schedule": g.schedule, "price": g.price} for g in groups]

@router.post("/enroll")
def enroll_student(
    data: EnrollStudent,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.director, RoleEnum.reception))
):
    existing = db.query(Enrollment).filter(
        Enrollment.student_id == data.student_id,
        Enrollment.group_id == data.group_id
    ).first()
    if existing:
        raise HTTPException(400, "Student allaqachon bu guruhda")
    enr = Enrollment(student_id=data.student_id, group_id=data.group_id)
    db.add(enr)
    db.commit()
    return {"detail": "Student guruhga qo'shildi"}

@router.get("/{group_id}/students")
def group_students(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.director, RoleEnum.reception, RoleEnum.teacher))
):
    enrollments = db.query(Enrollment).filter(Enrollment.group_id == group_id).all()
    result = []
    for e in enrollments:
        s = db.query(User).filter(User.id == e.student_id).first()
        if s:
            result.append({"id": s.id, "full_name": s.full_name, "phone": s.phone})
    return result
