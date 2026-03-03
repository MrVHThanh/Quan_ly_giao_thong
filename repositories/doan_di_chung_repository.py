from config.database import get_connection
from models.doan_di_chung import DoanDiChung
import sqlite3


# ==========================
# ROW → OBJECT
# ==========================

def _row_to_object(row):
    if not row:
        return None
    return DoanDiChung(
        id=row[0],
        tuyen_id=row[1],
        doan_id=row[2],
        ly_trinh_dau=row[3],
        ly_trinh_cuoi=row[4],
        ghi_chu=row[5],
        created_at=row[6]
    )


# ==========================
# LẤY TẤT CẢ THEO TUYẾN
# ==========================

def lay_theo_tuyen(tuyen_id):
    """Lấy tất cả đoạn đi chung của một tuyến, sắp xếp theo ly_trinh_dau."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, tuyen_id, doan_id, ly_trinh_dau, ly_trinh_cuoi, ghi_chu, created_at
        FROM doan_di_chung
        WHERE tuyen_id = ?
        ORDER BY ly_trinh_dau
    """, (tuyen_id,))

    rows = cursor.fetchall()
    conn.close()
    return [_row_to_object(row) for row in rows]


# ==========================
# LẤY THEO ID
# ==========================

def lay_theo_id(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, tuyen_id, doan_id, ly_trinh_dau, ly_trinh_cuoi, ghi_chu, created_at
        FROM doan_di_chung
        WHERE id = ?
    """, (id,))

    row = cursor.fetchone()
    conn.close()
    return _row_to_object(row)


# ==========================
# LẤY THEO TUYẾN + ĐOẠN
# ==========================

def lay_theo_tuyen_va_doan(tuyen_id, doan_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, tuyen_id, doan_id, ly_trinh_dau, ly_trinh_cuoi, ghi_chu, created_at
        FROM doan_di_chung
        WHERE tuyen_id = ? AND doan_id = ?
    """, (tuyen_id, doan_id))

    row = cursor.fetchone()
    conn.close()
    return _row_to_object(row)


# ==========================
# THÊM
# ==========================

def them_doan_di_chung(tuyen_id, doan_id, ly_trinh_dau, ly_trinh_cuoi, ghi_chu):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO doan_di_chung (tuyen_id, doan_id, ly_trinh_dau, ly_trinh_cuoi, ghi_chu)
            VALUES (?, ?, ?, ?, ?)
        """, (tuyen_id, doan_id, ly_trinh_dau, ly_trinh_cuoi, ghi_chu))

        conn.commit()
        return cursor.lastrowid

    except sqlite3.IntegrityError:
        raise

    finally:
        conn.close()


# ==========================
# XOÁ
# ==========================

def xoa_doan_di_chung(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM doan_di_chung WHERE id = ?", (id,))

    conn.commit()
    conn.close()


# ==========================
# TÍNH TỔNG CHIỀU DÀI ĐI CHUNG THEO TUYẾN
# ==========================

def tinh_tong_chieu_dai_di_chung(tuyen_id):
    """Tổng chiều dài các đoạn đi chung của một tuyến."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(ly_trinh_cuoi - ly_trinh_dau), 0)
        FROM doan_di_chung
        WHERE tuyen_id = ?
    """, (tuyen_id,))

    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0