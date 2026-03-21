"""
Route: auth.py — Xác thực & phân quyền
GET  /auth/login         → form đăng nhập
POST /auth/login         → xử lý đăng nhập, set session cookie
GET  /auth/logout        → đăng xuất
GET  /auth/dang-ky       → form đăng ký
POST /auth/dang-ky       → xử lý đăng ký
GET  /auth/cho-duyet     → danh sách chờ duyệt (ADMIN)
POST /auth/duyet/{id}    → duyệt tài khoản (ADMIN)
"""

import os
import sys

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.database import get_db
from api.routes._auth_helper import (
    lay_user_hien_tai, yeu_cau_dang_nhap, yeu_cau_quyen_admin,
    tao_session_token, xoa_session_token, SESSION_COOKIE
)
import services.nguoi_dung_service as nd_service

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(_ROOT, "templates"))


@router.get("/login", response_class=HTMLResponse)
async def form_dang_nhap(request: Request):
    return templates.TemplateResponse("auth/login.html", {
        "request": request, "loi": None
    })


@router.post("/login")
async def xu_ly_dang_nhap(
    request: Request,
    ten_dang_nhap: str = Form(...),
    mat_khau: str = Form(...),
    conn=Depends(get_db),
):
    try:
        nguoi_dung = nd_service.dang_nhap(conn, ten_dang_nhap, mat_khau)
        token = tao_session_token(nguoi_dung.id, nguoi_dung.loai_quyen)
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(SESSION_COOKIE, token, httponly=True, max_age=86400 * 7)
        return response
    except nd_service.DangNhapThatBaiError as e:
        return templates.TemplateResponse("auth/login.html", {
            "request": request, "loi": str(e)
        }, status_code=401)


@router.get("/logout")
async def dang_xuat(response: Response):
    resp = RedirectResponse(url="/auth/login", status_code=302)
    resp.delete_cookie(SESSION_COOKIE)
    return resp


@router.get("/dang-ky", response_class=HTMLResponse)
async def form_dang_ky(request: Request):
    return templates.TemplateResponse("auth/dang_ky.html", {
        "request": request, "loi": None
    })


@router.post("/dang-ky")
async def xu_ly_dang_ky(
    request: Request,
    ten_dang_nhap: str = Form(...),
    mat_khau: str = Form(...),
    ho_ten: str = Form(...),
    chuc_vu: str = Form(None),
    email: str = Form(None),
    so_dien_thoai: str = Form(None),
    conn=Depends(get_db),
):
    try:
        nd_service.dang_ky(conn, ten_dang_nhap, mat_khau, ho_ten,
                           chuc_vu=chuc_vu, email=email, so_dien_thoai=so_dien_thoai)
        return templates.TemplateResponse("auth/dang_ky_thanh_cong.html", {"request": request})
    except nd_service.NguoiDungServiceError as e:
        return templates.TemplateResponse("auth/dang_ky.html", {
            "request": request, "loi": str(e)
        }, status_code=400)


@router.get("/cho-duyet", response_class=HTMLResponse)
async def danh_sach_cho_duyet(
    request: Request,
    user=Depends(yeu_cau_quyen_admin),
    conn=Depends(get_db),
):
    danh_sach = nd_service.lay_cho_duyet(conn)
    return templates.TemplateResponse("auth/cho_duyet.html", {
        "request": request, "danh_sach": danh_sach, "user": user
    })


@router.post("/duyet/{id}")
async def duyet_tai_khoan(
    id: int,
    loai_quyen: str = Form("BIEN_TAP"),
    user=Depends(yeu_cau_quyen_admin),
    conn=Depends(get_db),
):
    nd_service.duyet_tai_khoan(conn, id, approved_by_id=user["id"], loai_quyen=loai_quyen)
    return RedirectResponse(url="/auth/cho-duyet", status_code=302)
