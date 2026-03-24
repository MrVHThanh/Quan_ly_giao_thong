# DỰ ÁN QUẢN LÝ TUYẾN ĐƯỜNG BỘ TỈNH LÀO CAI
## Hệ thống quản lý đường bộ — Sở Xây dựng tỉnh Lào Cai

> **Ngôn ngữ:** Python 3.10+ · **Database:** SQLite · **Web:** FastAPI + Jinja2
> **Thư mục gốc:** `D:\Dropbox\@Giaothong2\` · **Database file:** `database/giao_thong.db`
> **Trạng thái:** Hoàn thành đầy đủ 8/8 bước — sẵn sàng triển khai

---

## MỤC LỤC

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Số liệu thực tế đã xác nhận](#2-số-liệu-thực-tế-đã-xác-nhận)
3. [Kiến trúc tổng thể](#3-kiến-trúc-tổng-thể)
4. [Sơ đồ thư mục đầy đủ](#4-sơ-đồ-thư-mục-đầy-đủ)
5. [Cơ sở dữ liệu — 13 bảng, 6 triggers, 5 indexes](#5-cơ-sở-dữ-liệu)
6. [Tầng Models (13 files)](#6-tầng-models)
7. [Tầng Repositories (13 files)](#7-tầng-repositories)
8. [Tầng Services (13 files)](#8-tầng-services)
9. [Data Config + Seeds](#9-data-config--seeds)
10. [Migrations](#10-migrations)
11. [Tools — Công cụ phụ trợ](#11-tools--công-cụ-phụ-trợ)
12. [Web Application — FastAPI](#12-web-application--fastapi)
13. [Bản đồ GeoJSON + Leaflet](#13-bản-đồ-geojson--leaflet)
14. [Luồng dữ liệu tổng thể](#14-luồng-dữ-liệu-tổng-thể)
15. [Quy tắc lập trình bắt buộc](#15-quy-tắc-lập-trình-bắt-buộc)
16. [Cài đặt & khởi chạy](#16-cài-đặt--khởi-chạy)

---

## 1. TỔNG QUAN DỰ ÁN

Hệ thống quản lý toàn bộ tuyến đường bộ do **Sở Xây dựng tỉnh Lào Cai** quản lý, bao gồm:
- **49 tuyến đường** (9 Quốc lộ + 27 Đường tỉnh + 13 Đường xã/khác)
- **222 đoạn tuyến** vật lý với đầy đủ thông tin kỹ thuật
- **15 đoạn đi chung** (một tuyến đi nhờ vật lý của tuyến khác)
- Giao diện **Web FastAPI** với phân quyền 3 cấp (ADMIN / BIÊN TẬP / XEM)
- **Bản đồ Leaflet.js** tương tác từ dữ liệu GeoJSON
- Xuất/nhập dữ liệu qua **Excel** và **GeoJSON**

---

## 2. SỐ LIỆU THỰC TẾ ĐÃ XÁC NHẬN

| Hạng mục | Số lượng | Chi tiết |
|---|---|---|
| Tuyến đường | **49** | 9 QL + 27 DT + 13 DX |
| Đoạn tuyến | **222** | Đoạn vật lý cơ sở |
| Đoạn đi chung | **15** | Mỗi bản ghi = 1 đoạn vật lý |
| Bảng DB | **13** | Tăng từ 6 bảng ban đầu |
| Triggers SQLite | **6** | Tự động cập nhật chiều dài |
| Indexes | **5** | Tối ưu JOIN và WHERE |
| Đơn vị | **17** | TINH → SXD → BAN_BT + 13 CT độc lập |
| Kết cấu mặt đường | **8** | BTN, BTXM, HH, LN, CP, DAT, BTN+LN, BTXM+LN |
| Tình trạng mặt đường | **9** | TOT, TB, KEM, HH_NANG, THI_CONG, BAO_TRI, TAM_DONG, NGUNG, CHUA_XD |
| File GeoJSON hiện có | **2** | QL4E (5039 điểm), DT158 (4274 điểm) |

---

## 3. KIẾN TRÚC TỔNG THỂ

### Mô hình 4 tầng (Layered Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                    WEB LAYER (FastAPI)                      │
│  api/main.py  →  api/routes/  →  templates/  →  static/     │
│  auth | tuyen_duong | doan_tuyen | doan_di_chung             │
│  thong_ke | ban_do                                           │
└──────────────────────────┬──────────────────────────────────┘
                           │ gọi
┌──────────────────────────▼──────────────────────────────────┐
│              SERVICE LAYER (Business Logic)                 │
│  Validate · Transform · Orchestrate · Authorize             │
│  13 services — TOÀN BỘ nghiệp vụ nằm ở đây                │
└──────────────────────────┬──────────────────────────────────┘
                           │ gọi
┌──────────────────────────▼──────────────────────────────────┐
│            REPOSITORY LAYER (Data Access)                   │
│  SQL thuần · sqlite3.Row · KHÔNG chứa logic nghiệp vụ      │
│  13 repositories — mỗi file tương ứng 1 bảng DB            │
└──────────────────────────┬──────────────────────────────────┘
                           │ truy cập
┌──────────────────────────▼──────────────────────────────────┐
│              DATABASE LAYER (SQLite)                        │
│  13 bảng · 6 triggers · 5 indexes                          │
│  database/giao_thong.db                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. SƠ ĐỒ THƯ MỤC ĐẦY ĐỦ

```
@Giaothong2/
│
├── config/
│   ├── database.py              # get_connection(), create_tables(), get_db(), drop_all_tables()
│   └── settings.py              # BASE_DIR, DB_PATH, cấu hình chung
│
├── models/                      # Plain Objects — KHÔNG logic DB, KHÔNG validate
│   ├── cap_quan_ly.py           # CapQuanLy
│   ├── cap_duong.py             # CapDuong
│   ├── ket_cau_mat_duong.py     # KetCauMatDuong
│   ├── tinh_trang.py            # TinhTrang
│   ├── don_vi.py                # DonVi
│   ├── nguoi_dung.py            # NguoiDung (bcrypt hash)
│   ├── tuyen_duong.py           # TuyenDuong + @property toa_do_dau/cuoi
│   ├── thong_tin_tuyen.py       # ThongTinTuyen (metadata mô tả tuyến)
│   ├── doan_tuyen.py            # DoanTuyen + @property chieu_dai, chieu_dai_tinh
│   ├── doan_di_chung.py         # DoanDiChung + @property chieu_dai
│   ├── hinh_anh_doan_tuyen.py   # HinhAnhDoanTuyen (đường dẫn + EXIF GPS)
│   ├── tuyen_duong_geo.py       # TuyenDuongGeo (tọa độ GeoJSON Giai đoạn 1)
│   └── thong_ke.py              # ThongKeToanTinh, ThongKeMoiTuyen (aggregate)
│
├── repositories/                # SQL thuần — sqlite3.Row, KHÔNG dùng index cứng
│   ├── cap_quan_ly_repository.py
│   ├── cap_duong_repository.py
│   ├── ket_cau_mat_duong_repository.py
│   ├── tinh_trang_repository.py
│   ├── don_vi_repository.py
│   ├── nguoi_dung_repository.py
│   ├── tuyen_duong_repository.py
│   ├── thong_tin_tuyen_repository.py
│   ├── doan_tuyen_repository.py
│   ├── doan_di_chung_repository.py
│   ├── hinh_anh_doan_tuyen_repository.py
│   ├── tuyen_duong_geo_repository.py
│   └── thong_ke_repository.py   # 3 query JOIN phức tạp
│
├── services/                    # Toàn bộ validate + business logic
│   ├── cap_quan_ly_service.py
│   ├── cap_duong_service.py
│   ├── ket_cau_mat_duong_service.py
│   ├── tinh_trang_service.py
│   ├── don_vi_service.py
│   ├── nguoi_dung_service.py    # bcrypt, phân quyền, duyệt tài khoản
│   ├── tuyen_duong_service.py
│   ├── thong_tin_tuyen_service.py
│   ├── doan_tuyen_service.py    # validate lý trình + cập nhật chiều dài
│   ├── doan_di_chung_service.py # validate chống tự-tham chiếu
│   ├── hinh_anh_doan_tuyen_service.py
│   ├── tuyen_duong_geo_service.py
│   └── thong_ke_service.py      # tổng hợp báo cáo toàn tỉnh và từng tuyến
│
├── data/                        # Config Python — nguồn sự thật (từ Excel)
│   ├── cap_quan_ly_data.py      # CAP_QUAN_LY_CONFIG (8)
│   ├── cap_duong_data.py        # CAP_DUONG_CONFIG (7)
│   ├── ket_cau_mat_data.py      # KET_CAU_MAT_CONFIG (8)
│   ├── tinh_trang_data.py       # TINH_TRANG_CONFIG (9)
│   ├── don_vi_data.py           # DON_VI_CONFIG (17)
│   ├── nguoi_dung_data.py       # NGUOI_DUNG_CONFIG (3 tài khoản mặc định)
│   ├── tuyen_duong_data.py      # TUYEN_CONFIG (49 tuyến)
│   ├── thong_tin_tuyen_data.py  # THONG_TIN_TUYEN_CONFIG
│   ├── doan_tuyen_data.py       # DOAN_CONFIG (222 đoạn)
│   ├── doan_di_chung_data.py    # DOAN_DI_CHUNG_CONFIG (15 đoạn đi chung)
│   └── giao_thong_data_upadate.xlsx  # File Excel nguồn (10 sheets)
│
├── seeds/                       # Khởi tạo dữ liệu — idempotent
│   ├── seed_all.py              # Gọi tất cả theo đúng thứ tự
│   ├── seed_danh_muc.py         # cap_quan_ly, cap_duong, ket_cau_mat, tinh_trang
│   ├── seed_don_vi.py           # 17 đơn vị (cây cha-con)
│   ├── seed_nguoi_dung.py       # 3 tài khoản mặc định (bcrypt)
│   └── seed_tuyen_doan.py       # 49 tuyến + 222 đoạn + 15 DDC
│
├── migrations/
│   └── m001_initial_schema.py   # up() / down() — 13 bảng, 6 triggers, 5 indexes
│
├── tools/                       # Công cụ tiện ích
│   ├── excel_to_data.py         # Excel (10 sheets) → 9 file data/*.py
│   ├── import_geojson.py        # *.geojson → bảng tuyen_duong_geo
│   └── export_geojson.py        # DB → xuất file *.geojson (RFC 7946)
│
├── api/                         # Web Application FastAPI
│   ├── main.py                  # FastAPI app, mount routes, Jinja2 filters
│   └── routes/
│       ├── _auth_helper.py      # Session cookie HMAC (không JWT)
│       ├── auth.py              # /auth/* — đăng nhập, đăng ký, duyệt
│       ├── tuyen_duong_route.py # /tuyen-duong/*
│       ├── doan_tuyen_route.py  # /doan-tuyen/*
│       ├── doan_di_chung_route.py  # /doan-di-chung/*
│       ├── thong_ke.py          # /thong-ke/*
│       └── ban_do.py            # /ban-do/*
│
├── templates/                   # Jinja2 HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── thong_ke.html
│   ├── ban_do.html
│   ├── auth/
│   │   ├── login.html
│   │   └── dang_ky.html
│   ├── tuyen_duong/
│   │   ├── danh_sach.html
│   │   ├── chi_tiet.html
│   │   └── form.html
│   └── doan_tuyen/
│       ├── danh_sach.html
│       ├── chi_tiet.html
│       └── form.html
│
├── static/                      # CSS, JS, ảnh tĩnh
│   ├── css/
│   └── js/
│
├── map/
│   ├── QL4E_merged.geojson      # 5039 điểm tọa độ
│   ├── TL158_merged.geojson     # (DT158) 4274 điểm tọa độ
│   └── generate_map_multi_mahoa_onefile.py  # Sinh HTML bản đồ Leaflet self-contained
│
├── database/
│   └── giao_thong.db            # File SQLite (trong .gitignore)
│
├── main.py                      # Script chạy báo cáo ra console (dev/test)
├── requirements.txt             # Dependencies đã pin version
└── PROJECT_STRUCTURE.md         # File này
```

---

## 5. CƠ SỞ DỮ LIỆU

### 5.1. Danh sách 13 bảng (theo thứ tự phụ thuộc FK)

| # | Tên bảng | Bản ghi | Mô tả |
|---|---|---|---|
| 1 | `cap_quan_ly` | 8 | Cấp quản lý: QL, DT, DH, DX, DD, DDB... |
| 2 | `cap_duong` | 7 | Cấp kỹ thuật: Cấp III, IV, V, VI miền núi... |
| 3 | `ket_cau_mat_duong` | 8 | BTN, BTXM, HH, LN, CP, DAT, BTN+LN, BTXM+LN |
| 4 | `tinh_trang` | 9 | TOT, TB, KEM, HH_NANG, THI_CONG, BAO_TRI... |
| 5 | `don_vi` | 17 | Cây cha-con: TINH → SXD → BAN_BT + 13 CT |
| 6 | `nguoi_dung` | 3+ | Tài khoản đăng nhập, mật khẩu bcrypt, phân quyền |
| 7 | `tuyen_duong` | 49 | Tuyến đường chính, tọa độ GPS đầu/cuối |
| 8 | `thong_tin_tuyen` | 49+ | Metadata mô tả bổ sung cho từng tuyến |
| 9 | `doan_tuyen` | 222 | Đoạn vật lý, lý trình, kích thước mặt/nền |
| 10 | `doan_di_chung` | 15 | Tuyến đi nhờ vật lý của tuyến khác |
| 11 | `hinh_anh_doan_tuyen` | — | Ảnh hiện trường + EXIF GPS |
| 12 | `tuyen_duong_geo` | 2+ | Tọa độ GeoJSON tuyến (Giai đoạn 1) |
| 13 | `doan_tuyen_geo` | — | Tọa độ GeoJSON đoạn (Giai đoạn 2 — tạo sẵn) |

### 5.2. Schema các bảng quan trọng

**`tuyen_duong`**
```
id, ma_tuyen, ten_tuyen, cap_quan_ly_id, don_vi_quan_ly_id,
diem_dau, diem_cuoi, lat_dau, lng_dau, lat_cuoi, lng_cuoi,
chieu_dai_thuc_te,    ← trigger tự cập nhật: tổng đoạn chính + đi chung
chieu_dai_quan_ly,    ← trigger tự cập nhật: chỉ tổng đoạn chính
nam_xay_dung, nam_hoan_thanh, ghi_chu, created_at
```

**`doan_tuyen`**
```
id, ma_doan, tuyen_id, cap_duong_id, tinh_trang_id, ket_cau_mat_id,
ly_trinh_dau, ly_trinh_cuoi,
chieu_dai_thuc_te,
chieu_rong_mat_min, chieu_rong_mat_max,
chieu_rong_nen_min, chieu_rong_nen_max,
don_vi_bao_duong_id,
nam_lam_moi,
ngay_cap_nhat_tinh_trang,
ghi_chu, created_at, updated_at, updated_by_id
```

**`doan_di_chung`**
```
id, tuyen_di_chung_id,   ← tuyến đi nhờ (FK → tuyen_duong)
doan_id,                  ← đoạn vật lý đi nhờ (FK → doan_tuyen)
ly_trinh_dau_di_chung,
ly_trinh_cuoi_di_chung,
ghi_chu, created_at
```

**`nguoi_dung`**
```
id, ten_dang_nhap, mat_khau_hash, ho_ten, chuc_vu,
don_vi_id, so_dien_thoai, email,
loai_quyen,     ← ADMIN | BIEN_TAP | XEM
is_active,      ← 0 = bị khóa
is_approved,    ← 0 = chờ ADMIN duyệt
created_at, last_login
```

### 5.3. Sơ đồ quan hệ (ERD rút gọn)

```
cap_quan_ly ──┐
              ├──→ tuyen_duong ──→ thong_tin_tuyen
