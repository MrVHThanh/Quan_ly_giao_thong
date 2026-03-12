from config.database import get_connection
from models.thong_ke import (
    ThongKeCapKyThuat,
    ThongKeCapKyThuatTheoTuyen,
    ChiTietDoanTheoTuyen
)


def _row_to_thong_ke(row):
    return ThongKeCapKyThuat(
        ma_cap_quan_ly      = row[0],
        ten_cap_quan_ly     = row[1],
        thu_tu_cap_quan_ly  = row[2],
        ma_cap_ky_thuat     = row[3],
        ten_cap_ky_thuat    = row[4],
        thu_tu_cap_ky_thuat = row[5],
        tong_chieu_dai      = row[6]
    )


# ==========================
# THONG KE TONG HOP
# cap_quan_ly x cap_duong
# ==========================

def lay_thong_ke_cap_ky_thuat_theo_cap_quan_ly():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            cql.ma_cap, cql.ten_cap, cql.thu_tu_hien_thi,
            cd.ma_cap,  cd.ten_cap,  cd.thu_tu_hien_thi,
            COALESCE(
                SUM(COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)),
                0
            ) AS tong_chieu_dai
        FROM doan_tuyen dt
        JOIN tuyen_duong  td  ON td.id  = dt.tuyen_id
        JOIN cap_quan_ly  cql ON cql.id = td.cap_quan_ly_id
        JOIN cap_duong    cd  ON cd.id  = dt.cap_duong_id
        GROUP BY cql.id, cd.id
        ORDER BY cql.thu_tu_hien_thi, cd.thu_tu_hien_thi
    """)
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_thong_ke(row) for row in rows]


# ==========================
# THONG KE THEO TUNG TUYEN
# tuyen_id x cap_duong
# ==========================

def lay_thong_ke_cap_ky_thuat_theo_tung_tuyen():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            dt.tuyen_id,
            cd.ma_cap, cd.ten_cap, cd.thu_tu_hien_thi,
            COALESCE(
                SUM(COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)),
                0
            ) AS tong_chieu_dai
        FROM doan_tuyen dt
        JOIN cap_duong cd ON cd.id = dt.cap_duong_id
        GROUP BY dt.tuyen_id, cd.id
        ORDER BY dt.tuyen_id, cd.thu_tu_hien_thi
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        ThongKeCapKyThuatTheoTuyen(
            tuyen_id            = row[0],
            ma_cap_ky_thuat     = row[1],
            ten_cap_ky_thuat    = row[2],
            thu_tu_cap_ky_thuat = row[3],
            tong_chieu_dai      = row[4]
        )
        for row in rows
    ]


# ==========================
# CHI TIET DOAN THEO TUNG TUYEN
# Tinh trang lay tu doan_tuyen.tinh_trang_id (chinh xac nhat)
# ==========================

def lay_chi_tiet_doan_theo_tung_tuyen():
    conn = get_connection()
    cursor = conn.cursor()

    # --- Doan chinh ---
    # Tinh trang lay tu doan_tuyen.tinh_trang_id
    cursor.execute("""
        SELECT
            dt.tuyen_id,
            dt.ma_doan,
            dt.ly_trinh_dau,
            dt.ly_trinh_cuoi,
            COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau) AS chieu_dai,
            cd.ten_cap AS ten_cap_ky_thuat,
            tt.ten     AS ten_tinh_trang,
            'CHINH'    AS loai
        FROM doan_tuyen dt
        JOIN cap_duong   cd ON cd.id = dt.cap_duong_id
        LEFT JOIN tinh_trang tt ON tt.id = dt.tinh_trang_id
        ORDER BY dt.tuyen_id, dt.ly_trinh_dau
    """)
    rows_chinh = cursor.fetchall()

    # --- Doan di chung ---
    # Doan vat ly thuoc tuyen chu, lay tinh_trang cua doan vat ly do (dt.tinh_trang_id)
    cursor.execute("""
        SELECT
            ddc.tuyen_id,
            dt.ma_doan,
            ddc.ly_trinh_dau,
            ddc.ly_trinh_cuoi,
            (ddc.ly_trinh_cuoi - ddc.ly_trinh_dau) AS chieu_dai,
            cd.ten_cap AS ten_cap_ky_thuat,
            tt.ten     AS ten_tinh_trang,
            'DI CHUNG' AS loai
        FROM doan_di_chung ddc
        JOIN doan_tuyen dt ON dt.id = ddc.doan_id
        JOIN cap_duong  cd ON cd.id = dt.cap_duong_id
        LEFT JOIN tinh_trang tt ON tt.id = dt.tinh_trang_id
        ORDER BY ddc.tuyen_id, ddc.ly_trinh_dau
    """)
    rows_di_chung = cursor.fetchall()

    conn.close()

    def to_obj(row, loai):
        return ChiTietDoanTheoTuyen(
            tuyen_id         = row[0],
            ma_doan          = row[1],
            ly_trinh_dau     = row[2],
            ly_trinh_cuoi    = row[3],
            chieu_dai        = row[4],
            ten_cap_ky_thuat = row[5],
            ten_tinh_trang   = row[6],
            loai             = loai
        )

    result = (
        [to_obj(r, "CHINH")      for r in rows_chinh]
        + [to_obj(r, "DI CHUNG") for r in rows_di_chung]
    )
    result.sort(key=lambda x: (x.tuyen_id, x.ly_trinh_dau))
    return result