"""
Seed: DonVi — 17 đơn vị theo cây cha-con
Idempotent: INSERT OR IGNORE.

Xử lý đặc biệt:
- parent_ma (mã chuỗi) → tra id thực trước khi INSERT
- Thứ tự trong RECORDS đã đảm bảo cha trước con
"""

import sqlite3

import data.don_vi_data as don_vi_data


def seed(conn: sqlite3.Connection) -> None:
    dem = 0
    for rec in don_vi_data.RECORDS:
        # Tra parent_id từ parent_ma
        parent_id = None
        if rec.get("parent_ma"):
            row = conn.execute(
                "SELECT id FROM don_vi WHERE ma_don_vi = ?", (rec["parent_ma"],)
            ).fetchone()
            if row is None:
                raise ValueError(
                    f"[seed_don_vi] Không tìm thấy đơn vị cha '{rec['parent_ma']}' "
                    f"khi seed '{rec['ma_don_vi']}'. Kiểm tra thứ tự RECORDS."
                )
            parent_id = row["id"]

        sql = """
            INSERT OR IGNORE INTO don_vi
                (ma_don_vi, ten_don_vi, ten_viet_tat, parent_id,
                 cap_don_vi, dia_chi, so_dien_thoai, email, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """
        conn.execute(sql, (
            rec["ma_don_vi"],
            rec["ten_don_vi"],
            rec.get("ten_viet_tat"),
            parent_id,
            rec.get("cap_don_vi"),
            rec.get("dia_chi"),
            rec.get("so_dien_thoai"),
            rec.get("email"),
        ))
        dem += 1

    print(f"[seed_don_vi] Hoàn thành: {dem} đơn vị (cây TINH→SXD→BAN_BT + 13 CT).")
