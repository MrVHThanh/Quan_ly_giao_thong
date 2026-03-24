# CLAUDE.md — Hướng dẫn làm việc với dự án Quản lý Đường bộ Lào Cai

> File này là **nguồn tham chiếu chính** cho Claude Code khi làm việc trong dự án.
> Đọc toàn bộ file này trước khi bắt đầu bất kỳ tác vụ nào.

---

## 1. THÔNG TIN DỰ ÁN

| Hạng mục | Giá trị |
|---|---|
| **Tên hệ thống** | Quản lý tuyến đường bộ tỉnh Lào Cai |
| **Đơn vị chủ quản** | Sở Xây dựng tỉnh Lào Cai |
| **Stack chính** | Python 3.10+ · SQLite · FastAPI · Jinja2 |
| **Thư mục gốc** | `D:\Dropbox\@Giaothong2\` |
| **Database** | `database/giao_thong.db` |
| **File dữ liệu nguồn** | `data/giao_thong_data_upadate.xlsx` (10 sheets) |
| **Tài liệu chi tiết** | Xem `ARCHITECTURE.md` và `PROJECT_MAP.md` |

---

## 2. LỆNH THƯỜNG DÙNG

```bash
# Cài dependencies
pip install -r requirements.txt

# Khởi tạo DB + seed dữ liệu (chạy 1 lần, idempotent)
python seeds/seed_all.py

# Chạy web server (development)
uvicorn api.main:app --reload

# Chạy web server (bind toàn mạng)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Chạy báo cáo console (dev/test)
python main.py

# Sinh lại data/*.py từ Excel sau khi cập nhật file xlsx
python tools/excel_to_data.py

# Import GeoJSON vào DB
python tools/import_geojson.py map/QL4E_merged.geojson

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
- Swagger API: `http://localhost:8000/api/docs`
- Health check: `http://localhost:8000/api/health`

---

## 3. KIẾN TRÚC 4 TẦNG — QUY TẮC BẤT BIẾN

```
Web (FastAPI) → Service → Repository → Database (SQLite)
```

| Tầng | Thư mục | Trách nhiệm |
|---|---|---|
| **Web** | `api/` | Nhận HTTP request, render template, trả response |
| **Service** | `services/` | **TOÀN BỘ** validate + business logic ở đây |
| **Repository** | `repositories/` | Chỉ SQL thuần, không logic nghiệp vụ |
| **Model** | `models/` | Plain Object, không gọi DB, không validate |

> **Nguyên tắc tuyệt đối:** Không bao giờ đặt business logic vào Model hoặc Repository.
> Không bao giờ gọi DB trực tiếp từ tầng Web — phải qua Service.

---

## 4. QUY TẮC CODE BẮT BUỘC

### 4.1 Import — dùng alias module, không dùng `from ... import`

```python
# ✅ ĐÚNG
import models.doan_tuyen as doan_tuyen_model
import repositories.doan_tuyen_repository as doan_tuyen_repo
import services.tuyen_duong_service as tuyen_duong_service

obj = doan_tuyen_model.DoanTuyen(id=1, ...)
results = doan_tuyen_repo.lay_tat_ca(conn)

# ❌ SAI — không được dùng
from models.doan_tuyen import DoanTuyen
from repositories import doan_tuyen_repository
```

### 4.2 sqlite3.Row — truy cập bằng tên cột, không dùng index số

```python
# ✅ ĐÚNG
def _row_to_object(row) -> DoanTuyen:
    obj = DoanTuyen()
    obj.id           = row["id"]
    obj.ma_doan      = row["ma_doan"]
    obj.tuyen_id     = row["tuyen_id"]
    obj.ly_trinh_dau = row["ly_trinh_dau"]
    return obj

# ❌ SAI — không được dùng index số
obj.id      = row[0]
obj.ma_doan = row[1]
```

### 4.3 Soft delete — không bao giờ DELETE vật lý (ngoại trừ dev)

