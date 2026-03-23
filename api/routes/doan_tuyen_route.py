"""
Route: doan_tuyen.py
GET  /doan-tuyen/                 → danh sách (lọc theo tuyen_id, tinh_trang, cap_duong)
GET  /doan-tuyen/{id}             → chi tiết 1 đoạn
GET  /doan-tuyen/them             → form thêm đoạn
POST /doan-tuyen/them             → lưu đoạn mới
GET  /doan-tuyen/{id}/sua         → form sửa
POST /doan-tuyen/{id}/sua         → lưu cập nhật
POST /doan-tuyen/{id}/cap-nhat-tinh-trang → cập nhật nhanh tình trạng
POST /doan-tuyen/{id}/xoa         → xóa đoạn (ADMIN)
"""

import os, sys
from typing import Optional

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.database import get_db
from api.routes._auth_helper import yeu_cau_dang_nhap, yeu_cau_quyen_bien_tap, yeu_cau_quyen_admin
import services.doan_tuyen_service as dt_service
import repositories.tuyen_duong_repository as td_repo
import repositories.cap_duong_repository as cd_repo
import repositories.tinh_trang_repository as tt_repo
import repositories.ket_cau_mat_repository as kcm_repo
import repositories.don_vi_repository as dv_repo

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(_ROOT, "templates"))


def _format_ly_trinh(value) -> str:
    """Chuyển lý trình số thực → KmXXX+YYY.
    Ví dụ: 190.0 → Km190+000 | 37.557 → Km37+557
    """
    if value is None:
        return "—"
    try:
        value = float(value)
        km = int(value)
        m  = round((value - km) * 1000)
        if m >= 1000:
            km += 1
            m = 0
        return f"Km{km}+{m:03d}"
    except (ValueError, TypeError):
        return str(value)

templates.env.filters["format_ly_trinh"] = _format_ly_trinh


def _to_int(val: Optional[str]) -> Optional[int]:
    """Chuyển chuỗi rỗng / None → None; chuỗi số hợp lệ → int.
    Tránh lỗi 422 khi form gửi chuỗi rỗng "" cho tham số kiểu int."""
    try:
        return int(val) if val else None
    except (ValueError, TypeError):
        return None


def _to_float(val: Optional[str]) -> Optional[float]:
    """Chuyển chuỗi rỗng / None → None; chuỗi số hợp lệ → float.
    Tránh lỗi float_parsing khi form gửi chuỗi rỗng "" cho tham số kiểu float."""
    try:
        return float(val) if val and str(val).strip() else None
    except (ValueError, TypeError):
        return None


@router.get("/", response_class=HTMLResponse)
async def danh_sach(
    request: Request,
    tuyen_id:       Optional[str] = Query(default=None),
    tinh_trang_id:  Optional[str] = Query(default=None),
    cap_duong_id:   Optional[str] = Query(default=None),
    ket_cau_mat_id: Optional[str] = Query(default=None),
    user=Depends(yeu_cau_dang_nhap), conn=Depends(get_db),
):
    tuyen_id_int       = _to_int(tuyen_id)
    tinh_trang_id_int  = _to_int(tinh_trang_id)
    cap_duong_id_int   = _to_int(cap_duong_id)
    ket_cau_mat_id_int = _to_int(ket_cau_mat_id)

    doan_list = dt_service.lay_co_loc(
        conn,
        tuyen_id=tuyen_id_int,
        tinh_trang_id=tinh_trang_id_int,
        cap_duong_id=cap_duong_id_int,
        ket_cau_mat_id=ket_cau_mat_id_int,
    )

    # --- Lookup maps: id → object (dùng trong template để hiển thị tên thay ID) ---
    tuyen_list = td_repo.lay_tat_ca(conn)
    tt_list    = tt_repo.lay_dang_hoat_dong(conn)
    cap_list   = cd_repo.lay_dang_hoat_dong(conn)
    kcm_list   = kcm_repo.lay_dang_hoat_dong(conn)

    map_tuyen = {t.id: t for t in tuyen_list}
    map_tt    = {t.id: t for t in tt_list}
    map_cap   = {c.id: c for c in cap_list}
    map_kcm   = {k.id: k for k in kcm_list}

    # --- Tổng chiều dài để tính cột Tỉ lệ (%) ---
    tong_chieu_dai = sum((d.chieu_dai or 0) for d in doan_list)

    return templates.TemplateResponse("doan_tuyen/list.html", {
        "request": request, "user": user,
        "doan_list":        doan_list,
        "tuyen_list":       tuyen_list,
        "tinh_trang_list":  tt_list,
        "cap_duong_list":   cap_list,    # dropdown filter Cấp đường
        "ket_cau_mat_list": kcm_list,   # dropdown filter Kết cấu mặt
        "map_tuyen":        map_tuyen,
        "map_tt":           map_tt,
        "map_cap":          map_cap,
        "map_kcm":          map_kcm,
        "tong_chieu_dai":   tong_chieu_dai,
        "bo_loc": {
            "tuyen_id":       tuyen_id_int,
            "tinh_trang_id":  tinh_trang_id_int,
            "cap_duong_id":   cap_duong_id_int,
            "ket_cau_mat_id": ket_cau_mat_id_int,
        },
    })


@router.get("/{id}", response_class=HTMLResponse)
async def chi_tiet(request: Request, id: int,
                   user=Depends(yeu_cau_dang_nhap), conn=Depends(get_db)):
    doan = dt_service.lay_theo_id(conn, id)
    return templates.TemplateResponse("doan_tuyen/detail.html", {
        "request": request, "user": user, "doan": doan,
        "tinh_trang_list": tt_repo.lay_dang_hoat_dong(conn),
    })


