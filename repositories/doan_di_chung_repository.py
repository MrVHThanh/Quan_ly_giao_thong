"""
Repository: DoanDiChung — Đoạn đi chung giữa các tuyến
Chỉ SQL thuần, dùng sqlite3.Row. KHÔNG hardcode index cột.

Cấu trúc mới với 2 cặp lý trình (theo tuyến đi nhờ + theo tuyến chủ).
"""

import sqlite3
from typing import Optional, List
import models.doan_di_chung as doan_di_chung_model


def lay_tat_ca(conn: sqlite3.Connection) -> List[doan_di_chung_model.DoanDiChung]:
    sql = "SELECT * FROM doan_di_chung ORDER BY tuyen_di_chung_id, ly_trinh_dau_di_chung"
    rows = conn.execute(sql).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_id(conn: sqlite3.Connection, id: int) -> Optional[doan_di_chung_model.DoanDiChung]:
    row = conn.execute("SELECT * FROM doan_di_chung WHERE id = ?", (id,)).fetchone()
    return _row_to_object(row) if row else None


def lay_theo_tuyen_di_chung(
    conn: sqlite3.Connection, tuyen_di_chung_id: int
) -> List[doan_di_chung_model.DoanDiChung]:
    """Lấy tất cả đoạn mà tuyến này đi nhờ trên tuyến khác."""
    sql = """
        SELECT * FROM doan_di_chung
        WHERE tuyen_di_chung_id = ?
        ORDER BY ly_trinh_dau_di_chung
    """
    rows = conn.execute(sql, (tuyen_di_chung_id,)).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_tuyen_chinh(
    conn: sqlite3.Connection, tuyen_chinh_id: int
) -> List[doan_di_chung_model.DoanDiChung]:
    """Lấy tất cả đoạn mà tuyến khác đi nhờ trên tuyến này."""
    sql = """
        SELECT * FROM doan_di_chung
        WHERE tuyen_chinh_id = ?
        ORDER BY ly_trinh_dau_tuyen_chinh
    """
    rows = conn.execute(sql, (tuyen_chinh_id,)).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_doan_id(
    conn: sqlite3.Connection, doan_id: int
) -> List[doan_di_chung_model.DoanDiChung]:
    """Lấy tất cả đoạn đi chung tham chiếu đến một đoạn vật lý."""
    sql = "SELECT * FROM doan_di_chung WHERE doan_id = ?"
    rows = conn.execute(sql, (doan_id,)).fetchall()
    return [_row_to_object(r) for r in rows]


def them(conn: sqlite3.Connection, obj: doan_di_chung_model.DoanDiChung) -> int:
    sql = """
        INSERT INTO doan_di_chung (
            ma_doan_di_chung, tuyen_di_chung_id, tuyen_chinh_id, doan_id,
            ly_trinh_dau_di_chung, ly_trinh_cuoi_di_chung,
            ly_trinh_dau_tuyen_chinh, ly_trinh_cuoi_tuyen_chinh,
            ghi_chu
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur = conn.execute(sql, (
        obj.ma_doan_di_chung, obj.tuyen_di_chung_id, obj.tuyen_chinh_id, obj.doan_id,
        obj.ly_trinh_dau_di_chung, obj.ly_trinh_cuoi_di_chung,
        obj.ly_trinh_dau_tuyen_chinh, obj.ly_trinh_cuoi_tuyen_chinh,
        obj.ghi_chu,
    ))
    conn.commit()
    return cur.lastrowid


def sua(conn: sqlite3.Connection, obj: doan_di_chung_model.DoanDiChung) -> bool:
    sql = """
        UPDATE doan_di_chung
        SET ma_doan_di_chung=?, tuyen_di_chung_id=?, tuyen_chinh_id=?, doan_id=?,
            ly_trinh_dau_di_chung=?, ly_trinh_cuoi_di_chung=?,
            ly_trinh_dau_tuyen_chinh=?, ly_trinh_cuoi_tuyen_chinh=?,
            ghi_chu=?
        WHERE id=?
    """
    cur = conn.execute(sql, (
        obj.ma_doan_di_chung, obj.tuyen_di_chung_id, obj.tuyen_chinh_id, obj.doan_id,
        obj.ly_trinh_dau_di_chung, obj.ly_trinh_cuoi_di_chung,
        obj.ly_trinh_dau_tuyen_chinh, obj.ly_trinh_cuoi_tuyen_chinh,
        obj.ghi_chu, obj.id,
    ))
    conn.commit()
    return cur.rowcount > 0


def xoa(conn: sqlite3.Connection, id: int) -> bool:
    cur = conn.execute("DELETE FROM doan_di_chung WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


def _row_to_object(row: sqlite3.Row) -> doan_di_chung_model.DoanDiChung:
    return doan_di_chung_model.DoanDiChung(
        id=row["id"],
        ma_doan_di_chung=row["ma_doan_di_chung"],
        tuyen_di_chung_id=row["tuyen_di_chung_id"],
        tuyen_chinh_id=row["tuyen_chinh_id"],
        doan_id=row["doan_id"],
        ly_trinh_dau_di_chung=row["ly_trinh_dau_di_chung"],
        ly_trinh_cuoi_di_chung=row["ly_trinh_cuoi_di_chung"],
        ly_trinh_dau_tuyen_chinh=row["ly_trinh_dau_tuyen_chinh"],
        ly_trinh_cuoi_tuyen_chinh=row["ly_trinh_cuoi_tuyen_chinh"],
        ghi_chu=row["ghi_chu"],
        created_at=row["created_at"],
    )
