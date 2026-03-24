"""
Route: he_thong_route.py — Quản lý hệ thống (chỉ ADMIN)
GET  /he-thong/nguoi-dung              → danh sách người dùng
POST /he-thong/nguoi-dung/them         → tạo mới người dùng
POST /he-thong/nguoi-dung/{id}/sua     → sửa thông tin người dùng
POST /he-thong/nguoi-dung/{id}/doi-mk  → đặt lại mật khẩu
POST /he-thong/nguoi-dung/{id}/xoa     → vô hiệu hóa / khôi phục
POST /he-thong/nguoi-dung/{id}/duyet   → duyệt tài khoản chờ duyệt
"""

import os, sys
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.database import get_db
from api.routes._auth_helper import yeu_cau_quyen_admin
import services.nguoi_dung_service as nd_service
import repositories.don_vi_repository as dv_repo

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(_ROOT, "templates"))


def _to_int(val: Optional[str]) -> Optional[int]:
    try:
        return int(val) if val and str(val).strip() else None
    except (ValueError, TypeError):
        return None


def _err(url: str, msg: str) -> RedirectResponse:
    return RedirectResponse(url=f"{url}?loi={quote(msg)}", status_code=302)


# ── DANH SÁCH ─────────────────────────────────────────────────────────────

@router.get("/nguoi-dung", response_class=HTMLResponse)
async def danh_sach(
    request: Request,
    loi: Optional[str] = None,
    ok: Optional[str] = None,
    user=Depends(yeu_cau_quyen_admin),
    conn=Depends(get_db),
):
    nguoi_dung_list = nd_service.lay_tat_ca(conn)
    don_vi_list     = dv_repo.lay_tat_ca(conn)
    map_don_vi      = {d.id: d for d in don_vi_list}
    return templates.TemplateResponse("he_thong/nguoi_dung.html", {
        "request":          request,
        "user":             user,
        "nguoi_dung_list":  nguoi_dung_list,
        "don_vi_list":      don_vi_list,
        "map_don_vi":       map_don_vi,
        "loi":              loi,
        "ok":               ok,
    })


# ── TẠO MỚI ───────────────────────────────────────────────────────────────

@router.post("/nguoi-dung/them")
async def them(
    ten_dang_nhap: str = Form(...),
    mat_khau:      str = Form(...),
    ho_ten:        str = Form(...),
    loai_quyen:    str = Form("XEM"),
    chuc_vu:       Optional[str] = Form(None),
    don_vi_id:     Optional[str] = Form(None),
    so_dien_thoai: Optional[str] = Form(None),
    email:         Optional[str] = Form(None),
    user=Depends(yeu_cau_quyen_admin),
    conn=Depends(get_db),
):
    try:
        nd_service.tao_boi_admin(
            conn, ten_dang_nhap, mat_khau, ho_ten, loai_quyen,
            chuc_vu=chuc_vu or None,
            don_vi_id=_to_int(don_vi_id),
            so_dien_thoai=so_dien_thoai or None,
            email=email or None,
            admin_id=user["id"],
        )
    except nd_service.NguoiDungServiceError as e:
        return _err("/he-thong/nguoi-dung", str(e))
    return RedirectResponse(url="/he-thong/nguoi-dung?ok=1", status_code=302)


# ── SỬA THÔNG TIN ─────────────────────────────────────────────────────────

@router.post("/nguoi-dung/{id}/sua")
async def sua(
    id: int,
    ho_ten:        str = Form(...),
    loai_quyen:    str = Form(...),
    chuc_vu:       Optional[str] = Form(None),
    don_vi_id:     Optional[str] = Form(None),
    so_dien_thoai: Optional[str] = Form(None),
    email:         Optional[str] = Form(None),
    is_active:     Optional[str] = Form("1"),
    user=Depends(yeu_cau_quyen_admin),
    conn=Depends(get_db),
):
    try:
        nd_service.sua_thong_tin(
            conn, id, ho_ten, loai_quyen,
            chuc_vu=chuc_vu or None,
            don_vi_id=_to_int(don_vi_id),
            so_dien_thoai=so_dien_thoai or None,
            email=email or None,
            is_active=1 if is_active == "1" else 0,
        )
    except nd_service.NguoiDungServiceError as e:
        return _err("/he-thong/nguoi-dung", str(e))
    return RedirectResponse(url="/he-thong/nguoi-dung?ok=1", status_code=302)


# ── ĐỔI MẬT KHẨU (admin đặt lại) ────────────────────────────────────────

@router.post("/nguoi-dung/{id}/doi-mk")
async def doi_mat_khau(
    id: int,
    mat_khau_moi: str = Form(...),
    user=Depends(yeu_cau_quyen_admin),
    conn=Depends(get_db),
):
    try:
        nd_service.doi_mat_khau_admin(conn, id, mat_khau_moi)
    except nd_service.NguoiDungServiceError as e:
        return _err("/he-thong/nguoi-dung", str(e))
    return RedirectResponse(url="/he-thong/nguoi-dung?ok=1", status_code=302)


# ── VÔ HIỆU / KHÔI PHỤC ──────────────────────────────────────────────────

@router.post("/nguoi-dung/{id}/xoa")
async def xoa(
    id: int,
    user=Depends(yeu_cau_quyen_admin),
    conn=Depends(get_db),
):
    # Ngăn admin tự vô hiệu chính mình
    if id == user["id"]:
        return _err("/he-thong/nguoi-dung", "Không thể vô hiệu hóa tài khoản đang đăng nhập.")
    try:
        nd = nd_service.lay_theo_id(conn, id)
        if nd.is_active:
            nd_service.vo_hieu_hoa(conn, id)
        else:
            nd_service.khoi_phuc(conn, id)
    except nd_service.NguoiDungServiceError as e:
        return _err("/he-thong/nguoi-dung", str(e))
    return RedirectResponse(url="/he-thong/nguoi-dung?ok=1", status_code=302)


# ── DUYỆT TÀI KHOẢN ──────────────────────────────────────────────────────

@router.post("/nguoi-dung/{id}/duyet")
async def duyet(
    id: int,
    loai_quyen: str = Form("XEM"),
    user=Depends(yeu_cau_quyen_admin),
    conn=Depends(get_db),
):
    try:
        nd_service.duyet_tai_khoan(conn, id, approved_by_id=user["id"],
                                   loai_quyen=loai_quyen)
    except nd_service.NguoiDungServiceError as e:
        return _err("/he-thong/nguoi-dung", str(e))
    return RedirectResponse(url="/he-thong/nguoi-dung?ok=1", status_code=302)