```python
# ✅ ĐÚNG
xoa_mem_*(conn, id)       # → UPDATE ... SET is_active = 0
khoi_phuc_*(conn, id)     # → UPDATE ... SET is_active = 1

# ❌ SAI — không dùng ngoài dev/test
DELETE FROM doan_tuyen WHERE id = ?
```

### 4.4 Chiều dài tuyến — không tính thủ công, trigger tự xử lý

```python
# ✅ ĐÚNG — chỉ cần INSERT/UPDATE doan_tuyen hoặc doan_di_chung
# 6 SQLite triggers sẽ tự động cập nhật tuyen_duong.chieu_dai_*

# ❌ SAI — không gọi hàm tính thủ công
cap_nhat_chieu_dai_tuyen(conn, tuyen_id)  # hàm này đã xóa
```

### 4.5 Cấu trúc chuẩn Repository

```python
# Mỗi repository PHẢI có:
_SELECT_COLS = "id, ma_*, ten_*, ..."    # chuỗi SELECT cố định — tên cột tường minh

def _row_to_object(row) -> Model: ...    # sqlite3.Row → Object, dùng row["col"]
def lay_tat_ca(conn) -> list[Model]: ...
def lay_theo_ma(conn, ma: str) -> Model | None: ...
def lay_theo_id(conn, id: int) -> Model | None: ...
def them_*(conn, ...) -> int: ...        # trả lastrowid
def cap_nhat_*(conn, ...) -> bool: ...
def xoa_mem_*(conn, id) -> bool: ...     # is_active = 0
def khoi_phuc_*(conn, id) -> bool: ...   # is_active = 1
```

### 4.6 Cấu trúc chuẩn Service

```python
# Mỗi service PHẢI có:
def lay_tat_ca(conn) -> list[Model]: ...
def lay_theo_ma(conn, ma: str) -> Model | None: ...
def lay_theo_id(conn, id: int) -> Model | None: ...
def them_*(conn, ...) -> int:           # validate rồi mới gọi repo
    # 1. Kiểm tra tồn tại các FK
    # 2. Kiểm tra business rules
    # 3. Gọi repo.them_*()
    # 4. Trả lastrowid
def xoa_mem_*(conn, id) -> bool: ...
def get_or_create_*(conn, ma) -> tuple[Model, bool]: ...  # dùng trong seed
```

### 4.7 Xử lý lỗi trong Service

