# ARCHITECTURE.md — Kiến trúc kỹ thuật Quản lý Đường bộ Lào Cai

> Tài liệu mô tả kiến trúc kỹ thuật đầy đủ.
> Đọc `CLAUDE.md` để biết quy tắc code · Xem `PROJECT_MAP.md` để tìm file cụ thể.
> Cập nhật lần cuối: 2026-03-27

---

## 1. TỔNG QUAN

### Stack kỹ thuật

| Thành phần | Công nghệ | Phiên bản |
|---|---|---|
| Web Framework | FastAPI | 0.115.12 |
| ASGI Server (dev) | Uvicorn | 0.34.0 |
| WSGI Server (prod) | Gunicorn + UvicornWorker | 21.2.0 |
| Template Engine | Jinja2 | 3.1.6 |
| Database | SQLite | (built-in Python) |
| Mật khẩu | bcrypt | 4.3.0 |
| Excel | openpyxl | 3.1.5 |
| Rate Limiting | slowapi | 0.1.9 |
| Env Vars | python-dotenv | 1.1.0 |
| Frontend Map | Leaflet.js | 1.9.4 (CDN) |
| Frontend CSS | Bootstrap | 5.3.2 (CDN) + custom Design System |
| Reverse Proxy | Nginx | (VPS) |
| Process Manager | systemd | (VPS) |

### Mô hình triển khai

```
Internet
    ↓ HTTPS (port 443)
  Nginx (reverse proxy + SSL/TLS)
    ↓ HTTP (127.0.0.1:8000)
  Gunicorn (multi-worker)
    ↓
  UvicornWorker × N (N = CPU×2+1)
    ↓
  FastAPI Application
    ↓
  SQLite (single file: giao_thong.db)
    Local: [project_root]/giao_thong.db
    VPS:   /home/giaothong/data/giao_thong.db  (qua DB_PATH trong .env)
```

---

## 2. KIẾN TRÚC 4 TẦNG

```
┌─────────────────────────────────────────────────────────────┐
│  Web Layer (api/routes/)                                      │
│  FastAPI routes — nhận HTTP, render Jinja2 template          │
│  Không chứa business logic, không gọi DB trực tiếp           │
├─────────────────────────────────────────────────────────────┤
│  Service Layer (services/)                                    │
│  TOÀN BỘ validate + business logic ở đây                     │
│  Ném ServiceError với message tiếng Việt                      │
├─────────────────────────────────────────────────────────────┤
│  Repository Layer (repositories/)                             │
│  Chỉ SQL thuần — không chứa logic nghiệp vụ                  │
│  Trả về Model objects, dùng row["ten_cot"]                    │
├─────────────────────────────────────────────────────────────┤
│  Model Layer (models/)                                        │
│  Plain Python Objects — type hints, không gọi DB             │
└─────────────────────────────────────────────────────────────┘
                         ↓
              SQLite (giao_thong.db)
```

### Luồng xử lý request điển hình

```
POST /doan-tuyen/them
    ↓
doan_tuyen_route.py::them_doan_tuyen()
    ├── yeu_cau_dang_nhap() → kiểm tra session cookie
    ├── get_db() → lấy SQLite connection
    ↓
doan_tuyen_service.py::them_doan_tuyen(conn, ...)
    ├── Validate: ly_trinh_cuoi > ly_trinh_dau
    ├── Validate: tuyen_id tồn tại (gọi tuyen_duong_repo)
    ├── Validate: cap_duong_id tồn tại
    ├── Validate: tinh_trang_id tồn tại
    ├── raise DoanTuyenServiceError nếu lỗi
    ↓
doan_tuyen_repository.py::them_doan_tuyen(conn, ...)
    ├── INSERT INTO doan_tuyen (...)
    ├── SQLite TRIGGER trg_doan_tuyen_sau_them tự kích hoạt
    └── → UPDATE tuyen_duong SET chieu_dai_quan_ly = ..., chieu_dai_thuc_te = ...
    ↓
RedirectResponse("/doan-tuyen/") hoặc HTTPException(400)
```

---

## 3. DATABASE SCHEMA

### Sơ đồ quan hệ (ERD)

