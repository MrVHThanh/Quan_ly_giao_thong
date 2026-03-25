# CLAUDE.md — Hướng dẫn làm việc với dự án Quản lý Đường bộ Lào Cai

> File này là **nguồn tham chiếu chính** cho Claude Code khi làm việc trong dự án.
> Đọc toàn bộ file này trước khi bắt đầu bất kỳ tác vụ nào.
> Cập nhật lần cuối: 2025-03-25

---

## 1. THÔNG TIN DỰ ÁN

| Hạng mục | Giá trị |
|---|---|
| **Tên hệ thống** | Quản lý tuyến đường bộ tỉnh Lào Cai |
| **Đơn vị chủ quản** | Sở Xây dựng tỉnh Lào Cai |
| **Stack chính** | Python 3.10 · SQLite · FastAPI 0.115 · Jinja2 3.1 |
| **Thư mục gốc** | `D:\Dropbox\@Giaothong2\` |
| **Database** | `giao_thong.db` (thư mục gốc, gitignored) |
| **File dữ liệu nguồn** | `data/giao_thong_data_upadate.xlsx` (10 sheets) |
| **Tài liệu chi tiết** | `ARCHITECTURE.md` và `PROJECT_MAP.md` |
| **Branch chính** | `main` (production), `develop` (integration) |

---

## 2. LỆNH THƯỜNG DÙNG

```bash
# Cài dependencies
pip install -r requirements.txt

# Khởi tạo DB + seed dữ liệu (chạy 1 lần, idempotent)
python seeds/seed_all.py

# Chạy web server (development)
uvicorn api.main:app --reload

# Chạy web server (bind toàn mạng LAN)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Chạy production với Gunicorn
gunicorn -c gunicorn.conf.py api.main:app

# Báo cáo console (dev/test)
python main.py

# Sinh lại data/*.py từ Excel sau khi cập nhật file xlsx
python tools/excel_to_data.py

# Import GeoJSON vào DB
python tools/import_geojson.py map/QL4E.geojson

# Export GeoJSON từ DB
python tools/export_geojson.py --ma-tuyen QL4E

# Reset DB hoàn toàn (DEV ONLY — mất dữ liệu!)
python config/database.py --reset
python seeds/seed_all.py
```

**Tài khoản mặc định sau khi seed:**

| Tên đăng nhập | Mật khẩu | Quyền |
|---|---|---|
| `huuthanh` | `Laocai@2024` | ADMIN |
| `bientap` | `Laocai@2024` | BIEN_TAP |
| `xem` | `Laocai@2024` | XEM |

**URL sau khi chạy:**
- Trang chủ: `http://localhost:8000`
- Swagger API (chỉ DEBUG=true): `http://localhost:8000/api/docs`
- Health check: `http://localhost:8000/api/health`

---

## 3. BIẾN MÔI TRƯỜNG (.env)

File `.env` phải tồn tại ở thư mục gốc (gitignored). Xem mẫu `.env.example`.

```env
SESSION_SECRET=<chuỗi ngẫu nhiên 64 ký tự>
DEBUG=true
DB_PATH=giao_thong.db
ALLOWED_ORIGINS=http://localhost:8000
```

> **Quan trọng:** Không có `SESSION_SECRET` → app crash khi khởi động (thiết kế bảo mật chủ ý).
> `python-dotenv` đọc `.env` tự động khi app khởi động (`load_dotenv()` trong `api/main.py`).

---

## 4. KIẾN TRÚC 4 TẦNG — QUY TẮC BẤT BIẾN

```
HTTP Request → Web (FastAPI) → Service → Repository → Database (SQLite)
```

| Tầng | Thư mục | Trách nhiệm |
|---|---|---|
| **Web** | `api/routes/` | Nhận HTTP, render template, trả response |
| **Service** | `services/` | **TOÀN BỘ** validate + business logic |
| **Repository** | `repositories/` | Chỉ SQL thuần, không logic nghiệp vụ |
| **Model** | `models/` | Plain Object, không gọi DB, không validate |

> **Nguyên tắc tuyệt đối:**
> - Không đặt business logic vào Model hoặc Repository
> - Không gọi DB trực tiếp từ tầng Web — phải qua Service
> - Service ném exception riêng (VD: `TuyenDuongServiceError`) — Web bắt và trả HTTP

---

## 5. QUY TẮC CODE BẮT BUỘC

