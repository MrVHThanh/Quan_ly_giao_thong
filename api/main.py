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

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from api.limiter import limiter
import services.nhat_ky_service as nhat_ky_service
from config.database import get_connection, DB_PATH_DEFAULT
from api.routes._auth_helper import giai_ma_session_token, SESSION_COOKIE

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from api.routes import auth
from api.routes import tuyen_duong_route as tuyen_duong
from api.routes import doan_tuyen_route as doan_tuyen
from api.routes import doan_di_chung_route as doan_di_chung
from api.routes import danh_muc_route as danh_muc
from api.routes import he_thong_route as he_thong
from api.routes import thong_ke, ban_do

_IS_DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

app = FastAPI(
    title="Hệ thống Quản lý Đường bộ Lào Cai",
    description="Sở Xây dựng tỉnh Lào Cai",
    version="1.0.0",
    docs_url="/api/docs" if _IS_DEBUG else None,
    redoc_url="/api/redoc" if _IS_DEBUG else None,
)

# ── Rate limiter ────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ────────────────────────────────────────────────────────────────────
_allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _allowed_origins],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Security Headers ────────────────────────────────────────────────────────
class _SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if not _IS_DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(_SecurityHeadersMiddleware)


# ── Activity Log Middleware ──────────────────────────────────────────────────
class _ActivityLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Chỉ log POST thành công (2xx, 3xx redirect)
        if request.method == "POST" and response.status_code < 400:
            try:
                token = request.cookies.get(SESSION_COOKIE)
                user = giai_ma_session_token(token) if token else None
                ip = request.client.host if request.client else None
                conn = get_connection()
                try:
                    nhat_ky_service.tu_dong_ghi_hoat_dong(
                        conn, method=request.method,
                        path=request.url.path, user=user, ip_address=ip,
                    )
                finally:
                    conn.close()
            except Exception:
                pass
        return response

app.add_middleware(_ActivityLogMiddleware)

# Static files
_STATIC = os.path.join(_ROOT, "static")
if os.path.isdir(_STATIC):
    app.mount("/static", StaticFiles(directory=_STATIC), name="static")

templates = Jinja2Templates(directory=os.path.join(_ROOT, "templates"))

# ── Đọc version từ file VERSION ────────────────────────────────────────────
def _doc_version() -> str:
    try:
        with open(os.path.join(_ROOT, "VERSION"), "r") as f:
            return f.read().strip()
    except Exception:
        return "?"

_APP_VERSION = _doc_version()
templates.env.globals["app_version"] = _APP_VERSION


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
app.include_router(doan_tuyen.router,    prefix="/doan-tuyen",    tags=["Đoạn tuyến"])
app.include_router(doan_di_chung.router, prefix="/doan-di-chung", tags=["Đoạn đi chung"])
app.include_router(danh_muc.router,      prefix="/danh-muc",      tags=["Danh mục"])
app.include_router(he_thong.router,      prefix="/he-thong",      tags=["Hệ thống"])
app.include_router(thong_ke.router,      prefix="/thong-ke",      tags=["Thống kê"])
app.include_router(ban_do.router,      prefix="/ban-do",      tags=["Bản đồ"])


# ── Trang chủ → Dashboard ──────────────────────────────────────────────────
from fastapi import Depends
from api.routes._auth_helper import lay_user_hien_tai

@app.get("/", response_class=HTMLResponse)
async def trang_chu(request: Request, user=Depends(lay_user_hien_tai)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})


# ── Health check ───────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "Quản lý Đường bộ Lào Cai", "version": "1.0.0"}