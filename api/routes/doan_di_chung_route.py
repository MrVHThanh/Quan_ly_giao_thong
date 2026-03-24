"""
Route: doan_di_chung_route.py
GET  /doan-di-chung/           → danh sách đoạn đi chung
GET  /doan-di-chung/them       → form thêm mới
POST /doan-di-chung/them       → lưu thêm mới
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
import services.doan_di_chung_service as ddc_service

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
templates.env.filters["format_ly_trinh"] = _fmt_ly_trinh


def _to_float(val: Optional[str]) -> Optional[float]:
    try:
        return float(val) if val and str(val).strip() else None
    except (ValueError, TypeError):
        return None


# ── DANH SÁCH — GET /doan-di-chung/ ──────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def danh_sach(
    request: Request,
    tuyen_di_chung_id: Optional[int] = None,
    tuyen_chinh_id: Optional[int] = None,
    user=Depends(yeu_cau_dang_nhap), conn=Depends(get_db),
):
    ddc_list = ddc_repo.lay_tat_ca(conn)
    tuyen_list = td_repo.lay_tat_ca(conn)
    map_tuyen = {t.id: t for t in tuyen_list}

    # Lọc theo tuyến đi chung hoặc tuyến chủ nếu có
    if tuyen_di_chung_id:
        ddc_list = [d for d in ddc_list if d.tuyen_di_chung_id == tuyen_di_chung_id]
    if tuyen_chinh_id:
        ddc_list = [d for d in ddc_list if d.tuyen_chinh_id == tuyen_chinh_id]

    # Lấy đoạn vật lý liên quan
    doan_ids = {d.doan_id for d in ddc_list}
    map_doan = {}
    for did in doan_ids:
        doan = dt_repo.lay_theo_id(conn, did)
        if doan:
            map_doan[did] = doan

    return templates.TemplateResponse("doan_di_chung/list.html", {
        "request":          request,
        "user":             user,
        "ddc_list":         ddc_list,
        "tuyen_list":       tuyen_list,
        "map_tuyen":        map_tuyen,
        "map_doan":         map_doan,
        "bo_loc": {
            "tuyen_di_chung_id": tuyen_di_chung_id,
            "tuyen_chinh_id":    tuyen_chinh_id,
        },
    })


# ── FORM THÊM — GET /doan-di-chung/them ───────────────────────────────────

@router.get("/them", response_class=HTMLResponse)
async def form_them(
    request: Request,
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    tuyen_list = td_repo.lay_tat_ca(conn)
    doan_list  = dt_repo.lay_tat_ca(conn)
    return templates.TemplateResponse("doan_di_chung/form_them.html", {
        "request":    request,
        "user":       user,
        "tuyen_list": tuyen_list,
        "doan_list":  doan_list,
        "loi":        None,
        "form":       {},
    })


# ── LƯU THÊM — POST /doan-di-chung/them ──────────────────────────────────

@router.post("/them")
async def luu_them(
    request: Request,
    tuyen_di_chung_id:        int   = Form(...),
    tuyen_chinh_id:           int   = Form(...),
    doan_id:                  int   = Form(...),
    ly_trinh_dau_di_chung:    float = Form(...),
    ly_trinh_cuoi_di_chung:   float = Form(...),
    ly_trinh_dau_tuyen_chinh: Optional[str] = Form(None),
    ly_trinh_cuoi_tuyen_chinh: Optional[str] = Form(None),
    ghi_chu: Optional[str] = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    lt_dau_chinh  = _to_float(ly_trinh_dau_tuyen_chinh)
    lt_cuoi_chinh = _to_float(ly_trinh_cuoi_tuyen_chinh)

    # Gán mặc định nếu không nhập (service cần float, không phải None)
    if lt_dau_chinh is None:
        lt_dau_chinh = ly_trinh_dau_di_chung
    if lt_cuoi_chinh is None:
        lt_cuoi_chinh = ly_trinh_cuoi_di_chung

    form_data = {
        "tuyen_di_chung_id":        tuyen_di_chung_id,
        "tuyen_chinh_id":           tuyen_chinh_id,
        "doan_id":                  doan_id,
        "ly_trinh_dau_di_chung":    ly_trinh_dau_di_chung,
        "ly_trinh_cuoi_di_chung":   ly_trinh_cuoi_di_chung,
        "ly_trinh_dau_tuyen_chinh": ly_trinh_dau_tuyen_chinh,
        "ly_trinh_cuoi_tuyen_chinh": ly_trinh_cuoi_tuyen_chinh,
        "ghi_chu":                  ghi_chu,
    }

    try:
        ddc_service.them(
            conn,
            tuyen_di_chung_id=tuyen_di_chung_id,
            tuyen_chinh_id=tuyen_chinh_id,
            doan_id=doan_id,
            ly_trinh_dau_di_chung=ly_trinh_dau_di_chung,
            ly_trinh_cuoi_di_chung=ly_trinh_cuoi_di_chung,
            ly_trinh_dau_tuyen_chinh=lt_dau_chinh,
            ly_trinh_cuoi_tuyen_chinh=lt_cuoi_chinh,
            ghi_chu=ghi_chu or None,
        )
    except ddc_service.DoanDiChungServiceError as e:
        tuyen_list = td_repo.lay_tat_ca(conn)
        doan_list  = dt_repo.lay_tat_ca(conn)
        return templates.TemplateResponse("doan_di_chung/form_them.html", {
            "request":    request,
            "user":       user,
            "tuyen_list": tuyen_list,
            "doan_list":  doan_list,
            "loi":        str(e),
            "form":       form_data,
        }, status_code=400)

    return RedirectResponse(url="/doan-di-chung/", status_code=302)


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
        return RedirectResponse(url="/doan-di-chung/", status_code=302)
    # Lấy referer để redirect về đúng trang (list hoặc tuyến detail)
    ddc_repo.xoa(conn, id)
    return RedirectResponse(url="/doan-di-chung/", status_code=302)