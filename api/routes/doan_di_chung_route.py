"""
Route: doan_di_chung_route.py
GET  /doan-di-chung/{id}/sua   → form sửa đoạn đi chung
POST /doan-di-chung/{id}/sua   → lưu cập nhật
POST /doan-di-chung/{id}/xoa   → xóa đoạn đi chung (ADMIN)
"""

import os, sys
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.database import get_db
from api.routes._auth_helper import yeu_cau_dang_nhap, yeu_cau_quyen_bien_tap, yeu_cau_quyen_admin
import repositories.doan_di_chung_repository as ddc_repo
import repositories.tuyen_duong_repository as td_repo
import repositories.doan_tuyen_repository as dt_repo

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(_ROOT, "templates"))


# ── Jinja2 filter: định dạng lý trình ─────────────────────────────────────
def _fmt_ly_trinh(val) -> str:
    if val is None:
        return "—"
    try:
        val = float(val)
        km  = int(val)
        m   = round((val - km) * 1000)
        if m >= 1000:
            km += 1
            m = 0
        return f"Km{km}+{m:03d}"
    except (TypeError, ValueError):
        return str(val)

templates.env.filters["ly_trinh"] = _fmt_ly_trinh


def _to_float(val: Optional[str]) -> Optional[float]:
    try:
        return float(val) if val and str(val).strip() else None
    except (ValueError, TypeError):
        return None


# ── FORM SỬA — GET /doan-di-chung/{id}/sua ────────────────────────────────

@router.get("/{id}/sua", response_class=HTMLResponse)
async def form_sua(
    request: Request, id: int,
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    ddc = ddc_repo.lay_theo_id(conn, id)
    if not ddc:
        return RedirectResponse(url="/tuyen-duong/", status_code=302)

    tuyen_di_chung = td_repo.lay_theo_id(conn, ddc.tuyen_di_chung_id)
    tuyen_chinh    = td_repo.lay_theo_id(conn, ddc.tuyen_chinh_id)
    doan_vat_ly    = dt_repo.lay_theo_id(conn, ddc.doan_id)

    return templates.TemplateResponse("doan_di_chung/form.html", {
        "request":        request,
        "user":           user,
        "ddc":            ddc,
        "tuyen_di_chung": tuyen_di_chung,
        "tuyen_chinh":    tuyen_chinh,
        "doan_vat_ly":    doan_vat_ly,
        "loi":            None,
    })


# ── LƯU SỬA — POST /doan-di-chung/{id}/sua ────────────────────────────────

@router.post("/{id}/sua")
async def luu_sua(
    request: Request, id: int,
    # Lý trình theo tuyến đi nhờ
    ly_trinh_dau_di_chung:   float = Form(...),
    ly_trinh_cuoi_di_chung:  float = Form(...),
    # Lý trình theo tuyến chủ (tuỳ chọn)
    ly_trinh_dau_tuyen_chinh:  Optional[str] = Form(None),
    ly_trinh_cuoi_tuyen_chinh: Optional[str] = Form(None),
    ghi_chu: str = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    ddc = ddc_repo.lay_theo_id(conn, id)
    if not ddc:
        return RedirectResponse(url="/tuyen-duong/", status_code=302)

    # Validate cơ bản
    loi = None
    if ly_trinh_cuoi_di_chung <= ly_trinh_dau_di_chung:
        loi = "Lý trình cuối phải lớn hơn lý trình đầu."

    lt_dau_chinh  = _to_float(ly_trinh_dau_tuyen_chinh)
    lt_cuoi_chinh = _to_float(ly_trinh_cuoi_tuyen_chinh)
    if lt_dau_chinh and lt_cuoi_chinh and lt_cuoi_chinh <= lt_dau_chinh:
        loi = "Lý trình cuối tuyến chủ phải lớn hơn lý trình đầu."

    if loi:
        tuyen_di_chung = td_repo.lay_theo_id(conn, ddc.tuyen_di_chung_id)
        tuyen_chinh    = td_repo.lay_theo_id(conn, ddc.tuyen_chinh_id)
        doan_vat_ly    = dt_repo.lay_theo_id(conn, ddc.doan_id)
        return templates.TemplateResponse("doan_di_chung/form.html", {
            "request":        request,
            "user":           user,
            "ddc":            ddc,
            "tuyen_di_chung": tuyen_di_chung,
            "tuyen_chinh":    tuyen_chinh,
            "doan_vat_ly":    doan_vat_ly,
            "loi":            loi,
        }, status_code=400)

    # Cập nhật object
    ddc.ly_trinh_dau_di_chung        = ly_trinh_dau_di_chung
    ddc.ly_trinh_cuoi_di_chung       = ly_trinh_cuoi_di_chung
    ddc.ly_trinh_dau_tuyen_chinh     = lt_dau_chinh
    ddc.ly_trinh_cuoi_tuyen_chinh    = lt_cuoi_chinh
    ddc.ghi_chu                      = ghi_chu or None

    ddc_repo.sua(conn, ddc)

    # Sau khi sửa → quay về trang chi tiết tuyến đi nhờ
    return RedirectResponse(url=f"/tuyen-duong/{ddc.tuyen_di_chung_id}", status_code=302)


# ── XOÁ — POST /doan-di-chung/{id}/xoa (ADMIN) ────────────────────────────

@router.post("/{id}/xoa")
async def xoa(
    id: int,
    user=Depends(yeu_cau_quyen_admin), conn=Depends(get_db),
):
    ddc = ddc_repo.lay_theo_id(conn, id)
    if not ddc:
        return RedirectResponse(url="/tuyen-duong/", status_code=302)
    tuyen_id = ddc.tuyen_di_chung_id
    ddc_repo.xoa(conn, id)
    return RedirectResponse(url=f"/tuyen-duong/{tuyen_id}", status_code=302)