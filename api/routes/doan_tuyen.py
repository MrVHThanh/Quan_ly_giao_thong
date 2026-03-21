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


@router.get("/", response_class=HTMLResponse)
async def danh_sach(
    request: Request,
    tuyen_id: int = Query(None),
    tinh_trang_id: int = Query(None),
    cap_duong_id: int = Query(None),
    user=Depends(yeu_cau_dang_nhap), conn=Depends(get_db),
):
    if tuyen_id:
        doan_list = dt_service.lay_theo_tuyen_id(conn, tuyen_id)
    elif tinh_trang_id:
        doan_list = dt_service.lay_theo_tinh_trang(conn, tinh_trang_id)
    elif cap_duong_id:
        doan_list = dt_service.lay_theo_cap_duong(conn, cap_duong_id)
    else:
        from repositories.doan_tuyen_repository import lay_tat_ca
        doan_list = lay_tat_ca(conn)

    return templates.TemplateResponse("doan_tuyen/list.html", {
        "request": request, "user": user,
        "doan_list": doan_list,
        "tuyen_list": td_repo.lay_tat_ca(conn),
        "tinh_trang_list": tt_repo.lay_dang_hoat_dong(conn),
        "bo_loc": {"tuyen_id": tuyen_id, "tinh_trang_id": tinh_trang_id},
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
async def form_them(request: Request, tuyen_id: int = Query(None),
                    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db)):
    return templates.TemplateResponse("doan_tuyen/form.html",
                                      _form_context(conn, user=user, request=request))


@router.post("/them")
async def luu_them(
    request: Request,
    ma_doan: str = Form(...), tuyen_id: int = Form(...),
    cap_duong_id: int = Form(...), tinh_trang_id: int = Form(...),
    ly_trinh_dau: float = Form(...), ly_trinh_cuoi: float = Form(...),
    ket_cau_mat_id: int = Form(None),
    chieu_dai_thuc_te: float = Form(None),
    chieu_rong_mat_min: float = Form(None), chieu_rong_mat_max: float = Form(None),
    chieu_rong_nen_min: float = Form(None), chieu_rong_nen_max: float = Form(None),
    don_vi_bao_duong_id: int = Form(None), ghi_chu: str = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        doan = dt_service.them(
            conn, ma_doan, tuyen_id, cap_duong_id, tinh_trang_id,
            ly_trinh_dau, ly_trinh_cuoi,
            ket_cau_mat_id=ket_cau_mat_id, chieu_dai_thuc_te=chieu_dai_thuc_te,
            chieu_rong_mat_min=chieu_rong_mat_min, chieu_rong_mat_max=chieu_rong_mat_max,
            chieu_rong_nen_min=chieu_rong_nen_min, chieu_rong_nen_max=chieu_rong_nen_max,
            don_vi_bao_duong_id=don_vi_bao_duong_id, ghi_chu=ghi_chu,
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
    ket_cau_mat_id: int = Form(None), chieu_dai_thuc_te: float = Form(None),
    chieu_rong_mat_min: float = Form(None), chieu_rong_mat_max: float = Form(None),
    chieu_rong_nen_min: float = Form(None), chieu_rong_nen_max: float = Form(None),
    don_vi_bao_duong_id: int = Form(None), ghi_chu: str = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        dt_service.sua(conn, id, cap_duong_id, tinh_trang_id, ly_trinh_dau, ly_trinh_cuoi,
                       ket_cau_mat_id=ket_cau_mat_id, chieu_dai_thuc_te=chieu_dai_thuc_te,
                       chieu_rong_mat_min=chieu_rong_mat_min, chieu_rong_mat_max=chieu_rong_mat_max,
                       chieu_rong_nen_min=chieu_rong_nen_min, chieu_rong_nen_max=chieu_rong_nen_max,
                       don_vi_bao_duong_id=don_vi_bao_duong_id, ghi_chu=ghi_chu,
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
