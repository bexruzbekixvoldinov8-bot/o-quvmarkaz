from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.db import get_db
from app.models.models import User, Center, RoleEnum
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter()

class CenterRegister(BaseModel):
    name: str
    phone: str
    password: str

class LoginRequest(BaseModel):
    phone: str
    password: str

class UserCreate(BaseModel):
    full_name: str
    phone: str
    password: str
    role: RoleEnum
    center_id: int

@router.post("/register-center")
def register_center(data: CenterRegister, db: Session = Depends(get_db)):
    existing = db.query(Center).filter(Center.phone == data.phone).first()
    if existing:
        raise HTTPException(400, "Bu raqam allaqachon ro'yxatdan o'tgan")
    center = Center(
        name=data.name,
        phone=data.phone,
        password=hash_password(data.password)
    )
    db.add(center)
    db.commit()
    db.refresh(center)
    # Auto-create director user
    director = User(
        full_name=data.name + " (Director)",
        phone=data.phone,
        password=center.password,
        role=RoleEnum.director,
        center_id=center.id
    )
    db.add(director)
    db.commit()
    db.refresh(director)
    token = create_access_token({"sub": str(director.id), "role": director.role})
    return {"access_token": token, "token_type": "bearer", "center_id": center.id, "role": director.role}

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Telefon yoki parol noto'g'ri")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "full_name": user.full_name,
        "center_id": user.center_id
    }

@router.post("/create-user")
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == data.phone).first()
    if existing:
        raise HTTPException(400, "Bu raqam allaqachon mavjud")
    user = User(
        full_name=data.full_name,
        phone=data.phone,
        password=hash_password(data.password),
        role=data.role,
        center_id=data.center_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "full_name": user.full_name, "role": user.role}