```
cap_quan_ly ──────────────────────────────┐
cap_duong ──────────────────┐             │
ket_cau_mat_duong ────────┐ │             │
tinh_trang ─────────────┐ │ │             │
                         │ │ │             │
don_vi ──────────────────┼─┼─┼──────────┐ │
         (cây cha-con)   │ │ │          │ │
                         │ │ │          │ │
nguoi_dung ──────────────┼─┼─┼──┐       │ │
  (don_vi_id)            │ │ │  │       │ │
                         ↓ ↓ ↓  │       ↓ ↓
                      doan_tuyen     tuyen_duong
                         │  ↑           │
                         │  └───────────┘
                         │  (tuyen_id FK)
                         │
              ┌──────────┴──────────┐
              │                     │
    doan_di_chung           hinh_anh_doan_tuyen
    (tuyen_di_chung_id FK)   (doan_id FK)
    (tuyen_chinh_id FK)
    (doan_id FK)
                                tuyen_duong_geo
                                (tuyen_id FK UNIQUE)
                                doan_tuyen_geo
                                (doan_id FK UNIQUE)
                                thong_tin_tuyen
                                (tuyen_id FK UNIQUE)
```

### Schema 15 bảng (cột thực tế từ DB)

```sql
-- 1. DANH MỤC CẤP QUẢN LÝ
cap_quan_ly:
  id, ma_cap*, ten_cap, mo_ta, thu_tu_hien_thi, is_active
  -- Dữ liệu: 8 bản ghi (QL, DT, DX, DD, NT, TX, CD, DK)

-- 2. DANH MỤC CẤP ĐƯỜNG KỸ THUẬT
cap_duong:
  id, ma_cap*, ten_cap, mo_ta, thu_tu_hien_thi, is_active
  -- Dữ liệu: 7 bản ghi (III, IV, V, VI, mn_III, mn_IV, mn_V)

-- 3. DANH MỤC KẾT CẤU MẶT ĐƯỜNG (free-text từ 2025)
ket_cau_mat_duong:
  id, ma_ket_cau*, ten_ket_cau, mo_ta, thu_tu_hien_thi, is_active
  -- Dữ liệu: 8+ bản ghi (BTN, BTXM, HH, LN, CP, DAT, ...)

-- 4. DANH MỤC TÌNH TRẠNG MẶT ĐƯỜNG (free-text từ 2025)
tinh_trang:
  id, ma_tinh_trang*, ten_tinh_trang, mo_ta, mau_hien_thi, thu_tu_hien_thi, is_active
  -- Dữ liệu: 9+ bản ghi (TOT, TB, KEM, HH_NANG, THI_CONG, ...)

-- 5. ĐƠN VỊ (cây cha-con, tự tham chiếu)
don_vi:
  id, ma_don_vi*, ten_don_vi, ten_viet_tat, parent_id→don_vi,
  cap_don_vi, dia_chi, so_dien_thoai, email, is_active, created_at
  -- Dữ liệu: 17 đơn vị

-- 6. NGƯỜI DÙNG
nguoi_dung:
  id, ten_dang_nhap*, mat_khau_hash(bcrypt), ho_ten, chuc_vu,
  don_vi_id→don_vi, so_dien_thoai, email*, loai_quyen(ADMIN|BIEN_TAP|XEM),
  is_active, is_approved, approved_by_id→nguoi_dung, approved_at, created_at, last_login
  -- Dữ liệu: 4 bản ghi

-- 7. TUYẾN ĐƯỜNG (bảng trung tâm)
tuyen_duong:
  id, ma_tuyen*, ten_tuyen, cap_quan_ly_id→cap_quan_ly,
  don_vi_quan_ly_id→don_vi, diem_dau, diem_cuoi,
  lat_dau, lng_dau, lat_cuoi, lng_cuoi,
  chieu_dai_quan_ly(TRIGGER), chieu_dai_thuc_te(TRIGGER),
  nam_xay_dung, nam_hoan_thanh, ghi_chu, created_at
  -- Dữ liệu: 49 tuyến (9 QL + 27 DT + 13 DX)

-- 8. THÔNG TIN MÔ TẢ TUYẾN
thong_tin_tuyen:
  id, tuyen_id→tuyen_duong(UNIQUE), mo_ta, ly_do_xay_dung,
  dac_diem_dia_ly, lich_su_hinh_thanh, y_nghia_kinh_te, ghi_chu,
  created_at, updated_at
  -- Dữ liệu: 49 bản ghi

-- 9. ĐOẠN TUYẾN
doan_tuyen:
  id, ma_doan*, tuyen_id→tuyen_duong, cap_duong_id→cap_duong,
  tinh_trang_id→tinh_trang, ket_cau_mat_id→ket_cau_mat_duong,
  ly_trinh_dau, ly_trinh_cuoi, chieu_dai_thuc_te,
  chieu_rong_mat_min, chieu_rong_mat_max, chieu_rong_nen_min, chieu_rong_nen_max,
  don_vi_bao_duong_id→don_vi, nam_lam_moi, ngay_cap_nhat_tinh_trang,
  ghi_chu, created_at, updated_at, updated_by_id→nguoi_dung
  -- Dữ liệu: 222 đoạn
  -- CONSTRAINT: ly_trinh_cuoi > ly_trinh_dau

-- 10. ĐOẠN ĐI CHUNG
doan_di_chung:
  id, ma_doan_di_chung*, tuyen_di_chung_id→tuyen_duong,
  tuyen_chinh_id→tuyen_duong, doan_id→doan_tuyen,
  ly_trinh_dau_di_chung, ly_trinh_cuoi_di_chung,
  ly_trinh_dau_tuyen_chinh, ly_trinh_cuoi_tuyen_chinh, ghi_chu, created_at
  -- UNIQUE: (tuyen_di_chung_id, doan_id)
  -- Dữ liệu: 15 bản ghi

-- 11. HÌNH ẢNH ĐOẠN TUYẾN
hinh_anh_doan_tuyen:
  id, doan_id→doan_tuyen(CASCADE), duong_dan_file,
  mo_ta, ngay_chup, nguoi_chup, lat, lng, ly_trinh_anh, created_at

-- 12. GEO TUYẾN ĐƯỜNG (GeoJSON tọa độ)
tuyen_duong_geo:
  id, tuyen_id→tuyen_duong(CASCADE, UNIQUE), coordinates(JSON),
  so_diem, chieu_dai_gps(Haversine), nguon, updated_at
  -- Dữ liệu: 3 bản ghi (3 tuyến đã import GeoJSON)

-- 13. GEO ĐOẠN TUYẾN
doan_tuyen_geo:
  id, doan_id→doan_tuyen(CASCADE, UNIQUE), coordinates(JSON),
  so_diem, chieu_dai_gps, nguon, updated_at

-- 14. NHẬT KÝ ĐĂNG NHẬP (migration m002)
dang_nhap_log:
  id, ten_dang_nhap, nguoi_dung_id→nguoi_dung,
  ip_address, vi_tri (ip-api.com lookup), user_agent,
  thanh_cong(0|1), ghi_chu, thoi_gian
  -- INDEX: idx_dang_nhap_log_thoi_gian ON thoi_gian DESC

-- 15. NHẬT KÝ HOẠT ĐỘNG (migration m002)
nhat_ky_hoat_dong:
  id, nguoi_dung_id→nguoi_dung, ho_ten,
  hanh_dong (THEM|SUA|XOA|XUAT_EXCEL), doi_tuong, doi_tuong_id,
  mo_ta, ip_address, thoi_gian
  -- INDEX: idx_nhat_ky_thoi_gian ON thoi_gian DESC
  -- Tự động ghi qua ActivityLogMiddleware

-- * = UNIQUE constraint
```

