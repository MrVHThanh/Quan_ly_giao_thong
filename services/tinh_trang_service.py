"""
Service: TinhTrang — Tình trạng đường
Toàn bộ validation + business logic tập trung ở đây.
"""

import sqlite3
from typing import Optional, List

import models.tinh_trang as tinh_trang_model
import repositories.tinh_trang_repository as tinh_trang_repo

MA_HOP_LE = {"TOT", "TB", "KEM", "HH_NANG", "THI_CONG", "BAO_TRI", "TAM_DONG", "NGUNG", "CHUA_XD"}


class TinhTrangServiceError(Exception):
    pass


def lay_tat_ca(conn: sqlite3.Connection) -> List[tinh_trang_model.TinhTrang]:
    return tinh_trang_repo.lay_tat_ca(conn)


def lay_dang_hoat_dong(conn: sqlite3.Connection) -> List[tinh_trang_model.TinhTrang]:
    return tinh_trang_repo.lay_dang_hoat_dong(conn)


def lay_theo_id(conn: sqlite3.Connection, id: int) -> tinh_trang_model.TinhTrang:
    obj = tinh_trang_repo.lay_theo_id(conn, id)
    if obj is None:
        raise TinhTrangServiceError(f"Không tìm thấy tình trạng id={id}.")
    return obj


def lay_theo_ma(conn: sqlite3.Connection, ma_tinh_trang: str) -> tinh_trang_model.TinhTrang:
    obj = tinh_trang_repo.lay_theo_ma(conn, ma_tinh_trang)
    if obj is None:
        raise TinhTrangServiceError(f"Không tìm thấy tình trạng mã '{ma_tinh_trang}'.")
    return obj


def them(
    conn: sqlite3.Connection,
    ma_tinh_trang: str,
    ten_tinh_trang: str,
    mo_ta: Optional[str] = None,
    mau_hien_thi: Optional[str] = None,
    thu_tu_hien_thi: Optional[int] = None,
) -> tinh_trang_model.TinhTrang:
    _validate_ma(ma_tinh_trang)
    _validate_ten(ten_tinh_trang)
    if mau_hien_thi:
        _validate_mau(mau_hien_thi)
    if tinh_trang_repo.lay_theo_ma(conn, ma_tinh_trang) is not None:
        raise TinhTrangServiceError(f"Mã tình trạng '{ma_tinh_trang}' đã tồn tại.")

    obj = tinh_trang_model.TinhTrang(
        ma_tinh_trang=ma_tinh_trang.strip().upper(),
        ten_tinh_trang=ten_tinh_trang.strip(),
        mo_ta=mo_ta,
        mau_hien_thi=mau_hien_thi,
        thu_tu_hien_thi=thu_tu_hien_thi,
        is_active=1,
    )
    obj.id = tinh_trang_repo.them(conn, obj)
    return obj


def sua(
    conn: sqlite3.Connection,
    id: int,
    ten_tinh_trang: str,
    mo_ta: Optional[str] = None,
    mau_hien_thi: Optional[str] = None,
    thu_tu_hien_thi: Optional[int] = None,
) -> tinh_trang_model.TinhTrang:
    obj = lay_theo_id(conn, id)
    _validate_ten(ten_tinh_trang)
    if mau_hien_thi:
        _validate_mau(mau_hien_thi)
    obj.ten_tinh_trang = ten_tinh_trang.strip()
    obj.mo_ta = mo_ta
    obj.mau_hien_thi = mau_hien_thi
    obj.thu_tu_hien_thi = thu_tu_hien_thi
    tinh_trang_repo.sua(conn, obj)
    return obj


def xoa_mem(conn: sqlite3.Connection, id: int) -> None:
    lay_theo_id(conn, id)
    tinh_trang_repo.xoa_mem(conn, id)


def khoi_phuc(conn: sqlite3.Connection, id: int) -> None:
    lay_theo_id(conn, id)
    tinh_trang_repo.khoi_phuc(conn, id)


# ── Validation nội bộ ──────────────────────────────────────────────────────

def _validate_ma(ma_tinh_trang: str) -> None:
    if not ma_tinh_trang or not ma_tinh_trang.strip():
        raise TinhTrangServiceError("Mã tình trạng không được để trống.")
    if ma_tinh_trang.strip().upper() not in MA_HOP_LE:
        raise TinhTrangServiceError(
            f"Mã tình trạng '{ma_tinh_trang}' không hợp lệ. "
            f"Các mã được phép: {', '.join(sorted(MA_HOP_LE))}."
        )


def _validate_ten(ten: str) -> None:
    if not ten or not ten.strip():
        raise TinhTrangServiceError("Tên tình trạng không được để trống.")


def _validate_mau(mau: str) -> None:
    """Màu HEX phải đúng định dạng #RRGGBB hoặc #RGB."""
    import re
    if not re.match(r'^#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})$', mau.strip()):
        raise TinhTrangServiceError(
            f"Mã màu '{mau}' không hợp lệ. Phải theo định dạng #RRGGBB hoặc #RGB."
        )
