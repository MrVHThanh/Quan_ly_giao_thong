# DỰ ÁN QUẢN LÝ TUYẾN ĐƯỜNG LÀO CAI
## Hệ thống quản lý đường bộ tỉnh Lào Cai — Sở Xây dựng tỉnh Lào Cai

---

## 1. TỔNG QUAN

- **Ngôn ngữ:** Python + SQLite
- **Kiến trúc:** Model → Repository → Service (3 lớp)
- **Thư mục gốc:** `D:\Dropbox\@Giaothong2\`
- **Database:** `database/giao_thong.db`

---

## 2. SƠ ĐỒ THƯ MỤC

```
@Giaothong2/
├── config/
│   ├── database.py          # Kết nối DB, hàm create_tables()
│   └── settings.py          # Cấu hình đường dẫn BASE_DIR, DB_PATH...
├── models/                  # Plain Object — không chứa logic DB
│   ├── cap_quan_ly.py
│   ├── cap_duong.py
│   ├── don_vi.py
│   ├── tinh_trang.py
│   ├── tuyen_duong.py
│   ├── doan_tuyen.py
│   ├── doan_di_chung.py
│   └── thong_ke.py
├── repositories/            # Truy vấn SQL trực tiếp, trả về row hoặc Object
│   ├── cap_quan_ly_repository.py
│   ├── cap_duong_repository.py
│   ├── don_vi_repository.py
│   ├── tinh_trang_repository.py
│   ├── tuyen_duong_repository.py
│   ├── doan_tuyen_repository.py
│   ├── doan_di_chung_repository.py
│   └── thong_ke_repository.py
├── services/                # Logic nghiệp vụ, validate, gọi repository
│   ├── cap_quan_ly_service.py
│   ├── cap_duong_service.py
│   ├── don_vi_service.py
│   ├── tinh_trang_service.py
│   ├── tuyen_duong_service.py
│   ├── doan_tuyen_service.py
│   ├── doan_di_chung_service.py
│   └── thong_ke_service.py
├── seeds/                   # Dữ liệu khởi tạo hệ thống
│   ├── seed_all.py          # Gọi tất cả seed theo đúng thứ tự
│   ├── seed_cap_quan_ly.py
│   ├── seed_cap_duong.py
│   ├── seed_don_vi.py
│   ├── seed_tinh_trang.py
│   ├── seed_tuyen_doan.py   # Đọc từ data/ để seed tuyen+doan+ddi_chung
│   └── seed_doan_tuyen.py   # (cũ, seed thủ công — đã thay bởi seed_tuyen_doan.py)
├── data/                    # Số liệu thực tế dạng Python config
│   ├── tuyen_duong_data.py  # TUYEN_CONFIG — 49 tuyến
│   ├── doan_tuyen_data.py   # DOAN_CONFIG  — ~207 đoạn
│   ├── doan_di_chung_data.py# DOAN_DI_CHUNG_CONFIG
│   ├── excel_io.py          # Xuất/import dữ liệu qua file Excel 3 sheet
│   └── do_du_lieu.ipynb     # Notebook phân tích nhanh bằng pandas
├── map/
│   ├── QL4E_merged.geojson
│   ├── TL158_merged.geojson
│   └── generate_map_multi_mahoa_onefile.py  # Sinh HTML bản đồ Leaflet
├── database/
│   └── giao_thong.db        # File SQLite (gitignore)
└── main.py                  # Điểm chạy chính, in báo cáo ra console
```

---

## 3. CƠ SỞ DỮ LIỆU — SƠ ĐỒ QUAN HỆ

```
cap_quan_ly (id) ◄─── tuyen_duong (cap_quan_ly_id)
                           │
                           ├─── doan_tuyen (tuyen_id)
                           │         │
                           │         └─── doan_di_chung (doan_id)
                           │                    │
                           │              tuyen_duong (tuyen_id) ← tuyến đi nhờ
                           │
