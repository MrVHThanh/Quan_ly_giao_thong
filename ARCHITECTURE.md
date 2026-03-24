# ARCHITECTURE.md — Kiến trúc kỹ thuật hệ thống Quản lý Đường bộ Lào Cai

> Tài liệu mô tả kiến trúc kỹ thuật đầy đủ. Đọc `CLAUDE.md` để biết các quy tắc code.
> Xem `PROJECT_MAP.md` để tìm file cụ thể.

---

## 1. TỔNG QUAN KIẾN TRÚC

### Mô hình 4 tầng

```
┌────────────────────────────────────────────────────────────────┐
│                     WEB LAYER (FastAPI)                        │
│  api/main.py · api/routes/ · templates/ · static/              │
│  HTTP request → Jinja2 template hoặc JSON response             │
│  Xác thực session cookie HMAC · Phân quyền 3 cấp               │
└────────────────────────────┬───────────────────────────────────┘
                             │ gọi service.*
┌────────────────────────────▼───────────────────────────────────┐
│                  SERVICE LAYER (Business Logic)                │
│  services/*.py — TOÀN BỘ validate + business logic tại đây    │
│  Ném *ServiceError với message tiếng Việt khi vi phạm          │
│  Không truy cập DB trực tiếp — luôn qua Repository             │
└────────────────────────────┬───────────────────────────────────┘
                             │ gọi repo.*
┌────────────────────────────▼───────────────────────────────────┐
│                REPOSITORY LAYER (Data Access)                  │
│  repositories/*.py — SQL thuần · sqlite3.Row                   │
│  Truy cập bằng tên cột: row["id"], row["ma_tuyen"]             │
│  Không logic nghiệp vụ · Mỗi file = 1 bảng                    │
└────────────────────────────┬───────────────────────────────────┘
                             │ sqlite3.connect()
┌────────────────────────────▼───────────────────────────────────┐
│                   DATABASE (SQLite)                            │
│  database/giao_thong.db                                        │
│  13 bảng · 6 triggers · 5 indexes · PRAGMA foreign_keys=ON    │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. DATABASE — 13 BẢNG

### 2.1 Sơ đồ quan hệ (ERD)

```
cap_quan_ly ──┐
              │ FK
cap_duong ────┼──────────────────────────────┐
              │ FK                            │
ket_cau_mat ──┼──────────────────────────────┤
              │ FK                            │
tinh_trang ───┼──────────────────────────────┤
              │ FK                            │
don_vi ───────┼──→ nguoi_dung                │
              │                               │
              │ FK cap_quan_ly_id             │
              ├──→ tuyen_duong ──→ thong_tin_tuyen
              │         │         ──→ tuyen_duong_geo
              │         │
              │         │ FK tuyen_id    FK cap_duong_id
              │         ├──→ doan_tuyen ─────────────────────────┐
              │         │         │      FK tinh_trang_id        │
              │         │         │      FK ket_cau_mat_id       │
              │         │         │      FK don_vi_bao_duong_id  │
              │         │         ├──→ hinh_anh_doan_tuyen       │
              │         │         └──→ doan_tuyen_geo            │
              │         │                                        │
              │         └──→ doan_di_chung ←─────────────────────┘
              │               FK tuyen_di_chung_id (→tuyen_duong)
              │               FK doan_id           (→doan_tuyen)
              │               FK tuyen_chinh_id    (→tuyen_duong)
              │
              └── nguoi_dung (updated_by_id trong doan_tuyen)
