# PROJECT_MAP.md — Bản đồ toàn bộ file trong dự án

> File này liệt kê **mọi file** trong dự án với mô tả ngắn gọn về vai trò và nội dung.
> Dùng để tra cứu nhanh khi cần tìm đúng file để chỉnh sửa.
> Xem `CLAUDE.md` cho quy tắc code · Xem `ARCHITECTURE.md` cho kiến trúc chi tiết.

---

## CÂY THƯ MỤC TỔNG QUAN

```
@Giaothong2/
├── CLAUDE.md                    ← Hướng dẫn làm việc cho Claude Code
├── ARCHITECTURE.md              ← Kiến trúc kỹ thuật chi tiết
├── PROJECT_MAP.md               ← File này
├── PROJECT_STRUCTURE.md         ← Tài liệu cấu trúc (legacy)
├── main.py                      ← Entry point báo cáo console
├── requirements.txt             ← Dependencies pinned version
├── requirements-minimal.txt     ← Dependencies minimal (unpinned)
│
├── config/                      ← Cấu hình hệ thống
├── models/                      ← Plain Objects (13 files)
├── repositories/                ← Data Access Layer (13 files)
├── services/                    ← Business Logic Layer (13 files)
├── data/                        ← Data config + Excel nguồn
├── seeds/                       ← Khởi tạo dữ liệu
├── migrations/                  ← Schema migration
├── tools/                       ← Công cụ tiện ích
├── api/                         ← Web Application FastAPI
├── templates/                   ← Jinja2 HTML templates
├── static/                      ← CSS, JS, ảnh tĩnh
├── map/                         ← GeoJSON + bản đồ Leaflet
└── database/                    ← File SQLite (gitignored)
```

---

## ROOT FILES

| File | Mô tả |
|---|---|
| `main.py` | Entry point chạy báo cáo tổng hợp ra console. Dùng để test nhanh sau seed. |
| `requirements.txt` | Dependencies đã pin version cụ thể. Dùng cho production. |
| `requirements-minimal.txt` | Dependencies không pin version. Dùng khi deploy môi trường mới. |

---

## config/

Cấu hình kết nối DB và đường dẫn hệ thống.

| File | Nội dung chính |
|---|---|
| `config/database.py` | **File quan trọng nhất của tầng DB.** Chứa: `get_connection()` (sqlite3.Row factory), `create_tables()` (gọi migration), `get_db()` (generator cho FastAPI Depends), `drop_all_tables()` (DEV ONLY), `get_schema_info()` (kiểm tra schema hiện tại). |
| `config/settings.py` | `BASE_DIR`, `DB_PATH`, `DB_PATH_DEFAULT`. Import từ đây để lấy đường dẫn. |

---

## models/

Plain Objects — chỉ lưu dữ liệu. Không gọi DB, không validate nghiệp vụ, không import từ repositories hoặc services.

| File | Class | Thuộc tính đặc biệt |
|---|---|---|
| `models/cap_quan_ly.py` | `CapQuanLy` | `id, ma_cap, ten_cap, thu_tu_hien_thi, is_active` |
| `models/cap_duong.py` | `CapDuong` | `id, ma_cap, ten_cap, thu_tu_hien_thi, is_active` |
| `models/ket_cau_mat_duong.py` | `KetCauMatDuong` | `id, ma_ket_cau, ten_ket_cau, thu_tu_hien_thi, is_active` |
| `models/tinh_trang.py` | `TinhTrang` | `id, ma_tinh_trang, ten_tinh_trang, mau_hien_thi (hex), is_active` |
| `models/don_vi.py` | `DonVi` | `id, ma_don_vi, ten_don_vi, parent_id, cap_don_vi, is_active` |
| `models/nguoi_dung.py` | `NguoiDung` | `mat_khau_hash (bcrypt), loai_quyen (ADMIN/BIEN_TAP/XEM), is_approved` · `@property: la_admin, co_quyen_bien_tap` |
| `models/tuyen_duong.py` | `TuyenDuong` | `ma_tuyen, chieu_dai_quan_ly, chieu_dai_thuc_te (trigger quản lý), lat/lng dau/cuoi` · `@property: toa_do_dau, toa_do_cuoi` |
| `models/thong_tin_tuyen.py` | `ThongTinTuyen` | `tuyen_id, mo_ta` và các trường metadata bổ sung |
| `models/doan_tuyen.py` | `DoanTuyen` | `ma_doan, tuyen_id, ly_trinh_dau/cuoi, chieu_dai_thuc_te, ket_cau_mat_id, tinh_trang_id` · `@property: chieu_dai, chieu_dai_tinh` |
| `models/doan_di_chung.py` | `DoanDiChung` | `tuyen_di_chung_id, tuyen_chinh_id, doan_id, ly_trinh_dau/cuoi_di_chung, ly_trinh_dau/cuoi_tuyen_chinh` · `@property: chieu_dai_di_chung, chieu_dai_tuyen_chinh` |
| `models/hinh_anh_doan_tuyen.py` | `HinhAnhDoanTuyen` | `doan_id, duong_dan, lat_anh, lng_anh, mo_ta` · `@property: co_gps` |
| `models/tuyen_duong_geo.py` | `TuyenDuongGeo` | `tuyen_id, coordinates (JSON array), so_diem` |
| `models/thong_ke.py` | `ThongKeToanTinh`, `ThongKeMoiTuyen` | Aggregate objects — không map bảng DB. Dùng cho báo cáo. |