don_vi ───────┘         │
                        │ 1:N
              ┌─────────▼─────────┐
              │    doan_tuyen     │←── cap_duong
              │                   │←── tinh_trang
              └───────────────────┘←── ket_cau_mat_duong
                        │ N:M (qua doan_di_chung)
                        │
              ┌─────────▼─────────┐
              │  doan_di_chung    │←── tuyen_di_chung (FK tuyen_duong)
              └───────────────────┘

tuyen_duong ──→ tuyen_duong_geo (tọa độ GeoJSON)
doan_tuyen  ──→ hinh_anh_doan_tuyen (ảnh hiện trường)
doan_tuyen  ──→ doan_tuyen_geo (Giai đoạn 2)
```

### 5.4. 6 SQLite Triggers — tự động cập nhật chiều dài

| Trigger | Bảng nguồn | Sự kiện | Cập nhật |
|---|---|---|---|
| `trg_dt_sau_them` | `doan_tuyen` | AFTER INSERT | `tuyen_duong.chieu_dai_quan_ly` + `chieu_dai_thuc_te` |
| `trg_dt_sau_sua` | `doan_tuyen` | AFTER UPDATE | `tuyen_duong.chieu_dai_quan_ly` + `chieu_dai_thuc_te` |
| `trg_dt_sau_xoa` | `doan_tuyen` | AFTER DELETE | `tuyen_duong.chieu_dai_quan_ly` + `chieu_dai_thuc_te` |
| `trg_ddc_sau_them` | `doan_di_chung` | AFTER INSERT | `tuyen_duong.chieu_dai_thuc_te` |
| `trg_ddc_sau_sua` | `doan_di_chung` | AFTER UPDATE | `tuyen_duong.chieu_dai_thuc_te` |
| `trg_ddc_sau_xoa` | `doan_di_chung` | AFTER DELETE | `tuyen_duong.chieu_dai_thuc_te` |

**Logic tính chiều dài:**
```sql
-- chieu_dai_quan_ly = SUM đoạn chính (COALESCE thực_tế or lý trình)
chieu_dai_quan_ly = ROUND(SUM(COALESCE(chieu_dai_thuc_te, ly_trinh_cuoi - ly_trinh_dau)), 3)