### 6 Triggers tự động cập nhật chiều dài

```
Nhóm 1 — doan_tuyen triggers (cập nhật chieu_dai_quan_ly + chieu_dai_thuc_te):
  trg_doan_tuyen_sau_them  (AFTER INSERT)
  trg_doan_tuyen_sau_sua   (AFTER UPDATE — xử lý cả tuyen cũ và mới)
  trg_doan_tuyen_sau_xoa   (AFTER DELETE)

Nhóm 2 — doan_di_chung triggers (cập nhật chieu_dai_thuc_te):
  trg_ddc_sau_them  (AFTER INSERT)
  trg_ddc_sau_sua   (AFTER UPDATE — xử lý cả tuyen cũ và mới)
  trg_ddc_sau_xoa   (AFTER DELETE)

Công thức:
  chieu_dai_quan_ly = ROUND(SUM(COALESCE(dt.chieu_dai_thuc_te, dt.ly_trinh_cuoi - dt.ly_trinh_dau)), 3)
  chieu_dai_thuc_te = chieu_dai_quan_ly + ROUND(SUM(ddc.ly_trinh_cuoi_di_chung - ddc.ly_trinh_dau_di_chung), 3)
```

### Indexes tối ưu

```sql
-- 5 indexes chính (từ migrations):
idx_doan_tuyen_tuyen_id   ON doan_tuyen(tuyen_id)
idx_doan_di_chung_tuyen   ON doan_di_chung(tuyen_di_chung_id, tuyen_chinh_id, doan_id)
idx_tuyen_duong_cap       ON tuyen_duong(cap_quan_ly_id)
idx_nguoi_dung_tdn        ON nguoi_dung(ten_dang_nhap)
idx_tuyen_duong_geo       ON tuyen_duong_geo(tuyen_id)
```

