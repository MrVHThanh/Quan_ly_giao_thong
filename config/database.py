"""
config/database.py
Hệ thống Quản lý Giao thông Lào Cai — Sở Xây dựng tỉnh Lào Cai

Schema: 13 bảng, 6 triggers tự động, 5 indexes tối ưu
Kết nối: sqlite3.Row — truy cập cột theo tên, không dùng index số

Thứ tự bảng (theo phụ thuộc khóa ngoại):
  1.  cap_quan_ly
  2.  cap_duong
  3.  ket_cau_mat_duong
  4.  tinh_trang
  5.  don_vi
  6.  nguoi_dung
  7.  tuyen_duong
  8.  thong_tin_tuyen
  9.  doan_tuyen
  10. doan_di_chung
  11. hinh_anh_doan_tuyen
  12. tuyen_duong_geo
  13. doan_tuyen_geo  (Giai đoạn 2 — tạo sẵn, chưa dùng)
"""

import sqlite3
import os
from typing import Optional

# ── Đường dẫn mặc định ─────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH_DEFAULT = os.path.join(BASE_DIR, "giao_thong.db")


# ── Kết nối ────────────────────────────────────────────────────────────────

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Trả về kết nối SQLite với các cài đặt chuẩn:
      - row_factory = sqlite3.Row  → truy cập cột theo tên: row["ten_cot"]
      - foreign_keys = ON          → bảo đảm toàn vẹn tham chiếu
      - journal_mode = WAL         → ghi nhanh hơn, tránh lock khi đọc đồng thời
    """
    path = db_path or DB_PATH_DEFAULT
    os.makedirs(os.path.dirname(path), exist_ok=True)

    #conn = sqlite3.connect(path)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


# ══════════════════════════════════════════════════════════════════════════════
# SQL TẠO BẢNG
# ══════════════════════════════════════════════════════════════════════════════

# ── 1. cap_quan_ly ────────────────────────────────────────────────────────────
SQL_CAP_QUAN_LY = """
CREATE TABLE IF NOT EXISTS cap_quan_ly (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_cap            TEXT    NOT NULL UNIQUE,
    ten_cap           TEXT    NOT NULL,
    mo_ta             TEXT,
    thu_tu_hien_thi   INTEGER NOT NULL DEFAULT 99,
    is_active         INTEGER NOT NULL DEFAULT 1,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
# Dữ liệu: CT, QL, DT, NT, DX, TX, CD, DK

# ── 2. cap_duong ──────────────────────────────────────────────────────────────
SQL_CAP_DUONG = """
CREATE TABLE IF NOT EXISTS cap_duong (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_cap            TEXT    NOT NULL UNIQUE,
    ten_cap           TEXT    NOT NULL,
    mo_ta             TEXT,
    thu_tu_hien_thi   INTEGER NOT NULL DEFAULT 99,
    is_active         INTEGER NOT NULL DEFAULT 1,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
# Dữ liệu: I, II, III, IV, V, VI, NO (chưa vào cấp)

# ── 3. ket_cau_mat_duong ──────────────────────────────────────────────────────
SQL_KET_CAU_MAT_DUONG = """
CREATE TABLE IF NOT EXISTS ket_cau_mat_duong (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_ket_cau        TEXT    NOT NULL UNIQUE,
    ten_ket_cau       TEXT    NOT NULL,
    mo_ta             TEXT,
    thu_tu_hien_thi   INTEGER NOT NULL DEFAULT 99,
    is_active         INTEGER NOT NULL DEFAULT 1,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
# Dữ liệu: BTN, BTXM, HH, LN, CP, DAT, BTN+LN, BTXM+LN

# ── 4. tinh_trang ─────────────────────────────────────────────────────────────
SQL_TINH_TRANG = """
CREATE TABLE IF NOT EXISTS tinh_trang (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    ma                TEXT    NOT NULL UNIQUE,
    ten               TEXT    NOT NULL,
    mo_ta             TEXT,
    mau_hien_thi      TEXT,           -- mã màu hex, dùng cho bản đồ/UI
    thu_tu_hien_thi   INTEGER NOT NULL DEFAULT 99,
    is_active         INTEGER NOT NULL DEFAULT 1,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
# Dữ liệu: TOT, TB, KEM, HH_NANG, THI_CONG, BAO_TRI, TAM_DONG, NGUNG, CHUA_XD

# ── 5. don_vi ─────────────────────────────────────────────────────────────────
SQL_DON_VI = """
CREATE TABLE IF NOT EXISTS don_vi (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_don_vi         TEXT    NOT NULL UNIQUE,
    ten_don_vi        TEXT    NOT NULL,
    loai              TEXT,           -- Tinh, Xa, So, Ban, Donvi
    parent_id         INTEGER REFERENCES don_vi(id) ON DELETE SET NULL,
    is_active         INTEGER NOT NULL DEFAULT 1,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
# Cây: TINH(NULL) → XA, SXD → BAN_BT; 13 CT độc lập (parent=NULL)

# ── 6. nguoi_dung ─────────────────────────────────────────────────────────────
SQL_NGUOI_DUNG = """
CREATE TABLE IF NOT EXISTS nguoi_dung (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_dang_nhap     TEXT    NOT NULL UNIQUE,
    mat_khau_hash     TEXT    NOT NULL,   -- bcrypt hash, KHÔNG lưu mật khẩu rõ
    ho_ten            TEXT    NOT NULL,
    chuc_vu           TEXT,
    don_vi_id         INTEGER REFERENCES don_vi(id) ON DELETE SET NULL,
    so_dien_thoai     TEXT,
    email             TEXT    UNIQUE,
    loai_quyen        TEXT    NOT NULL DEFAULT 'XEM'
                              CHECK(loai_quyen IN ('ADMIN','BIEN_TAP','XEM')),
    is_active         INTEGER NOT NULL DEFAULT 0,   -- 0 = chờ duyệt
    is_approved       INTEGER NOT NULL DEFAULT 0,
    approved_by_id    INTEGER REFERENCES nguoi_dung(id) ON DELETE SET NULL,
    approved_at       TIMESTAMP,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login        TIMESTAMP
);
"""

# ── 7. tuyen_duong ────────────────────────────────────────────────────────────
SQL_TUYEN_DUONG = """
CREATE TABLE IF NOT EXISTS tuyen_duong (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_tuyen              TEXT    NOT NULL UNIQUE,
    ten_tuyen             TEXT    NOT NULL,
    cap_quan_ly_id        INTEGER NOT NULL REFERENCES cap_quan_ly(id),
    don_vi_quan_ly_id     INTEGER REFERENCES don_vi(id) ON DELETE SET NULL,
    diem_dau              TEXT,
    diem_cuoi             TEXT,
    lat_dau               REAL,
    lng_dau               REAL,
    lat_cuoi              REAL,
    lng_cuoi              REAL,
    chieu_dai_thuc_te     REAL DEFAULT 0,
    chieu_dai_quan_ly     REAL DEFAULT 0,
    nam_xay_dung          INTEGER,
    nam_hoan_thanh        INTEGER,
    ghi_chu               TEXT,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
# KHÔNG CÓ cột chieu_dai — đã bỏ theo quyết định thiết kế

# ── 8. thong_tin_tuyen ────────────────────────────────────────────────────────
SQL_THONG_TIN_TUYEN = """
CREATE TABLE IF NOT EXISTS thong_tin_tuyen (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    tuyen_id      INTEGER NOT NULL UNIQUE REFERENCES tuyen_duong(id) ON DELETE CASCADE,
    noi_dung      TEXT    NOT NULL,   -- văn bản mô tả đầy đủ (hướng tuyến, địa hình, cầu yếu...)
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by_id INTEGER REFERENCES nguoi_dung(id) ON DELETE SET NULL
);
"""

# ── 9. doan_tuyen ─────────────────────────────────────────────────────────────
SQL_DOAN_TUYEN = """
CREATE TABLE IF NOT EXISTS doan_tuyen (
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_doan                     TEXT    NOT NULL UNIQUE,
    tuyen_id                    INTEGER NOT NULL REFERENCES tuyen_duong(id),
    cap_duong_id                INTEGER REFERENCES cap_duong(id) ON DELETE SET NULL,
    tinh_trang_id               INTEGER REFERENCES tinh_trang(id) ON DELETE SET NULL,
    ket_cau_mat_id              INTEGER REFERENCES ket_cau_mat_duong(id) ON DELETE SET NULL,
    ly_trinh_dau                REAL    NOT NULL,
    ly_trinh_cuoi               REAL    NOT NULL,
    chieu_dai_thuc_te           REAL,
    chieu_rong_mat_min          REAL,
    chieu_rong_mat_max          REAL,
    chieu_rong_nen_min          REAL,
    chieu_rong_nen_max          REAL,
    don_vi_bao_duong_id         INTEGER REFERENCES don_vi(id) ON DELETE SET NULL,
    nam_lam_moi                 INTEGER,        -- năm sửa chữa/nâng cấp gần nhất
    ngay_cap_nhat_tinh_trang    DATE,           -- ngày khảo sát tình trạng gần nhất
    ghi_chu                     TEXT,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by_id               INTEGER REFERENCES nguoi_dung(id) ON DELETE SET NULL,
    CHECK (ly_trinh_cuoi > ly_trinh_dau)
);
"""

# ── 10. doan_di_chung ─────────────────────────────────────────────────────────
SQL_DOAN_DI_CHUNG = """
CREATE TABLE IF NOT EXISTS doan_di_chung (
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_doan_di_chung            TEXT    NOT NULL UNIQUE,
    tuyen_di_chung_id           INTEGER NOT NULL REFERENCES tuyen_duong(id),
    tuyen_chinh_id              INTEGER NOT NULL REFERENCES tuyen_duong(id),
    doan_id                     INTEGER NOT NULL REFERENCES doan_tuyen(id),
    ly_trinh_dau_di_chung       REAL    NOT NULL,
    ly_trinh_cuoi_di_chung      REAL    NOT NULL,
    ly_trinh_dau_tuyen_chinh    REAL    NOT NULL,
    ly_trinh_cuoi_tuyen_chinh   REAL    NOT NULL,
    ghi_chu                     TEXT,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (ly_trinh_cuoi_di_chung > ly_trinh_dau_di_chung),
    CHECK (ly_trinh_cuoi_tuyen_chinh > ly_trinh_dau_tuyen_chinh),
    UNIQUE (tuyen_di_chung_id, doan_id)
);
"""
# chieu_dai_di_chung KHÔNG lưu — tính từ ly_trinh_cuoi_di_chung - ly_trinh_dau_di_chung

# ── 11. hinh_anh_doan_tuyen ───────────────────────────────────────────────────
SQL_HINH_ANH_DOAN_TUYEN = """
CREATE TABLE IF NOT EXISTS hinh_anh_doan_tuyen (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    doan_id         INTEGER NOT NULL REFERENCES doan_tuyen(id) ON DELETE CASCADE,
    duong_dan_file  TEXT    NOT NULL,   -- VD: uploads/doan/QL4E-04_001.jpg
    mo_ta           TEXT,              -- VD: "Km18+300 nhìn về hướng Bắc"
    ngay_chup       DATE,
    nguoi_chup      TEXT,
    lat             REAL,              -- tọa độ trích từ EXIF GPS (NULL nếu không có)
    lng             REAL,              -- tọa độ trích từ EXIF GPS (NULL nếu không có)
    ly_trinh_anh    REAL,              -- tính từ lat/lng + đường tâm tuyến (Giai đoạn 2)
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# ── 12. tuyen_duong_geo ───────────────────────────────────────────────────────
SQL_TUYEN_DUONG_GEO = """
CREATE TABLE IF NOT EXISTS tuyen_duong_geo (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tuyen_id        INTEGER NOT NULL UNIQUE REFERENCES tuyen_duong(id) ON DELETE CASCADE,
    coordinates     TEXT    NOT NULL,
    so_diem         INTEGER,           -- số điểm tọa độ
    chieu_dai_gps   REAL,              -- chiều dài tính từ GPS bằng Haversine (km)
    nguon           TEXT DEFAULT 'geojson_import',
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
# Giai đoạn 1: lưu toàn bộ tọa độ tuyến
# Import: tools/import_geojson.py | Export: tools/export_geojson.py

# ── 13. doan_tuyen_geo ────────────────────────────────────────────────────────
SQL_DOAN_TUYEN_GEO = """
CREATE TABLE IF NOT EXISTS doan_tuyen_geo (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    doan_id         INTEGER NOT NULL UNIQUE REFERENCES doan_tuyen(id) ON DELETE CASCADE,
    coordinates     TEXT    NOT NULL,
    so_diem         INTEGER,
    chieu_dai_gps   REAL,              -- chiều dài GPS (km)
    nguon           TEXT DEFAULT 'cat_tu_tuyen',
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
# Giai đoạn 2 — tạo sẵn, chưa dùng
# Sẽ dùng khi cần hiển thị màu sắc từng đoạn theo tình trạng/cấp trên bản đồ


# ── 15. dang_nhap_log ────────────────────────────────────────────────────────
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

# ── 16. nhat_ky_hoat_dong ─────────────────────────────────────────────────────
SQL_NHAT_KY_HOAT_DONG = """
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


# ══════════════════════════════════════════════════════════════════════════════
# INDEXES
# ══════════════════════════════════════════════════════════════════════════════

SQL_INDEXES = """
-- Tăng tốc JOIN tuyến → đoạn (dùng rất nhiều)
CREATE INDEX IF NOT EXISTS idx_doan_tuyen_tuyen_id
    ON doan_tuyen(tuyen_id);

-- Tăng tốc thống kê theo cấp kỹ thuật
CREATE INDEX IF NOT EXISTS idx_doan_tuyen_cap_duong_id
    ON doan_tuyen(cap_duong_id);

-- Tăng tốc lọc/thống kê theo tình trạng mặt đường
CREATE INDEX IF NOT EXISTS idx_doan_tuyen_tinh_trang_id
    ON doan_tuyen(tinh_trang_id);

-- Tăng tốc tra đoạn đi chung theo tuyến đi nhờ
CREATE INDEX IF NOT EXISTS idx_ddc_tuyen_di_chung_id
    ON doan_di_chung(tuyen_di_chung_id);

-- Tăng tốc JOIN đoạn vật lý trong đoạn đi chung
CREATE INDEX IF NOT EXISTS idx_ddc_doan_id
    ON doan_di_chung(doan_id);
"""


# ══════════════════════════════════════════════════════════════════════════════
# TRIGGERS — TỰ ĐỘNG CẬP NHẬT CHIỀU DÀI TUYẾN
# ══════════════════════════════════════════════════════════════════════════════
#
# Logic cập nhật:
#   chieu_dai_quan_ly = SUM chiều dài đoạn CHÍNH của tuyến
#   chieu_dai_thuc_te = chieu_dai_quan_ly + SUM chiều dài đoạn ĐI CHUNG
#
# Chiều dài đoạn = COALESCE(chieu_dai_thuc_te, ly_trinh_cuoi - ly_trinh_dau)
# Chiều dài đi chung = ly_trinh_cuoi_di_chung - ly_trinh_dau_di_chung
#
# ══════════════════════════════════════════════════════════════════════════════

# Dùng chung một câu UPDATE cho cả 6 triggers
_SQL_UPDATE_CHIEU_DAI = """
    UPDATE tuyen_duong
    SET
        chieu_dai_quan_ly = (
            SELECT COALESCE(SUM(
                COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)
            ), 0)
            FROM doan_tuyen dt
            WHERE dt.tuyen_id = {tuyen_id_expr}
        ),
        chieu_dai_thuc_te = (
            SELECT COALESCE(SUM(
                COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)
            ), 0)
            FROM doan_tuyen dt
            WHERE dt.tuyen_id = {tuyen_id_expr}
        ) + (
            SELECT COALESCE(SUM(
                ddc.ly_trinh_cuoi_di_chung - ddc.ly_trinh_dau_di_chung
            ), 0)
            FROM doan_di_chung ddc
            WHERE ddc.tuyen_di_chung_id = {tuyen_id_expr}
        )
    WHERE id = {tuyen_id_expr};
"""

# ── Triggers cho doan_tuyen ───────────────────────────────────────────────────

SQL_TRG_DOAN_TUYEN_SAU_THEM = """
CREATE TRIGGER IF NOT EXISTS trg_doan_tuyen_sau_them
AFTER INSERT ON doan_tuyen
BEGIN
    UPDATE tuyen_duong
    SET
        chieu_dai_quan_ly = (
            SELECT COALESCE(SUM(
                COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)
            ), 0)
            FROM doan_tuyen dt
            WHERE dt.tuyen_id = NEW.tuyen_id
        ),
        chieu_dai_thuc_te = (
            SELECT COALESCE(SUM(
                COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)
            ), 0)
            FROM doan_tuyen dt
            WHERE dt.tuyen_id = NEW.tuyen_id
        ) + (
            SELECT COALESCE(SUM(
                ddc.ly_trinh_cuoi_di_chung - ddc.ly_trinh_dau_di_chung
            ), 0)
            FROM doan_di_chung ddc
            WHERE ddc.tuyen_di_chung_id = NEW.tuyen_id
        )
    WHERE id = NEW.tuyen_id;
END;
"""

SQL_TRG_DOAN_TUYEN_SAU_SUA = """
CREATE TRIGGER IF NOT EXISTS trg_doan_tuyen_sau_sua
AFTER UPDATE ON doan_tuyen
BEGIN
    UPDATE tuyen_duong
    SET
        chieu_dai_quan_ly = (
            SELECT COALESCE(SUM(
                COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)
            ), 0)
            FROM doan_tuyen dt
            WHERE dt.tuyen_id = OLD.tuyen_id
        ),
        chieu_dai_thuc_te = (
            SELECT COALESCE(SUM(
                COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)
            ), 0)
            FROM doan_tuyen dt
            WHERE dt.tuyen_id = OLD.tuyen_id
        ) + (
            SELECT COALESCE(SUM(
                ddc.ly_trinh_cuoi_di_chung - ddc.ly_trinh_dau_di_chung
            ), 0)
            FROM doan_di_chung ddc
            WHERE ddc.tuyen_di_chung_id = OLD.tuyen_id
        )
    WHERE id = OLD.tuyen_id;

    UPDATE tuyen_duong
    SET
        chieu_dai_quan_ly = (
            SELECT COALESCE(SUM(
                COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)
            ), 0)
            FROM doan_tuyen dt
            WHERE dt.tuyen_id = NEW.tuyen_id
        ),
        chieu_dai_thuc_te = (
            SELECT COALESCE(SUM(
                COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)
            ), 0)
            FROM doan_tuyen dt
            WHERE dt.tuyen_id = NEW.tuyen_id
        ) + (
            SELECT COALESCE(SUM(
                ddc.ly_trinh_cuoi_di_chung - ddc.ly_trinh_dau_di_chung
            ), 0)
            FROM doan_di_chung ddc
            WHERE ddc.tuyen_di_chung_id = NEW.tuyen_id
        )
    WHERE id = NEW.tuyen_id;