```python
# Định nghĩa exception riêng cho từng service
class DoanTuyenServiceError(Exception):
    pass

class DoanDiChungServiceError(Exception):
    pass

# Ném lỗi rõ ràng với message tiếng Việt
raise DoanTuyenServiceError("Lý trình cuối phải lớn hơn lý trình đầu.")

# Tầng Web bắt lỗi và trả HTTP response phù hợp
try:
    service.them_doan_tuyen(conn, ...)
except DoanTuyenServiceError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

---

## 5. NGHIỆP VỤ DOMAIN QUAN TRỌNG

### 5.1 Chiều dài tuyến đường (2 loại)

| Trường | Ý nghĩa |
|---|---|
| `chieu_dai_quan_ly` | Tổng chiều dài đoạn chính (vật lý thuộc tuyến đó) |
| `chieu_dai_thuc_te` | `chieu_dai_quan_ly` + tổng chiều dài các đoạn đi chung |

Cả hai được **tự động cập nhật bởi 6 SQLite triggers** sau mỗi INSERT/UPDATE/DELETE trên `doan_tuyen` hoặc `doan_di_chung`. Không cần gọi thủ công.

### 5.2 Đoạn đi chung (doan_di_chung)

Một tuyến có thể "đi nhờ" vật lý của tuyến khác. Ví dụ: QL4D đi nhờ đoạn QL70-05.

**Validation bắt buộc khi thêm DDC:**
1. `tuyen_di_chung_id` (tuyến đi nhờ) phải tồn tại
2. `tuyen_chinh_id` (tuyến chủ của đoạn vật lý) phải tồn tại
3. `doan_id` (đoạn vật lý) phải tồn tại
4. `tuyen_di_chung_id` ≠ `tuyen_chinh_id` — không được tự đi nhờ chính mình
5. Lý trình DDC phải nằm trong phạm vi lý trình đoạn vật lý
6. Cặp `(tuyen_di_chung_id, doan_id)` phải là UNIQUE

### 5.3 Lý trình — định dạng hiển thị

```python
# Số thực → KmXXX+YYY
# 190.0   → "Km190+000"
# 37.557  → "Km37+557"
# Jinja2 filter: {{ doan.ly_trinh_dau | format_ly_trinh }}
```

### 5.4 Phân quyền người dùng

```
ADMIN > BIEN_TAP > XEM
```

- Đăng ký mới → `is_active=0, is_approved=0` → chờ ADMIN duyệt
- Mật khẩu lưu bcrypt hash — không bao giờ lưu plaintext
- Session: cookie HMAC SHA-256, TTL 7 ngày, không dùng JWT

### 5.5 Dữ liệu danh mục

| Danh mục | Số lượng | Mã quan trọng |
|---|---|---|
| Cấp quản lý | 8 | QL, DT, DX, DD, NT, TX, CD, DK |
| Cấp kỹ thuật | 7 | III, IV, V, VI, mn_III, mn_IV, mn_V, mn_VI |
| Kết cấu mặt | 8 | BTN, BTXM, HH, LN, CP, DAT, BTN+LN, BTXM+LN |
| Tình trạng | 9 | TOT, TB, KEM, HH_NANG, THI_CONG, BAO_TRI, TAM_DONG, NGUNG, CHUA_XD |

---

## 6. KHI THÊM TÍNH NĂNG MỚI

### Thêm bảng mới

1. Viết SQL trong `migrations/m001_initial_schema.py` — thêm vào hàm `up()`
2. Tạo `models/ten_bang.py` — Plain Object, có type hints, @property nếu cần
3. Tạo `repositories/ten_bang_repository.py` — chuẩn _SELECT_COLS + _row_to_object
4. Tạo `services/ten_bang_service.py` — validate + business logic
5. Tạo `data/ten_bang_data.py` nếu cần seed dữ liệu
6. Thêm seed vào `seeds/seed_all.py` đúng thứ tự phụ thuộc FK
7. Tạo route trong `api/routes/ten_bang_route.py`
8. Đăng ký route trong `api/main.py`

### Thêm tuyến/đoạn mới

```bash
# 1. Cập nhật file Excel
data/giao_thong_data_upadate.xlsx  # sheet TuyenDuong hoặc DoanTuyen

# 2. Sinh lại data config
python tools/excel_to_data.py

