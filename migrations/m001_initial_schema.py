"""
Migration: 001_initial_schema
Tạo toàn bộ 13 bảng, 6 triggers, 5 indexes cho hệ thống quản lý giao thông Lào Cai.
Idempotent: dùng CREATE TABLE IF NOT EXISTS — chạy nhiều lần không lỗi.
"""

import sqlite3


def up(conn: sqlite3.Connection) -> None:
    """Áp dụng migration: tạo schema đầy đủ."""
    conn.executescript(_SCHEMA_SQL)
    conn.commit()
    print("[migration 001] Schema khởi tạo thành công.")


def down(conn: sqlite3.Connection) -> None:
    """Rollback migration: xóa toàn bộ bảng (ngược thứ tự FK)."""
    tables = [
        "doan_tuyen_geo", "tuyen_duong_geo", "hinh_anh_doan_tuyen",
        "doan_di_chung", "doan_tuyen", "thong_tin_tuyen",
        "tuyen_duong", "nguoi_dung", "don_vi",
        "tinh_trang", "ket_cau_mat_duong", "cap_duong", "cap_quan_ly",
    ]
    for t in tables:
        conn.execute(f"DROP TABLE IF EXISTS {t}")
    conn.commit()
    print("[migration 001] Schema đã bị xóa (rollback).")


# ── SQL Schema ─────────────────────────────────────────────────────────────

_SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

-- 1. cap_quan_ly
CREATE TABLE IF NOT EXISTS cap_quan_ly (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_cap           TEXT    NOT NULL UNIQUE,
    ten_cap          TEXT    NOT NULL,
    mo_ta            TEXT,
    thu_tu_hien_thi  INTEGER,
    is_active        INTEGER NOT NULL DEFAULT 1
);

-- 2. cap_duong
CREATE TABLE IF NOT EXISTS cap_duong (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_cap           TEXT    NOT NULL UNIQUE,
    ten_cap          TEXT    NOT NULL,
    mo_ta            TEXT,
    thu_tu_hien_thi  INTEGER,
    is_active        INTEGER NOT NULL DEFAULT 1
);

-- 3. ket_cau_mat_duong
CREATE TABLE IF NOT EXISTS ket_cau_mat_duong (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_ket_cau       TEXT    NOT NULL UNIQUE,
    ten_ket_cau      TEXT    NOT NULL,
    mo_ta            TEXT,
    thu_tu_hien_thi  INTEGER,
    is_active        INTEGER NOT NULL DEFAULT 1
);

-- 4. tinh_trang
CREATE TABLE IF NOT EXISTS tinh_trang (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_tinh_trang    TEXT    NOT NULL UNIQUE,
    ten_tinh_trang   TEXT    NOT NULL,
    mo_ta            TEXT,
    mau_hien_thi     TEXT,
    thu_tu_hien_thi  INTEGER,
    is_active        INTEGER NOT NULL DEFAULT 1
);

