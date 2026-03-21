"""
Repository: KetCauMatDuong — Kết cấu mặt đường  [MỚI]
Chỉ SQL thuần, dùng sqlite3.Row. KHÔNG hardcode index cột.
"""

import sqlite3
from typing import Optional, List
import models.ket_cau_mat_duong as ket_cau_mat_model


def lay_tat_ca(conn: sqlite3.Connection) -> List[ket_cau_mat_model.KetCauMatDuong]:
    sql = "SELECT * FROM ket_cau_mat_duong ORDER BY thu_tu_hien_thi"
    rows = conn.execute(sql).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_id(conn: sqlite3.Connection, id: int) -> Optional[ket_cau_mat_model.KetCauMatDuong]:
    sql = "SELECT * FROM ket_cau_mat_duong WHERE id = ?"
    row = conn.execute(sql, (id,)).fetchone()
    return _row_to_object(row) if row else None


def lay_theo_ma(conn: sqlite3.Connection, ma_ket_cau: str) -> Optional[ket_cau_mat_model.KetCauMatDuong]:
    sql = "SELECT * FROM ket_cau_mat_duong WHERE ma_ket_cau = ?"
    row = conn.execute(sql, (ma_ket_cau,)).fetchone()
    return _row_to_object(row) if row else None


def lay_dang_hoat_dong(conn: sqlite3.Connection) -> List[ket_cau_mat_model.KetCauMatDuong]:
    sql = "SELECT * FROM ket_cau_mat_duong WHERE is_active = 1 ORDER BY thu_tu_hien_thi"
    rows = conn.execute(sql).fetchall()
    return [_row_to_object(r) for r in rows]


def them(conn: sqlite3.Connection, obj: ket_cau_mat_model.KetCauMatDuong) -> int:
    sql = """
        INSERT INTO ket_cau_mat_duong (ma_ket_cau, ten_ket_cau, mo_ta, thu_tu_hien_thi, is_active)
        VALUES (?, ?, ?, ?, ?)
    """
    cur = conn.execute(sql, (obj.ma_ket_cau, obj.ten_ket_cau, obj.mo_ta,
                             obj.thu_tu_hien_thi, obj.is_active))
    conn.commit()
    return cur.lastrowid


def sua(conn: sqlite3.Connection, obj: ket_cau_mat_model.KetCauMatDuong) -> bool:
    sql = """
        UPDATE ket_cau_mat_duong
        SET ma_ket_cau=?, ten_ket_cau=?, mo_ta=?, thu_tu_hien_thi=?, is_active=?
        WHERE id=?
    """
    cur = conn.execute(sql, (obj.ma_ket_cau, obj.ten_ket_cau, obj.mo_ta,
                             obj.thu_tu_hien_thi, obj.is_active, obj.id))
    conn.commit()
    return cur.rowcount > 0


def xoa_mem(conn: sqlite3.Connection, id: int) -> bool:
    cur = conn.execute("UPDATE ket_cau_mat_duong SET is_active = 0 WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


def khoi_phuc(conn: sqlite3.Connection, id: int) -> bool:
    cur = conn.execute("UPDATE ket_cau_mat_duong SET is_active = 1 WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


def _row_to_object(row: sqlite3.Row) -> ket_cau_mat_model.KetCauMatDuong:
    return ket_cau_mat_model.KetCauMatDuong(
        id=row["id"],
        ma_ket_cau=row["ma_ket_cau"],
        ten_ket_cau=row["ten_ket_cau"],
        mo_ta=row["mo_ta"],
        thu_tu_hien_thi=row["thu_tu_hien_thi"],
        is_active=row["is_active"],
    )