---

## repositories/

Data Access Layer — SQL thuần, `sqlite3.Row`, không logic nghiệp vụ.

**Quy tắc:** Mọi repository đều có `_SELECT_COLS`, `_row_to_object()`, và các hàm CRUD chuẩn.
Truy cập row bằng `row["ten_cot"]` — không dùng `row[0]`, `row[1]`...

| File | Bảng tương ứng | Hàm đặc biệt |
|---|---|---|
| `repositories/cap_quan_ly_repository.py` | `cap_quan_ly` | `lay_tat_ca`, `lay_theo_ma`, `lay_theo_id`, `them`, `xoa_mem`, `khoi_phuc` |
| `repositories/cap_duong_repository.py` | `cap_duong` | Tương tự cap_quan_ly |
| `repositories/ket_cau_mat_duong_repository.py` | `ket_cau_mat_duong` | Tương tự cap_quan_ly |
| `repositories/tinh_trang_repository.py` | `tinh_trang` | Tương tự cap_quan_ly |
| `repositories/don_vi_repository.py` | `don_vi` | + `lay_cay_cha_con()` — trả cây phân cấp |
| `repositories/nguoi_dung_repository.py` | `nguoi_dung` | + `lay_theo_ten_dang_nhap()`, `cap_nhat_last_login()`, `lay_cho_duyet()` |
| `repositories/tuyen_duong_repository.py` | `tuyen_duong` | + `lay_theo_cap_quan_ly()`, `lay_co_geo()` — Không còn `cap_nhat_chieu_dai` (trigger thay thế) |
| `repositories/thong_tin_tuyen_repository.py` | `thong_tin_tuyen` | `lay_theo_tuyen_id()`, `them_hoac_cap_nhat()` |
| `repositories/doan_tuyen_repository.py` | `doan_tuyen` | + `lay_theo_tuyen_id()`, `lay_theo_tinh_trang()`, `lay_theo_ket_cau_mat()`, `cap_nhat_tinh_trang()` |
| `repositories/doan_di_chung_repository.py` | `doan_di_chung` | + `lay_theo_tuyen_di_chung_id()`, `lay_theo_doan_id()`, `kiem_tra_ton_tai()` |
| `repositories/hinh_anh_doan_tuyen_repository.py` | `hinh_anh_doan_tuyen` | + `lay_theo_doan_id()`, `xoa_vinh_vien()` (ảnh được xóa cứng) |
| `repositories/tuyen_duong_geo_repository.py` | `tuyen_duong_geo` | + `lay_theo_tuyen_id()`, `lay_tat_ca_co_geo()`, `them_hoac_cap_nhat()` |
| `repositories/thong_ke_repository.py` | Nhiều bảng (JOIN) | `lay_thong_ke_toan_tinh()`, `lay_thong_ke_mot_tuyen()` — query phức tạp |

---

## services/

Business Logic Layer — toàn bộ validate + nghiệp vụ tại đây.

**Quy tắc:** Service được phép gọi nhiều repository. Service không gọi service khác (tránh circular). Ném `*ServiceError` với message tiếng Việt.