-- 5. don_vi
CREATE TABLE IF NOT EXISTS don_vi (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_don_vi        TEXT    NOT NULL UNIQUE,
    ten_don_vi       TEXT    NOT NULL,
    ten_viet_tat     TEXT,
    parent_id        INTEGER REFERENCES don_vi(id),
    cap_don_vi       TEXT,
    dia_chi          TEXT,
    so_dien_thoai    TEXT,
    email            TEXT,
    is_active        INTEGER NOT NULL DEFAULT 1,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- 6. nguoi_dung
CREATE TABLE IF NOT EXISTS nguoi_dung (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_dang_nhap    TEXT    NOT NULL UNIQUE,
    mat_khau_hash    TEXT    NOT NULL,
    ho_ten           TEXT    NOT NULL,
    chuc_vu          TEXT,
    don_vi_id        INTEGER REFERENCES don_vi(id),
    so_dien_thoai    TEXT,
    email            TEXT    UNIQUE,
    loai_quyen       TEXT    NOT NULL DEFAULT 'XEM',
    is_active        INTEGER NOT NULL DEFAULT 0,
    is_approved      INTEGER NOT NULL DEFAULT 0,
    approved_by_id   INTEGER REFERENCES nguoi_dung(id),
    approved_at      TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    last_login       TEXT
);

-- 7. tuyen_duong
CREATE TABLE IF NOT EXISTS tuyen_duong (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_tuyen             TEXT    NOT NULL UNIQUE,
    ten_tuyen            TEXT    NOT NULL,
    cap_quan_ly_id       INTEGER NOT NULL REFERENCES cap_quan_ly(id),
    don_vi_quan_ly_id    INTEGER NOT NULL REFERENCES don_vi(id),
    diem_dau             TEXT,
    diem_cuoi            TEXT,
    lat_dau              REAL,
    lng_dau              REAL,
    lat_cuoi             REAL,
    lng_cuoi             REAL,
    chieu_dai_thuc_te    REAL    NOT NULL DEFAULT 0,
    chieu_dai_quan_ly    REAL    NOT NULL DEFAULT 0,
    nam_xay_dung         INTEGER,
    nam_hoan_thanh       INTEGER,
    ghi_chu              TEXT,
    created_at           TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- 8. thong_tin_tuyen
CREATE TABLE IF NOT EXISTS thong_tin_tuyen (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    tuyen_id            INTEGER NOT NULL UNIQUE REFERENCES tuyen_duong(id),
    mo_ta               TEXT,
    ly_do_xay_dung      TEXT,
    dac_diem_dia_ly     TEXT,
    lich_su_hinh_thanh  TEXT,
    y_nghia_kinh_te     TEXT,
    ghi_chu             TEXT,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    updated_at          TEXT
);

-- 9. doan_tuyen
CREATE TABLE IF NOT EXISTS doan_tuyen (
    id                        INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_doan                   TEXT    NOT NULL UNIQUE,
    tuyen_id                  INTEGER NOT NULL REFERENCES tuyen_duong(id),
    cap_duong_id              INTEGER REFERENCES cap_duong(id),
    tinh_trang_id             INTEGER REFERENCES tinh_trang(id),
    ket_cau_mat_id            INTEGER REFERENCES ket_cau_mat_duong(id),
    ly_trinh_dau              REAL    NOT NULL,
    ly_trinh_cuoi             REAL    NOT NULL,
    chieu_dai_thuc_te         REAL,
    chieu_rong_mat_min        REAL,
    chieu_rong_mat_max        REAL,
    chieu_rong_nen_min        REAL,
    chieu_rong_nen_max        REAL,
    don_vi_bao_duong_id       INTEGER REFERENCES don_vi(id),
    nam_lam_moi               INTEGER,
    ngay_cap_nhat_tinh_trang  TEXT,
    ghi_chu                   TEXT,
    created_at                TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    updated_at                TEXT,
    updated_by_id             INTEGER REFERENCES nguoi_dung(id)
);

-- 10. doan_di_chung
CREATE TABLE IF NOT EXISTS doan_di_chung (
    id                         INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_doan_di_chung           TEXT    NOT NULL UNIQUE,
    tuyen_di_chung_id          INTEGER NOT NULL REFERENCES tuyen_duong(id),
    tuyen_chinh_id             INTEGER NOT NULL REFERENCES tuyen_duong(id),
    doan_id                    INTEGER NOT NULL REFERENCES doan_tuyen(id),
    ly_trinh_dau_di_chung      REAL    NOT NULL,
    ly_trinh_cuoi_di_chung     REAL    NOT NULL,
    ly_trinh_dau_tuyen_chinh   REAL    NOT NULL,
    ly_trinh_cuoi_tuyen_chinh  REAL    NOT NULL,
    ghi_chu                    TEXT,
    created_at                 TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
    -- Bỏ UNIQUE(tuyen_di_chung_id, doan_id): thực tế DT159 đi nhờ QL4-04 ở 2 đoạn
    -- lý trình khác nhau → một tuyến có thể qua cùng đoạn vật lý nhiều lần
    -- Chỉ giữ UNIQUE trên ma_doan_di_chung
);

-- 11. hinh_anh_doan_tuyen
CREATE TABLE IF NOT EXISTS hinh_anh_doan_tuyen (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    doan_id         INTEGER NOT NULL REFERENCES doan_tuyen(id),
    duong_dan_file  TEXT    NOT NULL,
    mo_ta           TEXT,
    ngay_chup       TEXT,
    nguoi_chup      TEXT,
    lat             REAL,
    lng             REAL,
    ly_trinh_anh    REAL,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- 12. tuyen_duong_geo  (Giai đoạn 1 GeoJSON)
CREATE TABLE IF NOT EXISTS tuyen_duong_geo (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    tuyen_id       INTEGER NOT NULL UNIQUE REFERENCES tuyen_duong(id),
    coordinates    TEXT    NOT NULL,
    so_diem        INTEGER,
    chieu_dai_gps  REAL,
    nguon          TEXT,
    updated_at     TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- 13. doan_tuyen_geo  (Giai đoạn 2 — tạo sẵn, chưa dùng)
CREATE TABLE IF NOT EXISTS doan_tuyen_geo (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    doan_id        INTEGER NOT NULL UNIQUE REFERENCES doan_tuyen(id),
    coordinates    TEXT    NOT NULL,
    so_diem        INTEGER,
    chieu_dai_gps  REAL,
    nguon          TEXT,
    updated_at     TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- ── Triggers: cập nhật chiều dài tuyến ────────────────────────────────────

CREATE TRIGGER IF NOT EXISTS trg_doan_tuyen_sau_them
AFTER INSERT ON doan_tuyen
BEGIN
    UPDATE tuyen_duong SET
        chieu_dai_quan_ly = (
            SELECT ROUND(COALESCE(SUM(COALESCE(chieu_dai_thuc_te, ly_trinh_cuoi - ly_trinh_dau)), 0), 3)
            FROM doan_tuyen WHERE tuyen_id = NEW.tuyen_id
        ),
        chieu_dai_thuc_te = (
            SELECT ROUND(COALESCE(SUM(COALESCE(chieu_dai_thuc_te, ly_trinh_cuoi - ly_trinh_dau)), 0), 3)
            FROM doan_tuyen WHERE tuyen_id = NEW.tuyen_id
        ) + (
            SELECT ROUND(COALESCE(SUM(ly_trinh_cuoi_di_chung - ly_trinh_dau_di_chung), 0), 3)
            FROM doan_di_chung WHERE tuyen_di_chung_id = NEW.tuyen_id
        )
    WHERE id = NEW.tuyen_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_doan_tuyen_sau_sua
AFTER UPDATE ON doan_tuyen
BEGIN
    UPDATE tuyen_duong SET
        chieu_dai_quan_ly = (
            SELECT ROUND(COALESCE(SUM(COALESCE(chieu_dai_thuc_te, ly_trinh_cuoi - ly_trinh_dau)), 0), 3)
            FROM doan_tuyen WHERE tuyen_id = NEW.tuyen_id
        ),
        chieu_dai_thuc_te = (
            SELECT ROUND(COALESCE(SUM(COALESCE(chieu_dai_thuc_te, ly_trinh_cuoi - ly_trinh_dau)), 0), 3)
            FROM doan_tuyen WHERE tuyen_id = NEW.tuyen_id
        ) + (
            SELECT ROUND(COALESCE(SUM(ly_trinh_cuoi_di_chung - ly_trinh_dau_di_chung), 0), 3)
            FROM doan_di_chung WHERE tuyen_di_chung_id = NEW.tuyen_id
        )
    WHERE id = NEW.tuyen_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_doan_tuyen_sau_xoa
AFTER DELETE ON doan_tuyen
BEGIN
    UPDATE tuyen_duong SET
        chieu_dai_quan_ly = (
            SELECT ROUND(COALESCE(SUM(COALESCE(chieu_dai_thuc_te, ly_trinh_cuoi - ly_trinh_dau)), 0), 3)
            FROM doan_tuyen WHERE tuyen_id = OLD.tuyen_id
        ),
        chieu_dai_thuc_te = (
            SELECT ROUND(COALESCE(SUM(COALESCE(chieu_dai_thuc_te, ly_trinh_cuoi - ly_trinh_dau)), 0), 3)
            FROM doan_tuyen WHERE tuyen_id = OLD.tuyen_id
        ) + (
            SELECT ROUND(COALESCE(SUM(ly_trinh_cuoi_di_chung - ly_trinh_dau_di_chung), 0), 3)
            FROM doan_di_chung WHERE tuyen_di_chung_id = OLD.tuyen_id
        )
    WHERE id = OLD.tuyen_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_ddc_sau_them
AFTER INSERT ON doan_di_chung
BEGIN
    UPDATE tuyen_duong SET
        chieu_dai_thuc_te = chieu_dai_quan_ly + (
            SELECT ROUND(COALESCE(SUM(ly_trinh_cuoi_di_chung - ly_trinh_dau_di_chung), 0), 3)
            FROM doan_di_chung WHERE tuyen_di_chung_id = NEW.tuyen_di_chung_id
        )
    WHERE id = NEW.tuyen_di_chung_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_ddc_sau_sua
AFTER UPDATE ON doan_di_chung
BEGIN
    UPDATE tuyen_duong SET
        chieu_dai_thuc_te = chieu_dai_quan_ly + (
            SELECT ROUND(COALESCE(SUM(ly_trinh_cuoi_di_chung - ly_trinh_dau_di_chung), 0), 3)
            FROM doan_di_chung WHERE tuyen_di_chung_id = NEW.tuyen_di_chung_id
        )
    WHERE id = NEW.tuyen_di_chung_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_ddc_sau_xoa
AFTER DELETE ON doan_di_chung
BEGIN
    UPDATE tuyen_duong SET
        chieu_dai_thuc_te = chieu_dai_quan_ly + (
            SELECT ROUND(COALESCE(SUM(ly_trinh_cuoi_di_chung - ly_trinh_dau_di_chung), 0), 3)
            FROM doan_di_chung WHERE tuyen_di_chung_id = OLD.tuyen_di_chung_id
        )
    WHERE id = OLD.tuyen_di_chung_id;
END;

-- ── Indexes ────────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_doan_tuyen_tuyen_id       ON doan_tuyen(tuyen_id);
CREATE INDEX IF NOT EXISTS idx_doan_tuyen_cap_duong_id   ON doan_tuyen(cap_duong_id);
CREATE INDEX IF NOT EXISTS idx_doan_tuyen_tinh_trang_id  ON doan_tuyen(tinh_trang_id);
CREATE INDEX IF NOT EXISTS idx_ddc_tuyen_di_chung_id     ON doan_di_chung(tuyen_di_chung_id);
CREATE INDEX IF NOT EXISTS idx_ddc_doan_id               ON doan_di_chung(doan_id);
"""
