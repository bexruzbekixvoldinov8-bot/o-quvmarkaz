from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import datetime
import enum

class RoleEnum(str, enum.Enum):
    superadmin = "superadmin"
    director   = "director"
    reception  = "reception"
    teacher    = "teacher"
    student    = "student"
    parent     = "parent"

class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True, index=True)
    full_name  = Column(String(150))
    phone      = Column(String(20), unique=True, index=True)
    password   = Column(String(255))
    role       = Column(Enum(RoleEnum), default=RoleEnum.student)
    center_id  = Column(Integer, ForeignKey("centers.id"), nullable=True)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    center = relationship("Center", back_populates="users")

class Center(Base):
    __tablename__ = "centers"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(200), unique=True)
    phone      = Column(String(20))
    password   = Column(String(255))
    tariff     = Column(String(50), default="basic")
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users    = relationship("User",    back_populates="center")
    groups   = relationship("Group",   back_populates="center")
    payments = relationship("Payment", back_populates="center")

class Group(Base):
    __tablename__ = "groups"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(150))
    center_id  = Column(Integer, ForeignKey("centers.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    course     = Column(String(150))
    schedule   = Column(String(200))      # "Mon,Wed,Fri 10:00"
    price      = Column(Float, default=0)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    center     = relationship("Center", back_populates="groups")
    teacher    = relationship("User", foreign_keys=[teacher_id])
    enrollments = relationship("Enrollment", back_populates="group")
    attendances = relationship("Attendance", back_populates="group")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id         = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    group_id   = Column(Integer, ForeignKey("groups.id"))
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User", foreign_keys=[student_id])
    group   = relationship("Group", back_populates="enrollments")

class Attendance(Base):
    __tablename__ = "attendances"
    id         = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    group_id   = Column(Integer, ForeignKey("groups.id"))
    date       = Column(String(20))       # "2025-05-10"
    status     = Column(String(20), default="present")  # present / absent / late
    marked_by  = Column(Integer, ForeignKey("users.id"), nullable=True)

    student = relationship("User", foreign_keys=[student_id])
    group   = relationship("Group", back_populates="attendances")

class Payment(Base):
    __tablename__ = "payments"
    id         = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    center_id  = Column(Integer, ForeignKey("centers.id"))
    amount     = Column(Float)
    month      = Column(String(20))       # "2025-05"
    method     = Column(String(50), default="cash")
    note       = Column(Text, nullable=True)
    paid_at    = Column(DateTime, default=datetime.utcnow)

    student = relationship("User", foreign_keys=[student_id])
    center  = relationship("Center", back_populates="payments")

class Grade(Base):
    __tablename__ = "grades"
    id         = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    group_id   = Column(Integer, ForeignKey("groups.id"))
    score      = Column(Float)
    type       = Column(String(50))      # test / vazifa / baho
    comment    = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User", foreign_keys=[student_id])
    teacher = relationship("User", foreign_keys=[teacher_id])

class Notification(Base):
    __tablename__ = "notifications"
    id         = Column(Integer, primary_key=True, index=True)
    center_id  = Column(Integer, ForeignKey("centers.id"), nullable=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=True)
    title      = Column(String(200))
    message    = Column(Text)
    type       = Column(String(50), default="info")   # info / warning / payment
    is_read    = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Bonus(Base):
    __tablename__ = "bonuses"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    amount     = Column(Float)
    reason     = Column(String(255))
    type       = Column(String(20), default="bonus")  # bonus / jarima
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])
