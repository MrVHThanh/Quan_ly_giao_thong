# TÀI LIỆU RÀ SOÁT KỸ THUẬT — HỆ THỐNG QUẢN LÝ ĐƯỜNG BỘ LÀO CAI
**Sở Xây dựng tỉnh Lào Cai**
**Ngày cập nhật:** 22/03/2026
**Trạng thái dự án:** Hoàn thành 8/8 bước — Sẵn sàng triển khai

---

## MỤC LỤC

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Kiến trúc tổng thể](#2-kiến-trúc-tổng-thể)
3. [Cơ sở dữ liệu — 13 bảng](#3-cơ-sở-dữ-liệu--13-bảng)
4. [Tầng Models (13 files)](#4-tầng-models)
5. [Tầng Repositories (13 files)](#5-tầng-repositories)
6. [Tầng Services (13 files)](#6-tầng-services)
7. [Data files + Seeds](#7-data-files--seeds)
8. [Tools (công cụ phụ trợ)](#8-tools)
9. [Web Application — FastAPI](#9-web-application--fastapi)
10. [Luồng dữ liệu tổng thể](#10-luồng-dữ-liệu-tổng-thể)
11. [Hạn chế và vấn đề mở](#11-hạn-chế-và-vấn-đề-mở)
12. [Đề xuất tiến độ dự án tiếp theo](#12-đề-xuất-tiến-độ-dự-án-tiếp-theo)

---

## 1. TỔNG QUAN DỰ ÁN

| Hạng mục | Chi tiết |
|---|---|
| **Tên hệ thống** | Quản lý tuyến đường bộ tỉnh Lào Cai |
| **Đơn vị** | Sở Xây dựng tỉnh Lào Cai |
| **Stack** | Python + SQLite → FastAPI Web Application |
| **Thư mục gốc** | `D:\Dropbox\@Giaothong2\` |
| **Database** | `database/giao_thong.db` |
| **File dữ liệu nguồn** | `data/giao_thong_data_upadate.xlsx` (10 sheets) |

### Số liệu thực tế đã xác nhận

| Hạng mục | Số lượng | Chi tiết |
|---|---|---|
| Tuyến đường | **49** | 9 QL + 27 DT + 13 DX |
| Đoạn tuyến | **222** | Đoạn vật lý cơ sở |
| Đoạn đi chung | **15** | Mỗi bản ghi = 1 đoạn vật lý |
| Bảng DB | **13** | Tăng từ 6 bảng cũ |
| Đơn vị | **17** | TINH→SXD→BAN_BT + 13 CT độc lập |
| Kết cấu mặt đường | **8** | BTN, BTXM, HH, LN, CP, DAT, BTN+LN, BTXM+LN |
| Tình trạng mặt đường | **9** | TOT, TB, KEM, HH_NANG, THI_CONG, BAO_TRI, TAM_DONG, NGUNG, CHUA_XD |
| File GeoJSON | **2 hiện có** | QL4E.geojson (5039 điểm), DT158.geojson (4274 điểm) |

---

## 2. KIẾN TRÚC TỔNG THỂ

### Mô hình tầng (Layered Architecture)

```
┌─────────────────────────────────────────────────────┐
│                  WEB LAYER (FastAPI)                │
│  api/routes/  ←  api/main.py  ←  templates/         │
│  auth | tuyen_duong | doan_tuyen | thong_ke | ban_do │
└──────────────────────┬──────────────────────────────┘
                       │ gọi
┌──────────────────────▼──────────────────────────────┐
│              SERVICE LAYER (Business Logic)          │
│  Validate · Transform · Orchestrate · Authorize      │
│  13 services — toàn bộ nghiệp vụ nằm ở đây         │
└──────────────────────┬──────────────────────────────┘
                       │ gọi
┌──────────────────────▼──────────────────────────────┐
│            REPOSITORY LAYER (Data Access)            │
│  SQL thuần · sqlite3.Row · không logic nghiệp vụ   │
│  13 repositories — mỗi file = 1 bảng               │
└──────────────────────┬──────────────────────────────┘
                       │ truy cập
┌──────────────────────▼──────────────────────────────┐
│              DATABASE (SQLite)                       │
│  13 bảng · 6 triggers · 5 indexes                   │
│  database/giao_thong.db                             │
└─────────────────────────────────────────────────────┘
```

### Quy tắc import BẮT BUỘC toàn dự án

```python
# ĐÚNG — dùng alias module
import models.doan_tuyen as doan_tuyen_model
import repositories.doan_tuyen_repository as doan_tuyen_repo
import services.tuyen_duong_service as tuyen_duong_service

# SAI — không dùng from ... import
from models.doan_tuyen import DoanTuyen  # ❌
```

### Cấu trúc thư mục đầy đủ

```
@Giaothong2/
├── config/
│   ├── database.py          # get_connection(), create_tables(), sqlite3.Row
│   └── settings.py          # BASE_DIR, DB_PATH, cấu hình chung
├── models/                  # Plain Objects — KHÔNG logic DB, KHÔNG validate
│   ├── cap_quan_ly.py
│   ├── cap_duong.py
│   ├── ket_cau_mat_duong.py      ← MỚI
│   ├── tinh_trang.py
│   ├── don_vi.py
│   ├── nguoi_dung.py              ← MỚI
│   ├── tuyen_duong.py
│   ├── thong_tin_tuyen.py         ← MỚI
│   ├── doan_tuyen.py
│   ├── doan_di_chung.py           ← cấu trúc mới
│   ├── hinh_anh_doan_tuyen.py    ← MỚI
│   ├── tuyen_duong_geo.py         ← MỚI
│   └── thong_ke.py
├── repositories/            # SQL thuần, sqlite3.Row, KHÔNG index cứng
│   ├── [13 files tương ứng models]
├── services/                # Toàn bộ validate + business logic ở đây
│   ├── [13 files tương ứng models]
├── data/                    # Config Python từ Excel — nguồn sự thật
│   ├── cap_quan_ly_data.py  (8)
│   ├── cap_duong_data.py    (7)
│   ├── ket_cau_mat_data.py  (8)
│   ├── tinh_trang_data.py   (9)
│   ├── don_vi_data.py       (17)
│   ├── nguoi_dung_data.py   (3)
│   ├── tuyen_duong_data.py  (49)
│   ├── thong_tin_tuyen_data.py  (9 có đầy đủ, 40 còn thiếu)
│   ├── doan_tuyen_data.py   (222)
│   └── doan_di_chung_data.py (15)
├── seeds/
│   ├── seed_all.py          # Điều phối — gọi theo đúng thứ tự
│   ├── seed_danh_muc.py     # cap_quan_ly, cap_duong, ket_cau_mat, tinh_trang
│   ├── seed_don_vi.py       # Cây cha-con đúng thứ tự
│   ├── seed_nguoi_dung.py   # bcrypt hash mật khẩu
│   └── seed_tuyen_doan.py   # tuyen_duong → doan_tuyen → doan_di_chung
├── migrations/
│   └── 001_initial_schema.py
├── tools/
│   ├── excel_to_data.py     # Excel → 9 file data/*.py (CLI)
│   ├── import_geojson.py    # *.geojson → bảng tuyen_duong_geo
│   └── export_geojson.py    # DB → xuất file *.geojson
├── api/
│   ├── main.py              # FastAPI app, middleware, startup
│   └── routes/
│       ├── auth.py          # Đăng nhập, phân quyền JWT
│       ├── tuyen_duong.py   # CRUD tuyến
│       ├── doan_tuyen.py    # CRUD đoạn
│       ├── thong_ke.py      # Báo cáo thống kê
│       └── ban_do.py        # GeoJSON API cho Leaflet
├── templates/
│   ├── dashboard.html
│   ├── ban_do.html
│   ├── tuyen_duong/         # list, detail, form
│   └── doan_tuyen/          # list, detail, form
├── map/
│   ├── QL4E_merged.geojson
│   ├── DT158_merged.geojson
│   └── generate_map_multi_mahoa_onefile.py
├── database/
│   └── giao_thong.db        # gitignore
└── main.py                  # Điểm chạy console (báo cáo text)
```

---

## 3. CƠ SỞ DỮ LIỆU — 13 BẢNG

### Sơ đồ quan hệ đầy đủ

```
cap_quan_ly ────────────────────┐
cap_duong ───────────────────┐  │
ket_cau_mat_duong ────────┐  │  │
tinh_trang ─────────────┐ │  │  │
don_vi ──────────┐       │ │  │  │
nguoi_dung ──────┤       │ │  │  │
                 │       │ │  │  │
                 ▼       ▼ ▼  ▼  ▼
           tuyen_duong ◄──── doan_tuyen ◄──── doan_di_chung
                 │               │                  │
                 │          hinh_anh_doan_tuyen      │
                 │                             (tuyen_di_chung_id)
           thong_tin_tuyen                    (tuyen_chinh_id)
           tuyen_duong_geo                    (doan_id)
           doan_tuyen_geo ◄──── (giai đoạn 2)
```

### Chi tiết 13 bảng theo thứ tự tạo

#### Nhóm 1 — Danh mục (không phụ thuộc)

**cap_quan_ly** — 8 bản ghi (QL, DT, DX, CT, NT, TX, CD, DK)
```sql
id, ma_cap UNIQUE, ten_cap, thu_tu_hien_thi, is_active DEFAULT 1
```

**cap_duong** — 7 bản ghi (I, II, III, IV, V, VI, NO)
```sql
id, ma_cap UNIQUE, ten_cap, thu_tu_hien_thi, is_active DEFAULT 1
```

**ket_cau_mat_duong** — 8 bản ghi (BTN, BTXM, HH, LN, CP, DAT, BTN+LN, BTXM+LN) — MỚI
```sql
id, ma_ket_cau UNIQUE, ten_ket_cau, mo_ta, thu_tu_hien_thi, is_active DEFAULT 1
```

**tinh_trang** — 9 bản ghi (TOT, TB, KEM, HH_NANG, THI_CONG, BAO_TRI, TAM_DONG, NGUNG, CHUA_XD)
```sql
id, ma UNIQUE, ten, mau_hien_thi (hex), thu_tu_hien_thi, is_active DEFAULT 1
```

#### Nhóm 2 — Tổ chức

**don_vi** — 17 bản ghi (cây cha-con: TINH → SXD → BAN_BT + 13 CT độc lập)
```sql
id, ma_don_vi UNIQUE, ten_don_vi, loai (Tinh/So/Ban/Donvi),
parent_id FK→don_vi, is_active DEFAULT 1
```

**nguoi_dung** — MỚI — 3 bản ghi khởi tạo
```sql
id, ten_dang_nhap UNIQUE, mat_khau_hash (bcrypt),
ho_ten, chuc_vu, don_vi_id FK, so_dien_thoai, email UNIQUE,
loai_quyen (ADMIN|BIEN_TAP|XEM),
is_active DEFAULT 0, is_approved DEFAULT 0,
approved_by_id FK→nguoi_dung, approved_at, created_at, last_login
```
> Lưu ý: đăng ký → chờ ADMIN duyệt. Mật khẩu bcrypt, không bao giờ lưu rõ.

#### Nhóm 3 — Tuyến đường

**tuyen_duong** — 49 bản ghi — ⭐ BỎ cột `chieu_dai`
```sql
id, ma_tuyen UNIQUE, ten_tuyen,
cap_quan_ly_id FK, don_vi_quan_ly_id FK,
diem_dau, diem_cuoi, lat_dau, lng_dau, lat_cuoi, lng_cuoi,
chieu_dai_quan_ly,   -- tổng đoạn chính (trigger tự cập nhật)
chieu_dai_thuc_te,   -- tổng = chinh + di_chung (trigger tự cập nhật)
nam_xay_dung, nam_hoan_thanh, ghi_chu, created_at
```
> ⚠️ KHÔNG có `chieu_dai` — chỉ có `chieu_dai_quan_ly` và `chieu_dai_thuc_te`

**thong_tin_tuyen** — MỚI — 9 bản ghi đầy đủ, 40 còn thiếu
```sql
id, tuyen_id FK UNIQUE, mo_ta TEXT (dài)
```

#### Nhóm 4 — Đoạn tuyến

**doan_tuyen** — 222 bản ghi — ⭐ Thêm 5 trường mới
```sql
id, ma_doan UNIQUE, tuyen_id FK, cap_duong_id FK, tinh_trang_id FK,
ket_cau_mat_id FK,           -- MỚI
ly_trinh_dau, ly_trinh_cuoi,
chieu_dai_thuc_te,
chieu_rong_mat_min, chieu_rong_mat_max,
chieu_rong_nen_min, chieu_rong_nen_max,
don_vi_bao_duong_id FK,
nam_lam_moi,                 -- MỚI
ngay_cap_nhat_tinh_trang,    -- MỚI
ghi_chu, created_at,
updated_at,                  -- MỚI auto
updated_by_id FK→nguoi_dung  -- MỚI audit
```

**doan_di_chung** — 15 bản ghi — ⭐ Cấu trúc hoàn toàn mới
```sql
id, ma_doan_di_chung UNIQUE,   -- VD: DDC-DT159-QL4E-01-001
tuyen_di_chung_id FK,          -- tuyến đi nhờ (vd: DT159)
tuyen_chinh_id FK,             -- tuyến chủ sở hữu đoạn (vd: QL4E)  MỚI
doan_id FK,                    -- đoạn vật lý cụ thể (vd: QL4E-01)
ly_trinh_dau_di_chung,         -- lý trình theo tuyến đi nhờ
ly_trinh_cuoi_di_chung,        -- lý trình theo tuyến đi nhờ
ly_trinh_dau_tuyen_chinh,      -- lý trình theo tuyến chủ   MỚI
ly_trinh_cuoi_tuyen_chinh,     -- lý trình theo tuyến chủ   MỚI
ghi_chu, created_at
UNIQUE(tuyen_di_chung_id, doan_id)
```
> Quy tắc: mỗi bản ghi = 1 đoạn vật lý. Nếu DDC vắt qua nhiều đoạn → tách nhiều bản ghi.

#### Nhóm 5 — Phụ trợ

**hinh_anh_doan_tuyen** — MỚI — chưa có dữ liệu
```sql
id, doan_id FK, duong_dan_file,
mo_ta, ngay_chup, nguoi_chup,
lat, lng,         -- EXIF GPS (NULL nếu không có)
ly_trinh_anh,    -- tính từ lat/lng (giai đoạn 2)
created_at
```

**tuyen_duong_geo** — MỚI — Giai đoạn 1 (đang dùng)
```sql
id, tuyen_id FK UNIQUE,
coordinates TEXT,  -- JSON: [[lng,lat],[lng,lat],...]
so_diem, chieu_dai_gps, nguon, updated_at
```

**doan_tuyen_geo** — MỚI — Giai đoạn 2 (tạo sẵn, chưa dùng)
```sql
id, doan_id FK UNIQUE,
coordinates TEXT,  -- JSON: [[lng,lat],...]
so_diem, chieu_dai_gps, nguon, updated_at
```

### Triggers — 6 triggers tự động

```
trg_doan_tuyen_sau_them  → AFTER INSERT ON doan_tuyen
trg_doan_tuyen_sau_sua   → AFTER UPDATE ON doan_tuyen
trg_doan_tuyen_sau_xoa   → AFTER DELETE ON doan_tuyen
trg_ddc_sau_them         → AFTER INSERT ON doan_di_chung
trg_ddc_sau_sua          → AFTER UPDATE ON doan_di_chung
trg_ddc_sau_xoa          → AFTER DELETE ON doan_di_chung
```

Logic mỗi trigger:
- `tuyen_duong.chieu_dai_quan_ly` = `SUM(COALESCE(chieu_dai_thuc_te, ly_trinh_cuoi - ly_trinh_dau))` FROM doan_tuyen WHERE tuyen_id = affected
- `tuyen_duong.chieu_dai_thuc_te` = chieu_dai_quan_ly + `SUM(ly_trinh_cuoi_di_chung - ly_trinh_dau_di_chung)` FROM doan_di_chung WHERE tuyen_di_chung_id = affected

### Indexes — 5 indexes tối ưu truy vấn

```sql
idx_doan_tuyen_tuyen_id        ON doan_tuyen(tuyen_id)
idx_doan_tuyen_cap_duong_id    ON doan_tuyen(cap_duong_id)
idx_doan_tuyen_tinh_trang_id   ON doan_tuyen(tinh_trang_id)
idx_ddc_tuyen_di_chung_id      ON doan_di_chung(tuyen_di_chung_id)
idx_ddc_doan_id                ON doan_di_chung(doan_id)
```

### Soft delete

Các bảng danh mục dùng soft delete (`is_active = 0`), KHÔNG xóa cứng:
- `cap_quan_ly`, `cap_duong`, `ket_cau_mat_duong`, `tinh_trang`, `don_vi`

Các bảng còn lại dùng xóa cứng (có thể khôi phục qua seed lại nếu cần).

---

## 4. TẦNG MODELS

**Nguyên tắc:** Plain Object thuần túy — KHÔNG logic nghiệp vụ, KHÔNG gọi DB, KHÔNG validate.

### Quy tắc viết Model

```python
class DoanTuyen:
    def __init__(
        self,
        id: int | None = None,
        ma_doan: str | None = None,
        tuyen_id: int | None = None,
        # ... tất cả tham số có type hints + default None
    ):
        self.id = id
        self.ma_doan = ma_doan
        # ...

    @property
    def chieu_dai(self) -> float:
        """Tính từ lý trình — không truy vấn DB"""
        if self.ly_trinh_cuoi and self.ly_trinh_dau:
            return self.ly_trinh_cuoi - self.ly_trinh_dau
        return 0.0

    @property
    def chieu_dai_tinh(self) -> float:
        """Ưu tiên thực tế nếu có"""
        return self.chieu_dai_thuc_te or self.chieu_dai
```

### Danh sách 13 models và @property quan trọng

| File | @property chính | Ghi chú |
|---|---|---|
| `cap_quan_ly.py` | — | Danh mục đơn giản |
| `cap_duong.py` | — | Danh mục đơn giản |
| `ket_cau_mat_duong.py` | — | MỚI — danh mục đơn giản |
| `tinh_trang.py` | — | Có `mau_hien_thi` (hex color) |
| `don_vi.py` | — | Có `parent_id` cây cha-con |
| `nguoi_dung.py` | `la_admin`, `co_quyen_biet_tap` | MỚI |
| `tuyen_duong.py` | `toa_do_dau`, `toa_do_cuoi` | Bỏ `chieu_dai` |
| `thong_tin_tuyen.py` | — | MỚI — chỉ có `tuyen_id` + `mo_ta` |
| `doan_tuyen.py` | `chieu_dai`, `chieu_dai_tinh` | Validate chuyển sang Service |
| `doan_di_chung.py` | `chieu_dai_di_chung`, `chieu_dai_tuyen_chinh` | 2 cặp lý trình |
| `hinh_anh_doan_tuyen.py` | `co_gps` | MỚI |
| `tuyen_duong_geo.py` | `so_diem` | MỚI |
| `thong_ke.py` | `tong_chieu_dai` | Cập nhật thêm ket_cau_mat |

---

## 5. TẦNG REPOSITORIES

**Nguyên tắc:** Chỉ SQL thuần + `sqlite3.Row`. Tuyệt đối KHÔNG dùng index cứng `row[0]`, `row[7]`...

### Thay đổi cốt lõi so với phiên bản cũ

| Cũ (phiên bản cũ) | Mới (hiện tại) |
|---|---|
| `row[0]`, `row[8]`... | `row["id"]`, `row["tinh_trang_id"]` |
| `cap_nhat_chieu_dai_tuyen()` thủ công | SQLite trigger tự động |
| `_SELECT_COLS` + `_row_to_object` có thể lệch index | `sqlite3.Row` truy cập theo tên cột |

### Cấu trúc chuẩn mỗi repository

```python
# Ví dụ: doan_tuyen_repository.py
_SELECT_COLS = """
    id, ma_doan, tuyen_id, cap_duong_id, tinh_trang_id,
    ket_cau_mat_id, ly_trinh_dau, ly_trinh_cuoi,
    chieu_dai_thuc_te, chieu_rong_mat_min, chieu_rong_mat_max,
    chieu_rong_nen_min, chieu_rong_nen_max, don_vi_bao_duong_id,
    nam_lam_moi, ngay_cap_nhat_tinh_trang,
    ghi_chu, created_at, updated_at, updated_by_id
"""

def _row_to_object(row) -> DoanTuyen:
    return doan_tuyen_model.DoanTuyen(
        id=row["id"],
        ma_doan=row["ma_doan"],
        tinh_trang_id=row["tinh_trang_id"],
        # ... tất cả theo tên cột
    )

def lay_tat_ca(conn) -> list[DoanTuyen]: ...
def lay_theo_ma(conn, ma_doan: str) -> DoanTuyen | None: ...
def lay_theo_id(conn, id: int) -> DoanTuyen | None: ...
def lay_theo_tuyen_id(conn, tuyen_id: int) -> list[DoanTuyen]: ...
def them_doan_tuyen(conn, doan: DoanTuyen) -> int: ...  # trả lastrowid
def cap_nhat_doan_tuyen(conn, doan: DoanTuyen) -> bool: ...
```

### Danh sách 13 repositories và hàm đặc biệt

| File | Hàm đặc biệt |
|---|---|
| `cap_quan_ly_repository.py` | `xoa_mem()`, `khoi_phuc()` |
| `cap_duong_repository.py` | `xoa_mem()`, `khoi_phuc()` |
| `ket_cau_mat_repository.py` | MỚI |
| `tinh_trang_repository.py` | `xoa_mem()`, `khoi_phuc()` |
| `don_vi_repository.py` | `lay_cay_cha_con()` — đệ quy cây |
| `nguoi_dung_repository.py` | `lay_theo_ten_dang_nhap()`, `cap_nhat_last_login()` |
| `tuyen_duong_repository.py` | Bỏ `cap_nhat_chieu_dai` (trigger lo) |
| `thong_tin_tuyen_repository.py` | MỚI |
| `doan_tuyen_repository.py` | `lay_theo_tuyen_id()`, `lay_theo_tinh_trang()` |
| `doan_di_chung_repository.py` | `lay_theo_tuyen_di_chung_id()`, `lay_theo_doan_id()` |
| `hinh_anh_repository.py` | `lay_theo_doan_id()`, `lay_co_gps()` |
| `tuyen_duong_geo_repository.py` | `luu_toa_do()`, `lay_toa_do()` |
| `thong_ke_repository.py` | 3 query JOIN phức tạp (xem mục 6) |

### thong_ke_repository — 3 query phức tạp

```python
# Query 1: Ma trận cap_quan_ly × cap_duong → km
lay_thong_ke_cap_ky_thuat_theo_cap_quan_ly(conn)
# → GROUP BY cql.ma_cap, cd.ma_cap → SUM(COALESCE(chieu_dai_thuc_te, lt_cuoi - lt_dau))

# Query 2: Từng tuyến × cap_duong → km
lay_thong_ke_cap_ky_thuat_theo_tung_tuyen(conn)
# → GROUP BY tuyen_id, cap_duong_id

# Query 3: Chi tiết đoạn — UNION đoạn chính + đoạn đi chung
lay_chi_tiet_doan_theo_tung_tuyen(conn)
# UNION ALL:
#   SELECT ... FROM doan_tuyen (loai='CHINH')
#   SELECT ... FROM doan_di_chung JOIN doan_tuyen (loai='DI_CHUNG')
```

---

## 6. TẦNG SERVICES

**Nguyên tắc:** Toàn bộ business logic + validation nằm đây. Model và Repository không validate.

### Cấu trúc chuẩn mỗi service

```python
# Hàm đọc
def lay_tat_ca(conn) -> list[Model]: ...
def lay_theo_ma(conn, ma: str) -> Model | None: ...
def lay_theo_id(conn, id: int) -> Model | None: ...

# Hàm ghi (có validate)
def them_*(conn, ...) -> int: ...         # trả id mới
def cap_nhat_*(conn, ...) -> bool: ...
def xoa_mem_*(conn, id: int) -> bool: ... # soft delete

# Helper
def get_or_create_*(conn, ma: str) -> tuple[Model, bool]: ...
# → dùng trong seed: (object, created: True/False)
```

### Danh sách 13 services và nghiệp vụ quan trọng

**`nguoi_dung_service.py`** — MỚI
```python
def dang_ky(conn, ten_dang_nhap, mat_khau_ro, ...) -> NguoiDung:
    # bcrypt.hashpw() — không lưu mật khẩu rõ
    # is_active=0, is_approved=0 → chờ ADMIN duyệt

def xac_thuc(conn, ten_dang_nhap, mat_khau_ro) -> NguoiDung | None:
    # bcrypt.checkpw()

def duyet_nguoi_dung(conn, user_id, admin_id) -> bool:
    # Chỉ ADMIN mới duyệt được

def kiem_tra_quyen(nguoi_dung: NguoiDung, quyen_can: str) -> bool:
    # ADMIN > BIEN_TAP > XEM
```

**`doan_tuyen_service.py`** — Validation đã chuyển từ Model sang đây
```python
def them_doan_tuyen(conn, ...) -> int:
    # Validate: ly_trinh_cuoi > ly_trinh_dau
    # Validate: rong_mat_max >= rong_mat_min
    # Validate: rong_nen_max >= rong_nen_min
    # Validate: tuyen_id tồn tại
    # Validate: ma_doan chưa tồn tại
    # Trigger tự chạy sau INSERT → cập nhật chieu_dai tuyến

def cap_nhat_tinh_trang(conn, doan_id, tinh_trang_id, nguoi_dung_id) -> bool:
    # Cập nhật ngay_cap_nhat_tinh_trang, updated_by_id, updated_at
```

**`doan_di_chung_service.py`** — Validation lý trình 2 chiều
```python
def them_doan_di_chung(conn, ...) -> int:
    # 1. tuyen_di_chung_id phải tồn tại
    # 2. tuyen_chinh_id phải tồn tại
    # 3. doan_id phải tồn tại
    # 4. Đoạn KHÔNG được thuộc chính tuyến đi nhờ (tránh tự-tham chiếu)
    # 5. Cặp (tuyen_di_chung_id, doan_id) chưa tồn tại
    # 6. Trigger tự chạy → cập nhật chieu_dai_thuc_te của tuyến đi nhờ
```

**`tuyen_duong_geo_service.py`** — MỚI
```python
def import_tu_geojson(conn, duong_dan_file: str, tuyen_id: int) -> bool:
    # Đọc file *.geojson → trích tọa độ → lưu vào tuyen_duong_geo

def xuat_ra_geojson(conn, tuyen_id: int, duong_dan_output: str) -> bool:
    # Lấy từ DB → xuất file GeoJSON chuẩn

def lay_toa_do_cho_ban_do(conn, tuyen_ids: list[int]) -> dict:
    # Trả về dict {tuyen_id: [[lng, lat], ...]} cho Leaflet.js
```

**`hinh_anh_service.py`** — MỚI
```python
def luu_hinh_anh(conn, doan_id, file_path, ...) -> HinhAnhDoanTuyen:
    # Dùng Pillow để đọc EXIF → trích lat, lng nếu có GPS
    # Lưu vào hinh_anh_doan_tuyen

def tinh_ly_trinh_tu_gps(conn, doan_id, lat, lng) -> float | None:
    # Giai đoạn 2: nội suy từ đường tâm tuyến
```

**`thong_ke_service.py`** — Báo cáo tổng hợp
```python
def lay_thong_ke_cap_ky_thuat(conn) -> dict:
    # → { "QL": { ten, tong_km, chi_tiet: [cap_duong...] }, "DT": {...} }

def lay_thong_ke_theo_ket_cau_mat(conn) -> dict:
    # MỚI → thống kê km theo BTN, BTXM, HH...

def lay_thong_ke_theo_tinh_trang(conn) -> dict:
    # → km TOT, TB, KEM, HH_NANG theo từng cấp quản lý

def lay_chi_tiet_tung_tuyen(conn) -> dict:
    # → { tuyen_id: { tuyen, cap_ky_thuat, doan_chinh, doan_di_chung } }
```

---

## 7. DATA FILES + SEEDS

### Nguồn sự thật: file Excel (10 sheets)

| Sheet | Số bản ghi | Ghi chú |
|---|---|---|
| CapQuanLy | 8 | |
| CapDuong | 7 | |
| KetCauMat | 8 | |
| TinhTrang | 9 | |
| DonVi | 17 | parent_id dùng mã (SXD) — seed tra ra id thực |
| NguoiDung | 3 | Chỉ lưu thông tin — mật khẩu bcrypt khi seed |
| TuyenDuong | 49 | |
| ThongTinTuyen | 9 đầy đủ | 40 còn thiếu — bổ sung qua web |
| DoanTuyen | 222 | |
| DoanDiChung | 15 | Đã tách đúng từng đoạn vật lý |

### Tools tạo data files

```bash
# Chuyển Excel → 9 file data/*.py
python tools/excel_to_data.py

# Import GeoJSON vào DB
python tools/import_geojson.py map/QL4E_merged.geojson --tuyen QL4E

# Xuất GeoJSON từ DB
python tools/export_geojson.py --tuyen QL4E --output map/QL4E.geojson
```

### Thứ tự seed BẮT BUỘC

```python
# seeds/seed_all.py — chạy trong 1 transaction, rollback toàn bộ nếu lỗi
seed_danh_muc()    # 1. cap_quan_ly, cap_duong, ket_cau_mat, tinh_trang
seed_don_vi()      # 2. Cây cha-con (TINH trước, SXD sau, CT cuối)
seed_nguoi_dung()  # 3. bcrypt hash mật khẩu
seed_tuyen_duong() # 4. 49 tuyến + thong_tin_tuyen
seed_doan_tuyen()  # 5. 222 đoạn → trigger cập nhật chieu_dai_quan_ly
seed_doan_di_chung() # 6. 15 DDC → trigger cập nhật chieu_dai_thuc_te
```

Tất cả dùng `INSERT OR IGNORE` — có thể chạy lại nhiều lần (idempotent).

---

## 8. TOOLS

### tools/excel_to_data.py
- Đọc `data/giao_thong_data_upadate.xlsx` (10 sheets)
- Tạo/cập nhật 9 file `data/*_data.py`
- Xử lý đặc biệt: `don_vi_data.py` dùng mã thay id; `doan_di_chung_data.py` sinh mã tự động
- Bỏ qua dòng trống

### tools/import_geojson.py
- Đọc file `*.geojson` → trích `coordinates`
- Lưu vào bảng `tuyen_duong_geo` (Giai đoạn 1)
- Quy tắc tên file: `QL4E.geojson` → mã tuyến `QL4E`
- `road_name` trong file = tên tuyến trong DB

### tools/export_geojson.py
- Lấy tọa độ từ `tuyen_duong_geo`
- Xuất file GeoJSON chuẩn RFC 7946
- Hỗ trợ xuất 1 tuyến hoặc tất cả

### map/generate_map_multi_mahoa_onefile.py
- Đọc `*.geojson` → mã hóa 3 lớp: **Delta encoding → XOR (key 32 byte ngẫu nhiên) → Base64**
- Xuất 1 file HTML tích hợp Leaflet.js (self-contained)
- Hover/click → tính khoảng cách từ đầu tuyến
- 3 basemap: OSM, Topo, Vệ tinh

---

## 9. WEB APPLICATION — FASTAPI

### Cấu trúc API

```
api/main.py              → FastAPI app, CORS, startup, exception handler
api/routes/
    auth.py              → POST /dang-nhap, POST /dang-ky, POST /duyet/{id}
    tuyen_duong.py       → GET/POST /tuyen-duong, GET/PUT/DELETE /tuyen-duong/{id}
    doan_tuyen.py        → GET/POST /doan-tuyen, GET/PUT/DELETE /doan-tuyen/{id}
    thong_ke.py          → GET /thong-ke/cap-ky-thuat, GET /thong-ke/tung-tuyen
    ban_do.py            → GET /ban-do/geojson/{tuyen_id}
```

### Phân quyền 3 cấp

| Cấp | Quyền | Thao tác |
|---|---|---|
| `XEM` | Chỉ đọc | GET tất cả |
| `BIEN_TAP` | Thêm/sửa | GET + POST + PUT |
| `ADMIN` | Toàn quyền | GET + POST + PUT + DELETE + Duyệt user |

### Tính năng Web (đã hoàn thành)

1. Đăng nhập, phân quyền JWT
2. Xem danh sách tuyến, đoạn — thống kê cơ bản
3. Bản đồ Leaflet.js từ `tuyen_duong_geo`
4. CRUD tuyến, đoạn, DDC
5. Upload ảnh, đọc EXIF GPS (Pillow)
6. Import/Export GeoJSON và Excel

---

## 10. LUỒNG DỮ LIỆU TỔNG THỂ

```
NGUỒN THỰC TẾ (Khảo sát hiện trường)
    ↓
giao_thong_data_upadate.xlsx (10 sheets — nguồn sự thật)
    ↓
tools/excel_to_data.py → data/*_data.py (9 file Python config)
    ↓
seeds/seed_all.py → gọi services → gọi repositories
    ↓
database/giao_thong.db (SQLite — 13 bảng)
    ↑                           ↑
map/*.geojson                   │
    ↓                           │
tools/import_geojson.py → tuyen_duong_geo
                                │
                         thong_ke_repository.py (JOIN phức tạp)
                                ↓
                         thong_ke_service.py
                                ↓
                         api/routes/thong_ke.py
                                ↓
                         templates/ (Jinja2 + Leaflet.js)
                                ↓
                         Web Browser (ADMIN/BIEN_TAP/XEM)
```

---

## 11. HẠN CHẾ VÀ VẤN ĐỀ MỞ

### A. Dữ liệu còn thiếu

| Vấn đề | Mức độ | Hướng xử lý |
|---|---|---|
| 40 tuyến DT/DX chưa có `ThongTinTuyen` | Trung bình | Bổ sung dần qua Web BIEN_TAP |
| Chỉ có 2 file GeoJSON (QL4E, DT158) | Cao | Thu thập GPS từng tuyến theo ưu tiên |
| `nam_lam_moi`, `ngay_cap_nhat_tinh_trang` phần lớn NULL | Trung bình | Nhập dần qua khảo sát thực tế |
| `hinh_anh_doan_tuyen` chưa có dữ liệu | Thấp | Giai đoạn 2 |

### B. Hạn chế kỹ thuật

| Vấn đề | Mức độ | Ghi chú |
|---|---|---|
| SQLite không phù hợp multi-user đồng thời ghi | Cao | Cân nhắc PostgreSQL khi triển khai |
| Giai đoạn 2 GeoJSON theo đoạn chưa có thuật toán nội suy | Cao | Cần algo lý trình → tọa độ |
| `ly_trinh_anh` ảnh (từ EXIF GPS) chưa tính được | Trung bình | Cần đường tâm tuyến + Shapely |
| Chưa có API public (chỉ nội bộ SXD) | Thấp | Xem xét giai đoạn 3 |
| Không có lịch sử thay đổi (audit log) chi tiết | Trung bình | Chỉ có `updated_at`, `updated_by_id` |
| Chưa triển khai VPS | Cao | Vẫn đang test trên WSL/local |

### C. Các TODO đã biết (DDC tuyến chủ thuộc tỉnh khác)

Không thể nhập vào DB vì tuyến chủ không thuộc Lào Cai:
- QL4E đi nhờ QL4D Km79.757→82.957
- QL32 đi nhờ QL37 Km162→172
- DT155 đi nhờ QL4D Km43.5→47.1
- DT159 đi nhờ QL4 nhiều đoạn

---

## 12. ĐỀ XUẤT TIẾN ĐỘ DỰ ÁN TIẾP THEO

### Ưu tiên 1 — Triển khai và vận hành (Ngắn hạn)

| # | Việc cần làm | Ước thời gian |
|---|---|---|
| 1.1 | Test end-to-end trên WSL: seed → web → CRUD | 1 buổi |
| 1.2 | Deploy lên VPS (Ubuntu + Nginx + systemd) | 1 buổi |
| 1.3 | Cấu hình HTTPS (Let's Encrypt) | 0.5 buổi |
| 1.4 | Tạo tài khoản ADMIN thực tế cho SXD | 0.5 buổi |

### Ưu tiên 2 — Thu thập dữ liệu GeoJSON (Trung hạn)

| # | Việc cần làm | Ghi chú |
|---|---|---|
| 2.1 | Thu thập GeoJSON cho 9 QL (9 tuyến) | Ưu tiên cao nhất |
| 2.2 | Thu thập GeoJSON cho 27 DT | Từng tuyến, nhập dần |
| 2.3 | Nhập `ThongTinTuyen` còn thiếu (40 tuyến) | Qua giao diện Web |
| 2.4 | Cập nhật tình trạng mặt đường theo khảo sát | Qua giao diện Web |

### Ưu tiên 3 — Nâng cấp kỹ thuật (Trung hạn)

| # | Việc cần làm | Ghi chú |
|---|---|---|
| 3.1 | Thuật toán nội suy GeoJSON theo đoạn (Giai đoạn 2) | Shapely + lý trình → tọa độ |
| 3.2 | Tính `ly_trinh_anh` từ EXIF GPS | Cần đường tâm tuyến đủ |
| 3.3 | Xuất báo cáo Excel/PDF từ Web | openpyxl + ReportLab |
| 3.4 | Audit log chi tiết (lịch sử thay đổi từng đoạn) | Bảng `lich_su_thay_doi` |

### Ưu tiên 4 — Mở rộng (Dài hạn)

| # | Việc cần làm | Ghi chú |
|---|---|---|
| 4.1 | Chuyển sang PostgreSQL | Multi-user, production-grade |
| 4.2 | App mobile (PWA hoặc React Native) | Nhập liệu ngoài hiện trường |
| 4.3 | Tích hợp GPS thiết bị (nhập tọa độ trực tiếp) | — |
| 4.4 | Dashboard thống kê trực quan (Chart.js/D3) | Heatmap tình trạng đường |
| 4.5 | Kết nối dữ liệu với Bộ GTVT | API chuẩn quốc gia (nếu có) |

---

## PHỤ LỤC — QUICK REFERENCE CHO PHIÊN LÀM VIỆC MỚI

### Khởi động nhanh

```bash
cd D:\Dropbox\@Giaothong2
python seeds/seed_all.py        # Seed dữ liệu (idempotent)
python main.py                  # Chạy báo cáo console
uvicorn api.main:app --reload   # Chạy web dev
```

### Thêm tuyến mới

1. Thêm vào `data/giao_thong_data_upadate.xlsx` (sheet TuyenDuong)
2. Chạy `python tools/excel_to_data.py`
3. Chạy `python seeds/seed_all.py` (INSERT OR IGNORE — an toàn)

### Thêm đoạn tuyến mới

Tương tự — thêm vào sheet DoanTuyen → excel_to_data → seed_all.

### Lỗi thường gặp

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| `trigger không cập nhật chieu_dai` | Dùng hàm thủ công cũ | Chỉ cần gọi INSERT/UPDATE đoạn — trigger tự chạy |
| `UNIQUE constraint failed` | Mã tuyến/đoạn trùng | Kiểm tra dữ liệu Excel |
| `column not found` | Dùng `row[index]` cũ | Chuyển sang `row["ten_cot"]` |
| `ImportError: circular import` | Dùng `from ... import` | Đổi sang `import ... as` alias |

---

*Tài liệu này là nguồn tham khảo kỹ thuật đầy đủ của dự án tại thời điểm 22/03/2026.*
*Cập nhật khi có thay đổi kiến trúc hoặc thêm tính năng mới.*