### Cấu hình SQLite

```python
# WAL mode — cho phép đọc đồng thời khi đang ghi
conn.execute("PRAGMA journal_mode=WAL")
# Foreign key constraints bật (mặc định SQLite tắt)
conn.execute("PRAGMA foreign_keys=ON")
# sqlite3.Row factory — truy cập bằng tên cột
conn.row_factory = sqlite3.Row
```

---

## 4. AUTHENTICATION & SESSION

### Cơ chế

```
Đăng nhập:
  POST /auth/login
  ├── Kiểm tra ten_dang_nhap trong DB
  ├── bcrypt.checkpw(mat_khau, mat_khau_hash)
  ├── Kiểm tra is_active=1 và is_approved=1
  ├── Tạo session_token = HMAC-SHA256(user_data_json, SESSION_SECRET)
  └── Set-Cookie: session=<token>; HttpOnly; SameSite=Strict; [Secure nếu HTTPS]

Xác thực mỗi request:
  yeu_cau_dang_nhap() [FastAPI Depends]
  ├── Đọc cookie "session"
  ├── Verify HMAC signature
  ├── Check TTL (86400 giây = 1 ngày)
  └── Trả về user dict hoặc raise 302 redirect về /auth/login
```

### Phân quyền

```python
# Trong route — dùng Depends:
user = Depends(yeu_cau_dang_nhap)    # Bất kỳ user đã đăng nhập
user = Depends(yeu_cau_quyen_admin)  # Chỉ ADMIN
user = Depends(yeu_cau_bien_tap)     # ADMIN hoặc BIEN_TAP
```

---

## 5. MIDDLEWARE STACK

Thứ tự middleware (outer → inner):

```
1. _SecurityHeadersMiddleware (custom BaseHTTPMiddleware)
   → Thêm security headers vào tất cả response
   → X-Content-Type-Options: nosniff
   → X-Frame-Options: DENY
   → X-XSS-Protection: 1; mode=block
   → Referrer-Policy: strict-origin-when-cross-origin
   → Permissions-Policy: geolocation=(), microphone=(), camera=()
   → HSTS: max-age=31536000 (production only)

2. ActivityLogMiddleware (custom BaseHTTPMiddleware)
   → Tự động ghi nhật ký hoạt động vào bảng nhat_ky_hoat_dong
   → Theo dõi: POST /them, POST /sua, POST /xoa, GET /xuat-du-lieu
   → Lấy user từ session cookie, lấy IP từ request

3. CORSMiddleware
   → allow_origins từ ALLOWED_ORIGINS env var
   → allow_methods: GET, POST
   → allow_credentials: True

4. slowapi rate limiter
   → 5 request đăng nhập / phút / IP (áp dụng trên POST /auth/login)

5. Starlette ExceptionMiddleware (built-in)
6. Starlette ServerErrorMiddleware (built-in)
```

