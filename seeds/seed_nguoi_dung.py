"""
Seed: NguoiDung — 3 tài khoản khởi tạo
Idempotent: INSERT OR IGNORE (kiểm tra ten_dang_nhap).

Xử lý đặc biệt:
- Tạo bcrypt hash từ MAT_KHAU_MAC_DINH
- Tra don_vi_ma → don_vi_id thực
- is_active=1, is_approved=1 cho cả 3 tài khoản ban đầu

Yêu cầu: pip install bcrypt
"""

import sqlite3

import data.nguoi_dung_data as nguoi_dung_data


def seed(conn: sqlite3.Connection) -> None:
    try:
        import bcrypt
    except ImportError:
        raise ImportError(
            "[seed_nguoi_dung] Thiếu thư viện bcrypt. Chạy: pip install bcrypt"
        )

    mat_khau_hash = bcrypt.hashpw(
        nguoi_dung_data.MAT_KHAU_MAC_DINH.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    dem = 0
    for rec in nguoi_dung_data.RECORDS:
        # Tra don_vi_id
        don_vi_id = None
        if rec.get("don_vi_ma"):
            row = conn.execute(
                "SELECT id FROM don_vi WHERE ma_don_vi = ?", (rec["don_vi_ma"],)
            ).fetchone()
            if row is None:
                raise ValueError(
                    f"[seed_nguoi_dung] Không tìm thấy đơn vị '{rec['don_vi_ma']}'. "
                    "Hãy chạy seed_don_vi trước."
                )
            don_vi_id = row["id"]

        sql = """
            INSERT OR IGNORE INTO nguoi_dung
                (ten_dang_nhap, mat_khau_hash, ho_ten, chuc_vu,
                 don_vi_id, so_dien_thoai, email,
                 loai_quyen, is_active, is_approved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
        """
        conn.execute(sql, (
            rec["ten_dang_nhap"],
            mat_khau_hash,
            rec["ho_ten"],
            rec.get("chuc_vu"),
            don_vi_id,
            rec.get("so_dien_thoai"),
            rec.get("email"),
            rec.get("loai_quyen", "XEM"),
        ))
        dem += 1

    print(
        f"[seed_nguoi_dung] Hoàn thành: {dem} tài khoản. "
        f"Mật khẩu mặc định: '{nguoi_dung_data.MAT_KHAU_MAC_DINH}' — đổi ngay sau khi đăng nhập!"
    )