```

### 2.2 Chi tiết 13 bảng

#### Nhóm 1: Danh mục tra cứu (không phụ thuộc)

**`cap_quan_ly`** — 8 bản ghi
```sql
id  INTEGER PRIMARY KEY AUTOINCREMENT,
ma_cap           TEXT NOT NULL UNIQUE,   -- QL, DT, DX, DD, NT, TX, CD, DK
ten_cap          TEXT NOT NULL,
mo_ta            TEXT,
thu_tu_hien_thi  INTEGER,
is_active        INTEGER NOT NULL DEFAULT 1
```

**`cap_duong`** — 7 bản ghi
```sql
id  INTEGER PRIMARY KEY AUTOINCREMENT,
ma_cap           TEXT NOT NULL UNIQUE,   -- III, IV, V, VI + các cấp miền núi
ten_cap          TEXT NOT NULL,
mo_ta            TEXT,
thu_tu_hien_thi  INTEGER,
is_active        INTEGER NOT NULL DEFAULT 1
```

**`ket_cau_mat_duong`** — 8 bản ghi
```sql
id  INTEGER PRIMARY KEY AUTOINCREMENT,
ma_ket_cau       TEXT NOT NULL UNIQUE,   -- BTN, BTXM, HH, LN, CP, DAT, BTN+LN, BTXM+LN
ten_ket_cau      TEXT NOT NULL,
mo_ta            TEXT,
thu_tu_hien_thi  INTEGER,
is_active        INTEGER NOT NULL DEFAULT 1
```

**`tinh_trang`** — 9 bản ghi
```sql
id  INTEGER PRIMARY KEY AUTOINCREMENT,
ma_tinh_trang    TEXT NOT NULL UNIQUE,   -- TOT, TB, KEM, HH_NANG, THI_CONG...
ten_tinh_trang   TEXT NOT NULL,
mo_ta            TEXT,
mau_hien_thi     TEXT,                  -- hex color để hiển thị trên bản đồ
thu_tu_hien_thi  INTEGER,
is_active        INTEGER NOT NULL DEFAULT 1
```

#### Nhóm 2: Tổ chức

**`don_vi`** — 17 bản ghi (cây cha-con)
```sql
id               INTEGER PRIMARY KEY AUTOINCREMENT,
ma_don_vi        TEXT NOT NULL UNIQUE,
ten_don_vi       TEXT NOT NULL,
ten_viet_tat     TEXT,
parent_id        INTEGER REFERENCES don_vi(id),  -- cây cha-con
cap_don_vi       TEXT,                           -- Tinh/So/Ban/CT
dia_chi          TEXT,
so_dien_thoai    TEXT,
email            TEXT,
is_active        INTEGER NOT NULL DEFAULT 1,
created_at       TEXT NOT NULL DEFAULT (datetime('now','localtime'))
-- Cây: TINH → SXD → BAN_BT + 13 CT độc lập
```

**`nguoi_dung`** — 3+ bản ghi
```sql
id               INTEGER PRIMARY KEY AUTOINCREMENT,
ten_dang_nhap    TEXT NOT NULL UNIQUE,
mat_khau_hash    TEXT NOT NULL,          -- bcrypt, KHÔNG lưu plaintext
ho_ten           TEXT NOT NULL,
chuc_vu          TEXT,
don_vi_id        INTEGER REFERENCES don_vi(id),
so_dien_thoai    TEXT,
email            TEXT UNIQUE,
loai_quyen       TEXT NOT NULL DEFAULT 'XEM',  -- ADMIN|BIEN_TAP|XEM
is_active        INTEGER NOT NULL DEFAULT 0,   -- 0=chờ duyệt
is_approved      INTEGER NOT NULL DEFAULT 0,
approved_by_id   INTEGER REFERENCES nguoi_dung(id),
approved_at      TEXT,
created_at       TEXT NOT NULL DEFAULT (datetime('now','localtime')),
last_login       TEXT
```

#### Nhóm 3: Dữ liệu đường

**`tuyen_duong`** — 49 bản ghi
```sql
id                  INTEGER PRIMARY KEY AUTOINCREMENT,
ma_tuyen            TEXT NOT NULL UNIQUE,    -- QL4, DT151, DX01...
ten_tuyen           TEXT NOT NULL,
cap_quan_ly_id      INTEGER REFERENCES cap_quan_ly(id),
don_vi_quan_ly_id   INTEGER REFERENCES don_vi(id),
diem_dau            TEXT,
diem_cuoi           TEXT,
lat_dau             REAL,                   -- GPS điểm đầu
lng_dau             REAL,
lat_cuoi            REAL,                   -- GPS điểm cuối
lng_cuoi            REAL,
chieu_dai_quan_ly   REAL,       -- ← trigger cập nhật: chỉ đoạn chính
chieu_dai_thuc_te   REAL,       -- ← trigger cập nhật: đoạn chính + đi chung
nam_xay_dung        INTEGER,
nam_hoan_thanh      INTEGER,
ghi_chu             TEXT,
created_at          TEXT NOT NULL DEFAULT (datetime('now','localtime'))
```

**`thong_tin_tuyen`** — 49+ bản ghi (metadata mô tả)
```sql
id        INTEGER PRIMARY KEY AUTOINCREMENT,
tuyen_id  INTEGER NOT NULL REFERENCES tuyen_duong(id),
-- Các trường mô tả bổ sung về tuyến (lịch sử, đặc điểm địa hình, v.v.)
created_at TEXT
```

**`doan_tuyen`** — 222 bản ghi
```sql
id                      INTEGER PRIMARY KEY AUTOINCREMENT,
ma_doan                 TEXT NOT NULL UNIQUE,
tuyen_id                INTEGER NOT NULL REFERENCES tuyen_duong(id),
cap_duong_id            INTEGER REFERENCES cap_duong(id),
tinh_trang_id           INTEGER REFERENCES tinh_trang(id),
ket_cau_mat_id          INTEGER REFERENCES ket_cau_mat_duong(id),
ly_trinh_dau            REAL NOT NULL,     -- km (ví dụ: 35.6)
ly_trinh_cuoi           REAL NOT NULL,     -- ly_trinh_cuoi > ly_trinh_dau
chieu_dai_thuc_te       REAL,              -- NULL = tính từ lý trình
chieu_rong_mat_min      REAL,
chieu_rong_mat_max      REAL,              -- >= min
chieu_rong_nen_min      REAL,
chieu_rong_nen_max      REAL,              -- >= min
don_vi_bao_duong_id     INTEGER REFERENCES don_vi(id),
nam_lam_moi             INTEGER,
ngay_cap_nhat_tinh_trang TEXT,
ghi_chu                 TEXT,
created_at              TEXT NOT NULL DEFAULT (datetime('now','localtime')),
updated_at              TEXT,
updated_by_id           INTEGER REFERENCES nguoi_dung(id)
```

**`doan_di_chung`** — 15 bản ghi
```sql
id                      INTEGER PRIMARY KEY AUTOINCREMENT,
tuyen_di_chung_id       INTEGER NOT NULL REFERENCES tuyen_duong(id),  -- tuyến đi nhờ
tuyen_chinh_id          INTEGER NOT NULL REFERENCES tuyen_duong(id),  -- tuyến chủ
doan_id                 INTEGER NOT NULL REFERENCES doan_tuyen(id),   -- đoạn vật lý
ly_trinh_dau_di_chung   REAL,   -- lý trình theo hệ tọa độ tuyến đi nhờ
ly_trinh_cuoi_di_chung  REAL,
ly_trinh_dau_tuyen_chinh  REAL, -- lý trình theo hệ tọa độ tuyến chủ
ly_trinh_cuoi_tuyen_chinh REAL,
ghi_chu                 TEXT,
created_at              TEXT NOT NULL DEFAULT (datetime('now','localtime')),
UNIQUE(tuyen_di_chung_id, doan_id)  -- một tuyến không đi nhờ cùng đoạn 2 lần
```

**`hinh_anh_doan_tuyen`** — upload ảnh hiện trường
```sql
id         INTEGER PRIMARY KEY AUTOINCREMENT,
doan_id    INTEGER NOT NULL REFERENCES doan_tuyen(id),
duong_dan  TEXT NOT NULL,    -- đường dẫn file ảnh
lat_anh    REAL,             -- GPS từ EXIF
lng_anh    REAL,
mo_ta      TEXT,
created_at TEXT,
created_by_id INTEGER REFERENCES nguoi_dung(id)
```

**`tuyen_duong_geo`** — tọa độ GeoJSON Giai đoạn 1
```sql
id          INTEGER PRIMARY KEY AUTOINCREMENT,
tuyen_id    INTEGER NOT NULL REFERENCES tuyen_duong(id) UNIQUE,
coordinates TEXT NOT NULL,   -- JSON array [[lng,lat], ...]
so_diem     INTEGER,         -- số điểm tọa độ
created_at  TEXT,
updated_at  TEXT
```

**`doan_tuyen_geo`** — tọa độ GeoJSON Giai đoạn 2 (tạo sẵn, chưa dùng)
```sql
id          INTEGER PRIMARY KEY AUTOINCREMENT,
doan_id     INTEGER NOT NULL REFERENCES doan_tuyen(id) UNIQUE,
coordinates TEXT NOT NULL,
so_diem     INTEGER,
created_at  TEXT
```

### 2.3 Triggers — 6 triggers tự động cập nhật chiều dài

```
Tên trigger             | Bảng        | Sự kiện | Cập nhật
------------------------|-------------|---------|----------------------------------
trg_dt_sau_them         | doan_tuyen  | INSERT  | tuyen_duong.chieu_dai_quan_ly + thuc_te
trg_dt_sau_sua          | doan_tuyen  | UPDATE  | tuyen_duong.chieu_dai_quan_ly + thuc_te
trg_dt_sau_xoa          | doan_tuyen  | DELETE  | tuyen_duong.chieu_dai_quan_ly + thuc_te
trg_ddc_sau_them        | doan_di_chung | INSERT | tuyen_duong.chieu_dai_thuc_te
trg_ddc_sau_sua         | doan_di_chung | UPDATE | tuyen_duong.chieu_dai_thuc_te
trg_ddc_sau_xoa         | doan_di_chung | DELETE | tuyen_duong.chieu_dai_thuc_te
```

**Logic SQL trong trigger:**
```sql
-- chieu_dai_quan_ly = tổng đoạn chính (ưu tiên thực tế, fallback lý trình)
ROUND(SUM(COALESCE(chieu_dai_thuc_te, ly_trinh_cuoi - ly_trinh_dau)), 3)

