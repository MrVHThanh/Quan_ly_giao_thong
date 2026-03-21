"""
Seed: Danh mục — CapQuanLy, CapDuong, KetCauMatDuong, TinhTrang
Idempotent: INSERT OR IGNORE — chạy nhiều lần không lỗi, không trùng dữ liệu.
"""

import sqlite3

import data.cap_quan_ly_data as cap_quan_ly_data
import data.cap_duong_data as cap_duong_data
import data.ket_cau_mat_data as ket_cau_mat_data
import data.tinh_trang_data as tinh_trang_data


def seed(conn: sqlite3.Connection) -> None:
    _seed_cap_quan_ly(conn)
    _seed_cap_duong(conn)
    _seed_ket_cau_mat(conn)
    _seed_tinh_trang(conn)
    print("[seed_danh_muc] Hoàn thành: cap_quan_ly(8), cap_duong(7), ket_cau_mat(8), tinh_trang(9).")


def _seed_cap_quan_ly(conn: sqlite3.Connection) -> None:
    sql = """
        INSERT OR IGNORE INTO cap_quan_ly (ma_cap, ten_cap, mo_ta, thu_tu_hien_thi, is_active)
        VALUES (:ma_cap, :ten_cap, :mo_ta, :thu_tu_hien_thi, 1)
    """
    conn.executemany(sql, cap_quan_ly_data.RECORDS)


def _seed_cap_duong(conn: sqlite3.Connection) -> None:
    sql = """
        INSERT OR IGNORE INTO cap_duong (ma_cap, ten_cap, mo_ta, thu_tu_hien_thi, is_active)
        VALUES (:ma_cap, :ten_cap, :mo_ta, :thu_tu_hien_thi, 1)
    """
    conn.executemany(sql, cap_duong_data.RECORDS)


def _seed_ket_cau_mat(conn: sqlite3.Connection) -> None:
    sql = """
        INSERT OR IGNORE INTO ket_cau_mat_duong (ma_ket_cau, ten_ket_cau, mo_ta, thu_tu_hien_thi, is_active)
        VALUES (:ma_ket_cau, :ten_ket_cau, :mo_ta, :thu_tu_hien_thi, 1)
    """
    conn.executemany(sql, ket_cau_mat_data.RECORDS)


def _seed_tinh_trang(conn: sqlite3.Connection) -> None:
    sql = """
        INSERT OR IGNORE INTO tinh_trang
            (ma_tinh_trang, ten_tinh_trang, mo_ta, mau_hien_thi, thu_tu_hien_thi, is_active)
        VALUES (:ma_tinh_trang, :ten_tinh_trang, :mo_ta, :mau_hien_thi, :thu_tu_hien_thi, 1)
    """
    conn.executemany(sql, tinh_trang_data.RECORDS)