| File | Exception class | Nghiệp vụ đặc biệt |
|---|---|---|
| `services/cap_quan_ly_service.py` | `CapQuanLyServiceError` | `get_or_create_by_ma()` — dùng trong seed |
| `services/cap_duong_service.py` | `CapDuongServiceError` | `get_or_create_by_ma()` |
| `services/ket_cau_mat_duong_service.py` | `KetCauMatServiceError` | `get_or_create_by_ma()` |
| `services/tinh_trang_service.py` | `TinhTrangServiceError` | `get_or_create_by_ma()` |
| `services/don_vi_service.py` | `DonViServiceError` | `get_or_create_by_ma()`, `lay_cay()` |
| `services/nguoi_dung_service.py` | `NguoiDungServiceError`, `DangNhapThatBaiError` | `dang_ky()` bcrypt hash · `dang_nhap()` checkpw · `duyet_nguoi_dung()` chỉ ADMIN · phân quyền 3 cấp |
| `services/tuyen_duong_service.py` | `TuyenDuongServiceError` | Validate `ma_tuyen` unique · FK tồn tại · `get_or_create_by_ma()` |
| `services/thong_tin_tuyen_service.py` | `ThongTinTuyenServiceError` | `them_hoac_cap_nhat_theo_tuyen()` |
| `services/doan_tuyen_service.py` | `DoanTuyenServiceError` | Validate: lý trình hợp lệ, kích thước hợp lệ, FK tồn tại, ma_doan unique · `cap_nhat_tinh_trang()` ghi log thời gian |
| `services/doan_di_chung_service.py` | `DoanDiChungServiceError` | Validate 6 điều kiện (xem ARCHITECTURE.md §5) · sinh mã tự động DDC-* |
| `services/hinh_anh_doan_tuyen_service.py` | `HinhAnhServiceError` | Upload file · đọc EXIF GPS (Pillow) · validate định dạng ảnh |
| `services/tuyen_duong_geo_service.py` | `TuyenDuongGeoServiceError` | Parse GeoJSON · validate tọa độ · `them_hoac_cap_nhat()` |
| `services/thong_ke_service.py` | — | `lay_thong_ke_toan_tinh()` · `lay_thong_ke_mot_tuyen()` — aggregate không ném lỗi nghiệp vụ |

---

## data/

Config Python sinh từ Excel — **nguồn sự thật duy nhất** cho dữ liệu seed.
Không sửa tay — luôn sửa file Excel rồi chạy `tools/excel_to_data.py`.

| File | Hằng số | Số lượng |
|---|---|---|
| `data/cap_quan_ly_data.py` | `CAP_QUAN_LY_CONFIG` | 8 |
| `data/cap_duong_data.py` | `CAP_DUONG_CONFIG` | 7 |
| `data/ket_cau_mat_data.py` | `KET_CAU_MAT_CONFIG` | 8 |
| `data/tinh_trang_data.py` | `TINH_TRANG_CONFIG` | 9 |
| `data/don_vi_data.py` | `DON_VI_CONFIG` | 17 (cây cha-con: dùng `ma_don_vi` làm `parent_ma`) |
| `data/nguoi_dung_data.py` | `NGUOI_DUNG_CONFIG` | 3 tài khoản mặc định |
| `data/tuyen_duong_data.py` | `TUYEN_CONFIG` | 49 (9 QL + 27 DT + 13 DX) |
| `data/thong_tin_tuyen_data.py` | `THONG_TIN_TUYEN_CONFIG` | 49+ |
| `data/doan_tuyen_data.py` | `DOAN_CONFIG` | 222 |
| `data/doan_di_chung_data.py` | `DDC_CONFIG` | 15 |
| `data/giao_thong_data_upadate.xlsx` | — | File Excel gốc (10 sheets: CapQuanLy, CapDuong, KetCauMat, TinhTrang, DonVi, NguoiDung, TuyenDuong, ThongTinTuyen, DoanTuyen, DoanDiChung) |

