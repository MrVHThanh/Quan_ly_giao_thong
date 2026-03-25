# PROJECT_MAP.md — Bản đồ toàn bộ file trong dự án

> File này liệt kê **mọi file** trong dự án với mô tả vai trò và nội dung.
> Dùng để tra cứu nhanh khi cần tìm đúng file để chỉnh sửa.
> Xem `CLAUDE.md` cho quy tắc code · Xem `ARCHITECTURE.md` cho kiến trúc chi tiết.
> Cập nhật lần cuối: 2025-03-25

---

## CÂY THƯ MỤC TỔNG QUAN

```
D:\Dropbox\@Giaothong2\
├── CLAUDE.md                  ← Hướng dẫn làm việc cho Claude Code (ĐỌC TRƯỚC)
├── ARCHITECTURE.md            ← Kiến trúc kỹ thuật chi tiết
├── PROJECT_MAP.md             ← File này — bản đồ toàn bộ project
├── gunicorn.conf.py           ← Cấu hình Gunicorn production
├── main.py                    ← Entry point báo cáo console (dev/test)
├── requirements.txt           ← Dependencies đóng băng phiên bản
├── requirements-minimal.txt   ← Dependencies tối thiểu
├── .gitignore                 ← Ignore: venv/, *.db, .env, luu/, ...
├── .env                       ← Biến môi trường (GITIGNORED — tự tạo)
├── .env.example               ← Mẫu .env
├── giao_thong.db              ← SQLite database (GITIGNORED)
│
├── config/
├── migrations/
├── models/
├── repositories/
├── services/
├── data/
├── seeds/
├── api/
├── templates/
├── static/
├── tools/
├── map/
├── deploy/
└── prompts/
```

---

## config/ — Cấu hình hệ thống

| File | Mô tả |
|---|---|
| `config/__init__.py` | Package init |
| `config/database.py` | Kết nối SQLite, tạo bảng/triggers, hàm `get_db()` cho FastAPI Depends |
| `config/settings.py` | BASE_DIR, DEBUG (từ env), DATABASE_PATH, LOG_FILE |

**Quan trọng về `config/database.py`:**
- Hàm `get_connection()` — trả về `sqlite3.Connection` với WAL mode + foreign_keys=ON + Row factory
- Hàm `get_db()` — FastAPI Depends generator, tự đóng connection sau request
- Hàm `create_tables()` — gọi migration và tạo triggers
- `--reset` flag — xóa toàn bộ DB (DEV ONLY)

---

## migrations/ — Schema DB

| File | Mô tả |
|---|---|
| `migrations/__init__.py` | Package init |
| `migrations/m001_initial_schema.py` | Tạo 13 bảng + 6 triggers + 5 indexes (CREATE TABLE IF NOT EXISTS) |

**Khi thêm bảng mới:** Thêm vào `m001_initial_schema.py` hàm `up()`.

---

## models/ — Plain Objects (14 files)

