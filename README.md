# Markaz Platformasi — O'quv markazi boshqaruv tizimi

## Loyiha tuzilmasi

```
markaz/
├── main.py                  # FastAPI asosiy fayl
├── requirements.txt         # Python kutubxonalari
├── markaz.db                # SQLite ma'lumotlar bazasi (auto yaratiladi)
├── app/
│   ├── auth.py              # JWT autentifikatsiya
│   ├── database/db.py       # Ma'lumotlar bazasi ulanishi
│   ├── models/models.py     # Barcha jadvallar (ORM)
│   └── routers/
│       ├── auth.py          # Ro'yxatdan o'tish / Kirish
│       ├── directors.py     # Director API
│       ├── teachers.py      # Teacher API
│       ├── students.py      # Student API
│       ├── groups.py        # Guruh API
│       ├── attendance.py    # Davomat API
│       ├── payments.py      # To'lov API
│       └── notifications.py # Bildirishnoma API
├── templates/
│   └── index.html           # Asosiy UI (barcha rollar uchun)
└── static/                  # CSS/JS fayllari (ixtiyoriy)
```

## O'rnatish va ishga tushirish

### 1. Python virtual muhit yaratish
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 2. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. Serverni ishga tushirish
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Brauzerda ochish
```
http://localhost:8000
```

## API Dokumentatsiya
```
http://localhost:8000/docs       # Swagger UI
http://localhost:8000/redoc      # ReDoc
```

## Rollar va imkoniyatlar

| Rol        | Imkoniyatlar                                              |
|------------|-----------------------------------------------------------|
| Director   | Dashboard, O'qituvchilar CRUD, Hisobot, Bonus/Jarima      |
| Reception  | O'quvchilar CRUD, To'lov qabul qilish, Guruh boshqaruvi   |
| Teacher    | Davomat belgilash, Baho qo'yish, O'z guruhlarini ko'rish  |
| Student    | Profilim, Davomatim, Baholarim, To'lovlarim, Reyting      |

## Birinchi foydalanish

1. Brauzerda `http://localhost:8000` oching
2. "Ro'yxatdan o'tish" tabini tanlang
3. Markaz nomi, telefon va parol kiriting
4. Avtomatik Director sifatida kirasiz
5. Keyin Teacher va Student qo'shishingiz mumkin

## Texnologiyalar
- **Backend**: FastAPI (Python)
- **Database**: SQLite + SQLAlchemy ORM
- **Auth**: JWT (python-jose)
- **Frontend**: HTML + CSS + Vanilla JS (single page)
- **Server**: Uvicorn (ASGI)