**Cấu trúc dict trong `TUYEN_CONFIG`:**
```python
{
    "ma_tuyen": "QL4",
    "ten_tuyen": "Quốc lộ 4",
    "ma_cap_quan_ly": "QL",
    "chieu_dai_quan_ly": 105.3,
    "chieu_dai_thuc_te": None,       # None = chưa đo
    "ma_don_vi_quan_ly": "BAN_BT",   # None = chưa xác định
    "diem_dau": "Tp. Lào Cai",
    "diem_cuoi": "Bát Xát",
    "lat_dau": 22.485, "lng_dau": 103.975,
    "lat_cuoi": None, "lng_cuoi": None,  # None = chưa có GPS
    "nam_xay_dung": 1945,
    "nam_hoan_thanh": 1975,
    "ghi_chu": None
}
```

**Cấu trúc dict trong `DOAN_CONFIG`:**
```python
{
    "ma_doan": "QL4-01",
    "ma_tuyen": "QL4",
    "ma_cap_duong": "IV",
    "ly_trinh_dau": 0.0,
    "ly_trinh_cuoi": 15.3,
    "chieu_dai_thuc_te": None,
    "chieu_rong_mat_min": 5.5, "chieu_rong_mat_max": 6.0,
    "chieu_rong_nen_min": 8.0, "chieu_rong_nen_max": 9.0,
    "ma_ket_cau_mat": "BTN",
    "ma_tinh_trang": "TB",
    "ma_don_vi_bao_duong": "CT01",
    "nam_lam_moi": 2019,
    "ghi_chu": None
}
```

---

## seeds/

Khởi tạo dữ liệu. Tất cả dùng `INSERT OR IGNORE` — chạy lại nhiều lần không lỗi (idempotent).

| File | Gọi | Thứ tự |
|---|---|---|
| `seeds/seed_all.py` | **Entry point** — gọi tất cả theo đúng thứ tự. Chạy: `python seeds/seed_all.py` | — |
| `seeds/seed_danh_muc.py` | `seed_danh_muc(conn)` | 1 — cap_quan_ly, cap_duong, ket_cau_mat, tinh_trang |
| `seeds/seed_don_vi.py` | `seed_don_vi(conn)` | 2 — cây cha-con (TINH → SXD → BAN_BT → 13 CT) |
| `seeds/seed_nguoi_dung.py` | `seed_nguoi_dung(conn)` | 3 — bcrypt hash mật khẩu |
| `seeds/seed_tuyen_doan.py` | `seed_tuyen_doan(conn)` | 4 — 49 tuyến + 222 đoạn + 15 DDC |

**Tài khoản được seed:**

| ten_dang_nhap | mat_khau | loai_quyen |
|---|---|---|
| `huuthanh` | `Laocai@2024` | `ADMIN` |
| `bientap` | `Laocai@2024` | `BIEN_TAP` |
| `xem` | `Laocai@2024` | `XEM` |

---

## migrations/

| File | Nội dung |
|---|---|
| `migrations/m001_initial_schema.py` | `up(conn)` tạo 13 bảng + 6 triggers + 5 indexes. `down(conn)` xóa tất cả (DEV ONLY). SQL nằm trong `_SCHEMA_SQL`. |

---

## tools/

Công cụ tiện ích — chạy từ command line.

| File | Cách chạy | Chức năng |
|---|---|---|
| `tools/excel_to_data.py` | `python tools/excel_to_data.py` hoặc `--excel <path> --out <dir>` | Đọc `data/giao_thong_data_upadate.xlsx` (10 sheets) → sinh/cập nhật 9 file `data/*_data.py`. Xử lý đặc biệt: `don_vi_data.py` dùng mã thay vì id; `doan_di_chung_data.py` sinh mã DDC tự động. Bỏ qua dòng trống. |
| `tools/import_geojson.py` | `python tools/import_geojson.py map/QL4E_merged.geojson` | Đọc file `.geojson` → trích coordinates → lưu vào `tuyen_duong_geo`. Quy tắc: tên file = `MA_TUYEN.geojson`. |
| `tools/export_geojson.py` | `python tools/export_geojson.py --ma-tuyen QL4E` hoặc `--all` | Lấy tọa độ từ `tuyen_duong_geo` → xuất file GeoJSON chuẩn RFC 7946. |

---

## api/

Web Application — FastAPI + Jinja2 + Session Cookie HMAC.