### 5.1 Import — dùng alias module, không dùng `from ... import`

```python
# ✅ ĐÚNG
import models.doan_tuyen as doan_tuyen_model
import repositories.doan_tuyen_repository as doan_tuyen_repo
import services.tuyen_duong_service as tuyen_duong_service

# ❌ SAI
from models.doan_tuyen import DoanTuyen
from repositories import doan_tuyen_repository
```

### 5.2 sqlite3.Row — truy cập bằng tên cột, không dùng index số

```python
# ✅ ĐÚNG
obj.id      = row["id"]
obj.ma_doan = row["ma_doan"]

# ❌ SAI
obj.id      = row[0]
obj.ma_doan = row[1]
```

### 5.3 Soft delete — không bao giờ DELETE vật lý (ngoại trừ dev)

```python
# ✅ ĐÚNG
xoa_mem(conn, id)    # UPDATE ... SET is_active = 0
khoi_phuc(conn, id)  # UPDATE ... SET is_active = 1

# ❌ SAI (ngoài dev/test)
conn.execute("DELETE FROM doan_tuyen WHERE id = ?", (id,))
```

### 5.4 Chiều dài tuyến — không tính thủ công, trigger tự xử lý

6 SQLite triggers tự động cập nhật `tuyen_duong.chieu_dai_quan_ly` và `chieu_dai_thuc_te`
sau mỗi INSERT/UPDATE/DELETE trên `doan_tuyen` hoặc `doan_di_chung`.

```python
# ✅ ĐÚNG — chỉ cần INSERT/UPDATE doan_tuyen, trigger tự chạy
# ❌ SAI — hàm tính thủ công (đã xóa)
cap_nhat_chieu_dai_tuyen(conn, tuyen_id)
```

### 5.5 Cấu trúc chuẩn Repository

```python
_SELECT_COLS = "id, ma_*, ten_*, ..."    # tên cột tường minh, không dùng SELECT *

def _row_to_object(row) -> Model: ...    # sqlite3.Row → Object
def lay_tat_ca(conn) -> list[Model]: ...
def lay_theo_id(conn, id: int) -> Model | None: ...
def lay_theo_ma(conn, ma: str) -> Model | None: ...
def them_*(conn, ...) -> int: ...        # trả lastrowid
def cap_nhat_*(conn, ...) -> bool: ...
def xoa_mem_*(conn, id) -> bool: ...     # is_active = 0
def khoi_phuc_*(conn, id) -> bool: ...   # is_active = 1
```

### 5.6 Cấu trúc chuẩn Service

```python
class TenServiceError(Exception):
    pass

def lay_tat_ca(conn) -> list[Model]: ...
def lay_theo_id(conn, id: int) -> Model | None: ...
def them_*(conn, ...) -> int:
    # 1. Validate dữ liệu đầu vào
    # 2. Kiểm tra FK tồn tại
    # 3. Kiểm tra business rules
    # 4. Gọi repo.them_*()
    # raise TenServiceError("Thông báo tiếng Việt")
def xoa_mem_*(conn, id) -> bool: ...
def get_or_create_*(conn, ma) -> tuple[Model, bool]: ...  # dùng trong seed
```

### 5.7 Xử lý lỗi trong route (Web layer)

```python
import sqlite3

try:
    service.them_tuyen(conn, ...)
except TuyenDuongServiceError as e:
    raise HTTPException(status_code=400, detail=str(e))
except sqlite3.IntegrityError:
    raise HTTPException(status_code=409, detail="Dữ liệu bị trùng lặp.")
```

---

## 6. NGHIỆP VỤ DOMAIN QUAN TRỌNG

### 6.1 Hai loại chiều dài tuyến

| Trường | Công thức | Trigger |
|---|---|---|
| `chieu_dai_quan_ly` | `SUM(doan_tuyen.chieu_dai_thuc_te)` của tuyến | `trg_doan_tuyen_*` (3 triggers) |
| `chieu_dai_thuc_te` | `chieu_dai_quan_ly + SUM(DDC.ly_trinh_cuoi - DDC.ly_trinh_dau)` | `trg_ddc_*` (3 triggers) |

### 6.2 Đoạn đi chung (DDC) — 6 điều kiện validation bắt buộc

