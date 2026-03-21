"""
Route: thong_ke.py
GET /thong-ke/              → trang thống kê tổng hợp toàn tỉnh
GET /thong-ke/api/toan-tinh → JSON thống kê toàn tỉnh
GET /thong-ke/api/tuyen/{id} → JSON thống kê 1 tuyến
"""

import os, sys
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.database import get_db
from api.routes._auth_helper import yeu_cau_dang_nhap
import services.thong_ke_service as tk_service

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(_ROOT, "templates"))


@router.get("/", response_class=HTMLResponse)
async def trang_thong_ke(request: Request,
                         user=Depends(yeu_cau_dang_nhap), conn=Depends(get_db)):
    toan_tinh = tk_service.lay_thong_ke_toan_tinh(conn)
    return templates.TemplateResponse("thong_ke.html", {
        "request": request, "user": user, "toan_tinh": toan_tinh,
    })


@router.get("/api/toan-tinh")
async def api_toan_tinh(conn=Depends(get_db)):
    tk = tk_service.lay_thong_ke_toan_tinh(conn)
    return JSONResponse({
        "tong_so_tuyen":          tk.tong_so_tuyen,
        "tong_so_doan":           tk.tong_so_doan,
        "tong_so_doan_di_chung":  tk.tong_so_doan_di_chung,
        "tong_chieu_dai_quan_ly": tk.tong_chieu_dai_quan_ly,
        "tong_chieu_dai_thuc_te": tk.tong_chieu_dai_thuc_te,
        "tong_chieu_dai_di_chung":tk.tong_chieu_dai_di_chung,
        "theo_cap_quan_ly":       tk.theo_cap_quan_ly,
        "theo_tinh_trang":        tk.theo_tinh_trang,
        "theo_ket_cau_mat":       tk.theo_ket_cau_mat,
        "theo_cap_duong":         tk.theo_cap_duong,
    })


@router.get("/api/tuyen/{id}")
async def api_mot_tuyen(id: int, conn=Depends(get_db)):
    tk = tk_service.lay_thong_ke_mot_tuyen(conn, id)
    return JSONResponse({
        "ma_tuyen":           tk.ma_tuyen,
        "ten_tuyen":          tk.ten_tuyen,
        "tong_so_doan":       tk.tong_so_doan,
        "chieu_dai_quan_ly":  tk.chieu_dai_quan_ly,
        "chieu_dai_thuc_te":  tk.chieu_dai_thuc_te,
        "theo_tinh_trang": {
            "TOT": tk.chieu_dai_tot, "TB": tk.chieu_dai_tb,
            "KEM": tk.chieu_dai_kem, "HH_NANG": tk.chieu_dai_hu_hong_nang,
            "THI_CONG": tk.chieu_dai_thi_cong,
        },
        "theo_ket_cau_mat": {
            "BTN": tk.chieu_dai_btn,   "BTXM": tk.chieu_dai_btxm,
            "HH":  tk.chieu_dai_hh,    "LN":   tk.chieu_dai_ln,
            "CP":  tk.chieu_dai_cp,    "DAT":  tk.chieu_dai_dat,
            "BTN+LN": tk.chieu_dai_btn_ln, "BTXM+LN": tk.chieu_dai_btxm_ln,
        },
    })
