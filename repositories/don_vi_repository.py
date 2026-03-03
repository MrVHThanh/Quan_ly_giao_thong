from config.database import get_connection
from models.don_vi import DonVi
import sqlite3


# ================= LẤY TẤT CẢ (CHỈ HOẠT ĐỘNG) =================
def lay_tat_ca():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_don_vi, ten_don_vi, loai, parent_id, is_active, created_at
        FROM don_vi
        WHERE is_active = 1
        ORDER BY id
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


# ================= LẤY TẤT CẢ KỂ CẢ ĐÃ XOÁ =================
def lay_tat_ca_ke_ca_da_xoa():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_don_vi, ten_don_vi, loai, parent_id, is_active, created_at
        FROM don_vi
        ORDER BY id
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


# ================= LẤY THEO ID =================
def lay_theo_id(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_don_vi, ten_don_vi, loai, parent_id, is_active, created_at
        FROM don_vi
        WHERE id = ?
    """, (id,))

    row = cursor.fetchone()
    conn.close()
    return row


# ================= LẤY THEO ID (CHỈ HOẠT ĐỘNG) =================
def lay_theo_id_hoat_dong(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_don_vi, ten_don_vi, loai, parent_id, is_active, created_at
        FROM don_vi
        WHERE id = ? AND is_active = 1
    """, (id,))

    row = cursor.fetchone()
    conn.close()
    return row

# ================= LẤY THEO MA ĐƠN VỊ =========================
def lay_theo_ma_hoat_dong(ma_don_vi):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_don_vi, ten_don_vi, loai, parent_id, is_active
        FROM don_vi
        WHERE ma_don_vi = ? AND is_active = 1
    """, (ma_don_vi,))

    row = cursor.fetchone()
    conn.close()

    return row 

# ================= LẤY ĐƠN VỊ CON (CHỈ HOẠT ĐỘNG) =================
def lay_con(parent_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_don_vi, ten_don_vi, loai, parent_id, is_active, created_at
        FROM don_vi
        WHERE parent_id = ? AND is_active = 1
    """, (parent_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


# ================= THÊM =================
def them_don_vi(ma_don_vi, ten_don_vi, loai, parent_id, is_active):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO don_vi ( ma_don_vi, ten_don_vi, loai, parent_id, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (
            ma_don_vi,
            ten_don_vi,
            loai,
            parent_id,
            is_active
        ))

        conn.commit()
        return cursor.lastrowid

    except sqlite3.IntegrityError:
        raise

    finally:
        conn.close()


# ================= CẬP NHẬT =================
def cap_nhat_don_vi(id,  ma_don_vi, ten_don_vi, loai, parent_id, is_active):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE don_vi
        SET  ma_don_vi = ?, ten_don_vi = ?, loai = ?, parent_id = ?, is_active = ?
        WHERE id = ?
    """, (
        ma_don_vi,
        ten_don_vi,
        loai,
        parent_id,
        is_active,
        id
    ))

    conn.commit()
    conn.close()

# ================= XOÁ AN TOÀN (SOFT DELETE) =================
def xoa_don_vi(id):
    conn = get_connection()
    cursor = conn.cursor()

    # kiểm tra đơn vị con
    cursor.execute("""
        SELECT COUNT(*) FROM don_vi
        WHERE parent_id = ? AND is_active = 1
    """, (id,))

    so_luong_con = cursor.fetchone()[0]

    if so_luong_con > 0:
        conn.close()
        raise ValueError("Khong the xoa don vi dang co don vi con!")

    cursor.execute("""
        UPDATE don_vi
        SET is_active = 0
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()


# ================= KHÔI PHỤC =================
def khoi_phuc_don_vi(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE don_vi
        SET is_active = 1
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

# ================= LẤY THEO MÃ (KỂ CẢ ĐÃ XOÁ) =================
def lay_theo_ma(ma_don_vi):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_don_vi, ten_don_vi, loai, parent_id, is_active, created_at
        FROM don_vi
        WHERE ma_don_vi = ?
    """, (ma_don_vi,))

    row = cursor.fetchone()
    conn.close()
    return row