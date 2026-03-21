"""
Seed All — Orchestrator chạy toàn bộ seed theo đúng thứ tự.

Sử dụng:
    python seeds/seed_all.py
    python seeds/seed_all.py path/to/giao_thong.db

Tính chất:
- Toàn bộ trong 1 transaction — lỗi bất kỳ thì rollback hoàn toàn
- Idempotent — chạy nhiều lần không sinh dữ liệu trùng
- Áp dụng migration schema trước khi seed
"""

import os
import sqlite3
import sys

# Đảm bảo import được từ thư mục gốc dự án
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import migrations.m001_initial_schema as migration_001
import seeds.seed_danh_muc as seed_danh_muc
import seeds.seed_don_vi as seed_don_vi
import seeds.seed_nguoi_dung as seed_nguoi_dung
import seeds.seed_tuyen_doan as seed_tuyen_doan

DB_DEFAULT = os.path.join(_ROOT, "giao_thong.db")


def run(db_path: str = DB_DEFAULT) -> None:
    print(f"\n{'='*55}")
    print(f"  SEED HỆ THỐNG QUẢN LÝ GIAO THÔNG LÀO CAI")
    print(f"  DB: {db_path}")
    print(f"{'='*55}\n")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        # ── Bước 0: Migration — tạo schema nếu chưa có ───────────────────
        print("[0/5] Áp dụng migration schema...")
        migration_001.up(conn)

        # ── Bước 1: Danh mục cơ sở ───────────────────────────────────────
        print("\n[1/5] Seed danh mục (cap_quan_ly, cap_duong, ket_cau_mat, tinh_trang)...")
        seed_danh_muc.seed(conn)

        # ── Bước 2: Đơn vị ───────────────────────────────────────────────
        print("\n[2/5] Seed đơn vị (cây cha-con)...")
        seed_don_vi.seed(conn)

        # ── Bước 3: Người dùng ───────────────────────────────────────────
        print("\n[3/5] Seed người dùng (bcrypt hash)...")
        seed_nguoi_dung.seed(conn)

        # ── Bước 4+5: Tuyến, đoạn, đi chung ─────────────────────────────
        print("\n[4/5] Seed tuyến đường + thông tin tuyến...")
        print("[5/5] Seed đoạn tuyến + đoạn đi chung (trigger tự tính chiều dài)...")
        seed_tuyen_doan.seed(conn)

        conn.commit()

        # ── Kiểm tra kết quả ─────────────────────────────────────────────
        _kiem_tra_ket_qua(conn)

    except Exception as e:
        conn.rollback()
        print(f"\n[THẤT BẠI] Lỗi: {e}")
        print("→ Đã rollback toàn bộ. DB không bị thay đổi.")
        raise
    finally:
        conn.close()


def _kiem_tra_ket_qua(conn: sqlite3.Connection) -> None:
    bang_kiem_tra = [
        ("cap_quan_ly",      8),
        ("cap_duong",        7),
        ("ket_cau_mat_duong", 8),
        ("tinh_trang",       9),
        ("don_vi",          17),
        ("nguoi_dung",       3),
        ("tuyen_duong",     49),
        ("thong_tin_tuyen",  9),
        ("doan_tuyen",     222),
        ("doan_di_chung",   15),
    ]

    print(f"\n{'─'*45}")
    print(f"  Kiểm tra kết quả seed:")
    print(f"{'─'*45}")
    tat_ca_dung = True
    for bang, so_mong_doi in bang_kiem_tra:
        so_thuc_te = conn.execute(f"SELECT COUNT(*) FROM {bang}").fetchone()[0]
        trang_thai = "✓" if so_thuc_te >= so_mong_doi else "✗"
        if so_thuc_te < so_mong_doi:
            tat_ca_dung = False
        print(f"  {trang_thai}  {bang:<25} {so_thuc_te:>4} bản ghi")

    # Kiểm tra trigger: chiều dài tuyến QL4E phải > 0
    ql4e = conn.execute(
        "SELECT chieu_dai_quan_ly, chieu_dai_thuc_te FROM tuyen_duong WHERE ma_tuyen = 'QL4E'"
    ).fetchone()
    if ql4e:
        trang_thai = "✓" if ql4e["chieu_dai_quan_ly"] > 0 else "✗"
        if ql4e["chieu_dai_quan_ly"] == 0:
            tat_ca_dung = False
        print(f"  {trang_thai}  trigger QL4E chieu_dai_quan_ly = {ql4e['chieu_dai_quan_ly']} km")
        print(f"  {trang_thai}  trigger QL4E chieu_dai_thuc_te  = {ql4e['chieu_dai_thuc_te']} km")

    print(f"{'─'*45}")
    if tat_ca_dung:
        print("  ✅ SEED THÀNH CÔNG — Tất cả đúng kỳ vọng!\n")
    else:
        print("  ⚠️  Một số bảng có số bản ghi ít hơn dự kiến.\n")


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else DB_DEFAULT
    run(db_path)
