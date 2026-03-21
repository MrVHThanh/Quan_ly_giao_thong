# KẾ HOẠCH DỰ ÁN: HỆ THỐNG QUẢN LÝ GIAO THÔNG LÀO CAI

**Sở Xây dựng tỉnh Lào Cai** | Python + SQLite → FastAPI Web Application
**Thư mục dự án:** `D:\Dropbox\@Giaothong2\`
**File dữ liệu nguồn:** `data/giao_thong_data_upadate.xlsx`

---

## CÁCH SỬ DỤNG FILE NÀY

> Đầu mỗi buổi làm việc: gửi file này cho Claude + nêu việc cần làm hôm nay.
> Cuối mỗi buổi: cập nhật trạng thái các ô checkbox và ghi chú kết quả.
> Ký hiệu: `[x]` = hoàn thành · `[~]` = đang làm · `[ ]` = chưa làm · `[!]` = có vấn đề cần xử lý

---

## TRẠNG THÁI TỔNG QUAN

| Bước | Tên                            | Trạng thái    | Ghi chú |
| ------ | ------------------------------- | --------------- | -------- |
| 1      | Làm sạch dữ liệu Excel      | ✅ HOÀN THÀNH |          |
| 2      | Thiết kế lại Schema DB       | ✅ HOÀN THÀNH |          |
| 3      | Viết lại Models               | ✅ HOÀN THÀNH |          |
| 4      | Viết lại Repositories         | ✅ HOÀN THÀNH |          |
| 5      | Viết lại Services             | ✅ HOÀN THÀNH |          |
| 6      | Viết lại Data files từ Excel | ✅ HOÀN THÀNH |          |
| 7      | Seeds + Migration               | ✅ HOÀN THÀNH |          |
| 8      | GeoJSON Tools + Web FastAPI     | ⏳ TIẾP THEO   |          |

---

## SỐ LIỆU DỰ ÁN (ĐÃ XÁC NHẬN)

| Hạng mục           | Số lượng | Ghi chú                                                           |
| -------------------- | ----------- | ------------------------------------------------------------------ |
| Tuyến đường      | 49          | 9 QL + 27 DT + 13 DX                                               |
| Đoạn tuyến        | 222         |                                                                    |
| Đoạn đi chung     | 15          | Đã tách đúng từng đoạn vật lý                            |
| Bảng DB mới        | 13          | Tăng từ 6 bảng cũ                                              |
| Đơn vị            | 17          | TINH→SXD→BAN_BT + 13 CT độc lập                               |
| Loại kết cấu mặt | 8           | BTN, BTXM, HH, LN, CP, DAT, BTN+LN, BTXM+LN                        |
| Tình trạng         | 9           | TOT, TB, KEM, HH_NANG, THI_CONG, BAO_TRI, TAM_DONG, NGUNG, CHUA_XD |
| File GeoJSON         | 2 hiện có | QL4E.geojson (5039 điểm), DT158.geojson (4274 điểm)            |

---

## BƯỚC 1 — LÀM SẠCH DỮ LIỆU EXCEL ✅ HOÀN THÀNH

### Kết quả đã đạt được

- [X] 10 sheet dữ liệu đầy đủ và sạch
- [X] DoanDiChung: tách đúng từng đoạn vật lý (15 bản ghi), kiểm tra tự động lý trình
- [X] DonVi: cây cha-con đúng (TINH→SXD→BAN_BT), 13 CT parent=NULL
- [X] Tình trạng nhất quán với bảng TinhTrang
- [X] Kết cấu mặt: thêm mã tổ hợp BTN+LN và BTXM+LN
- [X] Đơn vị quản lý tuyến: thống nhất dùng mã TINH
- [X] Sheet NguoiDung: 3 tài khoản khởi tạo
- [X] Quy ước GeoJSON: tên file = mã tuyến (QL4E.geojson), road_name = tên tuyến trong DB

---

## BƯỚC 2 — THIẾT KẾ LẠI SCHEMA DATABASE ✅ HOÀN THÀNH

**File cần tạo/sửa:** `config/database.py`

### Công việc cần làm

- [X] Viết hàm `get_connection()` với `conn.row_factory = sqlite3.Row`
- [X] Tạo 13 bảng theo đúng thứ tự phụ thuộc khóa ngoại
- [X] Viết 6 SQLite triggers (INSERT/UPDATE/DELETE cho doan_tuyen và doan_di_chung)
- [X] Tạo 5 indexes tối ưu truy vấn
- [X] Viết hàm `create_tables()` gọi tất cả
- [X] Test: chạy create_tables() không lỗi, kiểm tra .schema trong SQLite

### 13 bảng theo thứ tự tạo

```
1.  cap_quan_ly          (8 bản ghi) — giữ nguyên
2.  cap_duong            (7 bản ghi) — giữ nguyên
3.  ket_cau_mat_duong    (8 bản ghi) — MỚI
4.  tinh_trang           (9 bản ghi) — giữ nguyên
5.  don_vi              (17 bản ghi) — giữ nguyên
6.  nguoi_dung           (3+ bản ghi) — MỚI
7.  tuyen_duong         (49 bản ghi) — bỏ chieu_dai, giữ chieu_dai_thuc_te + chieu_dai_quan_ly
8.  thong_tin_tuyen      (9+ bản ghi) — MỚI
9.  doan_tuyen          (222 bản ghi) — thêm ket_cau_mat_id, nam_lam_moi, ngay_cap_nhat_tinh_trang, updated_at, updated_by_id
10. doan_di_chung        (15 bản ghi) — cấu trúc mới (xem chi tiết bên dưới)
11. hinh_anh_doan_tuyen  (0 bản ghi) — MỚI
12. tuyen_duong_geo      (0 bản ghi) — MỚI (Giai đoạn 1 GeoJSON)
13. doan_tuyen_geo       (0 bản ghi) — MỚI (Giai đoạn 2 GeoJSON — tạo sẵn, chưa dùng)
```

### Schema chi tiết các bảng thay đổi

**tuyen_duong** — bỏ `chieu_dai`:

```
id, ma_tuyen, ten_tuyen, cap_quan_ly_id, don_vi_quan_ly_id,
diem_dau, diem_cuoi, lat_dau, lng_dau, lat_cuoi, lng_cuoi,
chieu_dai_thuc_te,    ← tổng đoạn chính + đoạn đi chung (trigger tự cập nhật)
chieu_dai_quan_ly,    ← chỉ tổng đoạn chính (trigger tự cập nhật)
nam_xay_dung, nam_hoan_thanh, ghi_chu, created_at
```

**doan_tuyen** — thêm 5 trường mới:

```
id, ma_doan, tuyen_id, cap_duong_id, tinh_trang_id,
ket_cau_mat_id,              ← MỚI FK→ket_cau_mat_duong
ly_trinh_dau, ly_trinh_cuoi,
chieu_dai_thuc_te,
chieu_rong_mat_min, chieu_rong_mat_max,
chieu_rong_nen_min, chieu_rong_nen_max,
don_vi_bao_duong_id,
nam_lam_moi,                 ← MỚI năm sửa chữa/nâng cấp gần nhất
ngay_cap_nhat_tinh_trang,    ← MỚI ngày khảo sát tình trạng
ghi_chu, created_at,
updated_at,                  ← MỚI tự động cập nhật
updated_by_id                ← MỚI FK→nguoi_dung
```

**doan_di_chung** — cấu trúc mới hoàn toàn:

```
id, ma_doan_di_chung,        ← MỚI VD: DDC-DT159-QL4E-01-001
tuyen_di_chung_id,           ← FK→tuyen_duong (tuyến đi nhờ: DT159)
tuyen_chinh_id,              ← MỚI FK→tuyen_duong (tuyến chủ: QL4E)
doan_id,                     ← FK→doan_tuyen (đoạn vật lý: QL4E-01)
ly_trinh_dau_di_chung,       ← lý trình theo tuyến đi nhờ
ly_trinh_cuoi_di_chung,      ← lý trình theo tuyến đi nhờ
ly_trinh_dau_tuyen_chinh,    ← lý trình theo tuyến chủ
ly_trinh_cuoi_tuyen_chinh,   ← lý trình theo tuyến chủ
ghi_chu, created_at
UNIQUE(tuyen_di_chung_id, doan_id)
```

**nguoi_dung** — MỚI:

```
id, ten_dang_nhap UNIQUE, mat_khau_hash,
ho_ten, chuc_vu, don_vi_id, so_dien_thoai, email UNIQUE,
loai_quyen,     ← ADMIN / BIEN_TAP / XEM
is_active DEFAULT 0, is_approved DEFAULT 0,
approved_by_id, approved_at, created_at, last_login
```

**ket_cau_mat_duong** — MỚI:

```
id, ma_ket_cau UNIQUE, ten_ket_cau, mo_ta,
thu_tu_hien_thi, is_active DEFAULT 1
```

**hinh_anh_doan_tuyen** — MỚI:

```
id, doan_id FK, duong_dan_file,
mo_ta, ngay_chup, nguoi_chup,
lat, lng,          ← tọa độ trích từ EXIF (NULL nếu không có)
ly_trinh_anh,      ← tính từ lat/lng + đường tâm tuyến (giai đoạn 2)
created_at
```

**tuyen_duong_geo** — MỚI (Giai đoạn 1):

```
id, tuyen_id FK UNIQUE,
coordinates TEXT,  ← JSON: [[lng,lat],[lng,lat],...]
so_diem, chieu_dai_gps, nguon, updated_at
```

**doan_tuyen_geo** — MỚI (Giai đoạn 2, tạo sẵn chưa dùng):

```
id, doan_id FK UNIQUE,
coordinates TEXT,  ← JSON: [[lng,lat],...]
so_diem, chieu_dai_gps, nguon, updated_at
```

### Triggers cần viết (6 triggers)

```
trg_doan_tuyen_sau_them     → AFTER INSERT ON doan_tuyen
trg_doan_tuyen_sau_sua      → AFTER UPDATE ON doan_tuyen
trg_doan_tuyen_sau_xoa      → AFTER DELETE ON doan_tuyen
trg_ddc_sau_them            → AFTER INSERT ON doan_di_chung
trg_ddc_sau_sua             → AFTER UPDATE ON doan_di_chung
trg_ddc_sau_xoa             → AFTER DELETE ON doan_di_chung
```

Mỗi trigger cập nhật:

- `tuyen_duong.chieu_dai_quan_ly` = SUM(COALESCE(chieu_dai_thuc_te, ly_trinh_cuoi-ly_trinh_dau)) FROM doan_tuyen WHERE tuyen_id = affected_tuyen_id
- `tuyen_duong.chieu_dai_thuc_te` = chieu_dai_quan_ly + SUM(ly_trinh_cuoi_di_chung - ly_trinh_dau_di_chung) FROM doan_di_chung WHERE tuyen_di_chung_id = affected_tuyen_id

### Indexes cần tạo (5 indexes)

```
idx_doan_tuyen_tuyen_id         ON doan_tuyen(tuyen_id)
idx_doan_tuyen_cap_duong_id     ON doan_tuyen(cap_duong_id)
idx_doan_tuyen_tinh_trang_id    ON doan_tuyen(tinh_trang_id)
idx_ddc_tuyen_di_chung_id       ON doan_di_chung(tuyen_di_chung_id)
idx_ddc_doan_id                 ON doan_di_chung(doan_id)
```

### Kết quả đạt được khi hoàn thành Bước 2

- [X] `config/database.py` chạy được, tạo đủ 13 bảng
- [X] Kết nối dùng `sqlite3.Row` toàn bộ dự án
- [X] Triggers hoạt động: thêm đoạn → chiều dài tuyến tự cập nhật
- [X] Schema sẵn sàng cho cả GeoJSON Giai đoạn 1 và 2

---

## BƯỚC 3 — VIẾT LẠI MODELS ✅ HOÀN THÀNH

**Thư mục:** `models/`
**Nguyên tắc:** Plain Object thuần túy — KHÔNG logic nghiệp vụ, KHÔNG gọi DB

### Danh sách 13 file models

| File                   | Trạng thái | Thay đổi                                                |
| ---------------------- | ------------ | --------------------------------------------------------- |
| cap_quan_ly.py         | [x ]         | Giữ nguyên + type hints                                 |
| cap_duong.py           | [x ]         | Giữ nguyên + type hints                                 |
| ket_cau_mat_duong.py   | [x ]         | MỚI                                                      |
| tinh_trang.py          | [x ]         | Giữ nguyên + type hints                                 |
| don_vi.py              | [x ]         | Giữ nguyên + type hints                                 |
| nguoi_dung.py          | [x ]         | MỚI                                                      |
| tuyen_duong.py         | [x ]         | Bỏ chieu_dai, giữ chieu_dai_thuc_te + chieu_dai_quan_ly |
| thong_tin_tuyen.py     | [x ]         | MỚI                                                      |
| doan_tuyen.py          | [x ]         | +5 trường mới, bỏ _validate()                         |
| doan_di_chung.py       | [x ]         | Cấu trúc mới 2 cặp lý trình                         |
| hinh_anh_doan_tuyen.py | [x ]         | MỚI                                                      |
| tuyen_duong_geo.py     | [x ]         | MỚI                                                      |
| thong_ke.py            | [x ]         | Cập nhật thêm trường ket_cau_mat                     |

### Quy tắc viết Model

- `__init__` nhận tham số, gán vào `self`
- `@property` cho tính toán đơn giản (vd: `chieu_dai = ly_trinh_cuoi - ly_trinh_dau`)
- KHÔNG có `_validate()` — chuyển sang Service
- Tất cả tham số có **type hints** + giá trị mặc định `None`

---

## BƯỚC 4 — VIẾT LẠI REPOSITORIES ✅ HOÀN THÀNH

**Thư mục:** `repositories/`
**Nguyên tắc:** Chỉ SQL thuần, dùng `sqlite3.Row`, KHÔNG hardcode index cột

### Thay đổi kỹ thuật cốt lõi

- **Bỏ hoàn toàn:** `row[0]`, `row[7]`, `row[8]`... (index cứng)
- **Thay bằng:** `row["id"]`, `row["tinh_trang_id"]`, `row["chieu_dai"]`
- **Bỏ:** hàm `cap_nhat_chieu_dai_tuyen()` (trigger tự động làm)

### Danh sách 13 repositories

| File                          | Trạng thái | Ghi chú                      |
| ----------------------------- | ------------ | ----------------------------- |
| cap_quan_ly_repository.py     | [x ]         | + xoa_mem, khoi_phuc          |
| cap_duong_repository.py       | [x ]        | + xoa_mem, khoi_phuc          |
| ket_cau_mat_repository.py     | [x ]         | MỚI                          |
| tinh_trang_repository.py      | [x ]         | + xoa_mem, khoi_phuc          |
| don_vi_repository.py          | [x ]         | + lay_cay_cha_con             |
| nguoi_dung_repository.py      | [x ]         | MỚI                          |
| tuyen_duong_repository.py     | [x ]         | Bỏ cap_nhat_chieu_dai        |
| thong_tin_tuyen_repository.py | [x ]         | MỚI                          |
| doan_tuyen_repository.py      | [x ]         | Cập nhật _SELECT_COLS mới  |
| doan_di_chung_repository.py   | [x ]         | Cấu trúc mới               |
| hinh_anh_repository.py        | [x ]         | MỚI                          |
| tuyen_duong_geo_repository.py | [x ]         | MỚI                          |
| thong_ke_repository.py        | [x ]         | + thống kê theo ket_cau_mat |

---

## BƯỚC 5 — VIẾT LẠI SERVICES ✅ HOÀN THÀNH

**Thư mục:** `services/`
**Nguyên tắc:** Toàn bộ business logic + validation tập trung ở đây

### Quy tắc import BẮT BUỘC (áp dụng cho toàn dự án)

```python
import models.cap_quan_ly as cap_quan_ly_model
import models.doan_tuyen as doan_tuyen_model
import repositories.doan_tuyen_repository as doan_tuyen_repo
import services.tuyen_duong_service as tuyen_duong_service
```

> Không dùng `from models.doan_tuyen import DoanTuyen` — dùng `doan_tuyen_model.DoanTuyen`

### Danh sách 13 services

| File                       | Trạng thái | Ghi chú                                         |
| -------------------------- | ------------ | ------------------------------------------------ |
| cap_quan_ly_service.py     | [x ]         | Chuyển validation từ model sang đây          |
| cap_duong_service.py       | [x ]         |                                                  |
| ket_cau_mat_service.py     | [x ]         | MỚI — get_or_create                            |
| tinh_trang_service.py      | [x ]         |                                                  |
| don_vi_service.py          | [x ]         | + kiểm tra vòng lặp cây cha-con              |
| nguoi_dung_service.py      | [x ]         | MỚI — bcrypt, phân quyền                     |
| tuyen_duong_service.py     | [x ]         | Bỏ cap_nhat_chieu_dai                           |
| thong_tin_tuyen_service.py | [x ]         | MỚI                                             |
| doan_tuyen_service.py      | [x ]         | Validation ra khỏi model, type hints            |
| doan_di_chung_service.py   | [x ]         | Validate lý trình, tham chiếu đoạn vật lý |
| hinh_anh_service.py        | [x ]         | MỚI — đọc EXIF GPS tự động (Pillow)       |
| tuyen_duong_geo_service.py | [x ]         | MỚI — import/export GeoJSON                    |
| thong_ke_service.py        | [x ]         | + thống kê theo ket_cau_mat                    |

---

## BƯỚC 6 — VIẾT LẠI DATA FILES TỪ EXCEL ✅ HOÀN THÀNH

**Thư mục:** `data/`
**Script tạo tự động:** `tools/excel_to_data.py`

### Danh sách 9 file data

| File                  | Sheet nguồn                      | Trạng thái |
| --------------------- | --------------------------------- | ------------ |
| cap_quan_ly_data.py   | CapQuanLy (8)                     | [x ]         |
| cap_duong_data.py     | CapDuong (7)                      | [x ]         |
| ket_cau_mat_data.py   | KetCauMat (8)                     | [x ]         |
| tinh_trang_data.py    | TinhTrang (9)                     | [x ]         |
| don_vi_data.py        | DonVi (17)                        | [x ]         |
| tuyen_duong_data.py   | TuyenDuong + ThongTinTuyen (49+9) | [x ]         |
| doan_tuyen_data.py    | DoanTuyen (222)                   | [x ]         |
| doan_di_chung_data.py | DoanDiChung (15)                  | [x ]         |
| nguoi_dung_data.py    | NguoiDung (3)                     | [x ]         |

### Xử lý đặc biệt

- `don_vi_data.py`: parent_id dùng mã (SXD) → code seed tra ra id thực
- `doan_di_chung_data.py`: sinh `ma_doan_di_chung` tự động
- Bỏ qua mọi dòng trống khi đọc Excel

---

## BƯỚC 7 — SEEDS + MIGRATION ✅ HOÀN THÀNH

**Thư mục:** `seeds/` và `migrations/`

### Thứ tự seed BẮT BUỘC

```
1. cap_quan_ly, cap_duong, ket_cau_mat_duong, tinh_trang
2. don_vi  (theo cây cha-con)
3. nguoi_dung  (mật khẩu bcrypt)
4. tuyen_duong → thong_tin_tuyen
5. doan_tuyen  (trigger tự cập nhật chieu_dai_quan_ly)
6. doan_di_chung  (trigger tự cập nhật chieu_dai_thuc_te)
```

### Files cần tạo

| File                             | Trạng thái |
| -------------------------------- | ------------ |
| seeds/seed_all.py                | [x ]         |
| seeds/seed_danh_muc.py           | [x ]         |
| seeds/seed_don_vi.py             | [x ]         |
| seeds/seed_nguoi_dung.py         | [x ]         |
| seeds/seed_tuyen_doan.py         | [x ]         |
| migrations/001_initial_schema.py | [x ]         |

### Tính chất Idempotent

- Tất cả seed dùng `INSERT OR IGNORE` (get_or_create)
- Toàn bộ chạy trong 1 transaction — lỗi thì rollback toàn bộ

---

## BƯỚC 8 — GEOJSON TOOLS + WEB FASTAPI ⏳ TIẾP THEO

### 8A — GeoJSON Tools

| File                    | Trạng thái | Chức năng                        |
| ----------------------- | ------------ | ---------------------------------- |
| tools/excel_to_data.py  | [ ]          | Excel → 9 file data/*.py          |
| tools/import_geojson.py | [ ]          | *.geojson → bảng tuyen_duong_geo |
| tools/export_geojson.py | [ ]          | DB → xuất file *.geojson         |

### 8B — Web Application

| Module                    | Trạng thái |
| ------------------------- | ------------ |
| api/main.py               | [ ]          |
| api/routes/auth.py        | [ ]          |
| api/routes/tuyen_duong.py | [ ]          |
| api/routes/doan_tuyen.py  | [ ]          |
| api/routes/thong_ke.py    | [ ]          |
| api/routes/ban_do.py      | [ ]          |
| templates/dashboard.html  | [ ]          |
| templates/ban_do.html     | [ ]          |
| templates/tuyen_duong/    | [ ]          |
| templates/doan_tuyen/     | [ ]          |

### Tính năng Web theo ưu tiên

1. [ ] Đăng nhập, phân quyền (ADMIN/BIEN_TAP/XEM)
2. [ ] Xem danh sách tuyến, đoạn — thống kê cơ bản
3. [ ] Bản đồ Leaflet.js từ tuyen_duong_geo
4. [ ] CRUD tuyến, đoạn, DDC
5. [ ] Upload ảnh, đọc EXIF GPS
6. [ ] Import/Export GeoJSON và Excel

---

## CÁC QUYẾT ĐỊNH THIẾT KẾ ĐÃ THỐNG NHẤT

> Đây là các quyết định đã được bàn và thống nhất. Không thay đổi trừ khi có thảo luận lại.

### DB và Schema

- `tuyen_duong` KHÔNG có cột `chieu_dai` — chỉ có `chieu_dai_thuc_te` và `chieu_dai_quan_ly`
- Chiều dài tuyến do **SQLite trigger** tự động cập nhật — KHÔNG gọi thủ công
- Kết nối DB dùng `conn.row_factory = sqlite3.Row` — truy cập theo tên cột
- Migration script thay vì xóa DB khi thêm cột/bảng mới

### Đoạn đi chung

- Mỗi bản ghi `doan_di_chung` tham chiếu đúng **1 đoạn vật lý** (doan_id)
- Nếu DDC vắt qua nhiều đoạn vật lý → tách thành nhiều bản ghi riêng
- Lưu lý trình **2 chiều**: theo tuyến đi nhờ VÀ theo tuyến chủ
- Cột `chieu_dai_di_chung` KHÔNG lưu — tính từ `ly_trinh_cuoi - ly_trinh_dau`

### GeoJSON

- Tên file = mã tuyến: `QL4E.geojson`, `DT158.geojson`
- `road_name` trong file = tên tuyến trong DB: "Quốc lộ 4E"
- Giai đoạn 1: lưu theo tuyến (`tuyen_duong_geo`)
- Giai đoạn 2: lưu theo đoạn (`doan_tuyen_geo`) — bảng tạo sẵn, chưa dùng
- Tọa độ ảnh: đọc EXIF tự động bằng Pillow khi upload

### Code Python

- **Import style bắt buộc:** `import models.doan_tuyen as doan_tuyen_model`
- Validation nằm ở **Service**, Model chỉ chứa `__init__` và `@property`
- Tất cả hàm có **type hints** đầy đủ
- Bỏ qua dòng trống khi đọc Excel hoặc file dữ liệu

### Phân quyền người dùng

- 3 cấp: `ADMIN` (toàn quyền) / `BIEN_TAP` (thêm/sửa) / `XEM` (chỉ xem)
- Đăng ký → chờ ADMIN duyệt mới được dùng
- Mật khẩu lưu bằng bcrypt hash, không lưu rõ

---

## VẤN ĐỀ CÒN MỞ / CẦN QUYẾT ĐỊNH SAU

| # | Vấn đề                                          | Ghi chú                                                 |
| - | -------------------------------------------------- | -------------------------------------------------------- |
| 1 | 40 tuyến DT/DX chưa có mô tả ThongTinTuyen    | Bổ sung dần qua Web                                    |
| 2 | Giai đoạn 2: tách tọa độ GeoJSON theo đoạn | Cần thuật toán nội suy lý trình → tọa độ       |
| 3 | Ảnh hiện trạng: ly_trinh_anh                    | Tính từ lat/lng + đường tâm tuyến (Giai đoạn 2) |
| 4 | Triển khai lên VPS                               | Sau khi hoàn thành test trên WSL                      |

---

## GHI CHÚ CÁC BUỔI LÀM VIỆC

| Ngày           | Bước | Công việc đã làm                  | Kết quả           | Việc còn lại |
| --------------- | ------ | -------------------------------------- | ------------------- | --------------- |
|                 |        |                                        |                     |                 |
| (buổi trước) | 1      | Làm sạch Excel, kiểm tra tự động | ✅ Excel sạch 100% | —              |
| 22/3/2026       | 2      | Thiết kế lại Schema DB              | ✅ HOÀN THÀNH     |                 |
| 22/3/2026       | 3      | Viết lại Models                      | ✅ HOÀN THÀNH     |                 |
| 22/3/2026       | 4      | Viết lại Repositories                | ✅ HOÀN THÀNH     |                 |
| 22/3/2026       | 5      | Viết lại Services                    | ✅ HOÀN THÀNH     |                 |
| 22/3/2026       | 6      | Viết lại Data files từ Excel        | ✅ HOÀN THÀNH     |                 |
| 22/3/2026       | 7      | Seeds + Migration                      | ✅ HOÀN THÀNH     |                 |
| 22/3/2026       | 8      | GeoJSON Tools + Web FastAPI            |                     |                 |
|                 |        |                                        |                     |                 |
|                 |        |                                        |                     |                 |

---

*File này được tạo và duy trì trong suốt quá trình phát triển dự án.*
*Cập nhật sau mỗi buổi làm việc để phản ánh đúng trạng thái hiện tại.*