def _form_context(conn, doan=None, loi=None, user=None, request=None):
    return {
        "request": request, "user": user, "doan": doan, "loi": loi,
        "tuyen_list": td_repo.lay_tat_ca(conn),
        "cap_duong_list": cd_repo.lay_dang_hoat_dong(conn),
        "tinh_trang_list": tt_repo.lay_dang_hoat_dong(conn),
        "ket_cau_mat_list": kcm_repo.lay_dang_hoat_dong(conn),
        "don_vi_list": dv_repo.lay_dang_hoat_dong(conn),
    }


@router.get("/them", response_class=HTMLResponse)
async def form_them(
    request: Request,
    tuyen_id: Optional[str] = Query(default=None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    return templates.TemplateResponse("doan_tuyen/form.html",
                                      _form_context(conn, user=user, request=request))


@router.post("/them")
async def luu_them(
    request: Request,
    ma_doan: str = Form(...), tuyen_id: int = Form(...),
    cap_duong_id: int = Form(...), tinh_trang_id: int = Form(...),
    ly_trinh_dau: float = Form(...), ly_trinh_cuoi: float = Form(...),
    ket_cau_mat_id:      Optional[str] = Form(None),
    chieu_dai_thuc_te:   Optional[str] = Form(None),
    chieu_rong_mat_min:  Optional[str] = Form(None),
    chieu_rong_mat_max:  Optional[str] = Form(None),
    chieu_rong_nen_min:  Optional[str] = Form(None),
    chieu_rong_nen_max:  Optional[str] = Form(None),
    don_vi_bao_duong_id: Optional[str] = Form(None),
    ghi_chu: str = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        doan = dt_service.them(
            conn, ma_doan, tuyen_id, cap_duong_id, tinh_trang_id,
            ly_trinh_dau, ly_trinh_cuoi,
            ket_cau_mat_id=_to_int(ket_cau_mat_id),
            chieu_dai_thuc_te=_to_float(chieu_dai_thuc_te),
            chieu_rong_mat_min=_to_float(chieu_rong_mat_min),
            chieu_rong_mat_max=_to_float(chieu_rong_mat_max),
            chieu_rong_nen_min=_to_float(chieu_rong_nen_min),
            chieu_rong_nen_max=_to_float(chieu_rong_nen_max),
            don_vi_bao_duong_id=_to_int(don_vi_bao_duong_id),
            ghi_chu=ghi_chu,
            updated_by_id=user["id"],
        )
        return RedirectResponse(url=f"/doan-tuyen/{doan.id}", status_code=302)
    except dt_service.DoanTuyenServiceError as e:
        return templates.TemplateResponse("doan_tuyen/form.html",
            _form_context(conn, loi=str(e), user=user, request=request), status_code=400)


@router.get("/{id}/sua", response_class=HTMLResponse)
async def form_sua(request: Request, id: int,
                   user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db)):
    doan = dt_service.lay_theo_id(conn, id)
    return templates.TemplateResponse("doan_tuyen/form.html",
                                      _form_context(conn, doan=doan, user=user, request=request))


@router.post("/{id}/sua")
async def luu_sua(
    request: Request, id: int,
    cap_duong_id: int = Form(...), tinh_trang_id: int = Form(...),
    ly_trinh_dau: float = Form(...), ly_trinh_cuoi: float = Form(...),
    ket_cau_mat_id:      Optional[str] = Form(None),
    chieu_dai_thuc_te:   Optional[str] = Form(None),
    chieu_rong_mat_min:  Optional[str] = Form(None),
    chieu_rong_mat_max:  Optional[str] = Form(None),
    chieu_rong_nen_min:  Optional[str] = Form(None),
    chieu_rong_nen_max:  Optional[str] = Form(None),
    don_vi_bao_duong_id: Optional[str] = Form(None),
    ghi_chu: str = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        dt_service.sua(conn, id, cap_duong_id, tinh_trang_id, ly_trinh_dau, ly_trinh_cuoi,
                       ket_cau_mat_id=_to_int(ket_cau_mat_id),
                       chieu_dai_thuc_te=_to_float(chieu_dai_thuc_te),
                       chieu_rong_mat_min=_to_float(chieu_rong_mat_min),
                       chieu_rong_mat_max=_to_float(chieu_rong_mat_max),
                       chieu_rong_nen_min=_to_float(chieu_rong_nen_min),
                       chieu_rong_nen_max=_to_float(chieu_rong_nen_max),
                       don_vi_bao_duong_id=_to_int(don_vi_bao_duong_id),
                       ghi_chu=ghi_chu,
                       updated_by_id=user["id"])
        return RedirectResponse(url=f"/doan-tuyen/{id}", status_code=302)
    except dt_service.DoanTuyenServiceError as e:
        doan = dt_service.lay_theo_id(conn, id)
        return templates.TemplateResponse("doan_tuyen/form.html",
            _form_context(conn, doan=doan, loi=str(e), user=user, request=request), status_code=400)


@router.post("/{id}/cap-nhat-tinh-trang")
async def cap_nhat_tinh_trang(
    id: int,
    tinh_trang_id: int = Form(...),
    ngay_cap_nhat: str = Form(...),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    dt_service.cap_nhat_tinh_trang(conn, id, tinh_trang_id, ngay_cap_nhat, user["id"])
    return RedirectResponse(url=f"/doan-tuyen/{id}", status_code=302)


@router.post("/{id}/xoa")
async def xoa(id: int, user=Depends(yeu_cau_quyen_admin), conn=Depends(get_db)):
    doan = dt_service.lay_theo_id(conn, id)
    tuyen_id = doan.tuyen_id
    dt_service.xoa(conn, id)
    return RedirectResponse(url=f"/tuyen-duong/{tuyen_id}", status_code=302)