# 3. Seed (idempotent — INSERT OR IGNORE)
python seeds/seed_all.py
```

### Thêm GeoJSON mới

```bash
# Đặt file .geojson vào map/ hoặc data/geojson/
python tools/import_geojson.py map/TENTUYEN.geojson
# Quy tắc: tên file = mã tuyến (QL4E.geojson → ma_tuyen='QL4E')
```

---

## 7. LỖI THƯỜNG GẶP VÀ CÁCH SỬA

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| `OperationalError: no such column` | Dùng `row[index]` cũ | Chuyển sang `row["ten_cot"]` |
| `UNIQUE constraint failed: tuyen_duong.ma_tuyen` | Mã tuyến trùng trong data | Kiểm tra `data/tuyen_duong_data.py` |
| `ImportError: circular import` | Dùng `from models.X import Y` | Đổi sang `import models.X as X_model` |
| `chiều dài không cập nhật` | Hàm thủ công cũ | Chỉ cần INSERT/UPDATE đoạn — trigger tự chạy |
| `403 Forbidden` | Chưa đăng nhập hoặc không đủ quyền | Kiểm tra `loai_quyen` và Depends trong route |
| `DoanDiChungServiceError: tự-tham chiếu` | `tuyen_di_chung_id == tuyen_chinh_id` | Kiểm tra lại data DDC |
| `pydantic ValidationError` | Thiếu field bắt buộc trong request | Kiểm tra schema Pydantic trong route |

---

## 8. BIẾN MÔI TRƯỜNG

| Biến | Mặc định | Mô tả |
|---|---|---|
| `SESSION_SECRET` | `laocai-giaothong-secret-2024` | Secret key ký HMAC session |
| `DB_PATH` | `database/giao_thong.db` | Đường dẫn file SQLite |

Đặt trong `.env` (không commit vào git):
```
SESSION_SECRET=<chuỗi ngẫu nhiên mạnh>
DB_PATH=database/giao_thong.db
```

---

## 9. THAM CHIẾU NHANH CÁC FILE

| Cần làm gì | File cần mở |
|---|---|
| Sửa schema DB | `migrations/m001_initial_schema.py` |
| Sửa kết nối DB | `config/database.py` |
| Sửa model tuyến đường | `models/tuyen_duong.py` |
| Sửa query tuyến đường | `repositories/tuyen_duong_repository.py` |
| Sửa validate tuyến | `services/tuyen_duong_service.py` |
| Sửa route web tuyến | `api/routes/tuyen_duong_route.py` |
| Sửa thống kê | `services/thong_ke_service.py` · `repositories/thong_ke_repository.py` |
| Sửa bản đồ | `api/routes/ban_do.py` · `map/generate_map_multi_mahoa_onefile.py` |
| Sửa auth / session | `api/routes/_auth_helper.py` · `api/routes/auth.py` |
| Cập nhật data từ Excel | `tools/excel_to_data.py` |
| Xem chi tiết từng file | `PROJECT_MAP.md` |
| Xem kiến trúc chi tiết | `ARCHITECTURE.md` |

---

## 10. PROMPTS SẴN CÓ — GỌI BẰNG `@` TRONG CLAUDE CODE

Thư mục `prompts/` chứa các file prompt viết sẵn cho từng tác vụ lớn.
Gọi trực tiếp trong cửa sổ chat của Claude Code bằng cú pháp `@prompts/ten_file.md`.

### Danh sách prompts hiện có

| File | Mô tả | Khi nào dùng |
|---|---|---|
| `prompts/chuan_hoa_css_ui.md` | Chuẩn hóa toàn bộ giao diện: CSS Design System, layout, responsive, hover effects, animations | Khi muốn làm mới hoặc đồng bộ UI toàn dự án |

### Cách gọi trong Claude Code (VSCode)

**Thực thi toàn bộ prompt một lần:**
```
@prompts/chuan_hoa_css_ui.md
```

**Chỉ làm một phần cụ thể:**
```
@prompts/chuan_hoa_css_ui.md chỉ thực hiện Phần 1 (khảo sát) và Phần 2 (Design System), báo cáo kết quả rồi dừng
```

**Tập trung vào một nhóm file:**
```
@prompts/chuan_hoa_css_ui.md chỉ cập nhật templates/tuyen_duong/ trước
```

### Cấu trúc thư mục `prompts/`

```
prompts/
├── chuan_hoa_css_ui.md        ✅ Sẵn sàng — UI/CSS Design System toàn dự án
├── them_tinh_nang_moi.md      (tương lai) Hướng dẫn thêm tính năng CRUD hoàn chỉnh
├── migrate_database.md        (tương lai) Hướng dẫn thêm cột / migration DB
└── deploy_production.md       (tương lai) Hướng dẫn deploy lên VPS Ubuntu + Nginx
```

> **Quan trọng:** File prompt phải nằm trong thư mục `prompts/` tại thư mục gốc
> `D:\Dropbox\@Giaothong2\prompts\`. Claude Code tìm file theo đường dẫn tương đối
> so với thư mục workspace đang mở trong VSCode.

---

*Cập nhật file này sau mỗi thay đổi kiến trúc lớn, thêm quy tắc mới, hoặc thêm prompt mới.*
