"""
Repository: TuyenDuongGeo — Dữ liệu tọa độ GeoJSON theo tuyến  [MỚI - Giai đoạn 1]
Chỉ SQL thuần, dùng sqlite3.Row. KHÔNG hardcode index cột.

Mỗi tuyen_duong có tối đa 1 bản ghi (UNIQUE tuyen_id).
"""

import sqlite3
from typing import Optional, List
import models.tuyen_duong_geo as tuyen_duong_geo_model


def lay_theo_tuyen_id(
    conn: sqlite3.Connection, tuyen_id: int
) -> Optional[tuyen_duong_geo_model.TuyenDuongGeo]:
    row = conn.execute(
        "SELECT * FROM tuyen_duong_geo WHERE tuyen_id = ?", (tuyen_id,)
    ).fetchone()
    return _row_to_object(row) if row else None


def lay_theo_id(
    conn: sqlite3.Connection, id: int
) -> Optional[tuyen_duong_geo_model.TuyenDuongGeo]:
    row = conn.execute("SELECT * FROM tuyen_duong_geo WHERE id = ?", (id,)).fetchone()
    return _row_to_object(row) if row else None


def lay_tat_ca(conn: sqlite3.Connection) -> List[tuyen_duong_geo_model.TuyenDuongGeo]:
    rows = conn.execute("SELECT * FROM tuyen_duong_geo ORDER BY tuyen_id").fetchall()
    return [_row_to_object(r) for r in rows]


def lay_danh_sach_co_geo(conn: sqlite3.Connection) -> List[int]:
    """Trả về list tuyen_id đã có dữ liệu GeoJSON."""
    rows = conn.execute("SELECT tuyen_id FROM tuyen_duong_geo").fetchall()
    return [r["tuyen_id"] for r in rows]


def them_hoac_cap_nhat(conn: sqlite3.Connection, obj: tuyen_duong_geo_model.TuyenDuongGeo) -> int:
    """INSERT OR REPLACE — mỗi tuyến chỉ có 1 bản ghi."""
    sql = """
        INSERT INTO tuyen_duong_geo (tuyen_id, coordinates, so_diem, chieu_dai_gps,
                                     nguon, updated_at)
        VALUES (?, ?, ?, ?, ?, datetime('now','localtime'))
        ON CONFLICT(tuyen_id) DO UPDATE SET
            coordinates=excluded.coordinates,
            so_diem=excluded.so_diem,
            chieu_dai_gps=excluded.chieu_dai_gps,
            nguon=excluded.nguon,
            updated_at=datetime('now','localtime')
    """
    cur = conn.execute(sql, (
        obj.tuyen_id, obj.coordinates, obj.so_diem, obj.chieu_dai_gps, obj.nguon,
    ))
    conn.commit()
    return cur.lastrowid


def xoa(conn: sqlite3.Connection, tuyen_id: int) -> bool:
    cur = conn.execute("DELETE FROM tuyen_duong_geo WHERE tuyen_id = ?", (tuyen_id,))
    conn.commit()
    return cur.rowcount > 0


def _row_to_object(row: sqlite3.Row) -> tuyen_duong_geo_model.TuyenDuongGeo:
    return tuyen_duong_geo_model.TuyenDuongGeo(
        id=row["id"],
        tuyen_id=row["tuyen_id"],
        coordinates=row["coordinates"],
        so_diem=row["so_diem"],
        chieu_dai_gps=row["chieu_dai_gps"],
        nguon=row["nguon"],
        updated_at=row["updated_at"],
    )
