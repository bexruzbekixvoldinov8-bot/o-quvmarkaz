from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import Base, engine
from app.routers import auth, directors, teachers, students, groups, attendance, payments, notifications

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Markaz Platformasi", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router,          prefix="/api/auth",          tags=["Auth"])
app.include_router(directors.router,     prefix="/api/directors",     tags=["Directors"])
app.include_router(teachers.router,      prefix="/api/teachers",      tags=["Teachers"])
app.include_router(students.router,      prefix="/api/students",      tags=["Students"])
app.include_router(groups.router,        prefix="/api/groups",        tags=["Groups"])
app.include_router(attendance.router,    prefix="/api/attendance",    tags=["Attendance"])
app.include_router(payments.router,      prefix="/api/payments",      tags=["Payments"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])

from fastapi import Request
from fastapi.responses import HTMLResponse
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
