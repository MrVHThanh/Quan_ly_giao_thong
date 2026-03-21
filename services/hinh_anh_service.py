"""
Service: HinhAnh — Hình ảnh hiện trạng đoạn tuyến  [MỚI]
Toàn bộ validation + business logic tập trung ở đây.

Tính năng chính:
- Đọc tọa độ GPS tự động từ EXIF ảnh bằng Pillow
- Lưu ảnh theo đoạn tuyến, kèm tọa độ GPS nếu có

Yêu cầu: pip install Pillow
"""

import os
import sqlite3
from typing import Optional, List

import models.hinh_anh_doan_tuyen as hinh_anh_model
import repositories.hinh_anh_repository as hinh_anh_repo
import repositories.doan_tuyen_repository as doan_tuyen_repo

DINH_DANG_HOP_LE = {".jpg", ".jpeg", ".png", ".webp"}


class HinhAnhServiceError(Exception):
    pass


def lay_theo_doan_id(
    conn: sqlite3.Connection, doan_id: int
) -> List[hinh_anh_model.HinhAnhDoanTuyen]:
    return hinh_anh_repo.lay_theo_doan_id(conn, doan_id)


def lay_theo_id(
    conn: sqlite3.Connection, id: int
) -> hinh_anh_model.HinhAnhDoanTuyen:
    obj = hinh_anh_repo.lay_theo_id(conn, id)
    if obj is None:
        raise HinhAnhServiceError(f"Không tìm thấy hình ảnh id={id}.")
    return obj


def them_hinh_anh(
    conn: sqlite3.Connection,
    doan_id: int,
    duong_dan_file: str,
    mo_ta: Optional[str] = None,
    ngay_chup: Optional[str] = None,
    nguoi_chup: Optional[str] = None,
    doc_exif_gps: bool = True,
) -> hinh_anh_model.HinhAnhDoanTuyen:
    """
    Thêm ảnh cho đoạn tuyến.
    Nếu doc_exif_gps=True, tự động đọc tọa độ GPS từ EXIF ảnh (nếu có).
    """
    _validate_doan_ton_tai(conn, doan_id)
    _validate_dinh_dang_file(duong_dan_file)

    lat: Optional[float] = None
    lng: Optional[float] = None

    if doc_exif_gps and os.path.isfile(duong_dan_file):
        lat, lng = _doc_gps_tu_exif(duong_dan_file)

    # Nếu chưa có ngày chụp, thử lấy từ EXIF
    if ngay_chup is None and os.path.isfile(duong_dan_file):
        ngay_chup = _doc_ngay_chup_tu_exif(duong_dan_file)

    obj = hinh_anh_model.HinhAnhDoanTuyen(
        doan_id=doan_id,
        duong_dan_file=duong_dan_file,
        mo_ta=mo_ta,
        ngay_chup=ngay_chup,
        nguoi_chup=nguoi_chup,
        lat=lat,
        lng=lng,
        ly_trinh_anh=None,  # Giai đoạn 2 mới tính
    )
    obj.id = hinh_anh_repo.them(conn, obj)
    return obj


def cap_nhat_ly_trinh_anh(
    conn: sqlite3.Connection, id: int, ly_trinh_anh: float
) -> None:
    """Cập nhật ly_trinh_anh sau khi tính từ GPS + đường tâm tuyến (Giai đoạn 2)."""
    lay_theo_id(conn, id)
    if ly_trinh_anh < 0:
        raise HinhAnhServiceError("Lý trình ảnh không được âm.")
    hinh_anh_repo.cap_nhat_ly_trinh(conn, id, ly_trinh_anh)


def xoa(conn: sqlite3.Connection, id: int) -> None:
    lay_theo_id(conn, id)
    hinh_anh_repo.xoa(conn, id)


# ── Đọc EXIF bằng Pillow ───────────────────────────────────────────────────

def _doc_gps_tu_exif(duong_dan_file: str) -> tuple[Optional[float], Optional[float]]:
    """
    Đọc tọa độ GPS từ EXIF ảnh JPEG.
    Trả về (lat, lng) hoặc (None, None) nếu không có/lỗi.
    """
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS

        img = Image.open(duong_dan_file)
        exif_data = img._getexif()
        if not exif_data:
            return None, None

        gps_info = None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                gps_info = {GPSTAGS.get(t, t): v for t, v in value.items()}
                break

        if not gps_info:
            return None, None

        lat = _chuyen_dms_sang_dd(
            gps_info.get("GPSLatitude"), gps_info.get("GPSLatitudeRef")
        )
        lng = _chuyen_dms_sang_dd(
            gps_info.get("GPSLongitude"), gps_info.get("GPSLongitudeRef")
        )
        return lat, lng

    except Exception:
        return None, None


def _doc_ngay_chup_tu_exif(duong_dan_file: str) -> Optional[str]:
    """Đọc ngày chụp từ EXIF. Trả về chuỗi 'YYYY-MM-DD' hoặc None."""
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS

        img = Image.open(duong_dan_file)
        exif_data = img._getexif()
        if not exif_data:
            return None
        for tag_id, value in exif_data.items():
            if TAGS.get(tag_id) == "DateTimeOriginal":
                # Định dạng EXIF: "YYYY:MM:DD HH:MM:SS"
                return str(value)[:10].replace(":", "-")
        return None
    except Exception:
        return None


def _chuyen_dms_sang_dd(
    dms: Optional[tuple], ref: Optional[str]
) -> Optional[float]:
    """Chuyển Degrees/Minutes/Seconds sang Decimal Degrees."""
    if not dms or not ref:
        return None
    try:
        degrees = float(dms[0])
        minutes = float(dms[1])
        seconds = float(dms[2])
        dd = degrees + minutes / 60 + seconds / 3600
        if ref in ("S", "W"):
            dd = -dd
        return round(dd, 7)
    except Exception:
        return None


# ── Validation nội bộ ──────────────────────────────────────────────────────

def _validate_doan_ton_tai(conn: sqlite3.Connection, doan_id: int) -> None:
    if doan_tuyen_repo.lay_theo_id(conn, doan_id) is None:
        raise HinhAnhServiceError(f"Đoạn tuyến id={doan_id} không tồn tại.")


def _validate_dinh_dang_file(duong_dan: str) -> None:
    ext = os.path.splitext(duong_dan)[1].lower()
    if ext not in DINH_DANG_HOP_LE:
        raise HinhAnhServiceError(
            f"Định dạng file '{ext}' không hợp lệ. "
            f"Chỉ chấp nhận: {', '.join(DINH_DANG_HOP_LE)}."
        )