---

## 6. ROUTES (URL MAP)

### Auth (`/auth/`)

| Method | URL | Mô tả | Quyền |
|---|---|---|---|
| GET | `/auth/login` | Form đăng nhập | Public |
| POST | `/auth/login` | Xử lý đăng nhập (rate limit 5/min) | Public |
| GET | `/auth/logout` | Đăng xuất | Đăng nhập |
| GET | `/auth/dang-ky` | Form đăng ký | Public |
| POST | `/auth/dang-ky` | Xử lý đăng ký | Public |
| GET | `/auth/cho-duyet` | Danh sách chờ duyệt | ADMIN |

### Tuyến đường (`/tuyen-duong/`)

| Method | URL | Mô tả |
|---|---|---|
| GET | `/tuyen-duong/` | Danh sách tuyến (filter theo cấp QL) |
| GET | `/tuyen-duong/them` | Form thêm tuyến |
| POST | `/tuyen-duong/them` | Lưu tuyến mới |
| GET | `/tuyen-duong/{id}` | Chi tiết tuyến + danh sách đoạn |
| POST | `/tuyen-duong/{id}/sua` | Cập nhật tuyến |
| POST | `/tuyen-duong/{id}/xoa` | Xóa mềm tuyến |
| GET | `/tuyen-duong/{id}/thong-tin` | Form metadata tuyến |
| POST | `/tuyen-duong/{id}/thong-tin` | Lưu metadata tuyến |

### Đoạn tuyến (`/doan-tuyen/`)

| Method | URL | Mô tả |
|---|---|---|
| GET | `/doan-tuyen/` | Danh sách đoạn |
| GET | `/doan-tuyen/them` | Form thêm đoạn |
| POST | `/doan-tuyen/them` | Lưu đoạn mới |
| GET | `/doan-tuyen/{id}` | Chi tiết đoạn |
| POST | `/doan-tuyen/{id}/sua` | Cập nhật đoạn |
| POST | `/doan-tuyen/{id}/xoa` | Xóa mềm đoạn |

### Đoạn đi chung (`/doan-di-chung/`)

| Method | URL | Mô tả |
|---|---|---|
| GET | `/doan-di-chung/` | Danh sách DDC |
| GET | `/doan-di-chung/them` | Form thêm DDC |
| POST | `/doan-di-chung/them` | Lưu DDC mới (validate 6 điều kiện) |
| GET | `/doan-di-chung/{id}/sua` | Form sửa DDC |
| POST | `/doan-di-chung/{id}/sua` | Cập nhật DDC |
| POST | `/doan-di-chung/{id}/xoa` | Xóa mềm DDC |

### Danh mục (`/danh-muc/`)

| Method | URL | Mô tả |
|---|---|---|
| GET | `/danh-muc/quan-ly` | Trang quản lý cấp QL + cấp đường + đơn vị |
| GET | `/danh-muc/ky-thuat` | Trang kết cấu mặt + tình trạng |
| POST | `/danh-muc/cap-quan-ly/them` | Thêm cấp QL |
| POST | `/danh-muc/cap-duong/them` | Thêm cấp đường |
| POST | `/danh-muc/ket-cau-mat/them` | Thêm kết cấu (free-text) |
| POST | `/danh-muc/tinh-trang/them` | Thêm tình trạng (free-text) |
| POST | `/danh-muc/don-vi/them` | Thêm đơn vị |

### Hệ thống (`/he-thong/`) — ADMIN only

| Method | URL | Mô tả |
|---|---|---|
| GET | `/he-thong/nguoi-dung` | Quản lý người dùng |
| POST | `/he-thong/nguoi-dung/them` | Tạo user mới |
| POST | `/he-thong/nguoi-dung/{id}/sua` | Sửa thông tin user |
| POST | `/he-thong/nguoi-dung/{id}/doi-mk` | Đặt lại mật khẩu |
| POST | `/he-thong/nguoi-dung/{id}/xoa` | Vô hiệu/khôi phục |
| POST | `/he-thong/nguoi-dung/{id}/duyet` | Duyệt tài khoản |
| GET | `/he-thong/xuat-du-lieu` | Xuất toàn bộ DB ra Excel |
| GET | `/he-thong/nhat-ky` | Nhật ký hệ thống: log đăng nhập + hoạt động |