-- chieu_dai_thuc_te = chieu_dai_quan_ly + tổng đoạn đi chung
chieu_dai_quan_ly + ROUND(SUM(ly_trinh_cuoi_di_chung - ly_trinh_dau_di_chung), 3)
```

### 2.4 Indexes — 5 indexes tối ưu JOIN

```sql
idx_doan_tuyen_tuyen_id       ON doan_tuyen(tuyen_id)
idx_doan_tuyen_cap_duong_id   ON doan_tuyen(cap_duong_id)
idx_doan_tuyen_tinh_trang_id  ON doan_tuyen(tinh_trang_id)
idx_ddc_tuyen_di_chung_id     ON doan_di_chung(tuyen_di_chung_id)
idx_ddc_doan_id               ON doan_di_chung(doan_id)
```

---

## 3. TẦNG MODELS

**Nguyên tắc:** Plain Object thuần túy. Không gọi DB, không validate nghiệp vụ, không import repository hoặc service.

### Bảng 13 models và @property

| Model | @property | Ghi chú |
|---|---|---|
| `CapQuanLy` | — | Danh mục đơn giản |
| `CapDuong` | — | Danh mục đơn giản |
| `KetCauMatDuong` | — | Danh mục đơn giản |
| `TinhTrang` | — | Có `mau_hien_thi` (hex color) |
| `DonVi` | — | Có `parent_id` cây cha-con |
| `NguoiDung` | `la_admin`, `co_quyen_bien_tap` | bcrypt hash, phân quyền |
| `TuyenDuong` | `toa_do_dau`, `toa_do_cuoi` | Bỏ field `chieu_dai` — trigger quản lý |
| `ThongTinTuyen` | — | Metadata mô tả tuyến |
| `DoanTuyen` | `chieu_dai`, `chieu_dai_tinh` | Validate chuyển sang Service |
| `DoanDiChung` | `chieu_dai_di_chung`, `chieu_dai_tuyen_chinh` | 2 cặp lý trình |
| `HinhAnhDoanTuyen` | `co_gps` | Ảnh + EXIF GPS |
| `TuyenDuongGeo` | `so_diem` | Tọa độ GeoJSON |
| `ThongKe*` | `tong_chieu_dai` | Aggregate — không map với bảng |

### Các @property quan trọng

```python
# DoanTuyen
@property
def chieu_dai(self) -> float:
    """Tính từ lý trình — không truy vấn DB"""
    if self.ly_trinh_cuoi and self.ly_trinh_dau:
        return round(self.ly_trinh_cuoi - self.ly_trinh_dau, 3)
    return 0.0

