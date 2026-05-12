from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.models import Attendance, RoleEnum
from app.auth import require_role, get_current_user

router = APIRouter()

@router.get("/stats/{group_id}")
def attendance_stats(
    group_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(RoleEnum.teacher, RoleEnum.director))
):
    records = db.query(Attendance).filter(Attendance.group_id == group_id).all()
    stats = {}
    for r in records:
        sid = r.student_id
        if sid not in stats:
            stats[sid] = {"present": 0, "absent": 0, "late": 0}
        stats[sid][r.status] = stats[sid].get(r.status, 0) + 1
    return stats