-- chieu_dai_thuc_te = chieu_dai_quan_ly + SUM đoạn đi chung
chieu_dai_thuc_te = chieu_dai_quan_ly + ROUND(SUM(ly_trinh_cuoi_di_chung - ly_trinh_dau_di_chung), 3)
```

### 5.5. 5 Indexes

```sql
idx_doan_tuyen_tuyen_id       ON doan_tuyen(tuyen_id)
idx_doan_tuyen_cap_duong_id   ON doan_tuyen(cap_duong_id)
idx_doan_tuyen_tinh_trang_id  ON doan_tuyen(tinh_trang_id)
idx_ddc_tuyen_di_chung_id     ON doan_di_chung(tuyen_di_chung_id)
idx_ddc_doan_id               ON doan_di_chung(doan_id)
```

---

## 6. TẦNG MODELS

Models là **Plain Objects** — chỉ lưu dữ liệu, không truy vấn DB, không validate nghiệp vụ.

### TuyenDuong (`models/tuyen_duong.py`)
```python
@property toa_do_dau → [lat_dau, lng_dau]
@property toa_do_cuoi → [lat_cuoi, lng_cuoi]
```

### DoanTuyen (`models/doan_tuyen.py`)
```python
@property chieu_dai → ly_trinh_cuoi - ly_trinh_dau
@property chieu_dai_tinh → chieu_dai_thuc_te or chieu_dai   # ưu tiên thực tế
```

### DoanDiChung (`models/doan_di_chung.py`)
```python
@property chieu_dai → ly_trinh_cuoi_di_chung - ly_trinh_dau_di_chung
```

### ThongKeToanTinh (`models/thong_ke.py`)
```python
tong_so_tuyen, tong_so_doan, tong_so_doan_di_chung
tong_chieu_dai_quan_ly, tong_chieu_dai_thuc_te, tong_chieu_dai_di_chung
theo_cap_quan_ly, theo_tinh_trang, theo_ket_cau_mat, theo_cap_duong  # dict
```

### ThongKeMoiTuyen (`models/thong_ke.py`)
```python
ma_tuyen, ten_tuyen, tong_so_doan
chieu_dai_quan_ly, chieu_dai_thuc_te
chieu_dai_tot, chieu_dai_tb, chieu_dai_kem, chieu_dai_hu_hong_nang, chieu_dai_thi_cong
chieu_dai_btn, chieu_dai_btxm, chieu_dai_hh, chieu_dai_ln, chieu_dai_cp, chieu_dai_dat
chieu_dai_btn_ln, chieu_dai_btxm_ln
```

### NguoiDung (`models/nguoi_dung.py`)
```python
# loai_quyen: "ADMIN" | "BIEN_TAP" | "XEM"
# mat_khau_hash: bcrypt (không bao giờ lưu rõ)
# is_approved: 0 = chờ duyệt, 1 = đã duyệt
```

---

## 7. TẦNG REPOSITORIES

**Nguyên tắc:** SQL thuần, dùng `sqlite3.Row` (truy cập bằng tên cột, không dùng index số), không chứa logic nghiệp vụ.

### Cấu trúc chuẩn mỗi repository

```python
_SELECT_COLS = "id, ma_*, ten_*, ..."   # chuỗi SELECT cố định

