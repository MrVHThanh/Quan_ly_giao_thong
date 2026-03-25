"""
Route: danh_muc_route.py — Quản lý danh mục hệ thống
GET  /danh-muc/quan-ly              → trang Thông tin quản lý
GET  /danh-muc/ky-thuat             → trang Thông tin kỹ thuật

Cấp quản lý (cap_quan_ly):
  POST /danh-muc/cap-quan-ly/them
  POST /danh-muc/cap-quan-ly/{id}/sua
  POST /danh-muc/cap-quan-ly/{id}/xoa

Đơn vị (don_vi):
  POST /danh-muc/don-vi/them
  POST /danh-muc/don-vi/{id}/sua
  POST /danh-muc/don-vi/{id}/xoa

Cấp đường (cap_duong):
  POST /danh-muc/cap-duong/them
  POST /danh-muc/cap-duong/{id}/sua
  POST /danh-muc/cap-duong/{id}/xoa

Kết cấu mặt (ket-cau-mat):
  POST /danh-muc/ket-cau-mat/them
  POST /danh-muc/ket-cau-mat/{id}/sua
  POST /danh-muc/ket-cau-mat/{id}/xoa

Tình trạng (tinh-trang):
  POST /danh-muc/tinh-trang/them
  POST /danh-muc/tinh-trang/{id}/sua
  POST /danh-muc/tinh-trang/{id}/xoa
"""

import os, sys, sqlite3
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.database import get_db
from api.routes._auth_helper import yeu_cau_dang_nhap, yeu_cau_quyen_bien_tap, yeu_cau_quyen_admin

import services.cap_quan_ly_service as cql_service
import services.don_vi_service as dv_service
import services.cap_duong_service as cd_service
import services.ket_cau_mat_service as kcm_service
import services.tinh_trang_service as tt_service

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(_ROOT, "templates"))


def _to_int(val: Optional[str]) -> Optional[int]:
    try:
        return int(val) if val and str(val).strip() else None
    except (ValueError, TypeError):
        return None


def _err_redirect(url: str, msg: str) -> RedirectResponse:
    """Redirect về url kèm thông báo lỗi dạng query param."""
    return RedirectResponse(url=f"{url}?loi={quote(msg)}", status_code=302)


# ══════════════════════════════════════════════════════════════════════
# TRANG: THÔNG TIN QUẢN LÝ
# ══════════════════════════════════════════════════════════════════════

@router.get("/quan-ly", response_class=HTMLResponse)
async def trang_quan_ly(
    request: Request,
    loi: Optional[str] = None,
    ok: Optional[str] = None,
    user=Depends(yeu_cau_dang_nhap), conn=Depends(get_db),
):
    cap_quan_ly_list = cql_service.lay_tat_ca(conn)
    don_vi_list      = dv_service.lay_tat_ca(conn)
    map_don_vi       = {d.id: d for d in don_vi_list}
    return templates.TemplateResponse("danh_muc/quan_ly.html", {
        "request":          request,
        "user":             user,
        "cap_quan_ly_list": cap_quan_ly_list,
        "don_vi_list":      don_vi_list,
        "map_don_vi":       map_don_vi,
        "loi":              loi,
        "ok":               ok,
    })


# ── Cấp quản lý ────────────────────────────────────────────────────────