| File | Nội dung |
|---|---|
| `api/main.py` | **Entry point web.** Khởi tạo FastAPI app, mount static, đăng ký 6 router, custom Jinja2 filter `format_ly_trinh`. Chạy: `uvicorn api.main:app --reload` |
| `api/how_to_run.py` | Hướng dẫn cài đặt và chạy dự án từ đầu (dạng comment). |
| `api/routes/_auth_helper.py` | Quản lý session cookie HMAC SHA-256. Cung cấp: `tao_session_token()`, `giai_ma_session_token()`, `lay_user_hien_tai()`, `yeu_cau_dang_nhap()`, `yeu_cau_quyen_bien_tap()`, `yeu_cau_quyen_admin()`. |
| `api/routes/auth.py` | Routes `/auth/*` — đăng nhập, đăng xuất, đăng ký, duyệt tài khoản. |
| `api/routes/tuyen_duong_route.py` | CRUD tuyến đường tại `/tuyen-duong/*`. |
| `api/routes/doan_tuyen_route.py` | CRUD đoạn tuyến tại `/doan-tuyen/*`. Upload ảnh, cập nhật tình trạng. |
| `api/routes/doan_di_chung_route.py` | CRUD đoạn đi chung tại `/doan-di-chung/*`. |
| `api/routes/thong_ke.py` | Thống kê tại `/thong-ke/*`. Trả HTML (trang) và JSON (API). |
| `api/routes/ban_do.py` | Bản đồ Leaflet tại `/ban-do/*`. Trả GeoJSON từ `tuyen_duong_geo`. |

---

## templates/

Jinja2 HTML templates. Kế thừa từ `base.html`.

| File/Thư mục | Nội dung |
|---|---|
| `templates/base.html` | Layout chung — navbar, sidebar, CSS/JS links |
| `templates/dashboard.html` | Trang chủ — tổng quan toàn tỉnh |
| `templates/thong_ke.html` | Trang thống kê chi tiết |
| `templates/ban_do.html` | Trang bản đồ Leaflet.js |
| `templates/auth/login.html` | Form đăng nhập |
| `templates/auth/dang_ky.html` | Form đăng ký |
| `templates/tuyen_duong/danh_sach.html` | Danh sách tuyến (bảng + filter) |
| `templates/tuyen_duong/chi_tiet.html` | Chi tiết tuyến + danh sách đoạn |
| `templates/tuyen_duong/form.html` | Form thêm/sửa tuyến |
| `templates/doan_tuyen/danh_sach.html` | Danh sách đoạn |
| `templates/doan_tuyen/chi_tiet.html` | Chi tiết đoạn + ảnh + DDC |
| `templates/doan_tuyen/form.html` | Form thêm/sửa đoạn |

---

## static/

CSS, JavaScript, ảnh tĩnh — phục vụ tại `/static/`.

```
static/
├── css/
│   └── style.css
└── js/
    └── app.js
```

---

## map/

GeoJSON dữ liệu tuyến và script sinh bản đồ HTML tự chứa.

| File | Nội dung |
|---|---|
| `map/QL4E_merged.geojson` | Tọa độ Quốc lộ 4E — 5039 điểm |
| `map/TL158_merged.geojson` | Tọa độ Tỉnh lộ 158 (DT158) — 4274 điểm |
| `map/generate_map_multi_mahoa_onefile.py` | Script sinh 1 file HTML tự chứa tích hợp Leaflet.js. Mã hóa 3 lớp: Delta encoding → XOR cipher (key 32 byte ngẫu nhiên) → Base64. Hỗ trợ hover/click tính khoảng cách từ đầu tuyến. 3 basemap: OSM, Topo, Vệ tinh. |

---

## database/

| File | Nội dung |
|---|---|
| `database/giao_thong.db` | **File SQLite chính.** Trong `.gitignore` — không commit. Tạo lại bằng `python seeds/seed_all.py`. |

---

## MA TRẬN FILE THEO DOMAIN

Khi cần thay đổi một chức năng, đây là các file cần xem/sửa:

### Tuyến đường (`tuyen_duong`)

| Tầng | File |
|---|---|
| Database | `migrations/m001_initial_schema.py` (bảng `tuyen_duong`) |
| Model | `models/tuyen_duong.py` |
| Repository | `repositories/tuyen_duong_repository.py` |
| Service | `services/tuyen_duong_service.py` |
| Web Route | `api/routes/tuyen_duong_route.py` |
| Template | `templates/tuyen_duong/` |
| Data seed | `data/tuyen_duong_data.py` |