@property
def chieu_dai_tinh(self) -> float:
    """Ưu tiên thực tế nếu có"""
    return self.chieu_dai_thuc_te if self.chieu_dai_thuc_te else self.chieu_dai

# TuyenDuong
@property
def toa_do_dau(self) -> list | None:
    if self.lat_dau and self.lng_dau:
        return [self.lat_dau, self.lng_dau]
    return None

# NguoiDung
@property
def la_admin(self) -> bool:
    return self.loai_quyen == "ADMIN"

@property
def co_quyen_bien_tap(self) -> bool:
    return self.loai_quyen in ("ADMIN", "BIEN_TAP")
```

---

## 4. TẦNG REPOSITORIES

**Nguyên tắc:** SQL thuần, `sqlite3.Row`, truy cập bằng tên cột. Không có logic nghiệp vụ.

### Cấu trúc chuẩn

```python
import sqlite3
import models.ten_bang as ten_bang_model

_SELECT_COLS = """
    id, ma_*, ten_*,
    truong_khac,
    is_active, created_at
"""

def _row_to_object(row) -> ten_bang_model.TenBang:
    obj = ten_bang_model.TenBang()
    obj.id        = row["id"]
    obj.ma_ten    = row["ma_ten"]
    obj.ten_ten   = row["ten_ten"]
    obj.is_active = row["is_active"]
    return obj