don_vi (id) ◄─────── tuyen_duong (don_vi_quan_ly_id)
            ◄─────── doan_tuyen (don_vi_bao_duong_id)
            ◄─────── don_vi (parent_id) ← cây cha-con

cap_duong (id) ◄──── doan_tuyen (cap_duong_id)
tinh_trang (id) ◄─── doan_tuyen (tinh_trang_id)
```

---

## 4. CÁC BẢNG VÀ CỘT QUAN TRỌNG

### 4.1 cap_quan_ly
| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| id | INTEGER PK | |
| ma_cap | TEXT UNIQUE | QL, DT, DX, CT, NT, TX, CD, DK |
| ten_cap | TEXT | Đường quốc lộ, Đường tỉnh... |
| thu_tu_hien_thi | INTEGER | Thứ tự hiển thị |
| is_active | INTEGER | 1=active, 0=soft delete |

### 4.2 cap_duong
| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| id | INTEGER PK | |
| ma_cap | TEXT UNIQUE | I, II, III, IV, V, VI, NO |
| ten_cap | TEXT | Cấp I → Cấp VI, Chưa vào cấp |
| thu_tu_hien_thi | INTEGER | |
| is_active | INTEGER | |

### 4.3 don_vi
| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| id | INTEGER PK | |
| ma_don_vi | TEXT UNIQUE | SXD, BAN_BT, CTY_MD, CTY_BT... |
| ten_don_vi | TEXT | |
| loai | TEXT | So, Ban, Donvi... |
| parent_id | INTEGER FK→don_vi | Cây cha-con |
| is_active | INTEGER | |

Cây hiện tại: `SXD → BAN_BT → CTY_MD, CTY_BT`

### 4.4 tinh_trang
| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| id | INTEGER PK | |
| ma | TEXT UNIQUE | TOT, TB, KEM, HH_NANG, THI_CONG, BAO_TRI, TAM_DONG, CHUA_XD, NGUNG |
| ten | TEXT | |
| mau_hien_thi | TEXT | Mã màu hex, dùng cho UI |
| thu_tu_hien_thi | INTEGER | |
| is_active | INTEGER | |

### 4.5 tuyen_duong ⭐
| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| id | INTEGER PK | |
| ma_tuyen | TEXT UNIQUE | QL4, QL4D, QL4E, QL279, DT151... |
| ten_tuyen | TEXT | |
| cap_quan_ly_id | INTEGER FK | |
| don_vi_quan_ly_id | INTEGER FK | |
| diem_dau, diem_cuoi | TEXT | Mô tả điểm đầu/cuối |
| lat_dau, lng_dau | REAL | Tọa độ điểm đầu |
| lat_cuoi, lng_cuoi | REAL | Tọa độ điểm cuối |
| chieu_dai | REAL | **Tự động tính** từ tổng đoạn (update trigger) |
| chieu_dai_thuc_te | REAL | Chiều dài đo thực tế |
| chieu_dai_quan_ly | REAL | Chiều dài theo quyết định quản lý |
| nam_xay_dung | INTEGER | |
| nam_hoan_thanh | INTEGER | |

**Index cột khi SELECT (dùng trong _row_to_object):**
```
0:id, 1:ma_tuyen, 2:ten_tuyen,
3:cap_quan_ly_id, 4:don_vi_quan_ly_id,
5:diem_dau, 6:diem_cuoi,
7:lat_dau, 8:lng_dau, 9:lat_cuoi, 10:lng_cuoi,
11:chieu_dai, 12:chieu_dai_thuc_te, 13:chieu_dai_quan_ly,
14:nam_xay_dung, 15:nam_hoan_thanh,
16:ghi_chu, 17:created_at
```

### 4.6 doan_tuyen ⭐
| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| id | INTEGER PK | |
| ma_doan | TEXT UNIQUE | QL4-01, QL4E-03, DT151-02... |
| tuyen_id | INTEGER FK | |
| cap_duong_id | INTEGER FK | |
| ly_trinh_dau | REAL | Km đầu đoạn |
| ly_trinh_cuoi | REAL | Km cuối đoạn |
| chieu_dai | REAL | = ly_trinh_cuoi - ly_trinh_dau |
| chieu_dai_thuc_te | REAL | Đo thực tế (ưu tiên hơn chieu_dai) |
| tinh_trang_id | INTEGER FK | Tình trạng mặt đường đoạn này |
| chieu_rong_mat_max/min | REAL | m |
| chieu_rong_nen_max/min | REAL | m |
| don_vi_bao_duong_id | INTEGER FK | |

**Index cột khi SELECT (quan trọng — phải khớp với _row_to_object):**
```
0:id, 1:ma_doan, 2:tuyen_id, 3:cap_duong_id,
4:ly_trinh_dau, 5:ly_trinh_cuoi,
6:chieu_dai (BỎ QUA), 7:chieu_dai_thuc_te,
8:tinh_trang_id,
9:chieu_rong_mat_max, 10:chieu_rong_mat_min,
11:chieu_rong_nen_max, 12:chieu_rong_nen_min,
13:don_vi_bao_duong_id, 14:ghi_chu, 15:created_at
```

### 4.7 doan_di_chung ⭐
| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| id | INTEGER PK | |
| tuyen_id | INTEGER FK | **Tuyến đi nhờ** (ví dụ: DT153) |
| doan_id | INTEGER FK | **Đoạn vật lý** của tuyến chủ (ví dụ: đoạn QL4E-04) |
| ly_trinh_dau | REAL | Lý trình theo **tuyến đi nhờ** |
| ly_trinh_cuoi | REAL | Lý trình theo **tuyến đi nhờ** |
| UNIQUE(tuyen_id, doan_id) | | Mỗi tuyến chỉ đi nhờ mỗi đoạn 1 lần |

**Ví dụ:** DT153 đi nhờ đoạn QL4E-04 từ Km18.3 đến Km21.1 (lý trình theo DT153)

---

## 5. MODELS — CÁC CLASS

### TuyenDuong (`models/tuyen_duong.py`)
```python
@property toa_do_dau → [lat_dau, lng_dau]
@property toa_do_cuoi → [lat_cuoi, lng_cuoi]
```

### DoanTuyen (`models/doan_tuyen.py`)
```python
@property chieu_dai → ly_trinh_cuoi - ly_trinh_dau
@property chieu_dai_tinh → chieu_dai_thuc_te or chieu_dai  # ưu tiên thực tế
_validate(): ly_trinh_cuoi > ly_trinh_dau
             rong_mat_max >= rong_mat_min
             rong_nen_max >= rong_nen_min