### Thống kê (`/thong-ke/`)

| Method | URL | Mô tả |
|---|---|---|
| GET | `/thong-ke/` | Trang thống kê |
| GET | `/thong-ke/api/toan-tinh` | API JSON tổng hợp toàn tỉnh |

### Bản đồ (`/ban-do/`)

| Method | URL | Mô tả |
|---|---|---|
| GET | `/ban-do/` | Trang bản đồ Leaflet |
| GET | `/ban-do/api/geo/{tuyen_id}` | GeoJSON 1 tuyến từ DB |
| GET | `/ban-do/api/geo-all` | GeoJSON tất cả tuyến từ DB |
| GET | `/ban-do/api/geojson-list` | Danh sách file .geojson trong `data/geojson/` |
| GET | `/ban-do/api/geojson-all` | Gộp tất cả file .geojson thành FeatureCollection |

---

## 7. JINJA2 CUSTOM FILTERS

```python
# Định nghĩa trong api/main.py
{{ value | format_ly_trinh }}
# 190.0  → "Km190+000"
# 37.557 → "Km37+557"
# None   → "—"
```

---

## 8. EXCEL EXPORT (`/he-thong/xuat-du-lieu`)

Xuất 9 bảng DB ra file `.xlsx`:

```
Sheet: cap_quan_ly      → id, ma_cap, ten_cap, mo_ta, thu_tu_hien_thi, is_active
Sheet: cap_duong        → id, ma_cap, ten_cap, mo_ta, thu_tu_hien_thi, is_active
Sheet: ket_cau_mat_duong → id, ma_ket_cau, ten_ket_cau, mo_ta, thu_tu_hien_thi, is_active
Sheet: tinh_trang       → id, ma_tinh_trang, ten_tinh_trang, mo_ta, mau_hien_thi, thu_tu_hien_thi, is_active
Sheet: don_vi           → id, ma_don_vi, ten_don_vi, ten_viet_tat, cap_don_vi, parent_id, dia_chi, so_dien_thoai, email, is_active
Sheet: nguoi_dung       → id, ten_dang_nhap, ho_ten, chuc_vu, don_vi_id, so_dien_thoai, email, loai_quyen, is_active, is_approved, created_at
Sheet: tuyen_duong      → id, ma_tuyen, ten_tuyen, cap_quan_ly_id, don_vi_quan_ly_id, diem_dau, diem_cuoi, chieu_dai_quan_ly, chieu_dai_thuc_te, nam_xay_dung, nam_hoan_thanh, ghi_chu
Sheet: doan_tuyen       → id, ma_doan, tuyen_id, cap_duong_id, tinh_trang_id, ket_cau_mat_id, ly_trinh_dau, ly_trinh_cuoi, chieu_dai_thuc_te, ... (không xuất mat_khau_hash)
Sheet: doan_di_chung    → id, ma_doan_di_chung, tuyen_di_chung_id, tuyen_chinh_id, doan_id, ly_trinh_*

Tên file: giao_thong_YYYYMMDD.xlsx
```

---

## 9. BẢN ĐỒ LEAFLET

### Kiến trúc bản đồ

```
ban_do.html (Leaflet.js 1.9.4)
    │
    ├── Promise.allSettled([
    │     fetch('/ban-do/api/geo-all'),      ← từ DB
    │     fetch('/ban-do/api/geojson-all'),  ← từ file
    │   ])
    │
    ├── veFeature(feature, nguon='db')
    │   └── Màu theo cap_quan_ly: QL=#e74c3c DT=#3498db DX=#27ae60 CT=#8e44ad
    │       Style: đường liền, weight=3, opacity=0.85
    │
    ├── veFeature(feature, nguon='file')
    │   └── Màu: #f39c12 (cam), dashArray: '6 4', weight=2
    │
    ├── Bộ lọc "Cấp quản lý" — toggleCap(cap, show)
    └── Bộ lọc "Nguồn dữ liệu" — toggleNguon(nguon, show)
```

