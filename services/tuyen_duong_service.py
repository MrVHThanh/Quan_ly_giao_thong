"""
Service: TuyenDuong — Tuyến đường
Toàn bộ validation + business logic tập trung ở đây.

Lưu ý: KHÔNG có hàm cap_nhat_chieu_dai — SQLite trigger tự động xử lý.
"""

import sqlite3
from typing import Optional, List

import models.tuyen_duong as tuyen_duong_model
import repositories.tuyen_duong_repository as tuyen_duong_repo
import repositories.doan_tuyen_repository as doan_tuyen_repo


class TuyenDuongServiceError(Exception):
    pass


def lay_tat_ca(conn: sqlite3.Connection) -> List[tuyen_duong_model.TuyenDuong]:
    return tuyen_duong_repo.lay_tat_ca(conn)


def lay_theo_id(conn: sqlite3.Connection, id: int) -> tuyen_duong_model.TuyenDuong:
    obj = tuyen_duong_repo.lay_theo_id(conn, id)
    if obj is None:
        raise TuyenDuongServiceError(f"Không tìm thấy tuyến đường id={id}.")
    return obj


def lay_theo_ma(conn: sqlite3.Connection, ma_tuyen: str) -> tuyen_duong_model.TuyenDuong:
    obj = tuyen_duong_repo.lay_theo_ma(conn, ma_tuyen)
    if obj is None:
        raise TuyenDuongServiceError(f"Không tìm thấy tuyến đường mã '{ma_tuyen}'.")
    return obj


def lay_theo_cap_quan_ly(
    conn: sqlite3.Connection, cap_quan_ly_id: int
) -> List[tuyen_duong_model.TuyenDuong]:
    return tuyen_duong_repo.lay_theo_cap_quan_ly(conn, cap_quan_ly_id)


def lay_theo_don_vi_quan_ly(
    conn: sqlite3.Connection, don_vi_id: int
) -> List[tuyen_duong_model.TuyenDuong]:
    return tuyen_duong_repo.lay_theo_don_vi_quan_ly(conn, don_vi_id)


def them(
    conn: sqlite3.Connection,
    ma_tuyen: str,
    ten_tuyen: str,
    cap_quan_ly_id: int,
    don_vi_quan_ly_id: int,
    diem_dau: Optional[str] = None,
    diem_cuoi: Optional[str] = None,
    lat_dau: Optional[float] = None,
    lng_dau: Optional[float] = None,
    lat_cuoi: Optional[float] = None,
    lng_cuoi: Optional[float] = None,
    nam_xay_dung: Optional[int] = None,
    nam_hoan_thanh: Optional[int] = None,
    ghi_chu: Optional[str] = None,
) -> tuyen_duong_model.TuyenDuong:
    _validate_ma(ma_tuyen)
    _validate_ten(ten_tuyen)
    _validate_toa_do(lat_dau, lng_dau, "điểm đầu")
    _validate_toa_do(lat_cuoi, lng_cuoi, "điểm cuối")
    _validate_nam(nam_xay_dung, nam_hoan_thanh)

    if tuyen_duong_repo.lay_theo_ma(conn, ma_tuyen) is not None:
        raise TuyenDuongServiceError(f"Mã tuyến '{ma_tuyen}' đã tồn tại.")

    obj = tuyen_duong_model.TuyenDuong(
        ma_tuyen=ma_tuyen.strip().upper(),
        ten_tuyen=ten_tuyen.strip(),
        cap_quan_ly_id=cap_quan_ly_id,
        don_vi_quan_ly_id=don_vi_quan_ly_id,
        diem_dau=diem_dau,
        diem_cuoi=diem_cuoi,
        lat_dau=lat_dau,
        lng_dau=lng_dau,
        lat_cuoi=lat_cuoi,
        lng_cuoi=lng_cuoi,
        nam_xay_dung=nam_xay_dung,
        nam_hoan_thanh=nam_hoan_thanh,
        ghi_chu=ghi_chu,
    )
    obj.id = tuyen_duong_repo.them(conn, obj)
    return obj


