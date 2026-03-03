from config.database import get_connection
import sqlite3


def lay_tat_ca():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma, ten, mo_ta, mau_hien_thi, thu_tu_hien_thi, is_active
        FROM tinh_trang
        WHERE is_active = 1
        ORDER BY thu_tu_hien_thi
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def lay_theo_ma(ma):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma, ten, mo_ta, mau_hien_thi, thu_tu_hien_thi, is_active
        FROM tinh_trang
        WHERE ma = ?
    """, (ma,))

    row = cursor.fetchone()
    conn.close()
    return row


def lay_theo_ma_hoat_dong(ma):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma, ten, mo_ta, mau_hien_thi, thu_tu_hien_thi, is_active
        FROM tinh_trang
        WHERE ma = ? AND is_active = 1
    """, (ma,))

    row = cursor.fetchone()
    conn.close()
    return row


def lay_theo_id_hoat_dong(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma, ten, mo_ta, mau_hien_thi, thu_tu_hien_thi, is_active
        FROM tinh_trang
        WHERE id = ? AND is_active = 1
    """, (id,))

    row = cursor.fetchone()
    conn.close()
    return row


def them_tinh_trang(ma, ten, mo_ta, mau_hien_thi, thu_tu_hien_thi, is_active):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO tinh_trang (ma, ten, mo_ta, mau_hien_thi, thu_tu_hien_thi, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ma, ten, mo_ta, mau_hien_thi, thu_tu_hien_thi, is_active))

        conn.commit()
        return cursor.lastrowid

    except sqlite3.IntegrityError:
        raise

    finally:
        conn.close()


def khoi_phuc_tinh_trang(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tinh_trang
        SET is_active = 1
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()