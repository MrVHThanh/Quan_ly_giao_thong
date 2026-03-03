from config.database import get_connection
from models.doan_tuyen import DoanTuyen
import sqlite3


# ==========================
# LẤY TẤT CẢ
# ==========================

def lay_tat_ca():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_doan, tuyen_id, cap_duong_id,
               ly_trinh_dau, ly_trinh_cuoi,
               chieu_dai, chieu_dai_thuc_te,
               chieu_rong_mat_max, chieu_rong_mat_min,
               chieu_rong_nen_max, chieu_rong_nen_min,
               don_vi_bao_duong_id, ghi_chu, created_at
        FROM doan_tuyen
        ORDER BY tuyen_id, ly_trinh_dau
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


# ==========================
# ROW → OBJECT
# ==========================

def _row_to_object(row):
    if not row:
        return None

    return DoanTuyen(
        id=row[0],
        ma_doan=row[1],
        tuyen_id=row[2],
        cap_duong_id=row[3],
        ly_trinh_dau=row[4],
        ly_trinh_cuoi=row[5],
        chieu_dai_thuc_te=row[7],   # row[6] = chieu_dai tính toán, bỏ qua
        chieu_rong_mat_max=row[8],
        chieu_rong_mat_min=row[9],
        chieu_rong_nen_max=row[10],
        chieu_rong_nen_min=row[11],
        don_vi_bao_duong_id=row[12],
        ghi_chu=row[13],
        created_at=row[14]
    )


# ==========================
# LẤY THEO MÃ
# ==========================

def lay_theo_ma(ma_doan):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_doan, tuyen_id, cap_duong_id,
               ly_trinh_dau, ly_trinh_cuoi,
               chieu_dai, chieu_dai_thuc_te,
               chieu_rong_mat_max, chieu_rong_mat_min,
               chieu_rong_nen_max, chieu_rong_nen_min,
               don_vi_bao_duong_id, ghi_chu, created_at
        FROM doan_tuyen
        WHERE ma_doan = ?
    """, (ma_doan,))

    row = cursor.fetchone()
    conn.close()
    return _row_to_object(row)


# ==========================
# LẤY THEO ID
# ==========================

def lay_theo_id(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_doan, tuyen_id, cap_duong_id,
               ly_trinh_dau, ly_trinh_cuoi,
               chieu_dai, chieu_dai_thuc_te,
               chieu_rong_mat_max, chieu_rong_mat_min,
               chieu_rong_nen_max, chieu_rong_nen_min,
               don_vi_bao_duong_id, ghi_chu, created_at
        FROM doan_tuyen
        WHERE id = ?
    """, (id,))

    row = cursor.fetchone()
    conn.close()
    return _row_to_object(row)


# ==========================
# LẤY THEO TUYẾN
# ==========================

def lay_theo_tuyen(tuyen_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_doan, tuyen_id, cap_duong_id,
               ly_trinh_dau, ly_trinh_cuoi,
               chieu_dai, chieu_dai_thuc_te,
               chieu_rong_mat_max, chieu_rong_mat_min,
               chieu_rong_nen_max, chieu_rong_nen_min,
               don_vi_bao_duong_id, ghi_chu, created_at
        FROM doan_tuyen
        WHERE tuyen_id = ?
        ORDER BY ly_trinh_dau
    """, (tuyen_id,))

    rows = cursor.fetchall()
    conn.close()
    return [_row_to_object(row) for row in rows]


# ==========================
# THÊM
# ==========================

def them_doan_tuyen(
    ma_doan, tuyen_id, cap_duong_id,
    ly_trinh_dau, ly_trinh_cuoi, chieu_dai,
    chieu_dai_thuc_te, chieu_rong_mat_max, chieu_rong_mat_min,
    chieu_rong_nen_max, chieu_rong_nen_min,
    don_vi_bao_duong_id, ghi_chu
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO doan_tuyen (
                ma_doan, tuyen_id, cap_duong_id,
                ly_trinh_dau, ly_trinh_cuoi, chieu_dai,
                chieu_dai_thuc_te,
                chieu_rong_mat_max, chieu_rong_mat_min,
                chieu_rong_nen_max, chieu_rong_nen_min,
                don_vi_bao_duong_id, ghi_chu
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ma_doan, tuyen_id, cap_duong_id,
            ly_trinh_dau, ly_trinh_cuoi, chieu_dai,
            chieu_dai_thuc_te,
            chieu_rong_mat_max, chieu_rong_mat_min,
            chieu_rong_nen_max, chieu_rong_nen_min,
            don_vi_bao_duong_id, ghi_chu
        ))

        conn.commit()
        return cursor.lastrowid

    except sqlite3.IntegrityError:
        raise

    finally:
        conn.close()