1. `tuyen_di_chung_id` (tuyến đi nhờ) phải tồn tại
2. `tuyen_chinh_id` (tuyến chủ của đoạn vật lý) phải tồn tại
3. `doan_id` (đoạn vật lý) phải tồn tại
4. `tuyen_di_chung_id ≠ tuyen_chinh_id` — không tự đi nhờ chính mình
5. Lý trình DDC phải nằm trong phạm vi lý trình đoạn vật lý
6. Cặp `(tuyen_di_chung_id, doan_id)` phải UNIQUE (có UNIQUE constraint trong DB)

### 6.3 Lý trình — định dạng hiển thị

```python
# Số thực → KmXXX+YYY (Jinja2 custom filter: format_ly_trinh, định nghĩa trong api/main.py)
190.0   → "Km190+000"
37.557  → "Km37+557"

# Dùng trong template:
{{ doan.ly_trinh_dau | format_ly_trinh }}
```

### 6.4 Phân quyền người dùng

```
ADMIN > BIEN_TAP > XEM
```

- Đăng ký mới → `is_active=0, is_approved=0` → chờ ADMIN duyệt qua `/auth/cho-duyet`
- Mật khẩu: bcrypt hash — không bao giờ lưu plaintext
- Session: cookie HMAC SHA-256, TTL 86400 giây (1 ngày)
- Rate limit đăng nhập: 5 request/phút/IP (slowapi)
- ADMIN có thể: tạo/sửa/xóa user, duyệt đăng ký, xuất Excel

### 6.5 Dữ liệu DB thực tế (2025-03-25)

| Bảng | Số bản ghi |
|---|---|
| tuyen_duong | 49 (9 QL + 27 DT + 13 DX) |
| doan_tuyen | 222 |
| doan_di_chung | 15 |
| don_vi | 17 |
| nguoi_dung | 4 |
| tuyen_duong_geo | 3 |
| cap_quan_ly | 8 (QL, DT, DX, DD, NT, TX, CD, DK) |
| cap_duong | 7 |
| ket_cau_mat_duong | 8+ (free-text từ 2025) |
| tinh_trang | 9+ (free-text từ 2025) |

### 6.6 Danh mục free-text (thay đổi 2025)

Từ phiên bản hiện tại, `ma_ket_cau` và `ma_tinh_trang` **không còn bị giới hạn** bởi danh sách cố định.
Người dùng có thể nhập mã mới tự do (regex `^[A-Z0-9_+\-]{1,20}`).
Cả template (input text) và service (regex validate) đều đã được cập nhật.

### 6.7 GeoJSON — hai nguồn dữ liệu trên bản đồ

| Nguồn | Cách lấy | Style trên bản đồ |
|---|---|---|
| DB (`tuyen_duong_geo`) | Import qua `tools/import_geojson.py` | Đường liền, màu theo cấp QL |
| File (`data/geojson/*.geojson`) | Đặt file vào thư mục, tự động load | Đường đứt nét màu cam |

API: `GET /ban-do/api/geo-all` (DB) và `GET /ban-do/api/geojson-all` (file).
Lưu ý: chỉ scan root của `data/geojson/`, không scan thư mục con `data/geojson/All/`.

---

## 7. KHI THÊM TÍNH NĂNG MỚI

### Thêm bảng mới

1. SQL trong `migrations/m001_initial_schema.py` — hàm `up()`
2. `models/ten_bang.py` — Plain Object, type hints
3. `repositories/ten_bang_repository.py` — `_SELECT_COLS` + `_row_to_object` chuẩn
4. `services/ten_bang_service.py` — validate + business logic + ServiceError
5. `data/ten_bang_data.py` nếu cần seed
6. Thêm vào `seeds/seed_all.py` đúng thứ tự FK
7. `api/routes/ten_bang_route.py`
8. Đăng ký `app.include_router(...)` trong `api/main.py`

### Thêm tuyến/đoạn mới

```bash
# 1. Cập nhật Excel: data/giao_thong_data_upadate.xlsx
# 2. Sinh lại data config
python tools/excel_to_data.py
# 3. Seed idempotent (INSERT OR IGNORE)
python seeds/seed_all.py
```

### Thêm GeoJSON

```bash
# Option A — Import vào DB (màu theo cấp QL)
python tools/import_geojson.py map/TENTUYEN.geojson

# Option B — File tự động load (màu cam đứt nét)
# Chỉ đặt vào ROOT của data/geojson/, KHÔNG đặt vào thư mục con
cp file.geojson data/geojson/TENTUYEN.geojson
```

---

