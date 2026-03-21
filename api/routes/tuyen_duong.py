"""
Route: tuyen_duong.py
GET  /tuyen-duong/                → danh sách tất cả tuyến
GET  /tuyen-duong/{id}            → chi tiết 1 tuyến + danh sách đoạn
GET  /tuyen-duong/them            → form thêm tuyến (BIEN_TAP+)
POST /tuyen-duong/them            → lưu tuyến mới
GET  /tuyen-duong/{id}/sua        → form sửa tuyến (BIEN_TAP+)
POST /tuyen-duong/{id}/sua        → lưu cập nhật
POST /tuyen-duong/{id}/xoa        → xóa tuyến (ADMIN)
GET  /tuyen-duong/api/list        → JSON danh sách (dùng cho bản đồ)
"""

import os, sys
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.database import get_db
from api.routes._auth_helper import (
    lay_user_hien_tai, yeu_cau_dang_nhap,
    yeu_cau_quyen_bien_tap, yeu_cau_quyen_admin,
)
import services.tuyen_duong_service as td_service
import services.doan_tuyen_service as dt_service
import repositories.cap_quan_ly_repository as cql_repo
import repositories.don_vi_repository as dv_repo
import repositories.tuyen_duong_geo_repository as geo_repo

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(_ROOT, "templates"))


@router.get("/", response_class=HTMLResponse)
async def danh_sach(request: Request, user=Depends(yeu_cau_dang_nhap), conn=Depends(get_db)):
    tuyen_list = td_service.lay_tat_ca(conn)
    co_geo = set(geo_repo.lay_danh_sach_co_geo(conn))
    return templates.TemplateResponse("tuyen_duong/list.html", {
        "request": request, "user": user,
        "tuyen_list": tuyen_list, "co_geo": co_geo,
    })


@router.get("/api/list")
async def api_danh_sach(conn=Depends(get_db)):
    """JSON dùng cho bản đồ Leaflet."""
    rows = conn.execute("""
        SELECT td.id, td.ma_tuyen, td.ten_tuyen, cql.ma_cap AS cap_quan_ly,
               td.chieu_dai_quan_ly, td.chieu_dai_thuc_te,
               CASE WHEN g.id IS NOT NULL THEN 1 ELSE 0 END AS co_geo
        FROM tuyen_duong td
        JOIN cap_quan_ly cql ON cql.id = td.cap_quan_ly_id
        LEFT JOIN tuyen_duong_geo g ON g.tuyen_id = td.id
        ORDER BY cql.thu_tu_hien_thi, td.ma_tuyen
    """).fetchall()
    return JSONResponse([dict(r) for r in rows])


@router.get("/them", response_class=HTMLResponse)
async def form_them(request: Request, user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db)):
    return templates.TemplateResponse("tuyen_duong/form.html", {
        "request": request, "user": user,
        "tuyen": None,
        "cap_quan_ly_list": cql_repo.lay_dang_hoat_dong(conn),
        "don_vi_list": dv_repo.lay_dang_hoat_dong(conn),
        "loi": None,
    })


@router.post("/them")
async def luu_them(
    request: Request,
    ma_tuyen: str = Form(...), ten_tuyen: str = Form(...),
    cap_quan_ly_id: int = Form(...), don_vi_quan_ly_id: int = Form(...),
    diem_dau: str = Form(None), diem_cuoi: str = Form(None),
    nam_xay_dung: int = Form(None), nam_hoan_thanh: int = Form(None),
    ghi_chu: str = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        tuyen = td_service.them(conn, ma_tuyen, ten_tuyen, cap_quan_ly_id,
                                don_vi_quan_ly_id, diem_dau=diem_dau, diem_cuoi=diem_cuoi,
                                nam_xay_dung=nam_xay_dung, nam_hoan_thanh=nam_hoan_thanh,
                                ghi_chu=ghi_chu)
        return RedirectResponse(url=f"/tuyen-duong/{tuyen.id}", status_code=302)
    except td_service.TuyenDuongServiceError as e:
        return templates.TemplateResponse("tuyen_duong/form.html", {
            "request": request, "user": user, "tuyen": None, "loi": str(e),
            "cap_quan_ly_list": cql_repo.lay_dang_hoat_dong(conn),
            "don_vi_list": dv_repo.lay_dang_hoat_dong(conn),
        }, status_code=400)


@router.get("/{id}", response_class=HTMLResponse)
async def chi_tiet(request: Request, id: int,
                   user=Depends(yeu_cau_dang_nhap), conn=Depends(get_db)):
    tuyen = td_service.lay_theo_id(conn, id)
    doan_list = dt_service.lay_theo_tuyen_id(conn, id)
    geo = geo_repo.lay_theo_tuyen_id(conn, id)
    return templates.TemplateResponse("tuyen_duong/detail.html", {
        "request": request, "user": user,
        "tuyen": tuyen, "doan_list": doan_list, "geo": geo,
    })


@router.get("/{id}/sua", response_class=HTMLResponse)
async def form_sua(request: Request, id: int,
                   user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db)):
    tuyen = td_service.lay_theo_id(conn, id)
    return templates.TemplateResponse("tuyen_duong/form.html", {
        "request": request, "user": user, "tuyen": tuyen, "loi": None,
        "cap_quan_ly_list": cql_repo.lay_dang_hoat_dong(conn),
        "don_vi_list": dv_repo.lay_dang_hoat_dong(conn),
    })


@router.post("/{id}/sua")
async def luu_sua(
    request: Request, id: int,
    ten_tuyen: str = Form(...),
    cap_quan_ly_id: int = Form(...), don_vi_quan_ly_id: int = Form(...),
    diem_dau: str = Form(None), diem_cuoi: str = Form(None),
    nam_xay_dung: int = Form(None), nam_hoan_thanh: int = Form(None),
    ghi_chu: str = Form(None),
    user=Depends(yeu_cau_quyen_bien_tap), conn=Depends(get_db),
):
    try:
        td_service.sua(conn, id, ten_tuyen, cap_quan_ly_id, don_vi_quan_ly_id,
                       diem_dau=diem_dau, diem_cuoi=diem_cuoi,
                       nam_xay_dung=nam_xay_dung, nam_hoan_thanh=nam_hoan_thanh,
                       ghi_chu=ghi_chu)
        return RedirectResponse(url=f"/tuyen-duong/{id}", status_code=302)
    except td_service.TuyenDuongServiceError as e:
        tuyen = td_service.lay_theo_id(conn, id)
        return templates.TemplateResponse("tuyen_duong/form.html", {
            "request": request, "user": user, "tuyen": tuyen, "loi": str(e),
            "cap_quan_ly_list": cql_repo.lay_dang_hoat_dong(conn),
            "don_vi_list": dv_repo.lay_dang_hoat_dong(conn),
        }, status_code=400)


@router.post("/{id}/xoa")
async def xoa(id: int, user=Depends(yeu_cau_quyen_admin), conn=Depends(get_db)):
    td_service.xoa(conn, id)
    return RedirectResponse(url="/tuyen-duong/", status_code=302)