def sua(
    conn: sqlite3.Connection,
    id: int,
    ten_tuyen: str,
    cap_quan_ly_id: int,
    don_vi_quan_ly_id: int,
    diem_dau: Optional[str] = None,
    diem_cuoi: Optional[str] = None,
    lat_dau: Optional[float] = None,
    lng_dau: Optional[float] = None,
    lat_cuoi: Optional[float] = None,
    lng_cuoi: Optional[float] = None,
    nam_xay_dung: Optional[int] = None,
    nam_hoan_thanh: Optional[int] = None,
    ghi_chu: Optional[str] = None,
) -> tuyen_duong_model.TuyenDuong:
    obj = lay_theo_id(conn, id)
    _validate_ten(ten_tuyen)
    _validate_toa_do(lat_dau, lng_dau, "điểm đầu")
    _validate_toa_do(lat_cuoi, lng_cuoi, "điểm cuối")
    _validate_nam(nam_xay_dung, nam_hoan_thanh)

    obj.ten_tuyen = ten_tuyen.strip()
    obj.cap_quan_ly_id = cap_quan_ly_id
    obj.don_vi_quan_ly_id = don_vi_quan_ly_id
    obj.diem_dau = diem_dau
    obj.diem_cuoi = diem_cuoi
    obj.lat_dau = lat_dau
    obj.lng_dau = lng_dau
    obj.lat_cuoi = lat_cuoi
    obj.lng_cuoi = lng_cuoi
    obj.nam_xay_dung = nam_xay_dung
    obj.nam_hoan_thanh = nam_hoan_thanh
    obj.ghi_chu = ghi_chu
    tuyen_duong_repo.sua(conn, obj)
    return obj


def xoa(conn: sqlite3.Connection, id: int) -> None:
    lay_theo_id(conn, id)
    doan_list = doan_tuyen_repo.lay_theo_tuyen_id(conn, id)
    if doan_list:
        raise TuyenDuongServiceError(
            f"Không thể xóa tuyến id={id} vì còn {len(doan_list)} đoạn tuyến. "
            "Xóa hết các đoạn trước."
        )
    tuyen_duong_repo.xoa(conn, id)


# ── Validation nội bộ ──────────────────────────────────────────────────────

def _validate_ma(ma: str) -> None:
    if not ma or not ma.strip():
        raise TuyenDuongServiceError("Mã tuyến không được để trống.")
    if len(ma.strip()) > 20:
        raise TuyenDuongServiceError("Mã tuyến không được vượt quá 20 ký tự.")


def _validate_ten(ten: str) -> None:
    if not ten or not ten.strip():
        raise TuyenDuongServiceError("Tên tuyến không được để trống.")


def _validate_toa_do(lat: Optional[float], lng: Optional[float], nhan: str) -> None:
    if lat is None and lng is None:
        return  # cả hai NULL: chấp nhận
    if lat is None or lng is None:
        raise TuyenDuongServiceError(f"Tọa độ {nhan}: phải cung cấp cả lat và lng.")
    if not (-90 <= lat <= 90):
        raise TuyenDuongServiceError(f"Latitude {nhan} phải trong khoảng -90 đến 90.")
    if not (100 <= lng <= 110):
        raise TuyenDuongServiceError(
            f"Longitude {nhan} phải trong khoảng 100–110 (lãnh thổ Việt Nam)."
        )


def _validate_nam(nam_xay_dung: Optional[int], nam_hoan_thanh: Optional[int]) -> None:
    if nam_xay_dung is not None and not (1900 <= nam_xay_dung <= 2100):
        raise TuyenDuongServiceError("Năm xây dựng không hợp lệ.")
    if nam_hoan_thanh is not None and not (1900 <= nam_hoan_thanh <= 2100):
        raise TuyenDuongServiceError("Năm hoàn thành không hợp lệ.")
    if (nam_xay_dung is not None and nam_hoan_thanh is not None
            and nam_hoan_thanh < nam_xay_dung):
        raise TuyenDuongServiceError("Năm hoàn thành không thể nhỏ hơn năm xây dựng.")
