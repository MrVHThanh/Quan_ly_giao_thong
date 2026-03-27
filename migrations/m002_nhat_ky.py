"""
Migration m002: Tạo bảng nhật ký đăng nhập và hoạt động.
Idempotent: dùng CREATE TABLE IF NOT EXISTS — chạy nhiều lần không lỗi.
"""

SQL_DANG_NHAP_LOG = """
CREATE TABLE IF NOT EXISTS dang_nhap_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_dang_nhap   TEXT    NOT NULL,
    nguoi_dung_id   INTEGER REFERENCES nguoi_dung(id),
    ip_address      TEXT,
    vi_tri          TEXT,
    user_agent      TEXT,
    thanh_cong      INTEGER NOT NULL DEFAULT 0,
    ghi_chu         TEXT,
    thoi_gian       TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);
"""

SQL_NHAT_KY = """
CREATE TABLE IF NOT EXISTS nhat_ky_hoat_dong (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nguoi_dung_id   INTEGER REFERENCES nguoi_dung(id),
    ho_ten          TEXT,
    hanh_dong       TEXT    NOT NULL,
    doi_tuong       TEXT,
    doi_tuong_id    INTEGER,
    mo_ta           TEXT,
    ip_address      TEXT,
    thoi_gian       TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);
"""

SQL_INDEX_DANG_NHAP = """
CREATE INDEX IF NOT EXISTS idx_dang_nhap_log_thoi_gian
    ON dang_nhap_log(thoi_gian DESC);
"""

SQL_INDEX_NHAT_KY = """
CREATE INDEX IF NOT EXISTS idx_nhat_ky_thoi_gian
    ON nhat_ky_hoat_dong(thoi_gian DESC);
"""


def up(conn):
    conn.executescript(
        SQL_DANG_NHAP_LOG +
        SQL_NHAT_KY +
        SQL_INDEX_DANG_NHAP +
        SQL_INDEX_NHAT_KY
    )
    conn.commit()