def _row_to_object(row) -> Model:       # sqlite3.Row → Object (dùng row["ten_cot"])
    ...

def lay_tat_ca(conn) -> list[Model]: ...
def lay_theo_ma(conn, ma: str) -> Model | None: ...
def lay_theo_id(conn, id: int) -> Model | None: ...
def them_*(conn, ...) -> int:           # trả lastrowid
def cap_nhat_*(conn, ...) -> bool: ...
def xoa_mem_*(conn, id) -> bool:        # soft delete: is_active = 0
def khoi_phuc_*(conn, id) -> bool:      # is_active = 1
```

### thong_ke_repository.py — 3 query tổng hợp phức tạp

```python
lay_thong_ke_toan_tinh(conn)
# → ThongKeToanTinh với COUNT, SUM, GROUP BY toàn bộ các chiều

lay_thong_ke_mot_tuyen(conn, tuyen_id)
# → ThongKeMoiTuyen với chiều dài theo từng tình trạng và kết cấu mặt
```

---

## 8. TẦNG SERVICES

**Nguyên tắc:** Toàn bộ business logic + validation nằm ở đây. Model và Repository không validate.

### Cấu trúc chuẩn mỗi service

```python
def lay_tat_ca(conn) -> list[Model]: ...
def lay_theo_ma(conn, ma: str) -> Model | None: ...
def lay_theo_id(conn, id: int) -> Model | None: ...
def them_*(conn, ...) -> int:           # validate → gọi repo → trả id
def cap_nhat_*(conn, ...) -> bool: ...
def xoa_mem_*(conn, id) -> bool: ...
def get_or_create_*(conn, ma) -> tuple[Model, bool]:  # dùng trong seed
```

### Nghiệp vụ quan trọng theo từng service

#### `nguoi_dung_service.py`
```python
def dang_ky(conn, ten_dang_nhap, mat_khau_ro, ...) -> NguoiDung:
    # bcrypt.hashpw() — không lưu mật khẩu rõ
    # is_active=0, is_approved=0 → chờ ADMIN duyệt