END;
"""

SQL_TRG_DOAN_TUYEN_SAU_XOA = """
CREATE TRIGGER IF NOT EXISTS trg_doan_tuyen_sau_xoa
AFTER DELETE ON doan_tuyen
BEGIN
    UPDATE tuyen_duong
    SET
        chieu_dai_quan_ly = (
            SELECT COALESCE(SUM(
                COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)
            ), 0)
            FROM doan_tuyen dt
            WHERE dt.tuyen_id = OLD.tuyen_id
        ),
        chieu_dai_thuc_te = (
            SELECT COALESCE(SUM(
                COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)
            ), 0)
            FROM doan_tuyen dt
            WHERE dt.tuyen_id = OLD.tuyen_id
        ) + (
            SELECT COALESCE(SUM(
                ddc.ly_trinh_cuoi_di_chung - ddc.ly_trinh_dau_di_chung
            ), 0)
            FROM doan_di_chung ddc
            WHERE ddc.tuyen_di_chung_id = OLD.tuyen_id
        )
    WHERE id = OLD.tuyen_id;
END;
"""

# ── Triggers cho doan_di_chung ────────────────────────────────────────────────

SQL_TRG_DDC_SAU_THEM = """
CREATE TRIGGER IF NOT EXISTS trg_ddc_sau_them
AFTER INSERT ON doan_di_chung
BEGIN
    UPDATE tuyen_duong
    SET chieu_dai_thuc_te = (
        SELECT COALESCE(SUM(
            COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)
        ), 0)
        FROM doan_tuyen dt
        WHERE dt.tuyen_id = NEW.tuyen_di_chung_id
    ) + (
        SELECT COALESCE(SUM(
            ddc.ly_trinh_cuoi_di_chung - ddc.ly_trinh_dau_di_chung
        ), 0)
        FROM doan_di_chung ddc
        WHERE ddc.tuyen_di_chung_id = NEW.tuyen_di_chung_id
    )
    WHERE id = NEW.tuyen_di_chung_id;
