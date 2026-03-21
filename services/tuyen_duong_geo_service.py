"""
Service: TuyenDuongGeo — Dữ liệu tọa độ GeoJSON theo tuyến  [MỚI]
Toàn bộ validation + business logic tập trung ở đây.

Tính năng:
- Import file *.geojson → lưu vào bảng tuyen_duong_geo
- Export DB → xuất file *.geojson
- Tính chiều dài GPS từ chuỗi tọa độ (Haversine)

Quy ước:
- Tên file = mã tuyến: QL4E.geojson, DT158.geojson
- road_name trong file = tên tuyến trong DB
"""

import json
import math
import os
import sqlite3
from typing import Optional, List

import models.tuyen_duong_geo as tuyen_duong_geo_model
import repositories.tuyen_duong_geo_repository as tuyen_duong_geo_repo
import repositories.tuyen_duong_repository as tuyen_duong_repo


class TuyenDuongGeoServiceError(Exception):
    pass


def lay_theo_tuyen_id(
    conn: sqlite3.Connection, tuyen_id: int
) -> Optional[tuyen_duong_geo_model.TuyenDuongGeo]:
    return tuyen_duong_geo_repo.lay_theo_tuyen_id(conn, tuyen_id)


def lay_tat_ca(conn: sqlite3.Connection) -> List[tuyen_duong_geo_model.TuyenDuongGeo]:
    return tuyen_duong_geo_repo.lay_tat_ca(conn)


def lay_danh_sach_co_geo(conn: sqlite3.Connection) -> List[int]:
    return tuyen_duong_geo_repo.lay_danh_sach_co_geo(conn)


def import_tu_file(
    conn: sqlite3.Connection,
    duong_dan_file: str,
    ma_tuyen: Optional[str] = None,
) -> tuyen_duong_geo_model.TuyenDuongGeo:
    """
    Import file GeoJSON vào DB.
    Nếu không truyền ma_tuyen, lấy từ tên file (VD: QL4E.geojson → QL4E).
    """
    if not os.path.isfile(duong_dan_file):
        raise TuyenDuongGeoServiceError(f"File không tồn tại: {duong_dan_file}")

    ten_file = os.path.basename(duong_dan_file)
    if ma_tuyen is None:
        ma_tuyen = os.path.splitext(ten_file)[0].upper()

    tuyen = tuyen_duong_repo.lay_theo_ma(conn, ma_tuyen)
    if tuyen is None:
        raise TuyenDuongGeoServiceError(
            f"Không tìm thấy tuyến mã '{ma_tuyen}' trong DB. "
            "Kiểm tra lại tên file hoặc truyền ma_tuyen."
        )

    with open(duong_dan_file, encoding="utf-8") as f:
        geojson = json.load(f)

    coordinates = _trich_xuat_coordinates(geojson, duong_dan_file)
    so_diem = len(coordinates)
    chieu_dai_gps = _tinh_chieu_dai_km(coordinates)

    obj = tuyen_duong_geo_model.TuyenDuongGeo(
        tuyen_id=tuyen.id,
        coordinates=json.dumps(coordinates),
        so_diem=so_diem,
        chieu_dai_gps=round(chieu_dai_gps, 3),
        nguon=ten_file,
    )
    tuyen_duong_geo_repo.them_hoac_cap_nhat(conn, obj)
    return tuyen_duong_geo_repo.lay_theo_tuyen_id(conn, tuyen.id)


def export_ra_file(
    conn: sqlite3.Connection,
    tuyen_id: int,
    thu_muc_xuat: str,
) -> str:
    """
    Xuất tuyến ra file GeoJSON.
    Trả về đường dẫn file đã xuất.
    """
    tuyen = tuyen_duong_repo.lay_theo_id(conn, tuyen_id)
    if tuyen is None:
        raise TuyenDuongGeoServiceError(f"Không tìm thấy tuyến id={tuyen_id}.")

    geo = tuyen_duong_geo_repo.lay_theo_tuyen_id(conn, tuyen_id)
    if geo is None:
        raise TuyenDuongGeoServiceError(
            f"Tuyến '{tuyen.ma_tuyen}' chưa có dữ liệu GeoJSON."
        )

    coordinates = json.loads(geo.coordinates)
    geojson_obj = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "road_id": tuyen.ma_tuyen,
                    "road_name": tuyen.ten_tuyen,
                    "chieu_dai_gps_km": geo.chieu_dai_gps,
                    "so_diem": geo.so_diem,
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates,
                },
            }
        ],
    }

    os.makedirs(thu_muc_xuat, exist_ok=True)
    ten_file = f"{tuyen.ma_tuyen}.geojson"
    duong_dan_xuat = os.path.join(thu_muc_xuat, ten_file)

    with open(duong_dan_xuat, "w", encoding="utf-8") as f:
        json.dump(geojson_obj, f, ensure_ascii=False, indent=2)

    return duong_dan_xuat


def xoa(conn: sqlite3.Connection, tuyen_id: int) -> None:
    if tuyen_duong_geo_repo.lay_theo_tuyen_id(conn, tuyen_id) is None:
        raise TuyenDuongGeoServiceError(
            f"Tuyến id={tuyen_id} chưa có dữ liệu GeoJSON."
        )
    tuyen_duong_geo_repo.xoa(conn, tuyen_id)


# ── Helpers GeoJSON ────────────────────────────────────────────────────────

def _trich_xuat_coordinates(geojson: dict, ten_file: str) -> List[List[float]]:
    """Trích xuất mảng [[lng, lat], ...] từ cấu trúc GeoJSON."""
    try:
        features = geojson.get("features", [])
        for feature in features:
            geom = feature.get("geometry", {})
            geom_type = geom.get("type", "")
            if geom_type == "LineString":
                return geom["coordinates"]
            if geom_type == "MultiLineString":
                # Nối tất cả LineString thành một mảng liên tục
                coords = []
                for part in geom["coordinates"]:
                    coords.extend(part)
                return coords
        # Thử đọc trực tiếp nếu là geometry đơn
        if geojson.get("type") == "LineString":
            return geojson["coordinates"]
        raise TuyenDuongGeoServiceError(
            f"Không tìm thấy geometry LineString trong file {ten_file}."
        )
    except TuyenDuongGeoServiceError:
        raise
    except Exception as e:
        raise TuyenDuongGeoServiceError(
            f"Lỗi đọc cấu trúc GeoJSON từ {ten_file}: {e}"
        )


def _tinh_chieu_dai_km(coordinates: List[List[float]]) -> float:
    """Tính tổng chiều dài từ chuỗi tọa độ [lng, lat] bằng công thức Haversine."""
    R = 6371.0  # bán kính Trái Đất (km)
    tong = 0.0
    for i in range(1, len(coordinates)):
        lng1, lat1 = coordinates[i - 1]
        lng2, lat2 = coordinates[i]
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = (math.sin(dlat / 2) ** 2
             + math.cos(math.radians(lat1))
             * math.cos(math.radians(lat2))
             * math.sin(dlng / 2) ** 2)
        tong += R * 2 * math.asin(math.sqrt(a))
    return tong