def dang_nhap(conn, ten_dang_nhap, mat_khau_ro) -> NguoiDung | None:
    # bcrypt.checkpw() — raise DangNhapThatBaiError nếu sai

def duyet_nguoi_dung(conn, user_id, admin_id) -> bool:
    # Chỉ ADMIN mới gọi được hàm này (kiểm tra ở service)
```

#### `doan_tuyen_service.py`
```python
def them_doan_tuyen(conn, ...) -> int:
    # Validate: ly_trinh_cuoi > ly_trinh_dau
    # Validate: rong_mat_max >= rong_mat_min
    # Validate: rong_nen_max >= rong_nen_min
    # Validate: tuyen_id tồn tại
    # Validate: ma_doan chưa tồn tại
    # → INSERT → trigger tự cập nhật chieu_dai tuyến

def cap_nhat_tinh_trang(conn, doan_id, tinh_trang_id, nguoi_dung_id) -> bool:
    # Cập nhật ngay_cap_nhat_tinh_trang, updated_by_id, updated_at
```

#### `doan_di_chung_service.py`
```python
def them_doan_di_chung(conn, ...) -> int:
    # 1. tuyen_di_chung_id phải tồn tại
    # 2. tuyen_chinh (của doan) phải tồn tại
    # 3. doan_id phải tồn tại
    # 4. Đoạn KHÔNG được thuộc chính tuyến đang đi nhờ (tránh tự-tham chiếu)
    # 5. Cặp (tuyen_di_chung_id, doan_id) chưa tồn tại
    # → INSERT → trigger tự cập nhật chieu_dai_thuc_te