END;
"""

SQL_TRG_DDC_SAU_SUA = """
CREATE TRIGGER IF NOT EXISTS trg_ddc_sau_sua
AFTER UPDATE ON doan_di_chung
BEGIN
    UPDATE tuyen_duong
    SET chieu_dai_thuc_te = (
        SELECT COALESCE(SUM(
            COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)
        ), 0)
        FROM doan_tuyen dt
        WHERE dt.tuyen_id = OLD.tuyen_di_chung_id
    ) + (
        SELECT COALESCE(SUM(
            ddc.ly_trinh_cuoi_di_chung - ddc.ly_trinh_dau_di_chung
        ), 0)
        FROM doan_di_chung ddc
        WHERE ddc.tuyen_di_chung_id = OLD.tuyen_di_chung_id
    )
    WHERE id = OLD.tuyen_di_chung_id;

    UPDATE tuyen_duong
    SET chieu_dai_thuc_te = (
        SELECT COALESCE(SUM(
            COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)
        ), 0)
        FROM doan_tuyen dt
        WHERE dt.tuyen_id = NEW.tuyen_di_chung_id
    ) + (
        SELECT COALESCE(SUM(
            ddc.ly_trinh_cuoi_di_chung - ddc.ly_trinh_dau_di_chung
        ), 0)
        FROM doan_di_chung ddc
        WHERE ddc.tuyen_di_chung_id = NEW.tuyen_di_chung_id
    )
    WHERE id = NEW.tuyen_di_chung_id;
