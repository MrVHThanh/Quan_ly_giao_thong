'''
python seeds/seed_all.py
python tools/import_geojson.py QL4E.geojson
python tools/import_geojson.py DT158.geojson
uvicorn api.main:app --reload

Dưới đây là hướng dẫn chạy toàn bộ dự án từ đầu:

Bước 1 — Cài Python & tạo lại venv
bash
# Xóa venv cũ (nếu có)
deactivate
rm -rf venv

# Tạo venv mới (dùng Python đang có trên máy)
python -m venv venv

# Kích hoạt
source venv/Scripts/activate   # Windows Git Bash
# hoặc: venv\Scripts\activate  # Windows CMD

Bước 2 — Cài thư viện
bash
pip install fastapi uvicorn jinja2 python-multipart bcrypt pandas openpyxl Pillow

Bước 3 — Khởi tạo DB và seed dữ liệu
bash
# Tạo schema + seed toàn bộ dữ liệu (chạy 1 lần)
python seeds/seed_all.py
```

Kết quả đúng sẽ ra:
```
✓ cap_quan_ly(8) cap_duong(7) ket_cau_mat(8) tinh_trang(9)
✓ don_vi(17) nguoi_dung(3) tuyen_duong(49) doan_tuyen(222) doan_di_chung(15)
✅ SEED THÀNH CÔNG

Bước 4 — Import GeoJSON (2 file đang có)
bash
python tools/import_geojson.py data/geojson/QL4E.geojson
python tools/import_geojson.py data/geojson/DT158.geojson

Đặt 2 file .geojson vào data/geojson/ trước, hoặc chỉ đường dẫn thẳng tới file.


Bước 5 — Chạy web
bash
uvicorn api.main:app --reload
Mở trình duyệt: http://localhost:8000
Đăng nhập bằng:

Tài khoản: huuthanh
Mật khẩu: Laocai@2024


Tóm tắt thứ tự mỗi lần chạy lại
bash
source venv/Scripts/activate
uvicorn api.main:app --reload
Chỉ cần 2 lệnh này sau lần đầu đã seed xong.

Nếu muốn reset DB làm lại từ đầu
bash# Xóa file DB cũ
del giao_thong.db        # Windows
# rm giao_thong.db       # Linux/Mac

# Seed lại
python seeds/seed_all.py


'''