### API `/ban-do/api/geojson-all` — chuẩn hóa 3 định dạng GeoJSON

```python
# FeatureCollection → lấy features[], gắn ma_tuyen từ tên file nếu thiếu
# Feature → wrap thành list [feature]
# Geometry thuần (LineString, ...) → tạo Feature wrapper
```

---

## 10. SEED DATA

```
seeds/seed_all.py — Orchestrator idempotent (INSERT OR IGNORE)

Thứ tự:
  [0] migration schema (CREATE TABLE IF NOT EXISTS + triggers + indexes)
  [1] seed_danh_muc.py
      → cap_quan_ly: 8 bản ghi
      → cap_duong: 7 bản ghi
      → ket_cau_mat_duong: 8 bản ghi
      → tinh_trang: 9 bản ghi
  [2] seed_don_vi.py → 17 đơn vị (UBND Tỉnh → SXD → các ban)
  [3] seed_nguoi_dung.py → 3 user (bcrypt hash)
  [4] seed_tuyen_doan.py
      → 49 tuyen_duong + 49 thong_tin_tuyen
      → 222 doan_tuyen (triggers tự cập nhật chiều dài)
      → 15 doan_di_chung
```

---

## 11. TOOLS

| File | Mô tả |
|---|---|
| `tools/excel_to_data.py` | Đọc `data/giao_thong_data_upadate.xlsx` → sinh các file `data/*_data.py` |
| `tools/import_geojson.py` | Import file .geojson vào bảng `tuyen_duong_geo` (parse, tính Haversine, lưu JSON) |
| `tools/export_geojson.py` | Export `tuyen_duong_geo` ra file .geojson theo `--ma-tuyen` |
| `tools/import_tai_khoan.py` | Import danh sách tài khoản từ `Danh_sach_tai_khoan_sxd.xlsx` → DB, idempotent |
| `migrate.py` | Chạy migration tự động, theo dõi lịch sử, idempotent (`python3 migrate.py`) |
| `map/generate_map_multi_mahoa_onefile.py` | Tạo file HTML bản đồ tĩnh nhiều tuyến (không dùng cho web app) |

---

## 12. DEPLOY PRODUCTION

### Cấu trúc file deploy

```
gunicorn.conf.py          → workers = CPU×2+1, bind 127.0.0.1:8000, max_requests=1000
deploy/nginx.conf         → HTTPS redirect, SSL, proxy_pass, /static serve trực tiếp
deploy/giaothong.service  → systemd unit, EnvironmentFile=/path/to/.env, Restart=on-failure
```

### Vị trí DB (phân biệt môi trường)

| Môi trường | DB_PATH trong .env | Vị trí thực tế |
|---|---|---|
| Local (dev) | `DB_PATH=giao_thong.db` | `[project_root]/giao_thong.db` |
| VPS (prod) | `DB_PATH=/home/giaothong/data/giao_thong.db` | Ngoài thư mục dự án — không mất khi cập nhật code |

### Checklist deploy VPS

```bash
# 0. Tạo thư mục DB ngoài project (1 lần duy nhất)
mkdir -p /home/giaothong/data

# 1. Clone repo
git clone <repo> ~/giaothong-app
cd ~/giaothong-app

# 2. Tạo venv và cài packages
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Tạo .env production
cp .env.example .env
# Điền SESSION_SECRET, DEBUG=false, DB_PATH=/home/giaothong/data/giao_thong.db, ALLOWED_ORIGINS

# 4. Khởi tạo DB + chạy migration
python3 seeds/seed_all.py
python3 migrate.py

# 5. Cấu hình Nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/giaothong
sudo ln -s /etc/nginx/sites-available/giaothong /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 6. Cấu hình systemd
sudo cp deploy/giaothong.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable giaothong
sudo systemctl start giaothong
```

> Xem hướng dẫn đầy đủ tại `deploy/HUONG_DAN_DEPLOY_VPS.md`.

---

*Cập nhật file này sau mỗi thay đổi kiến trúc, thêm bảng DB, thêm endpoint, hoặc thay đổi middleware.*
