from config.database import get_connection
from models.thong_ke import ThongKeCapKyThuat


def _row_to_object(row):
    return ThongKeCapKyThuat(
        ma_cap_quan_ly      = row[0],
        ten_cap_quan_ly     = row[1],
        thu_tu_cap_quan_ly  = row[2],
        ma_cap_ky_thuat     = row[3],
        ten_cap_ky_thuat    = row[4],
        thu_tu_cap_ky_thuat = row[5],
        tong_chieu_dai      = row[6]
    )


def lay_thong_ke_cap_ky_thuat_theo_cap_quan_ly():
    """
    Trả về list[ThongKeCapKyThuat] — tổng chiều dài đoạn tuyến
    theo từng nhóm (cap_quan_ly × cap_duong).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            cql.ma_cap            AS ma_cap_quan_ly,
            cql.ten_cap           AS ten_cap_quan_ly,
            cql.thu_tu_hien_thi   AS thu_tu_cap_quan_ly,
            cd.ma_cap             AS ma_cap_ky_thuat,
            cd.ten_cap            AS ten_cap_ky_thuat,
            cd.thu_tu_hien_thi    AS thu_tu_cap_ky_thuat,
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
    return [_row_to_object(row) for row in rows]