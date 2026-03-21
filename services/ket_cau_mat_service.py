"""
Service: KetCauMatDuong — Kết cấu mặt đường  [MỚI]
Toàn bộ validation + business logic tập trung ở đây.
Có hàm get_or_create dùng khi seed dữ liệu.
"""

import sqlite3
from typing import Optional, List

import models.ket_cau_mat_duong as ket_cau_mat_model
import repositories.ket_cau_mat_repository as ket_cau_mat_repo

MA_HOP_LE = {"BTN", "BTXM", "HH", "LN", "CP", "DAT", "BTN+LN", "BTXM+LN"}


class KetCauMatServiceError(Exception):
    pass


def lay_tat_ca(conn: sqlite3.Connection) -> List[ket_cau_mat_model.KetCauMatDuong]:
    return ket_cau_mat_repo.lay_tat_ca(conn)


def lay_dang_hoat_dong(conn: sqlite3.Connection) -> List[ket_cau_mat_model.KetCauMatDuong]:
    return ket_cau_mat_repo.lay_dang_hoat_dong(conn)


def lay_theo_id(conn: sqlite3.Connection, id: int) -> ket_cau_mat_model.KetCauMatDuong:
    obj = ket_cau_mat_repo.lay_theo_id(conn, id)
    if obj is None:
        raise KetCauMatServiceError(f"Không tìm thấy kết cấu mặt đường id={id}.")
    return obj


def lay_theo_ma(conn: sqlite3.Connection, ma_ket_cau: str) -> ket_cau_mat_model.KetCauMatDuong:
    obj = ket_cau_mat_repo.lay_theo_ma(conn, ma_ket_cau)
    if obj is None:
        raise KetCauMatServiceError(f"Không tìm thấy kết cấu mặt đường mã '{ma_ket_cau}'.")
    return obj


def get_or_create(
    conn: sqlite3.Connection,
    ma_ket_cau: str,
    ten_ket_cau: str,
    mo_ta: Optional[str] = None,
    thu_tu_hien_thi: Optional[int] = None,
) -> ket_cau_mat_model.KetCauMatDuong:
    """
    Trả về bản ghi đã có hoặc tạo mới nếu chưa tồn tại.
    Dùng khi seed dữ liệu để đảm bảo idempotent.
    """
    obj = ket_cau_mat_repo.lay_theo_ma(conn, ma_ket_cau)
    if obj is not None:
        return obj
    return them(conn, ma_ket_cau, ten_ket_cau, mo_ta, thu_tu_hien_thi)


def them(
    conn: sqlite3.Connection,
    ma_ket_cau: str,
    ten_ket_cau: str,
    mo_ta: Optional[str] = None,
    thu_tu_hien_thi: Optional[int] = None,
) -> ket_cau_mat_model.KetCauMatDuong:
    _validate_ma(ma_ket_cau)
    _validate_ten(ten_ket_cau)
    if ket_cau_mat_repo.lay_theo_ma(conn, ma_ket_cau) is not None:
        raise KetCauMatServiceError(f"Mã kết cấu mặt đường '{ma_ket_cau}' đã tồn tại.")

    obj = ket_cau_mat_model.KetCauMatDuong(
        ma_ket_cau=ma_ket_cau.strip().upper(),
        ten_ket_cau=ten_ket_cau.strip(),
        mo_ta=mo_ta,
        thu_tu_hien_thi=thu_tu_hien_thi,
        is_active=1,
    )
    obj.id = ket_cau_mat_repo.them(conn, obj)
    return obj


def sua(
    conn: sqlite3.Connection,
    id: int,
    ten_ket_cau: str,
    mo_ta: Optional[str] = None,
    thu_tu_hien_thi: Optional[int] = None,
) -> ket_cau_mat_model.KetCauMatDuong:
    obj = lay_theo_id(conn, id)
    _validate_ten(ten_ket_cau)
    obj.ten_ket_cau = ten_ket_cau.strip()
    obj.mo_ta = mo_ta
    obj.thu_tu_hien_thi = thu_tu_hien_thi
    ket_cau_mat_repo.sua(conn, obj)
    return obj


def xoa_mem(conn: sqlite3.Connection, id: int) -> None:
    lay_theo_id(conn, id)
    ket_cau_mat_repo.xoa_mem(conn, id)


def khoi_phuc(conn: sqlite3.Connection, id: int) -> None:
    lay_theo_id(conn, id)
    ket_cau_mat_repo.khoi_phuc(conn, id)


# ── Validation nội bộ ──────────────────────────────────────────────────────

def _validate_ma(ma_ket_cau: str) -> None:
    if not ma_ket_cau or not ma_ket_cau.strip():
        raise KetCauMatServiceError("Mã kết cấu mặt đường không được để trống.")
    if ma_ket_cau.strip().upper() not in MA_HOP_LE:
        raise KetCauMatServiceError(
            f"Mã kết cấu '{ma_ket_cau}' không hợp lệ. "
            f"Các mã được phép: {', '.join(sorted(MA_HOP_LE))}."
        )


def _validate_ten(ten_ket_cau: str) -> None:
    if not ten_ket_cau or not ten_ket_cau.strip():
        raise KetCauMatServiceError("Tên kết cấu mặt đường không được để trống.")