```

### DoanDiChung (`models/doan_di_chung.py`)
```python
@property chieu_dai → ly_trinh_cuoi - ly_trinh_dau
_validate(): ly_trinh_cuoi > ly_trinh_dau
```

### ThongKe (`models/thong_ke.py`)
- `ThongKeCapKyThuat` — 1 dòng ma trận (cap_quan_ly × cap_duong → km)
- `ThongKeCapKyThuatTheoTuyen` — chiều dài theo cấp kỹ thuật của 1 tuyến
- `ChiTietDoanTheoTuyen` — 1 đoạn (CHINH hoặc DI CHUNG) với đầy đủ thông tin

---

## 6. REPOSITORIES — QUY ƯỚC

Mỗi repository có cấu trúc:
- `_SELECT_COLS` — chuỗi tên cột dùng trong SELECT
- `_row_to_object(row)` — chuyển tuple → Object
- `lay_tat_ca()` → list rows
- `lay_theo_ma(ma)` → 1 row
- `lay_theo_id(id)` → 1 row
- `them_*(...)` → lastrowid
- Soft delete: `xoa_*` set `is_active=0`, `khoi_phuc_*` set `is_active=1`

### thong_ke_repository.py — 3 query phức tạp:
1. `lay_thong_ke_cap_ky_thuat_theo_cap_quan_ly()` — GROUP BY cap_quan_ly × cap_duong
2. `lay_thong_ke_cap_ky_thuat_theo_tung_tuyen()` — GROUP BY tuyen_id × cap_duong
3. `lay_chi_tiet_doan_theo_tung_tuyen()` — UNION đoạn chính + đoạn di chung

---

## 7. SERVICES — LOGIC NGHIỆP VỤ

Mỗi service bao gồm:
- `lay_tat_ca / lay_theo_ma / lay_theo_id / lay_theo_id_hoat_dong` — gọi repo, trả Object
- `them_*` — validate business rule → gọi repo
- `get_or_create_*` — kiểm tra tồn tại → tạo mới hoặc trả về cũ (dùng trong seed)

### Cơ chế tự cập nhật chiều dài:
Sau mỗi thao tác thêm/xóa `doan_tuyen` hoặc `doan_di_chung`:
```python
cap_nhat_chieu_dai_tuyen(tuyen_id)
# → SUM(COALESCE(chieu_dai_thuc_te, chieu_dai)) → UPDATE tuyen_duong.chieu_dai
```

### Validation của `doan_di_chung_service.them_doan_di_chung`:
1. Tuyến đi nhờ (`tuyen_id`) phải tồn tại
2. Đoạn vật lý (`doan_id`) phải tồn tại
3. Đoạn **không được** thuộc chính tuyến đó (tránh tự-tham chiếu)
4. Cặp (tuyen_id, doan_id) chưa tồn tại trong bảng

---

## 8. SEEDS — THỨ TỰ CHẠY

```python
# seed_all.py — thứ tự BẮT BUỘC:
seed_cap_quan_ly()   # 1. Danh mục cấp quản lý
seed_cap_duong()     # 2. Danh mục cấp kỹ thuật
seed_don_vi()        # 3. Đơn vị (cây cha-con)
seed_tinh_trang()    # 4. Tình trạng mặt đường
seed_tuyen_duong()   # 5. Tuyến đường (cần cap_quan_ly, don_vi)
seed_doan_tuyen()    # 6. Đoạn tuyến (cần tuyen, cap_duong, don_vi, tinh_trang)
seed_doan_di_chung() # 7. Đoạn đi chung (cần tuyen, doan đã tồn tại)
```

---

## 9. DATA CONFIG — NGUỒN SỐ LIỆU THỰC TẾ

### tuyen_duong_data.py — TUYEN_CONFIG
49 tuyến, gồm:
- 9 Quốc lộ: QL4, QL4D, QL4E, QL279, QL37, QL70, QL32C, QL2D, QL32
- 27 Đường tỉnh: DT151→DT175B
- 13 Đường khác: DX01→DX13

Cấu trúc mỗi phần tử:
```python
{
    "ma_tuyen", "ten_tuyen", "ma_cap_quan_ly",
    "chieu_dai_quan_ly", "chieu_dai_thuc_te",
    "ma_don_vi_quan_ly",  # None nếu chưa xác định
    "diem_dau", "diem_cuoi",
    "lat_dau", "lng_dau", "lat_cuoi", "lng_cuoi",  # None nếu chưa có GPS
    "nam_xay_dung", "nam_hoan_thanh", "ghi_chu"
}
```

### doan_tuyen_data.py — DOAN_CONFIG
~207 đoạn. Cấu trúc mỗi phần tử:
```python
{
    "ma_doan", "ma_tuyen", "ma_cap_duong",
    "ly_trinh_dau", "ly_trinh_cuoi",
    "chieu_dai_thuc_te",  # None nếu chưa đo
    "chieu_rong_mat_min", "chieu_rong_mat_max",
    "chieu_rong_nen_min", "chieu_rong_nen_max",
    "ma_don_vi_bao_duong",  # None nếu chưa xác định
    "ghi_chu"
}
```

### doan_di_chung_data.py — DOAN_DI_CHUNG_CONFIG
Các đoạn đi chung đã xác định, ví dụ:
- QL4D đi nhờ QL70-05 (Km140.893→149)
- QL4E đi nhờ QL70-01 (Km35.6→36.975)
- DT153 đi nhờ QL4E-04 (Km18.3→21.1)
- DT159 đi nhờ QL4E-08,09,10,11
- DT160 đi nhờ QL279-11,12,13
- DT162 đi nhờ DT151-03
- DX02 đi nhờ DT173-01

**Các TODO chưa xử lý được** (tuyến chủ thuộc tỉnh khác):
- QL4E đi nhờ QL4D Km79.757→82.957
- QL32 đi nhờ QL37 Km162→172
- DT155 đi nhờ QL4D Km43.5→47.1
- DT159 đi nhờ QL4 nhiều đoạn

---

## 10. THỐNG KÊ

### thong_ke_service.py
```python
lay_thong_ke_cap_ky_thuat()
# → dict nhóm theo cap_quan_ly:
# { "QL": { "ten_cap_quan_ly", "tong_chieu_dai", "chi_tiet": [...] } }

