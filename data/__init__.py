# data/__init__.py
# Gói chứa toàn bộ dữ liệu tĩnh của hệ thống quản lý giao thông Lào Cai.
# Mỗi file chứa list RECORDS dùng cho seed.
#
# Thứ tự import khi seed (theo phụ thuộc khóa ngoại):
#   1. cap_quan_ly_data, cap_duong_data, ket_cau_mat_data, tinh_trang_data
#   2. don_vi_data       (cha trước con sau — đã sắp xếp sẵn trong file)
#   3. nguoi_dung_data
#   4. tuyen_duong_data  (gồm cả thong_tin_tuyen)
#   5. doan_tuyen_data
#   6. doan_di_chung_data