| File | Class | Fields quan trọng |
|---|---|---|
| `models/cap_quan_ly.py` | `CapQuanLy` | id, ma_cap, ten_cap, mo_ta, thu_tu_hien_thi, is_active |
| `models/cap_duong.py` | `CapDuong` | id, ma_cap, ten_cap, mo_ta, thu_tu_hien_thi, is_active |
| `models/ket_cau_mat_duong.py` | `KetCauMatDuong` | id, ma_ket_cau, ten_ket_cau, mo_ta, thu_tu_hien_thi, is_active |
| `models/tinh_trang.py` | `TinhTrang` | id, ma_tinh_trang, ten_tinh_trang, mo_ta, mau_hien_thi, thu_tu_hien_thi, is_active |
| `models/don_vi.py` | `DonVi` | id, ma_don_vi, ten_don_vi, ten_viet_tat, parent_id, cap_don_vi, dia_chi, so_dien_thoai, email, is_active |
| `models/nguoi_dung.py` | `NguoiDung` | id, ten_dang_nhap, mat_khau_hash, ho_ten, chuc_vu, don_vi_id, loai_quyen, is_active, is_approved |
| `models/tuyen_duong.py` | `TuyenDuong` | id, ma_tuyen, ten_tuyen, cap_quan_ly_id, don_vi_quan_ly_id, diem_dau/cuoi, chieu_dai_quan_ly, chieu_dai_thuc_te |
| `models/thong_tin_tuyen.py` | `ThongTinTuyen` | id, tuyen_id, mo_ta, ly_do_xay_dung, dac_diem_dia_ly, lich_su_hinh_thanh, y_nghia_kinh_te |
| `models/doan_tuyen.py` | `DoanTuyen` | id, ma_doan, tuyen_id, cap_duong_id, tinh_trang_id, ket_cau_mat_id, ly_trinh_dau, ly_trinh_cuoi, chieu_dai_thuc_te, chieu_rong_* |
| `models/doan_di_chung.py` | `DoanDiChung` | id, ma_doan_di_chung, tuyen_di_chung_id, tuyen_chinh_id, doan_id, ly_trinh_* |
| `models/hinh_anh_doan_tuyen.py` | `HinhAnhDoanTuyen` | id, doan_id, duong_dan_file, mo_ta, ngay_chup, lat, lng, ly_trinh_anh |
| `models/tuyen_duong_geo.py` | `TuyenDuongGeo` | id, tuyen_id, coordinates (JSON), so_diem, chieu_dai_gps |
| `models/thong_ke.py` | `ThongKeToanTinh`, `ThongKeMoiTuyen` | Aggregate objects cho thống kê |
| `models/__init__.py` | — | Package init |

---

## repositories/ — Data Access Layer (14 files)

Tất cả dùng `_SELECT_COLS` + `_row_to_object(row)` theo chuẩn.
Không chứa business logic.

| File | Hàm chính |
|---|---|
| `repositories/cap_quan_ly_repository.py` | lay_tat_ca, lay_theo_id, lay_theo_ma, them_cap_quan_ly, cap_nhat, xoa_mem, khoi_phuc |
| `repositories/cap_duong_repository.py` | lay_tat_ca, lay_theo_id, lay_theo_ma, them, cap_nhat, xoa_mem, khoi_phuc |
| `repositories/ket_cau_mat_repository.py` | lay_tat_ca, lay_theo_id, lay_theo_ma, them, cap_nhat, xoa_mem, khoi_phuc |
| `repositories/tinh_trang_repository.py` | lay_tat_ca, lay_theo_id, lay_theo_ma, them, cap_nhat, xoa_mem, khoi_phuc |
| `repositories/don_vi_repository.py` | lay_tat_ca, lay_theo_id, lay_theo_ma, lay_cay_cha_con(), them, cap_nhat |
| `repositories/nguoi_dung_repository.py` | lay_tat_ca, lay_theo_id, lay_theo_ten_dang_nhap(), them, cap_nhat, vo_hieu, khoi_phuc |
| `repositories/tuyen_duong_repository.py` | lay_tat_ca, lay_theo_id, lay_theo_ma, lay_theo_cap_quan_ly(), lay_co_geo(), them, cap_nhat, xoa_mem |
| `repositories/thong_tin_tuyen_repository.py` | lay_theo_tuyen_id(), them_hoac_cap_nhat() |
| `repositories/doan_tuyen_repository.py` | lay_tat_ca, lay_theo_id, lay_theo_ma, lay_theo_tuyen_id(), lay_theo_tinh_trang(), them, cap_nhat, xoa_mem |
| `repositories/doan_di_chung_repository.py` | lay_tat_ca, lay_theo_id, lay_theo_tuyen_di_chung_id(), lay_theo_doan_id(), them, cap_nhat, xoa_mem |
| `repositories/hinh_anh_repository.py` | lay_theo_doan_id(), them, xoa_mem, xoa_vinh_vien() |
| `repositories/tuyen_duong_geo_repository.py` | lay_theo_tuyen_id(), lay_tat_ca_co_geo(), them_hoac_cap_nhat() |
| `repositories/thong_ke_repository.py` | lay_thong_ke_toan_tinh(), lay_thong_ke_moi_tuyen() — JOIN phức tạp |
| `repositories/__init__.py` | Package init |

---

## services/ — Business Logic Layer (14 files)

Mỗi service có exception riêng: `CapQuanLyServiceError`, `TuyenDuongServiceError`, v.v.