@router.post("/cap-quan-ly/them")
async def them_cap_quan_ly(
    ma_cap: str = Form(...),
    ten_cap: str = Form(...),
    mo_ta: Optional[str] = Form(None),
    thu_tu_hien_thi: Optional[str] = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        cql_service.them(conn, ma_cap, ten_cap, mo_ta or None,
                         _to_int(thu_tu_hien_thi))
    except cql_service.CapQuanLyServiceError as e:
        return _err_redirect("/danh-muc/quan-ly", str(e))
    return RedirectResponse(url="/danh-muc/quan-ly?ok=cap-quan-ly", status_code=302)


@router.post("/cap-quan-ly/{id}/sua")
async def sua_cap_quan_ly(
    id: int,
    ten_cap: str = Form(...),
    mo_ta: Optional[str] = Form(None),
    thu_tu_hien_thi: Optional[str] = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        cql_service.sua(conn, id, ten_cap, mo_ta or None,
                        _to_int(thu_tu_hien_thi))
    except cql_service.CapQuanLyServiceError as e:
        return _err_redirect("/danh-muc/quan-ly", str(e))
    return RedirectResponse(url="/danh-muc/quan-ly?ok=cap-quan-ly", status_code=302)


@router.post("/cap-quan-ly/{id}/xoa")
async def xoa_cap_quan_ly(
    id: int,
    user=Depends(yeu_cau_quyen_admin), conn=Depends(get_db),
):
    try:
        obj = cql_service.lay_theo_id(conn, id)
        if obj.is_active:
            cql_service.xoa_mem(conn, id)
        else:
            cql_service.khoi_phuc(conn, id)
    except cql_service.CapQuanLyServiceError as e:
        return _err_redirect("/danh-muc/quan-ly", str(e))
    return RedirectResponse(url="/danh-muc/quan-ly?ok=cap-quan-ly", status_code=302)


# ── Đơn vị ─────────────────────────────────────────────────────────────

@router.post("/don-vi/them")
async def them_don_vi(
    ma_don_vi: str = Form(...),
    ten_don_vi: str = Form(...),
    ten_viet_tat: Optional[str] = Form(None),
    parent_id: Optional[str] = Form(None),
    cap_don_vi: Optional[str] = Form(None),
    dia_chi: Optional[str] = Form(None),
    so_dien_thoai: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        dv_service.them(conn, ma_don_vi, ten_don_vi,
                        ten_viet_tat or None, _to_int(parent_id),
                        cap_don_vi or None, dia_chi or None,
                        so_dien_thoai or None, email or None)
    except dv_service.DonViServiceError as e:
        return _err_redirect("/danh-muc/quan-ly", str(e))
    return RedirectResponse(url="/danh-muc/quan-ly?ok=don-vi", status_code=302)


@router.post("/don-vi/{id}/sua")
async def sua_don_vi(
    id: int,
    ten_don_vi: str = Form(...),
    ten_viet_tat: Optional[str] = Form(None),
    parent_id: Optional[str] = Form(None),
    cap_don_vi: Optional[str] = Form(None),
    dia_chi: Optional[str] = Form(None),
    so_dien_thoai: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        dv_service.sua(conn, id, ten_don_vi,
                       ten_viet_tat or None, _to_int(parent_id),
                       cap_don_vi or None, dia_chi or None,
                       so_dien_thoai or None, email or None)
    except dv_service.DonViServiceError as e:
        return _err_redirect("/danh-muc/quan-ly", str(e))
    return RedirectResponse(url="/danh-muc/quan-ly?ok=don-vi", status_code=302)


@router.post("/don-vi/{id}/xoa")
async def xoa_don_vi(
    id: int,
    user=Depends(yeu_cau_quyen_admin), conn=Depends(get_db),
):
    try:
        obj = dv_service.lay_theo_id(conn, id)
        if obj.is_active:
            dv_service.xoa_mem(conn, id)
        else:
            dv_service.khoi_phuc(conn, id)
    except dv_service.DonViServiceError as e:
        return _err_redirect("/danh-muc/quan-ly", str(e))
    return RedirectResponse(url="/danh-muc/quan-ly?ok=don-vi", status_code=302)


# ══════════════════════════════════════════════════════════════════════
# TRANG: THÔNG TIN KỸ THUẬT
# ══════════════════════════════════════════════════════════════════════

@router.get("/ky-thuat", response_class=HTMLResponse)
async def trang_ky_thuat(
    request: Request,
    loi: Optional[str] = None,
    ok: Optional[str] = None,
    user=Depends(yeu_cau_dang_nhap), conn=Depends(get_db),
):
    cap_duong_list  = cd_service.lay_tat_ca(conn)
    ket_cau_list    = kcm_service.lay_tat_ca(conn)
    tinh_trang_list = tt_service.lay_tat_ca(conn)
    return templates.TemplateResponse("danh_muc/ky_thuat.html", {
        "request":          request,
        "user":             user,
        "cap_duong_list":   cap_duong_list,
        "ket_cau_list":     ket_cau_list,
        "tinh_trang_list":  tinh_trang_list,
        "loi":              loi,
        "ok":               ok,
    })


# ── Cấp đường ──────────────────────────────────────────────────────────

@router.post("/cap-duong/them")
async def them_cap_duong(
    ma_cap: str = Form(...),
    ten_cap: str = Form(...),
    mo_ta: Optional[str] = Form(None),
    thu_tu_hien_thi: Optional[str] = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        cd_service.them(conn, ma_cap, ten_cap, mo_ta or None,
                        _to_int(thu_tu_hien_thi))
    except cd_service.CapDuongServiceError as e:
        return _err_redirect("/danh-muc/ky-thuat", str(e))
    return RedirectResponse(url="/danh-muc/ky-thuat?ok=cap-duong", status_code=302)


@router.post("/cap-duong/{id}/sua")
async def sua_cap_duong(
    id: int,
    ten_cap: str = Form(...),
    mo_ta: Optional[str] = Form(None),
    thu_tu_hien_thi: Optional[str] = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        cd_service.sua(conn, id, ten_cap, mo_ta or None,
                       _to_int(thu_tu_hien_thi))
    except cd_service.CapDuongServiceError as e:
        return _err_redirect("/danh-muc/ky-thuat", str(e))
    return RedirectResponse(url="/danh-muc/ky-thuat?ok=cap-duong", status_code=302)


@router.post("/cap-duong/{id}/xoa")
async def xoa_cap_duong(
    id: int,
    user=Depends(yeu_cau_quyen_admin), conn=Depends(get_db),
):
    try:
        obj = cd_service.lay_theo_id(conn, id)
        if obj.is_active:
            cd_service.xoa_mem(conn, id)
        else:
            cd_service.khoi_phuc(conn, id)
    except cd_service.CapDuongServiceError as e:
        return _err_redirect("/danh-muc/ky-thuat", str(e))
    return RedirectResponse(url="/danh-muc/ky-thuat?ok=cap-duong", status_code=302)


# ── Kết cấu mặt đường ─────────────────────────────────────────────────

@router.post("/ket-cau-mat/them")
async def them_ket_cau_mat(
    ma_ket_cau: str = Form(...),
    ten_ket_cau: str = Form(...),
    mo_ta: Optional[str] = Form(None),
    thu_tu_hien_thi: Optional[str] = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        kcm_service.them(conn, ma_ket_cau, ten_ket_cau, mo_ta or None,
                         _to_int(thu_tu_hien_thi))
    except kcm_service.KetCauMatServiceError as e:
        return _err_redirect("/danh-muc/ky-thuat", str(e))
    except sqlite3.IntegrityError:
        return _err_redirect("/danh-muc/ky-thuat", f"Mã kết cấu '{ma_ket_cau.strip().upper()}' đã tồn tại.")
    return RedirectResponse(url="/danh-muc/ky-thuat?ok=ket-cau-mat", status_code=302)


@router.post("/ket-cau-mat/{id}/sua")
async def sua_ket_cau_mat(
    id: int,
    ten_ket_cau: str = Form(...),
    mo_ta: Optional[str] = Form(None),
    thu_tu_hien_thi: Optional[str] = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        kcm_service.sua(conn, id, ten_ket_cau, mo_ta or None,
                        _to_int(thu_tu_hien_thi))
    except kcm_service.KetCauMatServiceError as e:
        return _err_redirect("/danh-muc/ky-thuat", str(e))
    return RedirectResponse(url="/danh-muc/ky-thuat?ok=ket-cau-mat", status_code=302)


@router.post("/ket-cau-mat/{id}/xoa")
async def xoa_ket_cau_mat(
    id: int,
    user=Depends(yeu_cau_quyen_admin), conn=Depends(get_db),
):
    try:
        obj = kcm_service.lay_theo_id(conn, id)
        if obj.is_active:
            kcm_service.xoa_mem(conn, id)
        else:
            kcm_service.khoi_phuc(conn, id)
    except kcm_service.KetCauMatServiceError as e:
        return _err_redirect("/danh-muc/ky-thuat", str(e))
    return RedirectResponse(url="/danh-muc/ky-thuat?ok=ket-cau-mat", status_code=302)


# ── Tình trạng ─────────────────────────────────────────────────────────

@router.post("/tinh-trang/them")
async def them_tinh_trang(
    ma_tinh_trang: str = Form(...),
    ten_tinh_trang: str = Form(...),
    mo_ta: Optional[str] = Form(None),
    mau_hien_thi: Optional[str] = Form(None),
    thu_tu_hien_thi: Optional[str] = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        tt_service.them(conn, ma_tinh_trang, ten_tinh_trang,
                        mo_ta or None, mau_hien_thi or None,
                        _to_int(thu_tu_hien_thi))
    except tt_service.TinhTrangServiceError as e:
        return _err_redirect("/danh-muc/ky-thuat", str(e))
    except sqlite3.IntegrityError:
        return _err_redirect("/danh-muc/ky-thuat", f"Mã tình trạng '{ma_tinh_trang.strip().upper()}' đã tồn tại.")
    return RedirectResponse(url="/danh-muc/ky-thuat?ok=tinh-trang", status_code=302)


@router.post("/tinh-trang/{id}/sua")
async def sua_tinh_trang(
    id: int,
    ten_tinh_trang: str = Form(...),
    mo_ta: Optional[str] = Form(None),
    mau_hien_thi: Optional[str] = Form(None),
    thu_tu_hien_thi: Optional[str] = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        tt_service.sua(conn, id, ten_tinh_trang,
                       mo_ta or None, mau_hien_thi or None,
                       _to_int(thu_tu_hien_thi))
    except tt_service.TinhTrangServiceError as e:
        return _err_redirect("/danh-muc/ky-thuat", str(e))
    return RedirectResponse(url="/danh-muc/ky-thuat?ok=tinh-trang", status_code=302)


@router.post("/tinh-trang/{id}/xoa")
async def xoa_tinh_trang(
    id: int,
    user=Depends(yeu_cau_quyen_admin), conn=Depends(get_db),
):
    try:
        obj = tt_service.lay_theo_id(conn, id)
        if obj.is_active:
            tt_service.xoa_mem(conn, id)
        else:
            tt_service.khoi_phuc(conn, id)
    except tt_service.TinhTrangServiceError as e:
        return _err_redirect("/danh-muc/ky-thuat", str(e))
    return RedirectResponse(url="/danh-muc/ky-thuat?ok=tinh-trang", status_code=302)
