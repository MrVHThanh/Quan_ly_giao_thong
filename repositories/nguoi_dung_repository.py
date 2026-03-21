"""
Repository: NguoiDung — Tài khoản người dùng  [MỚI]
Chỉ SQL thuần, dùng sqlite3.Row. KHÔNG hardcode index cột.

Lưu ý: mat_khau_hash KHÔNG bao giờ đưa vào object trả về client.
       Dùng lay_hash_de_xac_thuc() riêng khi cần kiểm tra mật khẩu.
"""

import sqlite3
from typing import Optional, List
import models.nguoi_dung as nguoi_dung_model


def lay_tat_ca(conn: sqlite3.Connection) -> List[nguoi_dung_model.NguoiDung]:
    sql = "SELECT * FROM nguoi_dung ORDER BY created_at DESC"
    rows = conn.execute(sql).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_id(conn: sqlite3.Connection, id: int) -> Optional[nguoi_dung_model.NguoiDung]:
    row = conn.execute("SELECT * FROM nguoi_dung WHERE id = ?", (id,)).fetchone()
    return _row_to_object(row) if row else None


def lay_theo_ten_dang_nhap(conn: sqlite3.Connection, ten_dang_nhap: str) -> Optional[nguoi_dung_model.NguoiDung]:
    row = conn.execute(
        "SELECT * FROM nguoi_dung WHERE ten_dang_nhap = ?", (ten_dang_nhap,)
    ).fetchone()
    return _row_to_object(row) if row else None


def lay_theo_email(conn: sqlite3.Connection, email: str) -> Optional[nguoi_dung_model.NguoiDung]:
    row = conn.execute("SELECT * FROM nguoi_dung WHERE email = ?", (email,)).fetchone()
    return _row_to_object(row) if row else None


def lay_cho_duyet(conn: sqlite3.Connection) -> List[nguoi_dung_model.NguoiDung]:
    """Danh sách tài khoản đang chờ ADMIN duyệt."""
    sql = "SELECT * FROM nguoi_dung WHERE is_approved = 0 ORDER BY created_at"
    rows = conn.execute(sql).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_hash_de_xac_thuc(conn: sqlite3.Connection, ten_dang_nhap: str) -> Optional[str]:
    """Trả về mat_khau_hash để service so sánh bcrypt. KHÔNG dùng cho mục đích khác."""
    row = conn.execute(
        "SELECT mat_khau_hash FROM nguoi_dung WHERE ten_dang_nhap = ?", (ten_dang_nhap,)
    ).fetchone()
    return row["mat_khau_hash"] if row else None


def them(conn: sqlite3.Connection, obj: nguoi_dung_model.NguoiDung) -> int:
    sql = """
        INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau_hash, ho_ten, chuc_vu,
                                don_vi_id, so_dien_thoai, email, loai_quyen,
                                is_active, is_approved)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur = conn.execute(sql, (
        obj.ten_dang_nhap, obj.mat_khau_hash, obj.ho_ten, obj.chuc_vu,
        obj.don_vi_id, obj.so_dien_thoai, obj.email, obj.loai_quyen,
        obj.is_active, obj.is_approved,
    ))
    conn.commit()
    return cur.lastrowid


def sua(conn: sqlite3.Connection, obj: nguoi_dung_model.NguoiDung) -> bool:
    sql = """
        UPDATE nguoi_dung
        SET ho_ten=?, chuc_vu=?, don_vi_id=?, so_dien_thoai=?,
            email=?, loai_quyen=?, is_active=?
        WHERE id=?
    """
    cur = conn.execute(sql, (
        obj.ho_ten, obj.chuc_vu, obj.don_vi_id, obj.so_dien_thoai,
        obj.email, obj.loai_quyen, obj.is_active, obj.id,
    ))
    conn.commit()
    return cur.rowcount > 0


def cap_nhat_mat_khau(conn: sqlite3.Connection, id: int, mat_khau_hash: str) -> bool:
    cur = conn.execute(
        "UPDATE nguoi_dung SET mat_khau_hash = ? WHERE id = ?", (mat_khau_hash, id)
    )
    conn.commit()
    return cur.rowcount > 0


def duyet_tai_khoan(conn: sqlite3.Connection, id: int, approved_by_id: int) -> bool:
    sql = """
        UPDATE nguoi_dung
        SET is_approved=1, is_active=1, approved_by_id=?, approved_at=datetime('now','localtime')
        WHERE id=?
    """
    cur = conn.execute(sql, (approved_by_id, id))
    conn.commit()
    return cur.rowcount > 0


def cap_nhat_lan_dang_nhap(conn: sqlite3.Connection, id: int) -> bool:
    cur = conn.execute(
        "UPDATE nguoi_dung SET last_login = datetime('now','localtime') WHERE id = ?", (id,)
    )
    conn.commit()
    return cur.rowcount > 0


def vo_hieu_hoa(conn: sqlite3.Connection, id: int) -> bool:
    cur = conn.execute("UPDATE nguoi_dung SET is_active = 0 WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


def _row_to_object(row: sqlite3.Row) -> nguoi_dung_model.NguoiDung:
    return nguoi_dung_model.NguoiDung(
        id=row["id"],
        ten_dang_nhap=row["ten_dang_nhap"],
        mat_khau_hash=row["mat_khau_hash"],
        ho_ten=row["ho_ten"],
        chuc_vu=row["chuc_vu"],
        don_vi_id=row["don_vi_id"],
        so_dien_thoai=row["so_dien_thoai"],
        email=row["email"],
        loai_quyen=row["loai_quyen"],
        is_active=row["is_active"],
        is_approved=row["is_approved"],
        approved_by_id=row["approved_by_id"],
        approved_at=row["approved_at"],
        created_at=row["created_at"],
        last_login=row["last_login"],
    )
