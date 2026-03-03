from config.database import get_connection
from models.tuyen_duong import TuyenDuong
import sqlite3

# Thứ tự cột SELECT:
# 0  id
# 1  ma_tuyen
# 2  ten_tuyen
# 3  cap_quan_ly_id
# 4  don_vi_quan_ly_id
# 5  diem_dau
# 6  diem_cuoi
# 7  lat_dau
# 8  lng_dau
# 9  lat_cuoi
# 10 lng_cuoi
# 11 chieu_dai
# 12 chieu_dai_thuc_te
# 13 chieu_dai_quan_ly
# 14 nam_xay_dung
# 15 nam_hoan_thanh
# 16 ghi_chu
# 17 created_at

_SELECT_COLS = """
    id, ma_tuyen, ten_tuyen,
    cap_quan_ly_id, don_vi_quan_ly_id,
    diem_dau, diem_cuoi,
    lat_dau, lng_dau, lat_cuoi, lng_cuoi,
    chieu_dai, chieu_dai_thuc_te, chieu_dai_quan_ly,
    nam_xay_dung, nam_hoan_thanh,
    ghi_chu, created_at
"""


def _row_to_object(row):
    if not row:
        return None
    return TuyenDuong(
        id=row[0],
        ma_tuyen=row[1],
        ten_tuyen=row[2],
        cap_quan_ly_id=row[3],
        don_vi_quan_ly_id=row[4],
        diem_dau=row[5],
        diem_cuoi=row[6],
        lat_dau=row[7],
        lng_dau=row[8],
        lat_cuoi=row[9],
        lng_cuoi=row[10],
        chieu_dai=row[11],
        chieu_dai_thuc_te=row[12],
        chieu_dai_quan_ly=row[13],
        nam_xay_dung=row[14],
        nam_hoan_thanh=row[15],
        ghi_chu=row[16],
        created_at=row[17]
    )


# ================= LẤY TẤT CẢ =================
def lay_tat_ca():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {_SELECT_COLS} FROM tuyen_duong ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_object(row) for row in rows]


# ================= LẤY THEO MÃ =================
def lay_theo_ma(ma_tuyen):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {_SELECT_COLS} FROM tuyen_duong WHERE ma_tuyen = ?", (ma_tuyen,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_object(row)


# ================= LẤY THEO ID =================
def lay_theo_id(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {_SELECT_COLS} FROM tuyen_duong WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    return _row_to_object(row)


# ================= THÊM =================
def them_tuyen_duong(tuyen: TuyenDuong):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO tuyen_duong (
                ma_tuyen, ten_tuyen,
                cap_quan_ly_id, don_vi_quan_ly_id,
                diem_dau, diem_cuoi,
                lat_dau, lng_dau, lat_cuoi, lng_cuoi,
                chieu_dai, chieu_dai_thuc_te, chieu_dai_quan_ly,
                nam_xay_dung, nam_hoan_thanh,
                ghi_chu
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tuyen.ma_tuyen,
            tuyen.ten_tuyen,
            tuyen.cap_quan_ly_id,
            tuyen.don_vi_quan_ly_id,
            tuyen.diem_dau,
            tuyen.diem_cuoi,
            tuyen.lat_dau,
            tuyen.lng_dau,
            tuyen.lat_cuoi,
            tuyen.lng_cuoi,
            tuyen.chieu_dai,
            tuyen.chieu_dai_thuc_te,
            tuyen.chieu_dai_quan_ly,
            tuyen.nam_xay_dung,
            tuyen.nam_hoan_thanh,
            tuyen.ghi_chu
        ))
        conn.commit()
        tuyen.id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Ma tuyen '{tuyen.ma_tuyen}' da ton tai!")
    finally:
        conn.close()
    return tuyen


# ================= CẬP NHẬT CHIỀU DÀI =================
def cap_nhat_chieu_dai_tuyen(tuyen_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(COALESCE(chieu_dai_thuc_te, chieu_dai))
        FROM doan_tuyen
        WHERE tuyen_id = ?
    """, (tuyen_id,))
    result = cursor.fetchone()
    tong_chieu_dai = result[0] if result[0] else 0
    cursor.execute("""
        UPDATE tuyen_duong SET chieu_dai = ? WHERE id = ?
    """, (tong_chieu_dai, tuyen_id))
    conn.commit()
    conn.close()