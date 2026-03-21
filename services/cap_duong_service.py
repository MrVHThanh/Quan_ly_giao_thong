"""
Service: CapDuong — Cấp đường kỹ thuật
Toàn bộ validation + business logic tập trung ở đây.
"""

import sqlite3
from typing import Optional, List

import models.cap_duong as cap_duong_model
import repositories.cap_duong_repository as cap_duong_repo


class CapDuongServiceError(Exception):
    pass


def lay_tat_ca(conn: sqlite3.Connection) -> List[cap_duong_model.CapDuong]:
    return cap_duong_repo.lay_tat_ca(conn)


def lay_dang_hoat_dong(conn: sqlite3.Connection) -> List[cap_duong_model.CapDuong]:
    return cap_duong_repo.lay_dang_hoat_dong(conn)


def lay_theo_id(conn: sqlite3.Connection, id: int) -> cap_duong_model.CapDuong:
    obj = cap_duong_repo.lay_theo_id(conn, id)
    if obj is None:
        raise CapDuongServiceError(f"Không tìm thấy cấp đường id={id}.")
    return obj


def lay_theo_ma(conn: sqlite3.Connection, ma_cap: str) -> cap_duong_model.CapDuong:
    obj = cap_duong_repo.lay_theo_ma(conn, ma_cap)
    if obj is None:
        raise CapDuongServiceError(f"Không tìm thấy cấp đường mã '{ma_cap}'.")
    return obj


def them(
    conn: sqlite3.Connection,
    ma_cap: str,
    ten_cap: str,
    mo_ta: Optional[str] = None,
    thu_tu_hien_thi: Optional[int] = None,
) -> cap_duong_model.CapDuong:
    _validate_ma(ma_cap)
    _validate_ten(ten_cap)
    if cap_duong_repo.lay_theo_ma(conn, ma_cap) is not None:
        raise CapDuongServiceError(f"Mã cấp đường '{ma_cap}' đã tồn tại.")

    obj = cap_duong_model.CapDuong(
        ma_cap=ma_cap.strip().upper(),
        ten_cap=ten_cap.strip(),
        mo_ta=mo_ta,
        thu_tu_hien_thi=thu_tu_hien_thi,
        is_active=1,
    )
    obj.id = cap_duong_repo.them(conn, obj)
    return obj


def sua(
    conn: sqlite3.Connection,
    id: int,
    ten_cap: str,
    mo_ta: Optional[str] = None,
    thu_tu_hien_thi: Optional[int] = None,
) -> cap_duong_model.CapDuong:
    obj = lay_theo_id(conn, id)
    _validate_ten(ten_cap)
    obj.ten_cap = ten_cap.strip()
    obj.mo_ta = mo_ta
    obj.thu_tu_hien_thi = thu_tu_hien_thi
    cap_duong_repo.sua(conn, obj)
    return obj


def xoa_mem(conn: sqlite3.Connection, id: int) -> None:
    lay_theo_id(conn, id)
    cap_duong_repo.xoa_mem(conn, id)


def khoi_phuc(conn: sqlite3.Connection, id: int) -> None:
    lay_theo_id(conn, id)
    cap_duong_repo.khoi_phuc(conn, id)


# ── Validation nội bộ ──────────────────────────────────────────────────────

def _validate_ma(ma_cap: str) -> None:
    if not ma_cap or not ma_cap.strip():
        raise CapDuongServiceError("Mã cấp đường không được để trống.")
    if len(ma_cap.strip()) > 20:
        raise CapDuongServiceError("Mã cấp đường không được vượt quá 20 ký tự.")


def _validate_ten(ten_cap: str) -> None:
    if not ten_cap or not ten_cap.strip():
        raise CapDuongServiceError("Tên cấp đường không được để trống.")