def lay_tat_ca(conn: sqlite3.Connection) -> list[ten_bang_model.TenBang]:
    rows = conn.execute(f"SELECT {_SELECT_COLS} FROM ten_bang WHERE is_active=1").fetchall()
    return [_row_to_object(r) for r in rows]

def lay_theo_id(conn, id: int) -> ten_bang_model.TenBang | None:
    row = conn.execute(f"SELECT {_SELECT_COLS} FROM ten_bang WHERE id=?", (id,)).fetchone()
    return _row_to_object(row) if row else None

def them(conn, ...) -> int:
    with conn:
        cursor = conn.execute("INSERT INTO ten_bang(...) VALUES(...)", (...))
    return cursor.lastrowid

def xoa_mem(conn, id: int) -> bool:
    with conn:
        cursor = conn.execute("UPDATE ten_bang SET is_active=0 WHERE id=?", (id,))
    return cursor.rowcount > 0
```

### Repository đặc biệt: `thong_ke_repository.py`

3 query tổng hợp phức tạp (JOIN nhiều bảng, GROUP BY, SUM):

```python
def lay_thong_ke_toan_tinh(conn) -> ThongKeToanTinh:
    # COUNT(*) tuyen, doan, ddc
    # SUM chieu_dai_quan_ly, chieu_dai_thuc_te theo từng cap_quan_ly
    # GROUP BY tinh_trang, ket_cau_mat, cap_duong

def lay_thong_ke_mot_tuyen(conn, tuyen_id) -> ThongKeMoiTuyen:
    # SUM chiều dài theo từng tình trạng mặt đường
    # SUM chiều dài theo từng kết cấu mặt đường