lay_thong_ke_chi_tiet_tung_tuyen()
# → dict nhóm theo tuyen_id:
# { id: { "tuyen", "cap_ky_thuat": [...], "doan_chinh": [...], "doan_di_chung": [...] } }
```

---

## 11. BẢN ĐỒ (`map/`)

Script `generate_map_multi_mahoa_onefile.py`:
- Đọc file `*.geojson`
- Mã hóa tọa độ 3 lớp: **Delta encoding → XOR cipher (key 32 byte ngẫu nhiên) → Base64**
- Xuất 1 file HTML duy nhất tích hợp Leaflet.js
- Tính khoảng cách thực từ đầu tuyến khi hover/click
- Hỗ trợ nhiều basemap: OSM, Topo, Vệ tinh

---

## 12. LUỒNG DỮ LIỆU

```
data/*.py (config thực tế)
    ↓
seeds/seed_tuyen_doan.py (đọc config, gọi service)
    ↓
services/*_service.py (validate)
    ↓
repositories/*_repository.py (SQL)
    ↓
database/giao_thong.db
    ↑
thong_ke_repository.py (JOIN phức tạp)
    ↑
thong_ke_service.py
    ↑
main.py (in báo cáo console)
```

---

## 13. CÁC LƯU Ý KỸ THUẬT QUAN TRỌNG

1. **Index cột `doan_tuyen`:** cột `chieu_dai` ở index 6 bị BỎ QUA trong `_row_to_object` — `tinh_trang_id` ở index 8, `chieu_dai_thuc_te` ở index 7.

2. **`chieu_dai` vs `chieu_dai_thuc_te`:** Luôn dùng `COALESCE(chieu_dai_thuc_te, chieu_dai)` trong SQL thống kê.

3. **Soft delete:** `cap_quan_ly`, `cap_duong`, `don_vi`, `tinh_trang` đều dùng soft delete (`is_active=0`), không xóa cứng. `doan_di_chung` dùng xóa cứng.

4. **`cap_nhat_chieu_dai_tuyen`** phải được gọi sau mỗi thêm/xóa `doan_tuyen` hoặc `doan_di_chung`.

5. **Lý trình trong `doan_di_chung`** là lý trình theo **tuyến đi nhờ**, không phải tuyến chủ sở hữu đoạn.

6. **`excel_io.py`** có thể export dữ liệu từ `data/*.py` ra Excel hoặc import ngược lại, dùng CLI: `python excel_io.py export` / `python excel_io.py import --save`.
