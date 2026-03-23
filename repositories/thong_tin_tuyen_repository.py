"""
Repository: ThongTinTuyen — Mô tả / giới thiệu tuyến đường
Chỉ SQL thuần, dùng sqlite3.Row. KHÔNG hardcode index cột.

Cấu trúc bảng:
    id        INTEGER PRIMARY KEY
    tuyen_id  INTEGER NOT NULL UNIQUE FK → tuyen_duong
    mo_ta     TEXT
"""

import sqlite3
from typing import Optional
import models.thong_tin_tuyen as thong_tin_tuyen_model


def lay_theo_tuyen_id(
    conn: sqlite3.Connection, tuyen_id: int
) -> Optional[thong_tin_tuyen_model.ThongTinTuyen]:
    """Trả về bản ghi ThongTinTuyen của tuyến, hoặc None nếu chưa có."""
    row = conn.execute(
        "SELECT * FROM thong_tin_tuyen WHERE tuyen_id = ?", (tuyen_id,)
    ).fetchone()
    return _row_to_object(row) if row else None


def lay_theo_id(
    conn: sqlite3.Connection, id: int
) -> Optional[thong_tin_tuyen_model.ThongTinTuyen]:
    row = conn.execute(
        "SELECT * FROM thong_tin_tuyen WHERE id = ?", (id,)
    ).fetchone()
    return _row_to_object(row) if row else None


def them(conn: sqlite3.Connection, obj: thong_tin_tuyen_model.ThongTinTuyen) -> int:
    """Thêm mới bản ghi mô tả. Mỗi tuyến chỉ có 1 bản ghi (UNIQUE tuyen_id)."""
    sql = "INSERT INTO thong_tin_tuyen (tuyen_id, mo_ta) VALUES (?, ?)"
    cur = conn.execute(sql, (obj.tuyen_id, obj.mo_ta))
    conn.commit()
    return cur.lastrowid


def cap_nhat(conn: sqlite3.Connection, obj: thong_tin_tuyen_model.ThongTinTuyen) -> bool:
    """Cập nhật toàn bộ nội dung mô tả theo id."""
    sql = """
        UPDATE thong_tin_tuyen
        SET mo_ta              = ?,
            ly_do_xay_dung     = ?,
            dac_diem_dia_ly    = ?,
            lich_su_hinh_thanh = ?,
            y_nghia_kinh_te    = ?,
            ghi_chu            = ?,
            updated_at         = datetime('now', 'localtime')
        WHERE id = ?
    """
    cur = conn.execute(sql, (
        obj.mo_ta, obj.ly_do_xay_dung, obj.dac_diem_dia_ly,
        obj.lich_su_hinh_thanh, obj.y_nghia_kinh_te, obj.ghi_chu,
        obj.id,
    ))
    conn.commit()
    return cur.rowcount > 0


def them_hoac_cap_nhat(
    conn: sqlite3.Connection, tuyen_id: int, mo_ta: str
) -> thong_tin_tuyen_model.ThongTinTuyen:
    """
    Upsert: nếu đã có bản ghi cho tuyen_id → cập nhật mo_ta,
    chưa có → thêm mới. Trả về object sau khi lưu.
    """
    hien_co = lay_theo_tuyen_id(conn, tuyen_id)
    if hien_co:
        hien_co.mo_ta = mo_ta
        cap_nhat(conn, hien_co)
        return hien_co
    else:
        obj = thong_tin_tuyen_model.ThongTinTuyen(tuyen_id=tuyen_id, mo_ta=mo_ta)
        obj.id = them(conn, obj)
        return obj


def xoa(conn: sqlite3.Connection, tuyen_id: int) -> bool:
    cur = conn.execute(
        "DELETE FROM thong_tin_tuyen WHERE tuyen_id = ?", (tuyen_id,)
    )
    conn.commit()
    return cur.rowcount > 0


def _row_to_object(row: sqlite3.Row) -> thong_tin_tuyen_model.ThongTinTuyen:
    return thong_tin_tuyen_model.ThongTinTuyen(
        id=row["id"],
        tuyen_id=row["tuyen_id"],
        mo_ta=row["mo_ta"],
        ly_do_xay_dung=row["ly_do_xay_dung"],
        dac_diem_dia_ly=row["dac_diem_dia_ly"],
        lich_su_hinh_thanh=row["lich_su_hinh_thanh"],
        y_nghia_kinh_te=row["y_nghia_kinh_te"],
        ghi_chu=row["ghi_chu"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )