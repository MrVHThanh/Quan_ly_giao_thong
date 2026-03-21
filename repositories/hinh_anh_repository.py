"""
Repository: HinhAnhDoanTuyen — Hình ảnh hiện trạng đoạn tuyến  [MỚI]
Chỉ SQL thuần, dùng sqlite3.Row. KHÔNG hardcode index cột.
"""

import sqlite3
from typing import Optional, List
import models.hinh_anh_doan_tuyen as hinh_anh_model


def lay_theo_doan_id(conn: sqlite3.Connection, doan_id: int) -> List[hinh_anh_model.HinhAnhDoanTuyen]:
    sql = "SELECT * FROM hinh_anh_doan_tuyen WHERE doan_id = ? ORDER BY ngay_chup DESC"
    rows = conn.execute(sql, (doan_id,)).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_id(conn: sqlite3.Connection, id: int) -> Optional[hinh_anh_model.HinhAnhDoanTuyen]:
    row = conn.execute("SELECT * FROM hinh_anh_doan_tuyen WHERE id = ?", (id,)).fetchone()
    return _row_to_object(row) if row else None


def lay_co_toa_do_gps(conn: sqlite3.Connection, doan_id: int) -> List[hinh_anh_model.HinhAnhDoanTuyen]:
    """Lấy ảnh có tọa độ GPS để dùng cho Giai đoạn 2 (tính ly_trinh_anh)."""
    sql = """
        SELECT * FROM hinh_anh_doan_tuyen
        WHERE doan_id = ? AND lat IS NOT NULL AND lng IS NOT NULL
        ORDER BY ngay_chup DESC
    """
    rows = conn.execute(sql, (doan_id,)).fetchall()
    return [_row_to_object(r) for r in rows]


def them(conn: sqlite3.Connection, obj: hinh_anh_model.HinhAnhDoanTuyen) -> int:
    sql = """
        INSERT INTO hinh_anh_doan_tuyen (
            doan_id, duong_dan_file, mo_ta, ngay_chup,
            nguoi_chup, lat, lng, ly_trinh_anh
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur = conn.execute(sql, (
        obj.doan_id, obj.duong_dan_file, obj.mo_ta, obj.ngay_chup,
        obj.nguoi_chup, obj.lat, obj.lng, obj.ly_trinh_anh,
    ))
    conn.commit()
    return cur.lastrowid


def cap_nhat_ly_trinh(conn: sqlite3.Connection, id: int, ly_trinh_anh: float) -> bool:
    """Cập nhật ly_trinh_anh sau khi tính từ tọa độ GPS (Giai đoạn 2)."""
    cur = conn.execute(
        "UPDATE hinh_anh_doan_tuyen SET ly_trinh_anh = ? WHERE id = ?", (ly_trinh_anh, id)
    )
    conn.commit()
    return cur.rowcount > 0


def xoa(conn: sqlite3.Connection, id: int) -> bool:
    cur = conn.execute("DELETE FROM hinh_anh_doan_tuyen WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


def _row_to_object(row: sqlite3.Row) -> hinh_anh_model.HinhAnhDoanTuyen:
    return hinh_anh_model.HinhAnhDoanTuyen(
        id=row["id"],
        doan_id=row["doan_id"],
        duong_dan_file=row["duong_dan_file"],
        mo_ta=row["mo_ta"],
        ngay_chup=row["ngay_chup"],
        nguoi_chup=row["nguoi_chup"],
        lat=row["lat"],
        lng=row["lng"],
        ly_trinh_anh=row["ly_trinh_anh"],
        created_at=row["created_at"],
    )
