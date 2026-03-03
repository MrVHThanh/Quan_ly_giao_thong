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


# ================= THỐNG KÊ THEO CẤP QUẢN LÝ =================
def thong_ke_theo_cap_quan_ly(ds_ma_cap: list):
    """
    Thống kê tuyến đường theo một hoặc nhiều mã cấp quản lý.

    Args:
        ds_ma_cap: list mã cấp, ví dụ ["QL"] hoặc ["QL", "DT"]

    Returns:
        list[dict] - mỗi phần tử gồm:
            ma_cap, ten_cap, so_tuyen,
            tong_chieu_dai_quan_ly, tong_chieu_dai_thuc_te,
            ds_tuyen (list TuyenDuong)
    """
    if not ds_ma_cap:
        return []

    conn = get_connection()
    cursor = conn.cursor()
    placeholders = ",".join("?" * len(ds_ma_cap))

    # --- Tổng hợp theo cấp ---
    cursor.execute(f"""
        SELECT
            cql.id,
            cql.ma_cap,
            cql.ten_cap,
            COUNT(t.id)                             AS so_tuyen,
            COALESCE(SUM(t.chieu_dai_quan_ly), 0)   AS tong_quan_ly,
            COALESCE(SUM(t.chieu_dai_thuc_te), 0)   AS tong_thuc_te
        FROM cap_quan_ly cql
        LEFT JOIN tuyen_duong t ON t.cap_quan_ly_id = cql.id
        WHERE cql.ma_cap IN ({placeholders})
          AND cql.is_active = 1
        GROUP BY cql.id, cql.ma_cap, cql.ten_cap
        ORDER BY cql.thu_tu_hien_thi
    """, ds_ma_cap)

    rows_cap = cursor.fetchall()

    # --- Lấy danh sách tuyến chi tiết (dùng t. prefix để tránh ambiguous) ---
    cursor.execute(f"""
        SELECT
            t.id, t.ma_tuyen, t.ten_tuyen,
            t.cap_quan_ly_id, t.don_vi_quan_ly_id,
            t.diem_dau, t.diem_cuoi,
            t.lat_dau, t.lng_dau, t.lat_cuoi, t.lng_cuoi,
            t.chieu_dai, t.chieu_dai_thuc_te, t.chieu_dai_quan_ly,
            t.nam_xay_dung, t.nam_hoan_thanh,
            t.ghi_chu, t.created_at
        FROM tuyen_duong t
        JOIN cap_quan_ly cql ON cql.id = t.cap_quan_ly_id
        WHERE cql.ma_cap IN ({placeholders})
        ORDER BY cql.thu_tu_hien_thi, t.ma_tuyen
    """, ds_ma_cap)

    rows_tuyen = cursor.fetchall()
    conn.close()

    # --- Map tuyen theo cap_quan_ly_id ---
    from collections import defaultdict
    map_tuyen = defaultdict(list)
    for row in rows_tuyen:
        tuyen = _row_to_object(row)
        map_tuyen[tuyen.cap_quan_ly_id].append(tuyen)

    # --- Ghép kết quả ---
    ket_qua = []
    for row in rows_cap:
        cap_id, ma_cap, ten_cap, so_tuyen, tong_quan_ly, tong_thuc_te = row
        ket_qua.append({
            "ma_cap":                   ma_cap,
            "ten_cap":                  ten_cap,
            "so_tuyen":                 so_tuyen,
            "tong_chieu_dai_quan_ly":   round(tong_quan_ly, 2),
            "tong_chieu_dai_thuc_te":   round(tong_thuc_te, 2),
            "ds_tuyen":                 map_tuyen[cap_id]
        })

    return ket_qua