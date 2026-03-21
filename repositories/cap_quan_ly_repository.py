"""
Repository: CapQuanLy — Cấp quản lý đường
Chỉ SQL thuần, dùng sqlite3.Row. KHÔNG hardcode index cột.
"""

import sqlite3
from typing import Optional, List
import models.cap_quan_ly as cap_quan_ly_model


def lay_tat_ca(conn: sqlite3.Connection) -> List[cap_quan_ly_model.CapQuanLy]:
    sql = "SELECT * FROM cap_quan_ly ORDER BY thu_tu_hien_thi"
    rows = conn.execute(sql).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_id(conn: sqlite3.Connection, id: int) -> Optional[cap_quan_ly_model.CapQuanLy]:
    sql = "SELECT * FROM cap_quan_ly WHERE id = ?"
    row = conn.execute(sql, (id,)).fetchone()
    return _row_to_object(row) if row else None


def lay_theo_ma(conn: sqlite3.Connection, ma_cap: str) -> Optional[cap_quan_ly_model.CapQuanLy]:
    sql = "SELECT * FROM cap_quan_ly WHERE ma_cap = ?"
    row = conn.execute(sql, (ma_cap,)).fetchone()
    return _row_to_object(row) if row else None


def lay_dang_hoat_dong(conn: sqlite3.Connection) -> List[cap_quan_ly_model.CapQuanLy]:
    sql = "SELECT * FROM cap_quan_ly WHERE is_active = 1 ORDER BY thu_tu_hien_thi"
    rows = conn.execute(sql).fetchall()
    return [_row_to_object(r) for r in rows]


def them(conn: sqlite3.Connection, obj: cap_quan_ly_model.CapQuanLy) -> int:
    sql = """
        INSERT INTO cap_quan_ly (ma_cap, ten_cap, mo_ta, thu_tu_hien_thi, is_active)
        VALUES (?, ?, ?, ?, ?)
    """
    cur = conn.execute(sql, (obj.ma_cap, obj.ten_cap, obj.mo_ta,
                             obj.thu_tu_hien_thi, obj.is_active))
    conn.commit()
    return cur.lastrowid


def sua(conn: sqlite3.Connection, obj: cap_quan_ly_model.CapQuanLy) -> bool:
    sql = """
        UPDATE cap_quan_ly
        SET ma_cap=?, ten_cap=?, mo_ta=?, thu_tu_hien_thi=?, is_active=?
        WHERE id=?
    """
    cur = conn.execute(sql, (obj.ma_cap, obj.ten_cap, obj.mo_ta,
                             obj.thu_tu_hien_thi, obj.is_active, obj.id))
    conn.commit()
    return cur.rowcount > 0


def xoa_mem(conn: sqlite3.Connection, id: int) -> bool:
    """Vô hiệu hóa (is_active = 0), không xóa khỏi DB."""
    cur = conn.execute("UPDATE cap_quan_ly SET is_active = 0 WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


def khoi_phuc(conn: sqlite3.Connection, id: int) -> bool:
    """Kích hoạt lại (is_active = 1)."""
    cur = conn.execute("UPDATE cap_quan_ly SET is_active = 1 WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


def _row_to_object(row: sqlite3.Row) -> cap_quan_ly_model.CapQuanLy:
    return cap_quan_ly_model.CapQuanLy(
        id=row["id"],
        ma_cap=row["ma_cap"],
        ten_cap=row["ten_cap"],
        mo_ta=row["mo_ta"],
        thu_tu_hien_thi=row["thu_tu_hien_thi"],
        is_active=row["is_active"],
    )
