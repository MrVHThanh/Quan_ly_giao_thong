"""
Migration: Thêm các cột mô tả bổ sung vào bảng thong_tin_tuyen
Chạy: python migrations/alter_thong_tin_tuyen.py

Các cột thêm mới:
  - ly_do_xay_dung    TEXT
  - dac_diem_dia_ly   TEXT
  - lich_su_hinh_thanh TEXT
  - y_nghia_kinh_te   TEXT
  - ghi_chu           TEXT
  - updated_at        TEXT

Script an toàn — kiểm tra cột đã tồn tại trước khi thêm (idempotent).
"""

import sqlite3
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_ROOT, "giao_thong.db")


def lay_cot_hien_co(conn, ten_bang: str) -> set:
    rows = conn.execute(f"PRAGMA table_info({ten_bang})").fetchall()
    return {row["name"] for row in rows}


def chay_migration():
    if not os.path.exists(DB_PATH):
        print(f"LỖI: Không tìm thấy DB tại {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cot_hien_co = lay_cot_hien_co(conn, "thong_tin_tuyen")
    print(f"Cột hiện có: {sorted(cot_hien_co)}")

    # Danh sách cột cần thêm: (tên_cột, kiểu_dữ_liệu)
    cot_can_them = [
        ("ly_do_xay_dung",    "TEXT"),
        ("dac_diem_dia_ly",   "TEXT"),
        ("lich_su_hinh_thanh","TEXT"),
        ("y_nghia_kinh_te",   "TEXT"),
        ("ghi_chu",           "TEXT"),
        ("updated_at",        "TEXT"),
    ]

    them_duoc = []
    da_co = []

    for ten_cot, kieu in cot_can_them:
        if ten_cot in cot_hien_co:
            da_co.append(ten_cot)
        else:
            conn.execute(f"ALTER TABLE thong_tin_tuyen ADD COLUMN {ten_cot} {kieu}")
            them_duoc.append(ten_cot)
            print(f"  ✓ Đã thêm cột: {ten_cot} {kieu}")

    conn.commit()
    conn.close()

    print()
    if them_duoc:
        print(f"Thêm mới {len(them_duoc)} cột: {them_duoc}")
    if da_co:
        print(f"Đã có sẵn {len(da_co)} cột: {da_co}")
    print("Migration hoàn thành.")


def up(conn):
    """Chuẩn hàm up() để migrate.py gọi được."""
    cot_hien_co = lay_cot_hien_co(conn, "thong_tin_tuyen")
    cot_can_them = [
        ("ly_do_xay_dung",     "TEXT"),
        ("dac_diem_dia_ly",    "TEXT"),
        ("lich_su_hinh_thanh", "TEXT"),
        ("y_nghia_kinh_te",    "TEXT"),
        ("ghi_chu",            "TEXT"),
        ("updated_at",         "TEXT"),
    ]
    for ten_cot, kieu in cot_can_them:
        if ten_cot not in cot_hien_co:
            conn.execute(f"ALTER TABLE thong_tin_tuyen ADD COLUMN {ten_cot} {kieu}")
            print(f"         + Thêm cột: {ten_cot}")
    conn.commit()


if __name__ == "__main__":
    chay_migration()