```

#### `thong_ke_service.py`
```python
def lay_thong_ke_toan_tinh(conn) -> ThongKeToanTinh:
    # Gọi repo → trả object tổng hợp toàn tỉnh

def lay_thong_ke_mot_tuyen(conn, tuyen_id) -> ThongKeMoiTuyen:
    # Gọi repo → chiều dài phân theo tình trạng & kết cấu mặt của 1 tuyến
```

---

## 9. DATA CONFIG + SEEDS

### 9.1. Data Config — Nguồn sự thật

Toàn bộ dữ liệu thực tế được lưu dưới dạng Python dict trong `data/`, được sinh ra từ `data/giao_thong_data_upadate.xlsx` (10 sheets) bởi `tools/excel_to_data.py`.

**`tuyen_duong_data.py` — TUYEN_CONFIG (49 tuyến)**

```python
# 9 Quốc lộ: QL4, QL4D, QL4E, QL279, QL37, QL70, QL32C, QL2D, QL32
# 27 Đường tỉnh: DT151 → DT175B
# 13 Đường khác: DX01 → DX13
{
    "ma_tuyen", "ten_tuyen", "ma_cap_quan_ly",
    "chieu_dai_quan_ly",      # chiều dài theo hồ sơ
    "chieu_dai_thuc_te",      # None nếu chưa đo
    "ma_don_vi_quan_ly",      # None nếu chưa xác định
    "diem_dau", "diem_cuoi",
    "lat_dau", "lng_dau", "lat_cuoi", "lng_cuoi",  # None nếu chưa có GPS
    "nam_xay_dung", "nam_hoan_thanh", "ghi_chu"
}
```

**`doan_tuyen_data.py` — DOAN_CONFIG (222 đoạn)**

```python
{
    "ma_doan", "ma_tuyen", "ma_cap_duong",
    "ly_trinh_dau", "ly_trinh_cuoi",
    "chieu_dai_thuc_te",        # None nếu chưa đo
    "chieu_rong_mat_min", "chieu_rong_mat_max",
    "chieu_rong_nen_min", "chieu_rong_nen_max",
    "ma_ket_cau_mat",           # BTN, BTXM, HH...
    "ma_tinh_trang",            # TOT, TB, KEM...
    "ma_don_vi_bao_duong",      # None nếu chưa xác định
    "nam_lam_moi", "ghi_chu"
}
```

**`doan_di_chung_data.py` — DOAN_DI_CHUNG_CONFIG (15 đoạn)**

Các đoạn đi chung đã xác nhận, ví dụ:
- `QL4D` đi nhờ `QL70-05` (Km140.893 → 149)
- `QL4E` đi nhờ `QL70-01` (Km35.6 → 36.975)
- `DT153` đi nhờ `QL4E-04` (Km18.3 → 21.1)
- `DT159` đi nhờ `QL4E-08,09,10,11`
- `DT160` đi nhờ `QL279-11,12,13`
- `DT162` đi nhờ `DT151-03`
- `DX02` đi nhờ `DT173-01`

> ⚠️ **TODO chưa xử lý được** (tuyến chủ thuộc tỉnh khác, không có trong DB):
> QL4E đi nhờ QL4D Km79.757→82.957 · QL32 đi nhờ QL37 · DT155 đi nhờ QL4D

### 9.2. Seeds — Thứ tự bắt buộc

```python
# seeds/seed_all.py — phải chạy đúng thứ tự này:
seed_danh_muc()     # 1. cap_quan_ly + cap_duong + ket_cau_mat + tinh_trang
seed_don_vi()       # 2. 17 đơn vị (cây cha-con: TINH → SXD → BAN_BT → CT)
seed_nguoi_dung()   # 3. 3 tài khoản mặc định (bcrypt hash mật khẩu)
seed_tuyen_doan()   # 4. 49 tuyến + thong_tin_tuyen + 222 đoạn + 15 DDC
                    #    → trigger tự cập nhật chieu_dai_quan_ly và chieu_dai_thuc_te
```

**Tính chất:** Tất cả seed dùng `INSERT OR IGNORE` — có thể chạy lại nhiều lần (idempotent).

---

## 10. MIGRATIONS

**File:** `migrations/m001_initial_schema.py`

```python
def up(conn):
    # Tạo toàn bộ 13 bảng, 6 triggers, 5 indexes
    # Dùng CREATE TABLE IF NOT EXISTS — an toàn khi chạy lại