```

---

## 5. TẦNG SERVICES

**Nguyên tắc:** Toàn bộ business logic và validation ở đây. Service được phép gọi nhiều repository khác nhau.

### Các validation quan trọng

#### `doan_tuyen_service.py`

```python
def them_doan_tuyen(conn, ma_doan, tuyen_id, ...) -> int:
    # 1. tuyen_id phải tồn tại
    if tuyen_duong_repo.lay_theo_id(conn, tuyen_id) is None:
        raise DoanTuyenServiceError(f"Tuyến id={tuyen_id} không tồn tại.")
    # 2. ma_doan chưa tồn tại
    if doan_tuyen_repo.lay_theo_ma(conn, ma_doan) is not None:
        raise DoanTuyenServiceError(f"Mã đoạn '{ma_doan}' đã tồn tại.")
    # 3. lý trình hợp lệ
    if ly_trinh_cuoi <= ly_trinh_dau:
        raise DoanTuyenServiceError("Lý trình cuối phải lớn hơn lý trình đầu.")
    # 4. kích thước hợp lệ
    if rong_mat_max and rong_mat_min and rong_mat_max < rong_mat_min:
        raise DoanTuyenServiceError("Rộng mặt max phải >= min.")
    # INSERT → trigger tự cập nhật chieu_dai tuyến
    return doan_tuyen_repo.them(conn, ...)
```

#### `doan_di_chung_service.py`

```python
def them_doan_di_chung(conn, tuyen_di_chung_id, tuyen_chinh_id, doan_id, ...) -> int:
    # 1. Hai tuyến không được là một
    if tuyen_di_chung_id == tuyen_chinh_id:
        raise DoanDiChungServiceError("Tuyến đi chung ≠ tuyến chủ.")
    # 2. Cả hai tuyến phải tồn tại
    _validate_tuyen_ton_tai(conn, tuyen_di_chung_id, "Tuyến đi chung")
    _validate_tuyen_ton_tai(conn, tuyen_chinh_id, "Tuyến chủ")
    # 3. Đoạn vật lý phải tồn tại
    doan = _validate_doan_ton_tai(conn, doan_id)
    # 4. Đoạn phải thuộc tuyến chủ
    _validate_doan_thuoc_tuyen_chinh(doan, tuyen_chinh_id)
    # 5. Lý trình hợp lệ (cả 2 chiều)
    _validate_ly_trinh_cap(ly_trinh_dau_di_chung, ly_trinh_cuoi_di_chung, "tuyến đi chung")
    _validate_ly_trinh_cap(ly_trinh_dau_tuyen_chinh, ly_trinh_cuoi_tuyen_chinh, "tuyến chủ")
    # 6. Lý trình nằm trong phạm vi đoạn vật lý
    _validate_ly_trinh_nam_trong_doan(doan, ly_trinh_dau_tuyen_chinh, ly_trinh_cuoi_tuyen_chinh)
    # INSERT → trigger cập nhật chieu_dai_thuc_te
    return doan_di_chung_repo.them(conn, ...)
```

#### `nguoi_dung_service.py`

```python
def dang_ky(conn, ten_dang_nhap, mat_khau_ro, ...) -> NguoiDung:
    mat_khau_hash = bcrypt.hashpw(mat_khau_ro.encode(), bcrypt.gensalt()).decode()
    # is_active=0, is_approved=0 → chờ ADMIN duyệt

def dang_nhap(conn, ten_dang_nhap, mat_khau_ro) -> NguoiDung:
    nguoi_dung = nguoi_dung_repo.lay_theo_ten_dang_nhap(conn, ten_dang_nhap)
    if not nguoi_dung or not bcrypt.checkpw(mat_khau_ro.encode(), nguoi_dung.mat_khau_hash.encode()):
        raise DangNhapThatBaiError("Sai tên đăng nhập hoặc mật khẩu.")
    if not nguoi_dung.is_approved:
        raise DangNhapThatBaiError("Tài khoản chưa được duyệt.")
    # Cập nhật last_login
    return nguoi_dung

