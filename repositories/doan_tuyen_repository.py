from config.database import get_connection
from models.doan_tuyen import DoanTuyen
import sqlite3


# ==========================
# ROW → OBJECT
# ==========================

def _row_to_object(row):
    if not row:
        return None
    # Thứ tự cột SELECT:
    # 0  id
    # 1  ma_doan
    # 2  tuyen_id
    # 3  cap_duong_id
    # 4  ly_trinh_dau
    # 5  ly_trinh_cuoi
    # 6  chieu_dai         (tính toán, bỏ qua)
    # 7  chieu_dai_thuc_te
    # 8  tinh_trang_id
    # 9  chieu_rong_mat_max
    # 10 chieu_rong_mat_min
    # 11 chieu_rong_nen_max
    # 12 chieu_rong_nen_min
    # 13 don_vi_bao_duong_id
    # 14 ghi_chu
    # 15 created_at
    return DoanTuyen(
        id=row[0],
        ma_doan=row[1],
        tuyen_id=row[2],
        cap_duong_id=row[3],
        ly_trinh_dau=row[4],
        ly_trinh_cuoi=row[5],
        chieu_dai_thuc_te=row[7],
        tinh_trang_id=row[8],
        chieu_rong_mat_max=row[9],
        chieu_rong_mat_min=row[10],
        chieu_rong_nen_max=row[11],
        chieu_rong_nen_min=row[12],
        don_vi_bao_duong_id=row[13],
        ghi_chu=row[14],
        created_at=row[15]
    )


_SELECT_COLS = """
    id, ma_doan, tuyen_id, cap_duong_id,
    ly_trinh_dau, ly_trinh_cuoi,
    chieu_dai, chieu_dai_thuc_te, tinh_trang_id,
    chieu_rong_mat_max, chieu_rong_mat_min,
    chieu_rong_nen_max, chieu_rong_nen_min,
    don_vi_bao_duong_id, ghi_chu, created_at
"""


# ==========================
# LẤY TẤT CẢ
# ==========================

def lay_tat_ca():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT {_SELECT_COLS}
        FROM doan_tuyen
        ORDER BY tuyen_id, ly_trinh_dau
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


# ==========================
# LẤY THEO TUYẾN
# ==========================

def lay_theo_tuyen(tuyen_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT {_SELECT_COLS}
        FROM doan_tuyen
        WHERE tuyen_id = ?
        ORDER BY ly_trinh_dau
    """, (tuyen_id,))
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_object(row) for row in rows]


# ==========================
# LẤY THEO MÃ
# ==========================

def lay_theo_ma(ma_doan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT {_SELECT_COLS}
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
    cursor.execute(f"""
        SELECT {_SELECT_COLS}
        FROM doan_tuyen
        WHERE id = ?
    """, (id,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_object(row)


# ==========================
# THÊM
# ==========================

def them_doan_tuyen(
    ma_doan,
    tuyen_id,
    cap_duong_id,
    ly_trinh_dau,
    ly_trinh_cuoi,
    chieu_dai,
    chieu_dai_thuc_te,
    tinh_trang_id,
    chieu_rong_mat_max,
    chieu_rong_mat_min,
    chieu_rong_nen_max,
    chieu_rong_nen_min,
    don_vi_bao_duong_id,
    ghi_chu
):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO doan_tuyen (
                ma_doan, tuyen_id, cap_duong_id,
                ly_trinh_dau, ly_trinh_cuoi,
                chieu_dai, chieu_dai_thuc_te, tinh_trang_id,
                chieu_rong_mat_max, chieu_rong_mat_min,
                chieu_rong_nen_max, chieu_rong_nen_min,
                don_vi_bao_duong_id, ghi_chu
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ma_doan, tuyen_id, cap_duong_id,
            ly_trinh_dau, ly_trinh_cuoi,
            chieu_dai, chieu_dai_thuc_te, tinh_trang_id,
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


# ==========================
# THỐNG KÊ TÌNH TRẠNG THEO TUYẾN
# ==========================

def thong_ke_tinh_trang_tuyen(tuyen_id):
    """
    Trả về list of dict:
    [
        {
            "ma_doan": ...,
            "ly_trinh_dau": ...,
            "ly_trinh_cuoi": ...,
            "chieu_dai_tinh": ...,
            "tinh_trang_id": ...,
            "ma_tinh_trang": ...,
            "ten_tinh_trang": ...,
            "mau_hien_thi": ...
        },
        ...
    ]
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            dt.ma_doan,
            dt.ly_trinh_dau,
            dt.ly_trinh_cuoi,
            COALESCE(dt.chieu_dai_thuc_te, dt.chieu_dai) AS chieu_dai_tinh,
            dt.tinh_trang_id,
            tt.ma   AS ma_tinh_trang,
            tt.ten  AS ten_tinh_trang,
            tt.mau_hien_thi
        FROM doan_tuyen dt
        LEFT JOIN tinh_trang tt ON dt.tinh_trang_id = tt.id
        WHERE dt.tuyen_id = ?
        ORDER BY dt.ly_trinh_dau
    """, (tuyen_id,))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "ma_doan":        row[0],
            "ly_trinh_dau":   row[1],
            "ly_trinh_cuoi":  row[2],
            "chieu_dai_tinh": row[3],
            "tinh_trang_id":  row[4],
            "ma_tinh_trang":  row[5],
            "ten_tinh_trang": row[6],
            "mau_hien_thi":   row[7],
        })
    return result