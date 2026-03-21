"""
Repository: TinhTrang — Tình trạng đường
Chỉ SQL thuần, dùng sqlite3.Row. KHÔNG hardcode index cột.
"""

import sqlite3
from typing import Optional, List
import models.tinh_trang as tinh_trang_model


def lay_tat_ca(conn: sqlite3.Connection) -> List[tinh_trang_model.TinhTrang]:
    sql = "SELECT * FROM tinh_trang ORDER BY thu_tu_hien_thi"
    rows = conn.execute(sql).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_id(conn: sqlite3.Connection, id: int) -> Optional[tinh_trang_model.TinhTrang]:
    sql = "SELECT * FROM tinh_trang WHERE id = ?"
    row = conn.execute(sql, (id,)).fetchone()
    return _row_to_object(row) if row else None


def lay_theo_ma(conn: sqlite3.Connection, ma_tinh_trang: str) -> Optional[tinh_trang_model.TinhTrang]:
    sql = "SELECT * FROM tinh_trang WHERE ma_tinh_trang = ?"
    row = conn.execute(sql, (ma_tinh_trang,)).fetchone()
    return _row_to_object(row) if row else None


def lay_dang_hoat_dong(conn: sqlite3.Connection) -> List[tinh_trang_model.TinhTrang]:
    sql = "SELECT * FROM tinh_trang WHERE is_active = 1 ORDER BY thu_tu_hien_thi"
    rows = conn.execute(sql).fetchall()
    return [_row_to_object(r) for r in rows]


def them(conn: sqlite3.Connection, obj: tinh_trang_model.TinhTrang) -> int:
    sql = """
        INSERT INTO tinh_trang (ma_tinh_trang, ten_tinh_trang, mo_ta, mau_hien_thi,
                                thu_tu_hien_thi, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cur = conn.execute(sql, (obj.ma_tinh_trang, obj.ten_tinh_trang, obj.mo_ta,
                             obj.mau_hien_thi, obj.thu_tu_hien_thi, obj.is_active))
    conn.commit()
    return cur.lastrowid


def sua(conn: sqlite3.Connection, obj: tinh_trang_model.TinhTrang) -> bool:
    sql = """
        UPDATE tinh_trang
        SET ma_tinh_trang=?, ten_tinh_trang=?, mo_ta=?, mau_hien_thi=?,
            thu_tu_hien_thi=?, is_active=?
        WHERE id=?
    """
    cur = conn.execute(sql, (obj.ma_tinh_trang, obj.ten_tinh_trang, obj.mo_ta,
                             obj.mau_hien_thi, obj.thu_tu_hien_thi, obj.is_active, obj.id))
    conn.commit()
    return cur.rowcount > 0


def xoa_mem(conn: sqlite3.Connection, id: int) -> bool:
    cur = conn.execute("UPDATE tinh_trang SET is_active = 0 WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


def khoi_phuc(conn: sqlite3.Connection, id: int) -> bool:
    cur = conn.execute("UPDATE tinh_trang SET is_active = 1 WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


def _row_to_object(row: sqlite3.Row) -> tinh_trang_model.TinhTrang:
    return tinh_trang_model.TinhTrang(
        id=row["id"],
        ma_tinh_trang=row["ma_tinh_trang"],
        ten_tinh_trang=row["ten_tinh_trang"],
        mo_ta=row["mo_ta"],
        mau_hien_thi=row["mau_hien_thi"],
        thu_tu_hien_thi=row["thu_tu_hien_thi"],
        is_active=row["is_active"],
    )
