"""
Service: DonVi — Đơn vị quản lý / bảo dưỡng
Toàn bộ validation + business logic tập trung ở đây.
Có kiểm tra vòng lặp (cycle) khi thiết lập quan hệ cha-con.
"""

import sqlite3
from typing import Optional, List

import models.don_vi as don_vi_model
import repositories.don_vi_repository as don_vi_repo


class DonViServiceError(Exception):
    pass


def lay_tat_ca(conn: sqlite3.Connection) -> List[don_vi_model.DonVi]:
    return don_vi_repo.lay_tat_ca(conn)


def lay_dang_hoat_dong(conn: sqlite3.Connection) -> List[don_vi_model.DonVi]:
    return don_vi_repo.lay_dang_hoat_dong(conn)


def lay_theo_id(conn: sqlite3.Connection, id: int) -> don_vi_model.DonVi:
    obj = don_vi_repo.lay_theo_id(conn, id)
    if obj is None:
        raise DonViServiceError(f"Không tìm thấy đơn vị id={id}.")
    return obj


def lay_theo_ma(conn: sqlite3.Connection, ma_don_vi: str) -> don_vi_model.DonVi:
    obj = don_vi_repo.lay_theo_ma(conn, ma_don_vi)
    if obj is None:
        raise DonViServiceError(f"Không tìm thấy đơn vị mã '{ma_don_vi}'.")
    return obj


def lay_cay_cha_con(conn: sqlite3.Connection) -> List[dict]:
    return don_vi_repo.lay_cay_cha_con(conn)


def them(
    conn: sqlite3.Connection,
    ma_don_vi: str,
    ten_don_vi: str,
    ten_viet_tat: Optional[str] = None,
    parent_id: Optional[int] = None,
    cap_don_vi: Optional[str] = None,
    dia_chi: Optional[str] = None,
    so_dien_thoai: Optional[str] = None,
    email: Optional[str] = None,
) -> don_vi_model.DonVi:
    _validate_ma(ma_don_vi)
    _validate_ten(ten_don_vi)
    if don_vi_repo.lay_theo_ma(conn, ma_don_vi) is not None:
        raise DonViServiceError(f"Mã đơn vị '{ma_don_vi}' đã tồn tại.")
    if parent_id is not None:
        _kiem_tra_parent_ton_tai(conn, parent_id)

    obj = don_vi_model.DonVi(
        ma_don_vi=ma_don_vi.strip().upper(),
        ten_don_vi=ten_don_vi.strip(),
        ten_viet_tat=ten_viet_tat.strip() if ten_viet_tat else None,
        parent_id=parent_id,
        cap_don_vi=cap_don_vi,
        dia_chi=dia_chi,
        so_dien_thoai=so_dien_thoai,
        email=email,
        is_active=1,
    )
    obj.id = don_vi_repo.them(conn, obj)
    return obj


def sua(
    conn: sqlite3.Connection,
    id: int,
    ten_don_vi: str,
    ten_viet_tat: Optional[str] = None,
    parent_id: Optional[int] = None,
    cap_don_vi: Optional[str] = None,
    dia_chi: Optional[str] = None,
    so_dien_thoai: Optional[str] = None,
    email: Optional[str] = None,
) -> don_vi_model.DonVi:
    obj = lay_theo_id(conn, id)
    _validate_ten(ten_don_vi)
    if parent_id is not None:
        _kiem_tra_parent_ton_tai(conn, parent_id)
        _kiem_tra_vong_lap(conn, id, parent_id)

    obj.ten_don_vi = ten_don_vi.strip()
    obj.ten_viet_tat = ten_viet_tat.strip() if ten_viet_tat else None
    obj.parent_id = parent_id
    obj.cap_don_vi = cap_don_vi
    obj.dia_chi = dia_chi
    obj.so_dien_thoai = so_dien_thoai
    obj.email = email
    don_vi_repo.sua(conn, obj)
    return obj


def xoa_mem(conn: sqlite3.Connection, id: int) -> None:
    obj = lay_theo_id(conn, id)
    con_list = don_vi_repo.lay_con_truc_tiep(conn, id)
    if con_list:
        ten_con = ", ".join(c.ma_don_vi for c in con_list)
        raise DonViServiceError(
            f"Không thể vô hiệu hóa đơn vị '{obj.ma_don_vi}' "
            f"vì còn đơn vị con: {ten_con}."
        )
    don_vi_repo.xoa_mem(conn, id)


def khoi_phuc(conn: sqlite3.Connection, id: int) -> None:
    lay_theo_id(conn, id)
    don_vi_repo.khoi_phuc(conn, id)


# ── Validation nội bộ ──────────────────────────────────────────────────────

def _validate_ma(ma: str) -> None:
    if not ma or not ma.strip():
        raise DonViServiceError("Mã đơn vị không được để trống.")
    if len(ma.strip()) > 30:
        raise DonViServiceError("Mã đơn vị không được vượt quá 30 ký tự.")


def _validate_ten(ten: str) -> None:
    if not ten or not ten.strip():
        raise DonViServiceError("Tên đơn vị không được để trống.")


def _kiem_tra_parent_ton_tai(conn: sqlite3.Connection, parent_id: int) -> None:
    if don_vi_repo.lay_theo_id(conn, parent_id) is None:
        raise DonViServiceError(f"Đơn vị cha id={parent_id} không tồn tại.")


def _kiem_tra_vong_lap(conn: sqlite3.Connection, id: int, parent_id_moi: int) -> None:
    """
    Ngăn vòng lặp trong cây cha-con.
    Ví dụ: A→B→C, nếu đặt parent của A = C thì A→B→C→A (vòng lặp).
    Duyệt ngược từ parent_id_moi lên root, nếu gặp id thì báo lỗi.
    """
    visited = set()
    current_id: Optional[int] = parent_id_moi
    while current_id is not None:
        if current_id == id:
            raise DonViServiceError(
                "Không thể thiết lập quan hệ cha-con tạo thành vòng lặp."
            )
        if current_id in visited:
            break  # tránh lặp vô hạn nếu DB đã có vòng lặp từ trước
        visited.add(current_id)
        node = don_vi_repo.lay_theo_id(conn, current_id)
        current_id = node.parent_id if node else None
