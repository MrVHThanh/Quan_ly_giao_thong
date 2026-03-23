"""
API: main.py — FastAPI application chính
Hệ thống Quản lý Đường bộ tỉnh Lào Cai — Sở Xây dựng

Cách chạy:
    uvicorn api.main:app --reload
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

Yêu cầu: pip install fastapi uvicorn jinja2 python-multipart bcrypt
"""

import os
import sys

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from api.routes import auth, doan_tuyen_route, tuyen_duong, thong_ke, ban_do

app = FastAPI(
    title="Hệ thống Quản lý Đường bộ Lào Cai",
    description="Sở Xây dựng tỉnh Lào Cai",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Static files
_STATIC = os.path.join(_ROOT, "static")
if os.path.isdir(_STATIC):
    app.mount("/static", StaticFiles(directory=_STATIC), name="static")

templates = Jinja2Templates(directory=os.path.join(_ROOT, "templates"))


# ── Jinja2 custom filters ──────────────────────────────────────────────────
def _format_ly_trinh(value) -> str:
    """Chuyển lý trình số thực → định dạng KmXXX+YYY.
    Ví dụ: 190.0 → Km190+000 | 37.557 → Km37+557
    Dùng trong template: {{ d.ly_trinh_dau | format_ly_trinh }}
    """
    if value is None:
        return "—"
    try:
        value = float(value)
        km = int(value)
        m  = round((value - km) * 1000)
        if m >= 1000:        # xử lý làm tròn tràn
            km += 1
            m = 0
        return f"Km{km}+{m:03d}"
    except (ValueError, TypeError):
        return str(value)

templates.env.filters["format_ly_trinh"] = _format_ly_trinh

# ── Đăng ký routes ─────────────────────────────────────────────────────────
app.include_router(auth.router,        prefix="/auth",       tags=["Xác thực"])
app.include_router(tuyen_duong.router, prefix="/tuyen-duong", tags=["Tuyến đường"])
app.include_router(doan_tuyen_route.router,  prefix="/doan-tuyen",  tags=["Đoạn tuyến"])
app.include_router(thong_ke.router,    prefix="/thong-ke",    tags=["Thống kê"])
app.include_router(ban_do.router,      prefix="/ban-do",      tags=["Bản đồ"])


# ── Trang chủ → Dashboard ──────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def trang_chu(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# ── Health check ───────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "Quản lý Đường bộ Lào Cai", "version": "1.0.0"}