## 8. LỖI THƯỜNG GẶP VÀ CÁCH SỬA

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| `no such column: loai` | Query `don_vi` dùng cột cũ | Bảng `don_vi` dùng `cap_don_vi`, không phải `loai` |
| `ModuleNotFoundError: dotenv` | Chưa cài python-dotenv | `pip install python-dotenv` |
| `ModuleNotFoundError: slowapi` | Chưa cài slowapi | `pip install slowapi` |
| `RuntimeError: SESSION_SECRET` | Thiếu `.env` hoặc biến | Tạo `.env` với `SESSION_SECRET=...` |
| `OperationalError: no such column` | Tên cột sai hoặc dùng index | Kiểm tra schema thực tế bằng `PRAGMA table_info(ten_bang)` |
| `UNIQUE constraint failed` | Mã trùng lặp | Thêm `except sqlite3.IntegrityError` trong route |
| `403 Forbidden` | Chưa đăng nhập / thiếu quyền | Kiểm tra `loai_quyen` và `Depends` trong route |
| `chiều dài không cập nhật` | Gọi hàm thủ công cũ | Trigger tự cập nhật sau INSERT/UPDATE doan_tuyen |
| `ImportError: circular import` | Dùng `from models.X import Y` | Đổi sang `import models.X as X_model` |
| GeoJSON file không hiện bản đồ | Đặt trong thư mục con | Chỉ đặt trong ROOT của `data/geojson/` |

---

## 9. SECURITY — CHÚ Ý KHI DEPLOY VPS

- `SESSION_SECRET` phải là chuỗi ngẫu nhiên mạnh ≥ 64 ký tự, **không có fallback**
- `DEBUG=false` trên production (ẩn Swagger docs)
- `ALLOWED_ORIGINS` chỉ chứa domain HTTPS thực của server
- Cookie: `secure=True` (HTTPS), `httponly=True`, `samesite="Strict"`
- Rate limit đăng nhập: 5 request/phút/IP
- Security Headers: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, HSTS (production)
- Nginx reverse proxy — không expose Gunicorn trực tiếp ra internet
- File `.env`, `*.db`, `venv/` — **tuyệt đối không commit git**
- Systemd service: `deploy/giaothong.service` (chạy tự động khi reboot VPS)

---

## 10. THAM CHIẾU NHANH CÁC FILE

| Cần làm gì | File cần mở |
|---|---|
| Sửa schema DB / triggers | `migrations/m001_initial_schema.py` hoặc `config/database.py` |
| Sửa kết nối DB | `config/database.py` |
| Sửa biến môi trường | `config/settings.py` + `.env` |
| Sửa model tuyến đường | `models/tuyen_duong.py` |
| Sửa query tuyến đường | `repositories/tuyen_duong_repository.py` |
| Sửa validate tuyến | `services/tuyen_duong_service.py` |
| Sửa route web tuyến | `api/routes/tuyen_duong_route.py` |
| Sửa thống kê | `services/thong_ke_service.py` · `repositories/thong_ke_repository.py` |
| Sửa bản đồ Leaflet | `api/routes/ban_do.py` · `templates/ban_do.html` |
| Sửa auth / session | `api/routes/_auth_helper.py` · `api/routes/auth.py` |
| Sửa quản lý user / xuất Excel | `api/routes/he_thong_route.py` · `templates/he_thong/nguoi_dung.html` |
| Sửa danh mục kết cấu / tình trạng | `api/routes/danh_muc_route.py` · `templates/danh_muc/ky_thuat.html` |
| Sửa layout chung | `templates/base.html` · `static/css/design-system.css` |
| Cập nhật data từ Excel | `tools/excel_to_data.py` |
| Deploy production | `gunicorn.conf.py` · `deploy/nginx.conf` · `deploy/giaothong.service` |
| Xem kiến trúc chi tiết | `ARCHITECTURE.md` |
| Xem bản đồ file | `PROJECT_MAP.md` |

---

## 11. PROMPTS SẴN CÓ

Thư mục `prompts/` — gọi bằng `@prompts/ten_file.md` trong Claude Code.

| File | Mô tả |
|---|---|
| `prompts/chuan_hoa_css_ui.md` | Chuẩn hóa toàn bộ giao diện CSS Design System |

---

*Cập nhật file này sau mỗi thay đổi kiến trúc lớn, thêm quy tắc mới, hoặc thêm tính năng quan trọng.*