END;
"""

SQL_TRG_DDC_SAU_XOA = """
CREATE TRIGGER IF NOT EXISTS trg_ddc_sau_xoa
AFTER DELETE ON doan_di_chung
BEGIN
    UPDATE tuyen_duong
    SET chieu_dai_thuc_te = (
        SELECT COALESCE(SUM(
            COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)
        ), 0)
        FROM doan_tuyen dt
        WHERE dt.tuyen_id = OLD.tuyen_di_chung_id
    ) + (
        SELECT COALESCE(SUM(
            ddc.ly_trinh_cuoi_di_chung - ddc.ly_trinh_dau_di_chung
        ), 0)
        FROM doan_di_chung ddc
        WHERE ddc.tuyen_di_chung_id = OLD.tuyen_di_chung_id
    )
    WHERE id = OLD.tuyen_di_chung_id;
END;
"""


# ══════════════════════════════════════════════════════════════════════════════
# HÀM CHÍNH
# ══════════════════════════════════════════════════════════════════════════════

def create_tables(db_path: Optional[str] = None) -> None:
    """
    Tạo toàn bộ schema: 13 bảng, 6 triggers, 5 indexes.
    An toàn khi chạy nhiều lần — dùng CREATE TABLE IF NOT EXISTS.
    """
    conn = get_connection(db_path)
    try:
        with conn:
            # ── Bảng (theo thứ tự phụ thuộc FK) ──────────────────────────
            conn.execute(SQL_CAP_QUAN_LY)
            conn.execute(SQL_CAP_DUONG)
            conn.execute(SQL_KET_CAU_MAT_DUONG)
            conn.execute(SQL_TINH_TRANG)
            conn.execute(SQL_DON_VI)
            conn.execute(SQL_NGUOI_DUNG)
            conn.execute(SQL_TUYEN_DUONG)
            conn.execute(SQL_THONG_TIN_TUYEN)
            conn.execute(SQL_DOAN_TUYEN)
            conn.execute(SQL_DOAN_DI_CHUNG)
            conn.execute(SQL_HINH_ANH_DOAN_TUYEN)
            conn.execute(SQL_TUYEN_DUONG_GEO)
            conn.execute(SQL_DOAN_TUYEN_GEO)
            conn.execute(SQL_DANG_NHAP_LOG)
            conn.execute(SQL_NHAT_KY_HOAT_DONG)

            # ── Indexes ────────────────────────────────────────────────────
            for sql in SQL_INDEXES.strip().split(";"):
                sql = sql.strip()
                if sql:
                    conn.execute(sql)

            # ── Triggers ───────────────────────────────────────────────────
            conn.execute(SQL_TRG_DOAN_TUYEN_SAU_THEM)
            conn.execute(SQL_TRG_DOAN_TUYEN_SAU_SUA)
            conn.execute(SQL_TRG_DOAN_TUYEN_SAU_XOA)
            conn.execute(SQL_TRG_DDC_SAU_THEM)
            conn.execute(SQL_TRG_DDC_SAU_SUA)
            conn.execute(SQL_TRG_DDC_SAU_XOA)

        print("✅ create_tables(): 13 bảng, 6 triggers, 5 indexes — OK")
    finally:
        conn.close()


def drop_all_tables(db_path: Optional[str] = None) -> None:
    """
    Xóa toàn bộ bảng (theo thứ tự ngược FK).
    CHỈ DÙNG KHI DEVELOPMENT — KHÔNG dùng trên dữ liệu thật.
    """
    tables = [
        "doan_tuyen_geo", "tuyen_duong_geo", "hinh_anh_doan_tuyen",
        "doan_di_chung", "doan_tuyen", "thong_tin_tuyen",
        "tuyen_duong", "nguoi_dung", "don_vi",
        "tinh_trang", "ket_cau_mat_duong", "cap_duong", "cap_quan_ly",
    ]
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("PRAGMA foreign_keys = OFF")
            for t in tables:
                conn.execute(f"DROP TABLE IF EXISTS {t}")
            conn.execute("PRAGMA foreign_keys = ON")
        print(f"⚠️  drop_all_tables(): đã xóa {len(tables)} bảng")
    finally:
        conn.close()


def get_schema_info(db_path: Optional[str] = None) -> dict:
    """
    Trả về thông tin schema hiện tại:
      { 'tables': [...], 'indexes': [...], 'triggers': [...] }
    """
    conn = get_connection(db_path)
    try:
        tables = [
            r["name"] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
        ]
        indexes = [
            r["name"] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' ORDER BY name"
            )
        ]
        triggers = [
            r["name"] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name"
            )
        ]
        return {"tables": tables, "indexes": indexes, "triggers": triggers}
    finally:
        conn.close()



def get_db(db_path: str = DB_PATH_DEFAULT):
    """Generator dùng cho FastAPI Depends."""
    conn = get_connection(db_path)
    try:
        yield conn
    finally:
        conn.close()

# ══════════════════════════════════════════════════════════════════════════════
# CHẠY TRỰC TIẾP ĐỂ TEST
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    test_db = os.path.join(BASE_DIR, "database", "giao_thong_test.db")

    if "--reset" in sys.argv:
        drop_all_tables(test_db)

    create_tables(test_db)

    info = get_schema_info(test_db)
    print(f"\n📋 Schema hiện tại:")
    print(f"   Bảng    ({len(info['tables']):2d}): {', '.join(info['tables'])}")
    print(f"   Indexes ({len(info['indexes']):2d}): {', '.join(info['indexes'])}")
    print(f"   Triggers({len(info['triggers']):2d}): {', '.join(info['triggers'])}")

    # Kiểm tra nhanh triggers hoạt động
    print("\n🧪 Test trigger tự động cập nhật chiều dài...")
    conn = get_connection(test_db)
    try:
        with conn:
            # Thêm dữ liệu test tối thiểu
            conn.execute("INSERT OR IGNORE INTO cap_quan_ly(ma_cap,ten_cap,thu_tu_hien_thi) VALUES('QL','Quốc lộ',1)")
            conn.execute("INSERT OR IGNORE INTO tuyen_duong(ma_tuyen,ten_tuyen,cap_quan_ly_id) VALUES('QL_TEST','Test',1)")
            tuyen_id = conn.execute("SELECT id FROM tuyen_duong WHERE ma_tuyen='QL_TEST'").fetchone()["id"]
            conn.execute("""
                INSERT OR IGNORE INTO doan_tuyen(ma_doan,tuyen_id,ly_trinh_dau,ly_trinh_cuoi,chieu_dai_thuc_te)
                VALUES('DT_TEST_01',?,10,25,15.5)
            """, (tuyen_id,))

        row = conn.execute(
            "SELECT chieu_dai_quan_ly, chieu_dai_thuc_te FROM tuyen_duong WHERE id=?",
            (tuyen_id,)
        ).fetchone()

        cdql = row["chieu_dai_quan_ly"]
        cdtt = row["chieu_dai_thuc_te"]
        ok = abs(cdql - 15.5) < 0.001 and abs(cdtt - 15.5) < 0.001

        print(f"   chieu_dai_quan_ly = {cdql} (kỳ vọng 15.5) {'✅' if ok else '❌'}")
        print(f"   chieu_dai_thuc_te = {cdtt} (kỳ vọng 15.5) {'✅' if ok else '❌'}")

        # Dọn dữ liệu test
        with conn:
            conn.execute("DELETE FROM doan_tuyen WHERE ma_doan='DT_TEST_01'")
            conn.execute("DELETE FROM tuyen_duong WHERE ma_tuyen='QL_TEST'")
            conn.execute("DELETE FROM cap_quan_ly WHERE ma_cap='QL'")
    finally:
        conn.close()

    print("\n✅ Bước 2 hoàn thành. Sẵn sàng cho Bước 3 (Models).")
