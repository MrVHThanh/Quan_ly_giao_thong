"""
migrate.py — Chạy tất cả migration theo thứ tự trên VPS.

Cách dùng:
    python migrate.py            # Chạy tất cả migration chưa chạy
    python migrate.py --list     # Xem danh sách migration và trạng thái
    python migrate.py --reset    # Xóa bảng theo dõi (chạy lại từ đầu)
"""

import os
import sys
import sqlite3
import argparse
from datetime import datetime

# Fix encoding cho Windows terminal
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Đảm bảo import được các module trong dự án
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config.database import get_connection

# ── Danh sách migration theo thứ tự ──────────────────────────────────────────
# Thêm migration mới vào cuối danh sách này
MIGRATIONS = [
    ("m001_initial_schema",    "migrations.m001_initial_schema",    "Tạo schema ban đầu (15 bảng, triggers, indexes)"),
    ("alter_thong_tin_tuyen",  "migrations.alter_thong_tin_tuyen",  "Thêm cột mô tả bổ sung vào thong_tin_tuyen"),
    ("m002_nhat_ky",           "migrations.m002_nhat_ky",           "Tạo bảng nhật ký đăng nhập và hoạt động"),
]


def _ensure_migration_table(conn: sqlite3.Connection) -> None:
    """Tạo bảng theo dõi migration nếu chưa có."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS _migration_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            chay_luc    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
            thanh_cong  INTEGER NOT NULL DEFAULT 1
        )
    """)
    conn.commit()


def _da_chay(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM _migration_log WHERE name = ? AND thanh_cong = 1", (name,)
    ).fetchone()
    return row is not None


def _ghi_ket_qua(conn: sqlite3.Connection, name: str, thanh_cong: bool) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO _migration_log (name, thanh_cong) VALUES (?, ?)",
        (name, 1 if thanh_cong else 0),
    )
    conn.commit()


def chay_tat_ca(conn: sqlite3.Connection) -> None:
    _ensure_migration_table(conn)
    co_gi_moi = False

    for name, module_path, mo_ta in MIGRATIONS:
        if _da_chay(conn, name):
            print(f"  [SKIP] {name} — đã chạy trước đó")
            continue

        co_gi_moi = True
        print(f"  [RUN ] {name} — {mo_ta}")
        try:
            import importlib
            mod = importlib.import_module(module_path)
            mod.up(conn)
            _ghi_ket_qua(conn, name, True)
            print(f"         ✓ Thành công")
        except Exception as e:
            _ghi_ket_qua(conn, name, False)
            print(f"         ✗ LỖI: {e}")
            sys.exit(1)

    if not co_gi_moi:
        print("  Không có migration mới — DB đã cập nhật.")


def xem_danh_sach(conn: sqlite3.Connection) -> None:
    _ensure_migration_table(conn)
    print(f"\n{'Tên migration':<35} {'Trạng thái':<15} {'Thời gian'}")
    print("-" * 75)
    da_chay_set = {
        row["name"]: row
        for row in conn.execute("SELECT name, chay_luc, thanh_cong FROM _migration_log").fetchall()
    }
    for name, _, mo_ta in MIGRATIONS:
        if name in da_chay_set:
            row = da_chay_set[name]
            trang_thai = "✓ Đã chạy" if row["thanh_cong"] else "✗ Lỗi"
            thoi_gian  = row["chay_luc"]
        else:
            trang_thai = "○ Chưa chạy"
            thoi_gian  = "—"
        print(f"{name:<35} {trang_thai:<15} {thoi_gian}")
    print()


def reset_log(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS _migration_log")
    conn.commit()
    print("  Đã xóa bảng theo dõi migration. Chạy lại 'python migrate.py' để thực thi.")


# ── Main ──────────────────────────────────────────────────────────────────────

def _doc_version() -> str:
    version_file = os.path.join(BASE_DIR, "VERSION")
    try:
        with open(version_file) as f:
            return f.read().strip()
    except Exception:
        return "?"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Công cụ migration DB")
    parser.add_argument("--list",  action="store_true", help="Xem danh sách migration")
    parser.add_argument("--reset", action="store_true", help="Xóa log, chạy lại từ đầu")
    args = parser.parse_args()

    version = _doc_version()
    print(f"\n=== Migration Tool — Quản lý Đường bộ Lào Cai v{version} ===")
    print(f"    DB: {os.environ.get('DB_PATH', 'giao_thong.db')}")
    print(f"    Thời điểm: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    from dotenv import load_dotenv
    load_dotenv()

    conn = get_connection()
    try:
        if args.list:
            xem_danh_sach(conn)
        elif args.reset:
            reset_log(conn)
        else:
            chay_tat_ca(conn)
    finally:
        conn.close()

    print("=== Hoàn thành ===\n")