### Đoạn tuyến (`doan_tuyen`)

| Tầng | File |
|---|---|
| Database | `migrations/m001_initial_schema.py` (bảng `doan_tuyen` + 3 triggers) |
| Model | `models/doan_tuyen.py` |
| Repository | `repositories/doan_tuyen_repository.py` |
| Service | `services/doan_tuyen_service.py` |
| Web Route | `api/routes/doan_tuyen_route.py` |
| Template | `templates/doan_tuyen/` |
| Data seed | `data/doan_tuyen_data.py` |

### Đoạn đi chung (`doan_di_chung`)

| Tầng | File |
|---|---|
| Database | `migrations/m001_initial_schema.py` (bảng `doan_di_chung` + 3 triggers) |
| Model | `models/doan_di_chung.py` |
| Repository | `repositories/doan_di_chung_repository.py` |
| Service | `services/doan_di_chung_service.py` |
| Web Route | `api/routes/doan_di_chung_route.py` |
| Data seed | `data/doan_di_chung_data.py` |

### Người dùng / Xác thực

| Tầng | File |
|---|---|
| Database | `migrations/m001_initial_schema.py` (bảng `nguoi_dung`) |
| Model | `models/nguoi_dung.py` |
| Repository | `repositories/nguoi_dung_repository.py` |
| Service | `services/nguoi_dung_service.py` |
| Auth helper | `api/routes/_auth_helper.py` |
| Web Route | `api/routes/auth.py` |
| Template | `templates/auth/` |
| Data seed | `data/nguoi_dung_data.py` |

### Thống kê

| Tầng | File |
|---|---|
| Model | `models/thong_ke.py` |
| Repository | `repositories/thong_ke_repository.py` (JOIN phức tạp) |
| Service | `services/thong_ke_service.py` |
| Web Route | `api/routes/thong_ke.py` |
| Template | `templates/thong_ke.html` |

### Bản đồ GeoJSON

| Tầng | File |
|---|---|
| Database | `migrations/m001_initial_schema.py` (bảng `tuyen_duong_geo`) |
| Model | `models/tuyen_duong_geo.py` |
| Repository | `repositories/tuyen_duong_geo_repository.py` |
| Service | `services/tuyen_duong_geo_service.py` |
| Web Route | `api/routes/ban_do.py` |
| Template | `templates/ban_do.html` |
| Import tool | `tools/import_geojson.py` |
| Export tool | `tools/export_geojson.py` |
| GeoJSON files | `map/*.geojson` |
| Bản đồ HTML | `map/generate_map_multi_mahoa_onefile.py` |

---

## CHỈ MỤC TÌM KIẾM NHANH

| Cần tìm | Xem ở đây |
|---|---|
| Hàm `get_connection()` | `config/database.py` |
| Trigger cập nhật chiều dài | `migrations/m001_initial_schema.py` |
| Validate lý trình đoạn | `services/doan_tuyen_service.py` |
| Validate DDC chống tự-tham chiếu | `services/doan_di_chung_service.py` |
| Bcrypt hash/check mật khẩu | `services/nguoi_dung_service.py` |
| Session cookie HMAC | `api/routes/_auth_helper.py` |
| FastAPI Dependencies phân quyền | `api/routes/_auth_helper.py` |
| Jinja2 filter lý trình | `api/main.py` |
| Dữ liệu 49 tuyến | `data/tuyen_duong_data.py` |
| Dữ liệu 222 đoạn | `data/doan_tuyen_data.py` |
| Dữ liệu 15 DDC | `data/doan_di_chung_data.py` |
| Sinh data từ Excel | `tools/excel_to_data.py` |
| Import GeoJSON | `tools/import_geojson.py` |
| Sinh bản đồ HTML tự chứa | `map/generate_map_multi_mahoa_onefile.py` |
| Hướng dẫn khởi chạy | `api/how_to_run.py` hoặc `CLAUDE.md §2` |
| Quy tắc import alias | `CLAUDE.md §4.1` |
| Schema bảng chi tiết | `ARCHITECTURE.md §2.2` |
| ERD sơ đồ quan hệ | `ARCHITECTURE.md §2.1` |
| Định hướng phát triển | `ARCHITECTURE.md §9` |

---

*Cập nhật file này khi thêm file mới hoặc đổi tên/di chuyển file.*
