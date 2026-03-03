import sqlite3
import os

# =========================
# CẤU HÌNH DATABASE
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FOLDER = os.path.join(BASE_DIR, "database")
DB_NAME = "giao_thong.db"
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_tables():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

    conn = get_connection()
    cursor = conn.cursor()

    # =========================
    # CAP_QUAN_LY
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cap_quan_ly (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_cap TEXT NOT NULL UNIQUE,
        ten_cap TEXT NOT NULL,
        mo_ta TEXT,
        thu_tu_hien_thi INTEGER,
        is_active INTEGER DEFAULT 1
    )
    """)

    # =========================
    # CAP_DUONG
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cap_duong (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_cap TEXT NOT NULL UNIQUE,
        ten_cap TEXT NOT NULL,
        mo_ta TEXT,
        thu_tu_hien_thi INTEGER,
        is_active INTEGER DEFAULT 1
    )
    """)

    # =========================
    # DON_VI
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS don_vi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_don_vi TEXT UNIQUE NOT NULL,
        ten_don_vi TEXT NOT NULL,
        loai TEXT,
        parent_id INTEGER,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_id) REFERENCES don_vi(id)
    )
    """)

    # =========================
    # TINH_TRANG
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tinh_trang (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ma TEXT NOT NULL UNIQUE,
        ten TEXT NOT NULL,
        mo_ta TEXT,
        mau_hien_thi TEXT,
        thu_tu_hien_thi INTEGER,
        is_active INTEGER DEFAULT 1
    )
    """)

    # =========================
    # TUYEN_DUONG
    #   - chieu_dai_quan_ly : tổng đoạn chính (doan_tuyen)
    #   - chieu_dai_thuc_te : tổng quãng đường (kể cả đoạn đi chung)
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tuyen_duong (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_tuyen TEXT NOT NULL UNIQUE,
        ten_tuyen TEXT NOT NULL,
        cap_quan_ly_id INTEGER,
        don_vi_quan_ly_id INTEGER,
        diem_dau TEXT,
        diem_cuoi TEXT,
        lat_dau REAL,
        lng_dau REAL,
        lat_cuoi REAL,
        lng_cuoi REAL,
        chieu_dai_thuc_te REAL,
        chieu_dai_quan_ly REAL,
        nam_xay_dung INTEGER,
        nam_hoan_thanh INTEGER,
        tinh_trang_id INTEGER,
        ghi_chu TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cap_quan_ly_id) REFERENCES cap_quan_ly(id),
        FOREIGN KEY (don_vi_quan_ly_id) REFERENCES don_vi(id),
        FOREIGN KEY (tinh_trang_id) REFERENCES tinh_trang(id)
    )
    """)

    # =========================
    # DOAN_TUYEN
    # Đoạn vật lý — luôn thuộc một tuyến chủ sở hữu
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doan_tuyen (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_doan TEXT NOT NULL UNIQUE,
        tuyen_id INTEGER NOT NULL,
        cap_duong_id INTEGER NOT NULL,
        ly_trinh_dau REAL NOT NULL,
        ly_trinh_cuoi REAL NOT NULL,
        chieu_dai REAL,
        chieu_dai_thuc_te REAL,
        chieu_rong_mat_max REAL,
        chieu_rong_mat_min REAL,
        chieu_rong_nen_max REAL,
        chieu_rong_nen_min REAL,
        don_vi_bao_duong_id INTEGER,
        ghi_chu TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tuyen_id) REFERENCES tuyen_duong(id),
        FOREIGN KEY (cap_duong_id) REFERENCES cap_duong(id),
        FOREIGN KEY (don_vi_bao_duong_id) REFERENCES don_vi(id)
    )
    """)

    # =========================
    # DOAN_DI_CHUNG
    # Đoạn vật lý thuộc tuyến khác, nhưng được tuyến này đi chung.
    # Lý trình là lý trình theo tuyến ĐI CHUNG (không phải tuyến chủ).
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doan_di_chung (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tuyen_id INTEGER NOT NULL,
        doan_id INTEGER NOT NULL,
        ly_trinh_dau REAL NOT NULL,
        ly_trinh_cuoi REAL NOT NULL,
        ghi_chu TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tuyen_id) REFERENCES tuyen_duong(id),
        FOREIGN KEY (doan_id) REFERENCES doan_tuyen(id),
        UNIQUE (tuyen_id, doan_id)
    )
    """)

    conn.commit()
    conn.close()

    print("Database created!!!")