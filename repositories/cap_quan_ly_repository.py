from config.database import get_connection
import sqlite3


def lay_tat_ca():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_cap, ten_cap, mo_ta, thu_tu_hien_thi, is_active
        FROM cap_quan_ly
        WHERE is_active = 1
        ORDER BY thu_tu_hien_thi
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def lay_theo_ma(ma_cap):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_cap, ten_cap, mo_ta, thu_tu_hien_thi, is_active
        FROM cap_quan_ly
        WHERE ma_cap = ?
    """, (ma_cap,))

    row = cursor.fetchone()
    conn.close()
    return row


def lay_theo_ma_hoat_dong(ma_cap):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_cap, ten_cap, mo_ta, thu_tu_hien_thi, is_active
        FROM cap_quan_ly
        WHERE ma_cap = ? AND is_active = 1
    """, (ma_cap,))

    row = cursor.fetchone()
    conn.close()
    return row


def lay_theo_id_hoat_dong(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_cap, ten_cap, mo_ta, thu_tu_hien_thi, is_active
        FROM cap_quan_ly
        WHERE id = ? AND is_active = 1
    """, (id,))

    row = cursor.fetchone()
    conn.close()
    return row


def them_cap_quan_ly(ma_cap, ten_cap, mo_ta, thu_tu_hien_thi, is_active):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO cap_quan_ly (ma_cap, ten_cap, mo_ta, thu_tu_hien_thi, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (ma_cap, ten_cap, mo_ta, thu_tu_hien_thi, is_active))

        conn.commit()
        return cursor.lastrowid

    except sqlite3.IntegrityError:
        raise

    finally:
        conn.close()


def khoi_phuc_cap_quan_ly(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE cap_quan_ly
        SET is_active = 1
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()