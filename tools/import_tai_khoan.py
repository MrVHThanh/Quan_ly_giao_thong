"""
tools/import_tai_khoan.py
Import danh sách tài khoản từ file Excel vào hệ thống.

File Excel cần có các cột (dòng 1 là tiêu đề):
  A: Tên đăng nhập
  B: Mật khẩu       (bỏ qua — dùng MAT_KHAU_MAC_DINH)
  C: Họ tên
  D: Chức vụ
  E: Email
  F: Số điện thoại

Cấu hình mặc định:
  - Mật khẩu: sxd@1234
  - Quyền: XEM
  - Trạng thái: kích hoạt ngay (is_active=1, is_approved=1)

Chạy:
  python tools/import_tai_khoan.py
  python tools/import_tai_khoan.py --file path/to/file.xlsx
"""

import sys
import os
import argparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Load .env trước khi import config ──────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

# ── Thêm thư mục gốc vào sys.path ──────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bcrypt
import openpyxl
import config.database as db

# ── Cấu hình ───────────────────────────────────────────────────────────────
FILE_EXCEL_DEFAULT = os.path.join(ROOT, "Danh_sach_tai_khoan_sxd.xlsx")
MAT_KHAU_MAC_DINH  = "sxd@1234"
LOAI_QUYEN         = "XEM"


def _hash(mat_khau: str) -> str:
    return bcrypt.hashpw(mat_khau.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _doc_excel(duong_dan: str) -> list[dict]:
    wb = openpyxl.load_workbook(duong_dan)
    ws = wb.active
    tai_khoans = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        ten_dang_nhap = str(row[0]).strip() if row[0] else None
        ho_ten        = str(row[2]).strip() if row[2] else None
        chuc_vu       = str(row[3]).strip() if row[3] else None
        email         = str(row[4]).strip() if row[4] else None
        so_dt         = str(row[5]).strip() if row[5] else None

        if not ten_dang_nhap or ten_dang_nhap == "None":
            continue

        tai_khoans.append({
            "ten_dang_nhap": ten_dang_nhap,
            "ho_ten":        ho_ten or ten_dang_nhap,
            "chuc_vu":       chuc_vu if chuc_vu and chuc_vu != "None" else None,
            "email":         email   if email   and email   != "None" else None,
            "so_dien_thoai": so_dt   if so_dt   and so_dt   != "None" else None,
        })
    return tai_khoans


def chay_import(duong_dan: str) -> None:
    print(f"\n{'='*55}")
    print(f"  IMPORT TÀI KHOẢN — Quản lý Đường bộ Lào Cai")
    print(f"{'='*55}")
    print(f"  File  : {duong_dan}")
    print(f"  DB    : {db.DB_PATH_DEFAULT}")
    print(f"  Quyền : {LOAI_QUYEN} | is_active: 1 | is_approved: 1")
    print(f"{'='*55}\n")

    if not os.path.exists(duong_dan):
        print(f"LỖI: Không tìm thấy file '{duong_dan}'")
        sys.exit(1)

    tai_khoans = _doc_excel(duong_dan)
    print(f"  Đọc được {len(tai_khoans)} tài khoản từ file Excel.\n")

    conn = db.get_connection()
    mat_khau_hash = _hash(MAT_KHAU_MAC_DINH)

    them_moi = 0
    da_ton_tai = 0
    loi = 0

    for tk in tai_khoans:
        ten = tk["ten_dang_nhap"]
        try:
            ton_tai = conn.execute(
                "SELECT id FROM nguoi_dung WHERE ten_dang_nhap = ?", (ten,)
            ).fetchone()

            if ton_tai:
                print(f"  [BỎ QUA] {ten:<25} — đã tồn tại")
                da_ton_tai += 1
                continue

            conn.execute(
                """INSERT INTO nguoi_dung
                   (ten_dang_nhap, mat_khau_hash, ho_ten, chuc_vu,
                    email, so_dien_thoai, loai_quyen, is_active, is_approved)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1)""",
                (
                    ten,
                    mat_khau_hash,
                    tk["ho_ten"],
                    tk["chuc_vu"],
                    tk["email"],
                    tk["so_dien_thoai"],
                    LOAI_QUYEN,
                ),
            )
            conn.commit()
            print(f"  [THÊM]   {ten:<25} — {tk['ho_ten']}")
            them_moi += 1

        except Exception as e:
            print(f"  [LỖI]    {ten:<25} — {e}")
            loi += 1

    conn.close()

    print(f"\n{'─'*55}")
    print(f"  ✅ Thêm mới  : {them_moi} tài khoản")
    print(f"  ⏭  Đã có sẵn: {da_ton_tai} tài khoản")
    if loi:
        print(f"  ❌ Lỗi      : {loi} tài khoản")
    print(f"  Mật khẩu mặc định: {MAT_KHAU_MAC_DINH}")
    print(f"{'─'*55}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import tài khoản từ Excel")
    parser.add_argument(
        "--file", default=FILE_EXCEL_DEFAULT,
        help="Đường dẫn file Excel (mặc định: Danh_sach_tai_khoan_sxd.xlsx)"
    )
    args = parser.parse_args()
    chay_import(args.file)
