"""
Repository: ThongKe — Truy vấn thống kê tổng hợp
Chỉ SQL thuần, dùng sqlite3.Row. KHÔNG hardcode index cột.

Tất cả hàm trả về dict hoặc list[dict] thô — Service sẽ chuyển sang Model ThongKe.
Cập nhật: bổ sung thống kê theo ket_cau_mat_duong.
"""

import sqlite3
from typing import List, Dict, Optional


def thong_ke_toan_tinh(conn: sqlite3.Connection) -> Dict:
    """Thống kê tổng hợp toàn tỉnh."""
    sql = """
        SELECT
            (SELECT COUNT(*) FROM tuyen_duong)                       AS tong_so_tuyen,
            (SELECT COUNT(*) FROM doan_tuyen)                        AS tong_so_doan,
            (SELECT COUNT(*) FROM doan_di_chung)                     AS tong_so_doan_di_chung,
            (SELECT ROUND(SUM(chieu_dai_quan_ly), 3) FROM tuyen_duong) AS tong_chieu_dai_quan_ly,
            (SELECT ROUND(SUM(chieu_dai_thuc_te), 3) FROM tuyen_duong) AS tong_chieu_dai_thuc_te
    """
    row = conn.execute(sql).fetchone()
    return dict(row)


def thong_ke_theo_cap_quan_ly(conn: sqlite3.Connection) -> List[Dict]:
    """Chiều dài quản lý & số tuyến theo từng cấp quản lý."""
    sql = """
        SELECT
            cql.ma_cap,
            cql.ten_cap,
            COUNT(td.id)                              AS so_tuyen,
            ROUND(SUM(td.chieu_dai_quan_ly), 3)       AS chieu_dai_quan_ly,
            ROUND(SUM(td.chieu_dai_thuc_te), 3)       AS chieu_dai_thuc_te
        FROM cap_quan_ly cql
        LEFT JOIN tuyen_duong td ON td.cap_quan_ly_id = cql.id
        GROUP BY cql.id
        ORDER BY cql.thu_tu_hien_thi
    """
    rows = conn.execute(sql).fetchall()
    return [dict(r) for r in rows]


def thong_ke_theo_tinh_trang(conn: sqlite3.Connection) -> List[Dict]:
    """Tổng chiều dài theo từng tình trạng đường."""
    sql = """
        SELECT
            tt.ma_tinh_trang,
            tt.ten_tinh_trang,
            tt.mau_hien_thi,
            COUNT(dt.id)                                               AS so_doan,
            ROUND(SUM(COALESCE(dt.chieu_dai_thuc_te,
                  dt.ly_trinh_cuoi - dt.ly_trinh_dau)), 3)            AS tong_chieu_dai
        FROM tinh_trang tt
        LEFT JOIN doan_tuyen dt ON dt.tinh_trang_id = tt.id
        GROUP BY tt.id
        ORDER BY tt.thu_tu_hien_thi
    """
    rows = conn.execute(sql).fetchall()
    return [dict(r) for r in rows]


def thong_ke_theo_ket_cau_mat(conn: sqlite3.Connection) -> List[Dict]:
    """Tổng chiều dài theo từng loại kết cấu mặt đường."""
    sql = """
        SELECT
            kcm.ma_ket_cau,
            kcm.ten_ket_cau,
            COUNT(dt.id)                                               AS so_doan,
            ROUND(SUM(COALESCE(dt.chieu_dai_thuc_te,
                  dt.ly_trinh_cuoi - dt.ly_trinh_dau)), 3)            AS tong_chieu_dai
        FROM ket_cau_mat_duong kcm
        LEFT JOIN doan_tuyen dt ON dt.ket_cau_mat_id = kcm.id
        GROUP BY kcm.id
        ORDER BY kcm.thu_tu_hien_thi
    """
    rows = conn.execute(sql).fetchall()
    return [dict(r) for r in rows]


def thong_ke_theo_cap_duong(conn: sqlite3.Connection) -> List[Dict]:
    """Tổng chiều dài theo từng cấp đường kỹ thuật."""
    sql = """
        SELECT
            cd.ma_cap,
            cd.ten_cap,
            COUNT(dt.id)                                               AS so_doan,
            ROUND(SUM(COALESCE(dt.chieu_dai_thuc_te,
                  dt.ly_trinh_cuoi - dt.ly_trinh_dau)), 3)            AS tong_chieu_dai
        FROM cap_duong cd
        LEFT JOIN doan_tuyen dt ON dt.cap_duong_id = cd.id
        GROUP BY cd.id
        ORDER BY cd.thu_tu_hien_thi
    """
    rows = conn.execute(sql).fetchall()
    return [dict(r) for r in rows]


def thong_ke_mot_tuyen(conn: sqlite3.Connection, tuyen_id: int) -> Dict:
    """Thống kê chi tiết cho một tuyến: theo tình trạng và kết cấu mặt."""
    sql_tong_hop = """
        SELECT
            td.ma_tuyen,
            td.ten_tuyen,
            td.chieu_dai_quan_ly,
            td.chieu_dai_thuc_te,
            COUNT(dt.id) AS tong_so_doan
        FROM tuyen_duong td
        LEFT JOIN doan_tuyen dt ON dt.tuyen_id = td.id
        WHERE td.id = ?
        GROUP BY td.id
    """
    sql_tinh_trang = """
        SELECT
            tt.ma_tinh_trang,
            ROUND(SUM(COALESCE(dt.chieu_dai_thuc_te,
                  dt.ly_trinh_cuoi - dt.ly_trinh_dau)), 3) AS chieu_dai
        FROM doan_tuyen dt
        JOIN tinh_trang tt ON tt.id = dt.tinh_trang_id
        WHERE dt.tuyen_id = ?
        GROUP BY tt.id
    """
    sql_ket_cau = """
        SELECT
            kcm.ma_ket_cau,
            ROUND(SUM(COALESCE(dt.chieu_dai_thuc_te,
                  dt.ly_trinh_cuoi - dt.ly_trinh_dau)), 3) AS chieu_dai
        FROM doan_tuyen dt
        JOIN ket_cau_mat_duong kcm ON kcm.id = dt.ket_cau_mat_id
        WHERE dt.tuyen_id = ?
        GROUP BY kcm.id
    """
    tong_hop = conn.execute(sql_tong_hop, (tuyen_id,)).fetchone()
    tinh_trang_rows = conn.execute(sql_tinh_trang, (tuyen_id,)).fetchall()
    ket_cau_rows = conn.execute(sql_ket_cau, (tuyen_id,)).fetchall()

    return {
        "tong_hop": dict(tong_hop) if tong_hop else {},
        "theo_tinh_trang": [dict(r) for r in tinh_trang_rows],
        "theo_ket_cau_mat": [dict(r) for r in ket_cau_rows],
    }


def thong_ke_theo_don_vi_bao_duong(conn: sqlite3.Connection) -> List[Dict]:
    """Chiều dài được giao bảo dưỡng theo từng đơn vị."""
    sql = """
        SELECT
            dv.ma_don_vi,
            dv.ten_don_vi,
            COUNT(dt.id)                                               AS so_doan,
            ROUND(SUM(COALESCE(dt.chieu_dai_thuc_te,
                  dt.ly_trinh_cuoi - dt.ly_trinh_dau)), 3)            AS tong_chieu_dai
        FROM don_vi dv
        LEFT JOIN doan_tuyen dt ON dt.don_vi_bao_duong_id = dv.id
        GROUP BY dv.id
        ORDER BY dv.ma_don_vi
    """
    rows = conn.execute(sql).fetchall()
    return [dict(r) for r in rows]