def duyet_nguoi_dung(conn, user_id, admin_id) -> bool:
    admin = nguoi_dung_repo.lay_theo_id(conn, admin_id)
    if not admin or admin.loai_quyen != "ADMIN":
        raise NguoiDungServiceError("Chỉ ADMIN mới có thể duyệt tài khoản.")
```

---

## 6. WEB APPLICATION — FASTAPI

### 6.1 Cấu trúc API

```
GET  /                        → dashboard.html
GET  /api/health              → JSON {"status": "ok"}

GET  /auth/login              → form đăng nhập
POST /auth/login              → xử lý đăng nhập → set cookie
GET  /auth/logout             → xóa cookie → redirect /auth/login
GET  /auth/dang-ky            → form đăng ký
POST /auth/dang-ky            → tạo tài khoản chờ duyệt
GET  /auth/cho-duyet          → danh sách chờ duyệt (ADMIN only)
POST /auth/duyet/{id}         → duyệt tài khoản (ADMIN only)

GET  /tuyen-duong             → danh sách tuyến
POST /tuyen-duong             → thêm tuyến (BIEN_TAP+)
GET  /tuyen-duong/{id}        → chi tiết tuyến
PUT  /tuyen-duong/{id}        → sửa tuyến (BIEN_TAP+)
DELETE /tuyen-duong/{id}      → xóa mềm tuyến (ADMIN)

GET  /doan-tuyen              → danh sách đoạn
POST /doan-tuyen              → thêm đoạn (BIEN_TAP+)
GET  /doan-tuyen/{id}         → chi tiết đoạn
PUT  /doan-tuyen/{id}         → sửa đoạn (BIEN_TAP+)
DELETE /doan-tuyen/{id}       → xóa mềm đoạn (ADMIN)

GET  /doan-di-chung           → danh sách DDC
POST /doan-di-chung           → thêm DDC (BIEN_TAP+)
DELETE /doan-di-chung/{id}    → xóa DDC (ADMIN)

GET  /thong-ke                → trang thống kê (HTML)
GET  /thong-ke/api/toan-tinh  → JSON thống kê toàn tỉnh
GET  /thong-ke/api/tuyen/{id} → JSON thống kê 1 tuyến

GET  /ban-do                  → trang bản đồ (HTML)
GET  /ban-do/geojson/{id}     → GeoJSON tuyến

GET  /api/docs                → Swagger UI
GET  /api/redoc               → ReDoc
```

### 6.2 Xác thực — Session Cookie HMAC

Không dùng JWT. Dùng HMAC SHA-256 ký trên cookie (Python stdlib):

```python
# Token format: base64url(user_id:loai_quyen:timestamp).hmac_sha256
# SECRET_KEY: os.environ.get("SESSION_SECRET", default)
# TTL: 7 ngày

# FastAPI Dependencies (dùng trong route):
lay_user_hien_tai()         # → dict | None (không block)
yeu_cau_dang_nhap()         # → dict hoặc redirect 302 /auth/login
yeu_cau_quyen_bien_tap()    # → dict hoặc 403
yeu_cau_quyen_admin()       # → dict hoặc 403
```

### 6.3 Template Jinja2

Custom filter đăng ký trong `api/main.py`:
```python
{{ doan.ly_trinh_dau | format_ly_trinh }}  # 37.557 → "Km37+557"
{{ doan.ly_trinh_cuoi | format_ly_trinh }} # 190.0  → "Km190+000"
```

---

## 7. DATA PIPELINE

### 7.1 Luồng từ Excel đến Database

```
Excel (10 sheets)
    ↓ tools/excel_to_data.py
data/
  ├── cap_quan_ly_data.py   CAP_QUAN_LY_CONFIG  (8)
  ├── cap_duong_data.py     CAP_DUONG_CONFIG    (7)
  ├── ket_cau_mat_data.py   KET_CAU_MAT_CONFIG  (8)
  ├── tinh_trang_data.py    TINH_TRANG_CONFIG   (9)
  ├── don_vi_data.py        DON_VI_CONFIG       (17)
  ├── nguoi_dung_data.py    NGUOI_DUNG_CONFIG   (3)
  ├── tuyen_duong_data.py   TUYEN_CONFIG        (49)
  ├── thong_tin_tuyen_data.py                   (49+)
  ├── doan_tuyen_data.py    DOAN_CONFIG         (222)
  └── doan_di_chung_data.py DDC_CONFIG          (15)
    ↓ seeds/seed_all.py (INSERT OR IGNORE — idempotent)