| File | Exception | Hàm đặc biệt |
|---|---|---|
| `services/cap_quan_ly_service.py` | `CapQuanLyServiceError` | get_or_create_by_ma() |
| `services/cap_duong_service.py` | `CapDuongServiceError` | get_or_create_by_ma() |
| `services/ket_cau_mat_service.py` | `KetCauMatServiceError` | validate regex `^[A-Z0-9_+\-]{1,20}$`, get_or_create_by_ma() |
| `services/tinh_trang_service.py` | `TinhTrangServiceError` | validate regex `^[A-Z0-9_]{1,20}$`, get_or_create_by_ma() |
| `services/don_vi_service.py` | `DonViServiceError` | lay_cay(), validate parent_id |
| `services/nguoi_dung_service.py` | `NguoiDungServiceError` | xac_thuc(conn, tdn, mk), tao_boi_admin(), duyet_tai_khoan(), doi_mat_khau_admin() |
| `services/tuyen_duong_service.py` | `TuyenDuongServiceError` | validate ma_tuyen unique, get_or_create_by_ma() |
| `services/thong_tin_tuyen_service.py` | `ThongTinTuyenServiceError` | luu_hoac_cap_nhat() |
| `services/doan_tuyen_service.py` | `DoanTuyenServiceError` | validate lý trình (cuoi > dau), validate FK, validate kích thước |
| `services/doan_di_chung_service.py` | `DoanDiChungServiceError` | **validate 6 điều kiện DDC**, sinh ma_doan_di_chung |
| `services/hinh_anh_service.py` | `HinhAnhServiceError` | upload_anh(), doc_exif_gps() |
| `services/tuyen_duong_geo_service.py` | `TuyenDuongGeoServiceError` | parse_geojson(), tinh_haversine() |
| `services/thong_ke_service.py` | — | lay_thong_ke_toan_tinh(), lay_thong_ke_moi_tuyen() |
| `services/__init__.py` | — | Package init |

---

## data/ — Config Python sinh từ Excel

| File | Nội dung |
|---|---|
| `data/cap_quan_ly_data.py` | 8 bản ghi cấp quản lý |
| `data/cap_duong_data.py` | 7 bản ghi cấp đường |
| `data/ket_cau_mat_data.py` | 8 bản ghi kết cấu mặt |
| `data/tinh_trang_data.py` | 9 bản ghi tình trạng |
| `data/don_vi_data.py` | 17 đơn vị (cây cha-con) |
| `data/nguoi_dung_data.py` | 3 tài khoản mặc định |
| `data/tuyen_duong_data.py` | 49 tuyến (9 QL + 27 DT + 13 DX) |
| `data/thong_tin_tuyen_data.py` | 49 metadata tuyến |
| `data/doan_tuyen_data.py` | 222 đoạn tuyến |
| `data/doan_di_chung_data.py` | 15 đoạn đi chung |
| `data/giao_thong_data_upadate.xlsx` | Excel gốc 10 sheets (nguồn dữ liệu) |
| `data/geojson/` | Thư mục chứa file .geojson tự động load lên bản đồ |
| `data/geojson/All/` | Thư mục con — KHÔNG tự động load (raw/intermediate files) |
| `data/__init__.py` | Package init |

---

## seeds/ — Khởi tạo dữ liệu

| File | Mô tả |
|---|---|
| `seeds/seed_all.py` | Orchestrator — gọi tuần tự các seed, idempotent |
| `seeds/seed_danh_muc.py` | Seed 4 bảng danh mục base |
| `seeds/seed_don_vi.py` | Seed cây đơn vị |
| `seeds/seed_nguoi_dung.py` | Seed 3 user với bcrypt hash |
| `seeds/seed_tuyen_doan.py` | Seed 49 tuyến + 222 đoạn + 15 DDC |
| `seeds/__init__.py` | Package init |

---

## api/ — FastAPI Application

### api/main.py — Entry point

