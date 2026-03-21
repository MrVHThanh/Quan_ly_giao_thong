"""
Route: ban_do.py
GET /ban-do/                      → trang bản đồ Leaflet.js
GET /ban-do/api/geo/{tuyen_id}    → GeoJSON coordinates của 1 tuyến
GET /ban-do/api/geo-all           → GeoJSON tất cả tuyến (dạng FeatureCollection)
"""

import json
import os, sys
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.database import get_db
from api.routes._auth_helper import yeu_cau_dang_nhap

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(_ROOT, "templates"))


@router.get("/", response_class=HTMLResponse)
async def trang_ban_do(request: Request, user=Depends(yeu_cau_dang_nhap)):
    return templates.TemplateResponse("ban_do.html", {"request": request, "user": user})


@router.get("/api/geo/{tuyen_id}")
async def geo_mot_tuyen(tuyen_id: int, conn=Depends(get_db)):
    """GeoJSON LineString của 1 tuyến — dùng cho Leaflet popup."""
    row = conn.execute("""
        SELECT td.ma_tuyen, td.ten_tuyen, td.chieu_dai_quan_ly,
               g.coordinates, g.so_diem, g.chieu_dai_gps
        FROM tuyen_duong td
        JOIN tuyen_duong_geo g ON g.tuyen_id = td.id
        WHERE td.id = ?
    """, (tuyen_id,)).fetchone()

    if row is None:
        raise HTTPException(status_code=404,
                            detail=f"Tuyến id={tuyen_id} chưa có dữ liệu GeoJSON.")

    return JSONResponse({
        "type": "Feature",
        "properties": {
            "tuyen_id":          tuyen_id,
            "ma_tuyen":          row["ma_tuyen"],
            "ten_tuyen":         row["ten_tuyen"],
            "chieu_dai_quan_ly": row["chieu_dai_quan_ly"],
            "chieu_dai_gps":     row["chieu_dai_gps"],
            "so_diem":           row["so_diem"],
        },
        "geometry": {
            "type": "LineString",
            "coordinates": json.loads(row["coordinates"]),
        },
    })


@router.get("/api/geo-all")
async def geo_tat_ca(conn=Depends(get_db)):
    """FeatureCollection tất cả tuyến có GeoJSON — load 1 lần cho Leaflet."""
    rows = conn.execute("""
        SELECT td.id, td.ma_tuyen, td.ten_tuyen,
               cql.ma_cap AS cap_quan_ly,
               td.chieu_dai_quan_ly, td.chieu_dai_thuc_te,
               g.coordinates, g.chieu_dai_gps
        FROM tuyen_duong td
        JOIN cap_quan_ly cql ON cql.id = td.cap_quan_ly_id
        JOIN tuyen_duong_geo g ON g.tuyen_id = td.id
        ORDER BY cql.thu_tu_hien_thi, td.ma_tuyen
    """).fetchall()

    features = []
    for r in rows:
        features.append({
            "type": "Feature",
            "properties": {
                "tuyen_id":          r["id"],
                "ma_tuyen":          r["ma_tuyen"],
                "ten_tuyen":         r["ten_tuyen"],
                "cap_quan_ly":       r["cap_quan_ly"],
                "chieu_dai_quan_ly": r["chieu_dai_quan_ly"],
                "chieu_dai_gps":     r["chieu_dai_gps"],
            },
            "geometry": {
                "type": "LineString",
                "coordinates": json.loads(r["coordinates"]),
            },
        })

    return JSONResponse({"type": "FeatureCollection", "features": features})
