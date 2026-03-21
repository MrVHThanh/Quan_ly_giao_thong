"""
Repository: DonVi — Đơn vị quản lý / bảo dưỡng
Chỉ SQL thuần, dùng sqlite3.Row. KHÔNG hardcode index cột.
"""

import sqlite3
from typing import Optional, List
import models.don_vi as don_vi_model


def lay_tat_ca(conn: sqlite3.Connection) -> List[don_vi_model.DonVi]:
    sql = "SELECT * FROM don_vi ORDER BY parent_id NULLS FIRST, id"
    rows = conn.execute(sql).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_id(conn: sqlite3.Connection, id: int) -> Optional[don_vi_model.DonVi]:
    sql = "SELECT * FROM don_vi WHERE id = ?"
    row = conn.execute(sql, (id,)).fetchone()
    return _row_to_object(row) if row else None


def lay_theo_ma(conn: sqlite3.Connection, ma_don_vi: str) -> Optional[don_vi_model.DonVi]:
    sql = "SELECT * FROM don_vi WHERE ma_don_vi = ?"
    row = conn.execute(sql, (ma_don_vi,)).fetchone()
    return _row_to_object(row) if row else None


def lay_con_truc_tiep(conn: sqlite3.Connection, parent_id: int) -> List[don_vi_model.DonVi]:
    """Lấy danh sách đơn vị con trực tiếp của một đơn vị cha."""
    sql = "SELECT * FROM don_vi WHERE parent_id = ? AND is_active = 1 ORDER BY id"
    rows = conn.execute(sql, (parent_id,)).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_don_vi_goc(conn: sqlite3.Connection) -> List[don_vi_model.DonVi]:
    """Lấy các đơn vị không có cha (Công ty độc lập + TINH)."""
    sql = "SELECT * FROM don_vi WHERE parent_id IS NULL AND is_active = 1 ORDER BY id"
    rows = conn.execute(sql).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_dang_hoat_dong(conn: sqlite3.Connection) -> List[don_vi_model.DonVi]:
    sql = "SELECT * FROM don_vi WHERE is_active = 1 ORDER BY parent_id NULLS FIRST, id"
    rows = conn.execute(sql).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_cay_cha_con(conn: sqlite3.Connection) -> List[dict]:
    """
    Trả về cây cha-con dạng list[dict] với key 'don_vi' và 'con'.
    Chỉ lấy 2 cấp (cha → con trực tiếp).
    """
    cha_list = lay_don_vi_goc(conn)
    result = []
    for cha in cha_list:
        con_list = lay_con_truc_tiep(conn, cha.id)
        result.append({"don_vi": cha, "con": con_list})
    return result


def them(conn: sqlite3.Connection, obj: don_vi_model.DonVi) -> int:
    sql = """
        INSERT INTO don_vi (ma_don_vi, ten_don_vi, ten_viet_tat, parent_id,
                            cap_don_vi, dia_chi, so_dien_thoai, email, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur = conn.execute(sql, (
        obj.ma_don_vi, obj.ten_don_vi, obj.ten_viet_tat, obj.parent_id,
        obj.cap_don_vi, obj.dia_chi, obj.so_dien_thoai, obj.email, obj.is_active,
    ))
    conn.commit()
    return cur.lastrowid


def sua(conn: sqlite3.Connection, obj: don_vi_model.DonVi) -> bool:
    sql = """
        UPDATE don_vi
        SET ma_don_vi=?, ten_don_vi=?, ten_viet_tat=?, parent_id=?,
            cap_don_vi=?, dia_chi=?, so_dien_thoai=?, email=?, is_active=?
        WHERE id=?
    """
    cur = conn.execute(sql, (
        obj.ma_don_vi, obj.ten_don_vi, obj.ten_viet_tat, obj.parent_id,
        obj.cap_don_vi, obj.dia_chi, obj.so_dien_thoai, obj.email, obj.is_active,
        obj.id,
    ))
    conn.commit()
    return cur.rowcount > 0


def xoa_mem(conn: sqlite3.Connection, id: int) -> bool:
    cur = conn.execute("UPDATE don_vi SET is_active = 0 WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


def khoi_phuc(conn: sqlite3.Connection, id: int) -> bool:
    cur = conn.execute("UPDATE don_vi SET is_active = 1 WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


def _row_to_object(row: sqlite3.Row) -> don_vi_model.DonVi:
    return don_vi_model.DonVi(
        id=row["id"],
        ma_don_vi=row["ma_don_vi"],
        ten_don_vi=row["ten_don_vi"],
        ten_viet_tat=row["ten_viet_tat"],
        parent_id=row["parent_id"],
        cap_don_vi=row["cap_don_vi"],
        dia_chi=row["dia_chi"],
        so_dien_thoai=row["so_dien_thoai"],
        email=row["email"],
        is_active=row["is_active"],
        created_at=row["created_at"],
    )