- `load_dotenv()` — đọc `.env` trước tất cả import khác
- `FastAPI(docs_url=None nếu production)` — ẩn Swagger khi DEBUG=false
- Middleware: `_SecurityHeadersMiddleware`, `CORSMiddleware`, `slowapi`
- Jinja2 filter `format_ly_trinh` — số → "KmXXX+YYY"
- Đăng ký 8 router groups
- Route `GET /` → dashboard.html
- Route `GET /api/health` → JSON health check

### api/limiter.py

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
```
Shared limiter — import vào bất kỳ route nào cần rate limit.

### api/routes/ — Route Handlers

| File | Prefix | Mô tả |
|---|---|---|
| `api/routes/_auth_helper.py` | — | `yeu_cau_dang_nhap()`, `yeu_cau_quyen_admin()`, `yeu_cau_bien_tap()`, `SESSION_TTL`, `SECRET_KEY` |
| `api/routes/auth.py` | `/auth` | Đăng nhập (rate limited), đăng xuất, đăng ký, chờ duyệt |
| `api/routes/tuyen_duong_route.py` | `/tuyen-duong` | CRUD tuyến + metadata |
| `api/routes/doan_tuyen_route.py` | `/doan-tuyen` | CRUD đoạn + ảnh |
| `api/routes/doan_di_chung_route.py` | `/doan-di-chung` | CRUD DDC |
| `api/routes/danh_muc_route.py` | `/danh-muc` | Quản lý danh mục (cấp QL, cấp đường, kết cấu, tình trạng, đơn vị) |
| `api/routes/he_thong_route.py` | `/he-thong` | Quản lý user, xuất Excel (ADMIN only) |
| `api/routes/thong_ke.py` | `/thong-ke` | Thống kê tổng hợp |
| `api/routes/ban_do.py` | `/ban-do` | Bản đồ Leaflet + API GeoJSON (DB + file) |

---

## templates/ — Jinja2 HTML Templates

### Layout

| File | Mô tả |
|---|---|
| `templates/base.html` | Layout chung: sidebar, topbar, nav links, Bootstrap 5, icons |
| `templates/dashboard.html` | Trang chủ — thống kê tổng quan |
| `templates/thong_ke.html` | Trang thống kê chi tiết |
| `templates/ban_do.html` | Bản đồ Leaflet tương tác — 2 nguồn dữ liệu, bộ lọc |

### auth/

| File | Mô tả |
|---|---|
| `templates/auth/login.html` | Form đăng nhập |
| `templates/auth/dang_ky.html` | Form đăng ký tài khoản mới |
| `templates/auth/dang_ky_thanh_cong.html` | Thông báo đăng ký thành công, chờ duyệt |
| `templates/auth/cho_duyet.html` | Danh sách tài khoản chờ duyệt (ADMIN) |

### danh_muc/

| File | Mô tả |
|---|---|
| `templates/danh_muc/quan_ly.html` | Quản lý: cấp QL, đơn vị, cấp đường |
| `templates/danh_muc/ky_thuat.html` | Quản lý: kết cấu mặt đường, tình trạng (input free-text) |

### tuyen_duong/

| File | Mô tả |
|---|---|
| `templates/tuyen_duong/list.html` | Danh sách tuyến, filter theo cấp QL |
| `templates/tuyen_duong/form.html` | Form thêm/sửa tuyến đường |
| `templates/tuyen_duong/detail.html` | Chi tiết tuyến + danh sách đoạn |
| `templates/tuyen_duong/thong_tin_form.html` | Form metadata mô tả tuyến |

### doan_tuyen/

| File | Mô tả |
|---|---|
| `templates/doan_tuyen/list.html` | Danh sách đoạn, filter |
| `templates/doan_tuyen/form.html` | Form thêm/sửa đoạn (lý trình, chất lượng) |
| `templates/doan_tuyen/detail.html` | Chi tiết đoạn + ảnh |

### doan_di_chung/

| File | Mô tả |
|---|---|
| `templates/doan_di_chung/list.html` | Danh sách DDC |
| `templates/doan_di_chung/form.html` | Form sửa DDC |
| `templates/doan_di_chung/form_them.html` | Form thêm DDC mới |

### he_thong/

| File | Mô tả |
|---|---|
| `templates/he_thong/nguoi_dung.html` | Quản lý user: danh sách, thêm, sửa, duyệt, đổi mật khẩu |

---

## static/ — Tài nguyên tĩnh

| File | Mô tả |
|---|---|
| `static/css/design-system.css` | CSS Design System: variables, sidebar, topbar, buttons, cards |
| `static/css/style.css` | CSS custom bổ sung |
| `static/js/app.js` | JavaScript chung (toggle sidebar, v.v.) |

---

## tools/ — Công cụ tiện ích

| File | Mô tả |
|---|---|
| `tools/excel_to_data.py` | Đọc Excel 10 sheets → sinh file `data/*_data.py` |
| `tools/import_geojson.py` | Import .geojson → bảng `tuyen_duong_geo` (parse + Haversine + JSON) |
| `tools/export_geojson.py` | Export `tuyen_duong_geo` → file .geojson theo `--ma-tuyen` |

---

## map/ — GeoJSON và Bản đồ tĩnh

| File | Mô tả |
|---|---|
| `map/QL4E.geojson` | GeoJSON tuyến QL4E (132 KB) |
| `map/DT158.geojson` | GeoJSON tuyến DT158 (305 KB) |
| `map/Giao_thong_map_onefile.html` | Bản đồ HTML tĩnh nhiều tuyến (120 KB, không dùng cho web app) |
| `map/generate_map_multi_mahoa_onefile.py` | Script tạo bản đồ tĩnh |
| `map/merge_roads.py` | Merge nhiều GeoJSON thành 1 file |
| `map/csv2geojson.py` | Chuyển CSV toạ độ → GeoJSON |
| `map/dao_chieu_tuyen_geojson.py` | Đảo chiều tuyến (đổi hướng LineString) |
| `map/Laocai_thongtin.json` | Dữ liệu thông tin địa lý Lào Cai (62 KB) |

---

## deploy/ — Cấu hình Production

| File | Mô tả |
|---|---|
| `deploy/nginx.conf` | Nginx: HTTP→HTTPS redirect, SSL termination, proxy_pass 127.0.0.1:8000, serve /static |
| `deploy/giaothong.service` | systemd unit: EnvironmentFile, ExecStart gunicorn, Restart=on-failure |
| `gunicorn.conf.py` | bind="127.0.0.1:8000", workers=CPU×2+1, UvicornWorker, max_requests=1000 |

---

## prompts/ — Prompt Templates cho Claude Code

| File | Mô tả |
|---|---|
| `prompts/chuan_hoa_css_ui.md` | Chuẩn hóa toàn bộ giao diện CSS (gọi bằng `@prompts/chuan_hoa_css_ui.md`) |

---

## Tài liệu kỹ thuật (legacy — có thể bị lỗi thời)

| File | Mô tả |
|---|---|
| `PROJECT_STRUCTURE.md` | Cấu trúc cũ (legacy) |
| `PROJECT_STRUCTURE_1.md` | Tài liệu mở rộng cũ |
| `PROJECT_STRUCTURE_2.md` | Tài liệu mở rộng cũ |
| `REVIEW_DU_AN_KY_THUAT.md` | Đánh giá kỹ thuật |
| `TIEN_DO_DU_AN.md` | Tiến độ dự án |
| `PROMPT_CHUAN_HOA_CSS_UI.md` | Bản sao prompt CSS (xem `prompts/chuan_hoa_css_ui.md`) |
| `docs/He_thong_quan_ly_tuyen_duong_V1.md` | Tài liệu hệ thống v1 |

---

## Files gitignored (không commit)

```
venv/                    # Python virtual environment
giao_thong.db            # SQLite database (tạo bằng seed_all.py)
.env                     # Biến môi trường (tạo từ .env.example)
__pycache__/             # Python cache
*.pyc                    # Compiled Python
.vscode/                 # VS Code settings
luu/                     # Lưu trữ cũ
map/Luu/                 # Lưu trữ bản đồ cũ
data_noload/             # Dữ liệu không tải
api/how_to_run.py        # Hướng dẫn nội bộ (chứa thông tin nhạy cảm)
*.log                    # Log files
Thumbs.db, .DS_Store     # OS files
```

---

*Cập nhật file này mỗi khi thêm/xóa file quan trọng hoặc thay đổi cấu trúc thư mục.*
