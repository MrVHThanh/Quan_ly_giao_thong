"""
Repository: DoanTuyen — Đoạn tuyến
Chỉ SQL thuần, dùng sqlite3.Row. KHÔNG hardcode index cột.

Thay đổi so với phiên bản cũ:
- Dùng row["ten_cot"] thay vì row[0], row[7], row[8]...
- Thêm 5 cột mới: ket_cau_mat_id, nam_lam_moi, ngay_cap_nhat_tinh_trang,
  updated_at, updated_by_id
- Thêm hàm lay_co_loc(): lọc kết hợp nhiều tiêu chí (AND), tránh lỗi 422
"""

import sqlite3
from typing import Optional, List
import models.doan_tuyen as doan_tuyen_model


def lay_theo_tuyen_id(conn: sqlite3.Connection, tuyen_id: int) -> List[doan_tuyen_model.DoanTuyen]:
    sql = "SELECT * FROM doan_tuyen WHERE tuyen_id = ? ORDER BY ly_trinh_dau"
    rows = conn.execute(sql, (tuyen_id,)).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_id(conn: sqlite3.Connection, id: int) -> Optional[doan_tuyen_model.DoanTuyen]:
    row = conn.execute("SELECT * FROM doan_tuyen WHERE id = ?", (id,)).fetchone()
    return _row_to_object(row) if row else None


def lay_theo_ma(conn: sqlite3.Connection, ma_doan: str) -> Optional[doan_tuyen_model.DoanTuyen]:
    row = conn.execute("SELECT * FROM doan_tuyen WHERE ma_doan = ?", (ma_doan,)).fetchone()
    return _row_to_object(row) if row else None


def lay_tat_ca(conn: sqlite3.Connection) -> List[doan_tuyen_model.DoanTuyen]:
    sql = "SELECT * FROM doan_tuyen ORDER BY tuyen_id, ly_trinh_dau"
    rows = conn.execute(sql).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_cap_duong(conn: sqlite3.Connection, cap_duong_id: int) -> List[doan_tuyen_model.DoanTuyen]:
    sql = "SELECT * FROM doan_tuyen WHERE cap_duong_id = ? ORDER BY tuyen_id, ly_trinh_dau"
    rows = conn.execute(sql, (cap_duong_id,)).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_tinh_trang(conn: sqlite3.Connection, tinh_trang_id: int) -> List[doan_tuyen_model.DoanTuyen]:
    sql = "SELECT * FROM doan_tuyen WHERE tinh_trang_id = ? ORDER BY tuyen_id, ly_trinh_dau"
    rows = conn.execute(sql, (tinh_trang_id,)).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_theo_ket_cau_mat(conn: sqlite3.Connection, ket_cau_mat_id: int) -> List[doan_tuyen_model.DoanTuyen]:
    sql = "SELECT * FROM doan_tuyen WHERE ket_cau_mat_id = ? ORDER BY tuyen_id, ly_trinh_dau"
    rows = conn.execute(sql, (ket_cau_mat_id,)).fetchall()
    return [_row_to_object(r) for r in rows]


def lay_co_loc(
    conn: sqlite3.Connection,
    tuyen_id:      Optional[int] = None,
    tinh_trang_id: Optional[int] = None,
    cap_duong_id:  Optional[int] = None,
) -> List[doan_tuyen_model.DoanTuyen]:
    """
    Lọc kết hợp: tất cả tiêu chí nào có giá trị đều được áp dụng (AND).
    Nếu không có tiêu chí nào → trả về toàn bộ danh sách.
    Được gọi từ router thay cho các hàm if/elif riêng lẻ.
    """
    conditions: List[str] = []
    params: List[int] = []

    if tuyen_id is not None:
        conditions.append("tuyen_id = ?")
        params.append(tuyen_id)
    if tinh_trang_id is not None:
        conditions.append("tinh_trang_id = ?")
        params.append(tinh_trang_id)
    if cap_duong_id is not None:
        conditions.append("cap_duong_id = ?")
        params.append(cap_duong_id)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    sql   = f"SELECT * FROM doan_tuyen {where} ORDER BY tuyen_id, ly_trinh_dau"

    rows = conn.execute(sql, params).fetchall()
    return [_row_to_object(r) for r in rows]