def down(conn):
    # Xóa toàn bộ bảng theo thứ tự ngược FK
    # CHỈ dùng khi development — KHÔNG dùng trên dữ liệu thật
```

`config/database.py` cũng cung cấp:
```python
create_tables(db_path)       # Gọi migration up() — tạo schema
drop_all_tables(db_path)     # DEVELOPMENT ONLY
get_schema_info(db_path)     # → { tables, indexes, triggers }
get_db(db_path)              # Generator cho FastAPI Depends
```

---

## 11. TOOLS — CÔNG CỤ PHỤ TRỢ

### `tools/excel_to_data.py`
- Đọc `data/giao_thong_data_upadate.xlsx` (10 sheets)
- Tạo/cập nhật 9 file `data/*_data.py`
- Xử lý đặc biệt: `don_vi_data.py` dùng mã thay vì id; `doan_di_chung_data.py` sinh mã tự động
- Bỏ qua mọi dòng trống khi đọc Excel

### `tools/import_geojson.py`
- Đọc file `*.geojson` → trích `coordinates`
- Lưu vào bảng `tuyen_duong_geo`
- Quy tắc tên file: `QL4E.geojson` → mã tuyến `QL4E`
- `road_name` trong GeoJSON = tên tuyến trong DB

### `tools/export_geojson.py`
- Lấy tọa độ từ bảng `tuyen_duong_geo`
- Xuất file GeoJSON chuẩn RFC 7946
- Hỗ trợ xuất 1 tuyến hoặc tất cả

---

## 12. WEB APPLICATION — FASTAPI

### 12.1. Khởi chạy

```bash
uvicorn api.main:app --reload
# Hoặc bind toàn bộ IP:
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- Health check: `GET /api/health`

### 12.2. Cấu trúc Routes

| Route | File | Endpoints |
|---|---|---|
| `/auth/*` | `auth.py` | GET/POST `/login`, GET/POST `/dang-ky`, GET/POST `/duyet/{id}`, GET `/logout` |
| `/tuyen-duong/*` | `tuyen_duong_route.py` | GET (list), POST, GET `/{id}`, PUT `/{id}`, DELETE `/{id}` |
| `/doan-tuyen/*` | `doan_tuyen_route.py` | GET (list), POST, GET `/{id}`, PUT `/{id}`, DELETE `/{id}` |
| `/doan-di-chung/*` | `doan_di_chung_route.py` | GET (list), POST, DELETE `/{id}` |
| `/thong-ke/*` | `thong_ke.py` | GET `/` (trang), GET `/api/toan-tinh`, GET `/api/tuyen/{id}` |
| `/ban-do/*` | `ban_do.py` | GET `/` (trang), GET `/geojson/{tuyen_id}` |

### 12.3. Phân quyền 3 cấp

| Quyền | Thao tác cho phép |
|---|---|
| `XEM` | GET tất cả (chỉ đọc) |
| `BIEN_TAP` | GET + POST + PUT |
| `ADMIN` | GET + POST + PUT + DELETE + Duyệt tài khoản |

### 12.4. Cơ chế xác thực

**Không dùng JWT** — dùng **session cookie có ký HMAC** (Python stdlib):

```python
# _auth_helper.py
SESSION_COOKIE = "gt_session"
SESSION_TTL = 86400 * 7  # 7 ngày

# Token format: base64(user_id:loai_quyen:timestamp).hmac_sha256
# SECRET_KEY: lấy từ biến môi trường SESSION_SECRET
```

**FastAPI Dependencies:**
```python
lay_user_hien_tai(request)    # → dict | None
yeu_cau_dang_nhap(user)       # → dict hoặc redirect /auth/login
yeu_cau_quyen_bien_tap(user)  # → dict hoặc 403
yeu_cau_quyen_admin(user)     # → dict hoặc 403
```

### 12.5. Jinja2 Custom Filter

```python
# Chuyển lý trình số thực → định dạng KmXXX+YYY
# Ví dụ: 190.0 → "Km190+000"  |  37.557 → "Km37+557"
{{ doan.ly_trinh_dau | format_ly_trinh }}
```

### 12.6. Tính năng Web đã hoàn thành

1. Đăng nhập, đăng ký, phân quyền (ADMIN / BIÊN TẬP / XEM)
2. Duyệt tài khoản — ADMIN phê duyệt tài khoản mới
3. Dashboard tổng quan toàn tỉnh
4. Danh sách + chi tiết + CRUD tuyến đường
5. Danh sách + chi tiết + CRUD đoạn tuyến
6. Quản lý đoạn đi chung
7. Trang thống kê (tổng tỉnh + từng tuyến, JSON API)
8. Bản đồ Leaflet.js từ dữ liệu `tuyen_duong_geo`
9. Upload ảnh hiện trường, đọc EXIF GPS (Pillow)
10. Import GeoJSON từ file `.geojson`
11. Export GeoJSON từ DB
12. Export báo cáo Excel

---

## 13. BẢN ĐỒ GEOJSON + LEAFLET

### 13.1. Dữ liệu GeoJSON trong DB (`tuyen_duong_geo`)

- Import bằng `tools/import_geojson.py`
- Quy tắc tên file: `QL4E.geojson` → tìm tuyến có `ma_tuyen = 'QL4E'`
- **Giai đoạn 1** (hiện tại): tọa độ theo tuyến (`tuyen_duong_geo`)
- **Giai đoạn 2** (tạo sẵn): tọa độ theo đoạn (`doan_tuyen_geo`)

### 13.2. Map tự chứa (`map/generate_map_multi_mahoa_onefile.py`)

Script sinh 1 file HTML duy nhất tích hợp hoàn toàn Leaflet.js:
- Đọc `*.geojson` → **mã hóa 3 lớp bảo vệ tọa độ:**
  1. Delta encoding (nén sai phân)
  2. XOR cipher (key 32 byte ngẫu nhiên)
  3. Base64 encode
- Hover/click → tính khoảng cách thực từ đầu tuyến
- 3 basemap: OSM, Topo, Vệ tinh

---

## 14. LUỒNG DỮ LIỆU TỔNG THỂ

```
Excel (giao_thong_data_upadate.xlsx)
    ↓ tools/excel_to_data.py
data/*.py (TUYEN_CONFIG, DOAN_CONFIG, ...)
    ↓ seeds/seed_all.py → seed_*.py
services/*_service.py (validate)
    ↓
repositories/*_repository.py (SQL INSERT)
    ↓
database/giao_thong.db (SQLite + triggers)
    ↑
repositories/thong_ke_repository.py (JOIN phức tạp)
    ↑
services/thong_ke_service.py
    ↑ gọi qua FastAPI
api/routes/thong_ke.py → templates/thong_ke.html
                       → GET /thong-ke/api/toan-tinh (JSON)

*.geojson files
    ↓ tools/import_geojson.py
database: bảng tuyen_duong_geo
    ↑
api/routes/ban_do.py → templates/ban_do.html (Leaflet.js)
```

---

## 15. QUY TẮC LẬP TRÌNH BẮT BUỘC

### Import modules — BẮT BUỘC dùng alias

```python
# ✅ ĐÚNG — dùng alias module
import models.doan_tuyen as doan_tuyen_model
import repositories.doan_tuyen_repository as doan_tuyen_repo
import services.tuyen_duong_service as tuyen_duong_service

# ❌ SAI — không dùng from ... import
from models.doan_tuyen import DoanTuyen
```

### Truy cập sqlite3.Row — BẮT BUỘC dùng tên cột

```python
# ✅ ĐÚNG
obj.id = row["id"]
obj.ma_tuyen = row["ma_tuyen"]

# ❌ SAI — không dùng index số (dễ sai khi schema thay đổi)
obj.id = row[0]
obj.ma_tuyen = row[1]
```

### Luồng validate — BẮT BUỘC

```
Web/API layer → gọi service → service validate → service gọi repo → repo gọi DB
                ↑
                Mọi ValueError, BusinessRuleError bắn từ service
                Web layer chỉ bắt lỗi và trả HTTP response
```

### Soft delete — BẮT BUỘC

```python
# Không bao giờ DELETE vật lý (trừ dev)
xoa_*(conn, id)     # → is_active = 0
khoi_phuc_*(conn, id) # → is_active = 1
```

---

## 16. CÀI ĐẶT & KHỞI CHẠY

### Yêu cầu

- Python 3.10+
- Các thư viện trong `requirements.txt`

### Cài đặt

```bash
pip install -r requirements.txt
```

### Khởi tạo database và seed dữ liệu

```bash
# Bước 1: Tạo schema (13 bảng, 6 triggers, 5 indexes)
python config/database.py

# Bước 2: Seed dữ liệu thực tế
python seeds/seed_all.py
```

### Chạy web application

```bash
uvicorn api.main:app --reload --port 8000
```

### Chạy báo cáo console (dev/test)

```bash
python main.py
```

### Biến môi trường

| Biến | Mặc định | Mô tả |
|---|---|---|
| `SESSION_SECRET` | `laocai-giaothong-secret-2024` | Secret key ký HMAC session |
| `DB_PATH` | `database/giao_thong.db` | Đường dẫn file SQLite |

---

## PHỤ LỤC — Dependencies chính

| Thư viện | Version | Dùng cho |
|---|---|---|
| `fastapi` | 0.115.12 | Web framework |
| `uvicorn` | 0.34.0 | ASGI server |
| `jinja2` | 3.1.6 | Template engine |
| `python-multipart` | 0.0.20 | Upload file, form HTML |
| `bcrypt` | 4.3.0 | Hash mật khẩu |
| `openpyxl` | 3.1.5 | Đọc/ghi Excel |
| `pandas` | 2.3.3 | Phân tích dữ liệu |
| `pillow` | 12.1.1 | Đọc EXIF GPS từ ảnh |
| `sqlite3` | built-in | Database |

---

*Tài liệu cập nhật lần cuối: tháng 3/2026*