database/giao_thong.db
```

### 7.2 Thứ tự seed bắt buộc

```python
seed_danh_muc()      # 1. cap_quan_ly, cap_duong, ket_cau_mat, tinh_trang
seed_don_vi()        # 2. 17 đơn vị (cây cha-con: TINH → SXD → BAN_BT → CT)
seed_nguoi_dung()    # 3. 3 tài khoản mặc định (bcrypt hash)
seed_tuyen_doan()    # 4. 49 tuyến + 222 đoạn + 15 DDC
                     #    (trigger tự cập nhật chiều dài sau mỗi INSERT)
```

### 7.3 GeoJSON Pipeline

```
*.geojson file (map/ hoặc data/geojson/)
    ↓ tools/import_geojson.py
bảng tuyen_duong_geo (Giai đoạn 1 — theo tuyến)
    ↓ (Giai đoạn 2 — chưa triển khai)
bảng doan_tuyen_geo (theo đoạn, dùng Shapely nội suy)

tuyen_duong_geo → api/routes/ban_do.py → Leaflet.js
map/*.geojson   → map/generate_map_multi_mahoa_onefile.py → HTML tự chứa
```

**Mã hóa GeoJSON trong file HTML tự chứa (3 lớp):**
```
coordinates → Delta encoding → XOR cipher (key 32 byte ngẫu nhiên) → Base64
```

---

## 8. SỐ LIỆU THỰC TẾ

| Hạng mục | Số lượng |
|---|---|
| Quốc lộ (QL) | 9 |
| Đường tỉnh (DT) | 27 |
| Đường xã/khác (DX) | 13 |
| **Tổng tuyến** | **49** |
| Đoạn tuyến | 222 |
| Đoạn đi chung | 15 |
| File GeoJSON hiện có | 2 (QL4E: 5039 điểm, DT158: 4274 điểm) |
| Đơn vị quản lý | 17 |

**Đoạn đi chung đã xác nhận:**
- QL4D đi nhờ QL70-05 (Km140.893 → 149)
- QL4E đi nhờ QL70-01 (Km35.6 → 36.975)
- DT153 đi nhờ QL4E-04 (Km18.3 → 21.1)
- DT159 đi nhờ QL4E-08, 09, 10, 11
- DT160 đi nhờ QL279-11, 12, 13
- DT162 đi nhờ DT151-03
- DX02 đi nhờ DT173-01

**TODO chưa xử lý** (tuyến chủ thuộc tỉnh khác — không có trong DB):
- QL4E đi nhờ QL4D Km79.757→82.957
- QL32 đi nhờ QL37 Km162→172
- DT155 đi nhờ QL4D Km43.5→47.1

---

## 9. ĐỊNH HƯỚNG PHÁT TRIỂN TIẾP THEO

### Ngắn hạn (ưu tiên cao)
1. Test end-to-end trên môi trường thật
2. Deploy lên VPS (Ubuntu + Nginx + systemd)
3. Cấu hình HTTPS (Let's Encrypt)

### Trung hạn
1. Thu thập GeoJSON cho 47 tuyến còn lại
2. Thuật toán nội suy GeoJSON theo đoạn (Shapely) — Giai đoạn 2
3. Xuất báo cáo Excel/PDF từ Web

### Dài hạn
1. Chuyển sang PostgreSQL (multi-user production)
2. App mobile nhập liệu hiện trường (PWA)
3. Audit log — lịch sử thay đổi từng đoạn
4. Dashboard Chart.js — heatmap tình trạng đường

---

*Cập nhật khi có thay đổi kiến trúc hoặc thêm bảng/tính năng mới.*