def them(conn: sqlite3.Connection, obj: doan_tuyen_model.DoanTuyen) -> int:
    sql = """
        INSERT INTO doan_tuyen (
            ma_doan, tuyen_id, cap_duong_id, tinh_trang_id, ket_cau_mat_id,
            ly_trinh_dau, ly_trinh_cuoi, chieu_dai_thuc_te,
            chieu_rong_mat_min, chieu_rong_mat_max,
            chieu_rong_nen_min, chieu_rong_nen_max,
            don_vi_bao_duong_id, nam_lam_moi, ngay_cap_nhat_tinh_trang,
            ghi_chu, updated_by_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur = conn.execute(sql, (
        obj.ma_doan, obj.tuyen_id, obj.cap_duong_id, obj.tinh_trang_id, obj.ket_cau_mat_id,
        obj.ly_trinh_dau, obj.ly_trinh_cuoi, obj.chieu_dai_thuc_te,
        obj.chieu_rong_mat_min, obj.chieu_rong_mat_max,
        obj.chieu_rong_nen_min, obj.chieu_rong_nen_max,
        obj.don_vi_bao_duong_id, obj.nam_lam_moi, obj.ngay_cap_nhat_tinh_trang,
        obj.ghi_chu, obj.updated_by_id,
    ))
    conn.commit()
    return cur.lastrowid


def sua(conn: sqlite3.Connection, obj: doan_tuyen_model.DoanTuyen) -> bool:
    sql = """
        UPDATE doan_tuyen
        SET ma_doan=?, tuyen_id=?, cap_duong_id=?, tinh_trang_id=?, ket_cau_mat_id=?,
            ly_trinh_dau=?, ly_trinh_cuoi=?, chieu_dai_thuc_te=?,
            chieu_rong_mat_min=?, chieu_rong_mat_max=?,
            chieu_rong_nen_min=?, chieu_rong_nen_max=?,
            don_vi_bao_duong_id=?, nam_lam_moi=?, ngay_cap_nhat_tinh_trang=?,
            ghi_chu=?, updated_by_id=?
        WHERE id=?
    """
    cur = conn.execute(sql, (
        obj.ma_doan, obj.tuyen_id, obj.cap_duong_id, obj.tinh_trang_id, obj.ket_cau_mat_id,
        obj.ly_trinh_dau, obj.ly_trinh_cuoi, obj.chieu_dai_thuc_te,
        obj.chieu_rong_mat_min, obj.chieu_rong_mat_max,
        obj.chieu_rong_nen_min, obj.chieu_rong_nen_max,
        obj.don_vi_bao_duong_id, obj.nam_lam_moi, obj.ngay_cap_nhat_tinh_trang,
        obj.ghi_chu, obj.updated_by_id, obj.id,
    ))
    conn.commit()
    return cur.rowcount > 0


def cap_nhat_tinh_trang(
    conn: sqlite3.Connection,
    id: int,
    tinh_trang_id: int,
    ngay_cap_nhat: str,
    updated_by_id: int,
) -> bool:
    """Cập nhật nhanh tình trạng + ngày khảo sát cho một đoạn."""
    sql = """
        UPDATE doan_tuyen
        SET tinh_trang_id=?, ngay_cap_nhat_tinh_trang=?, updated_by_id=?
        WHERE id=?
    """
    cur = conn.execute(sql, (tinh_trang_id, ngay_cap_nhat, updated_by_id, id))
    conn.commit()
    return cur.rowcount > 0


def xoa(conn: sqlite3.Connection, id: int) -> bool:
    cur = conn.execute("DELETE FROM doan_tuyen WHERE id = ?", (id,))
    conn.commit()
    return cur.rowcount > 0


def _row_to_object(row: sqlite3.Row) -> doan_tuyen_model.DoanTuyen:
    return doan_tuyen_model.DoanTuyen(
        id=row["id"],
        ma_doan=row["ma_doan"],
        tuyen_id=row["tuyen_id"],
        cap_duong_id=row["cap_duong_id"],
        tinh_trang_id=row["tinh_trang_id"],
        ket_cau_mat_id=row["ket_cau_mat_id"],
        ly_trinh_dau=row["ly_trinh_dau"],
        ly_trinh_cuoi=row["ly_trinh_cuoi"],
        chieu_dai_thuc_te=row["chieu_dai_thuc_te"],
        chieu_rong_mat_min=row["chieu_rong_mat_min"],
        chieu_rong_mat_max=row["chieu_rong_mat_max"],
        chieu_rong_nen_min=row["chieu_rong_nen_min"],
        chieu_rong_nen_max=row["chieu_rong_nen_max"],
        don_vi_bao_duong_id=row["don_vi_bao_duong_id"],
        nam_lam_moi=row["nam_lam_moi"],
        ngay_cap_nhat_tinh_trang=row["ngay_cap_nhat_tinh_trang"],
        ghi_chu=row["ghi_chu"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        updated_by_id=row["updated_by_id"],
    )