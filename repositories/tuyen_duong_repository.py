"""
Repository: TuyenDuong — Tuyến đường
Chỉ SQL thuần, dùng sqlite3.Row. KHÔNG hardcode index cột.

Lưu ý quan trọng:
- KHÔNG có hàm cap_nhat_chieu_dai() — SQLite trigger tự động xử lý
- tuyen_duong KHÔNG có cột chieu_dai, chỉ có chieu_dai_thuc_te và chieu_dai_quan_ly
"""

import sqlite3
from typing import Optional, List
import models.tuyen_duong as tuyen_duong_model


def lay_tat_ca(conn: sqlite3.Connection) -> List[tuyen_duong_model.TuyenDuong]:
    sql = "SELECT * FROM tuyen_duong ORDER BY cap_quan_ly_id, ma_tuyen"
    rows = conn.execute(sql).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_id(conn: sqlite3.Connection, id: int) -> Optional[tuyen_duong_model.TuyenDuong]:
    row = conn.execute("SELECT * FROM tuyen_duong WHERE id = ?", (id,)).fetchone()
    return _row_to_object(row) if row else None


def lay_theo_ma(conn: sqlite3.Connection, ma_tuyen: str) -> Optional[tuyen_duong_model.TuyenDuong]:
    row = conn.execute("SELECT * FROM tuyen_duong WHERE ma_tuyen = ?", (ma_tuyen,)).fetchone()
    return _row_to_object(row) if row else None


def lay_theo_cap_quan_ly(conn: sqlite3.Connection, cap_quan_ly_id: int) -> List[tuyen_duong_model.TuyenDuong]:
    sql = "SELECT * FROM tuyen_duong WHERE cap_quan_ly_id = ? ORDER BY ma_tuyen"
    rows = conn.execute(sql, (cap_quan_ly_id,)).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_don_vi_quan_ly(conn: sqlite3.Connection, don_vi_id: int) -> List[tuyen_duong_model.TuyenDuong]:
    sql = "SELECT * FROM tuyen_duong WHERE don_vi_quan_ly_id = ? ORDER BY ma_tuyen"
    rows = conn.execute(sql, (don_vi_id,)).fetchall()
    return [_row_to_object(r) for r in rows]


def them(conn: sqlite3.Connection, obj: tuyen_duong_model.TuyenDuong) -> int:
    sql = """
        INSERT INTO tuyen_duong (
            ma_tuyen, ten_tuyen, cap_quan_ly_id, don_vi_quan_ly_id,
            diem_dau, diem_cuoi, lat_dau, lng_dau, lat_cuoi, lng_cuoi,
            nam_xay_dung, nam_hoan_thanh, ghi_chu
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur = conn.execute(sql, (
        obj.ma_tuyen, obj.ten_tuyen, obj.cap_quan_ly_id, obj.don_vi_quan_ly_id,
        obj.diem_dau, obj.diem_cuoi, obj.lat_dau, obj.lng_dau, obj.lat_cuoi, obj.lng_cuoi,
        obj.nam_xay_dung, obj.nam_hoan_thanh, obj.ghi_chu,
    ))
    conn.commit()
    return cur.lastrowid


def sua(conn: sqlite3.Connection, obj: tuyen_duong_model.TuyenDuong) -> bool:
    sql = """
        UPDATE tuyen_duong
        SET ma_tuyen=?, ten_tuyen=?, cap_quan_ly_id=?, don_vi_quan_ly_id=?,
            diem_dau=?, diem_cuoi=?, lat_dau=?, lng_dau=?, lat_cuoi=?, lng_cuoi=?,
            nam_xay_dung=?, nam_hoan_thanh=?, ghi_chu=?
        WHERE id=?
    """
    cur = conn.execute(sql, (
        obj.ma_tuyen, obj.ten_tuyen, obj.cap_quan_ly_id, obj.don_vi_quan_ly_id,
        obj.diem_dau, obj.diem_cuoi, obj.lat_dau, obj.lng_dau, obj.lat_cuoi, obj.lng_cuoi,
        obj.nam_xay_dung, obj.nam_hoan_thanh, obj.ghi_chu, obj.id,
    ))
    conn.commit()
    return cur.rowcount > 0


def xoa(conn: sqlite3.Connection, id: int) -> bool:
    """Xóa thật — chỉ dùng khi không còn đoạn tuyến nào thuộc tuyến này."""
    cur = conn.execute("DELETE FROM tuyen_duong WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


def _row_to_object(row: sqlite3.Row) -> tuyen_duong_model.TuyenDuong:
    return tuyen_duong_model.TuyenDuong(
        id=row["id"],
        ma_tuyen=row["ma_tuyen"],
        ten_tuyen=row["ten_tuyen"],
        cap_quan_ly_id=row["cap_quan_ly_id"],
        don_vi_quan_ly_id=row["don_vi_quan_ly_id"],
        diem_dau=row["diem_dau"],
        diem_cuoi=row["diem_cuoi"],
        lat_dau=row["lat_dau"],
        lng_dau=row["lng_dau"],
        lat_cuoi=row["lat_cuoi"],
        lng_cuoi=row["lng_cuoi"],
        chieu_dai_thuc_te=row["chieu_dai_thuc_te"],
        chieu_dai_quan_ly=row["chieu_dai_quan_ly"],
        nam_xay_dung=row["nam_xay_dung"],
        nam_hoan_thanh=row["nam_hoan_thanh"],
        ghi_chu=row["ghi_chu"],
        created_at=row["created_at"],
    )
