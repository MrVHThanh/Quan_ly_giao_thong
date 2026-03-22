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
import repositories.cap_duong_repository as cd_repo
import repositories.tinh_trang_repository as tt_repo
import repositories.ket_cau_mat_repository as kcm_repo
import repositories.don_vi_repository as dv_repo
import repositories.tuyen_duong_geo_repository as geo_repo

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(_ROOT, "templates"))


# ── Custom Jinja2 filter: định dạng lý trình ───────────────────────────────
# VD: 39.0 → "Km39+000" | 66.5 → "Km66+500" | 0.005 → "Km0+005"
def _fmt_ly_trinh(val) -> str:
    if val is None:
        return "—"
    try:
        val = float(val)
        km = int(val)
        m  = round((val - km) * 1000)
        return f"Km{km}+{m:03d}"
    except (TypeError, ValueError):
        return str(val)

templates.env.filters["ly_trinh"] = _fmt_ly_trinh


@router.get("/", response_class=HTMLResponse)
async def danh_sach(request: Request, user=Depends(yeu_cau_dang_nhap), conn=Depends(get_db)):
    tuyen_list = td_service.lay_tat_ca(conn)
    co_geo     = set(geo_repo.lay_danh_sach_co_geo(conn))

    # --- Lookup cấp quản lý ---
    cql_list = cql_repo.lay_dang_hoat_dong(conn)
    map_cql  = {c.id: c for c in cql_list}

    # --- Thống kê tổng quan theo cấp quản lý ---
    tong_cd_toan_tinh = sum(t.chieu_dai_quan_ly or 0 for t in tuyen_list)

    # Gom nhóm
    _cap_data: dict = {}
    for t in tuyen_list:
        cid = t.cap_quan_ly_id
        if cid not in _cap_data:
            cql = map_cql.get(cid)
            _cap_data[cid] = {
                "ma_cap":   cql.ma_cap   if cql else "?",
                "ten_cap":  cql.ten_cap  if cql else "Không rõ",
                "so_tuyen": 0,
                "chieu_dai": 0.0,
            }
        _cap_data[cid]["so_tuyen"]  += 1
        _cap_data[cid]["chieu_dai"] += t.chieu_dai_quan_ly or 0

    # Sắp xếp theo thu_tu_hien_thi của cql_list, tính tỉ lệ
    thong_ke_cap = []
    for cql in cql_list:
        if cql.id in _cap_data:
            item = _cap_data[cql.id]
            item["ti_le"] = round(
                item["chieu_dai"] / tong_cd_toan_tinh * 100, 1
            ) if tong_cd_toan_tinh else 0.0
            thong_ke_cap.append(item)

    return templates.TemplateResponse("tuyen_duong/list.html", {
        "request": request, "user": user,
        "tuyen_list":          tuyen_list,
        "co_geo":              co_geo,
        "map_cql":             map_cql,
        "thong_ke_cap":        thong_ke_cap,
        "tong_so_tuyen":       len(tuyen_list),
        "tong_cd_toan_tinh":   round(tong_cd_toan_tinh, 3),
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
    tuyen     = td_service.lay_theo_id(conn, id)
    doan_list = dt_service.lay_theo_tuyen_id(conn, id)
    geo       = geo_repo.lay_theo_tuyen_id(conn, id)

    # --- Lookup maps: id → object (hiển thị tên thay ID trong bảng đoạn) ---
    cap_list = cd_repo.lay_dang_hoat_dong(conn)
    tt_list  = tt_repo.lay_dang_hoat_dong(conn)
    kcm_list = kcm_repo.lay_dang_hoat_dong(conn)

    map_cap = {c.id: c for c in cap_list}
    map_tt  = {t.id: t for t in tt_list}
    map_kcm = {k.id: k for k in kcm_list}

    # Tổng chiều dài quản lý của tuyến (dùng tính Tỉ lệ %)
    tong_chieu_dai = tuyen.chieu_dai_quan_ly or sum(
        (d.chieu_dai or 0) for d in doan_list
    )

    return templates.TemplateResponse("tuyen_duong/detail.html", {
        "request":       request,
        "user":          user,
        "tuyen":         tuyen,
        "doan_list":     doan_list,
        "geo":           geo,
        "map_cap":       map_cap,
        "map_tt":        map_tt,
        "map_kcm":       map_kcm,
        "tong_chieu_dai": tong_chieu_dai,
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