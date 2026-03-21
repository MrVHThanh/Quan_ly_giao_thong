"""
Data: NguoiDung — 3 tài khoản khởi tạo
Nguồn: Sheet NguoiDung | giao_thong_data_upadate.xlsx

Lưu ý seed:
- mat_khau_hash do seed tự tạo bằng bcrypt từ mat_khau_mac_dinh
- is_approved=1, is_active=1 cho cả 3 tài khoản ban đầu
- Tài khoản 1 (admin) cần được đặt loai_quyen=ADMIN
- don_vi_ma: seed sẽ tra ma_don_vi → don_vi_id thực trước khi INSERT
"""

# Mật khẩu mặc định khi seed — phải đổi ngay sau lần đăng nhập đầu tiên
MAT_KHAU_MAC_DINH = "Laocai@2024"

RECORDS = [
    {
        "ten_dang_nhap": "huuthanh",
        "ho_ten": "Hữu Thành",
        "chuc_vu": "Phó Giám đốc",
        "don_vi_ma": "SXD",
        "so_dien_thoai": "0979898636",
        "email": "vanhuuthanh@gmail.com",
        "loai_quyen": "ADMIN",
    },
    {
        "ten_dang_nhap": "trongluong",
        "ho_ten": "Nguyễn Trọng Lượng",
        "chuc_vu": "Trưởng phòng",
        "don_vi_ma": "BAN_BT",
        "so_dien_thoai": "0913287687",
        "email": None,
        "loai_quyen": "BIEN_TAP",
    },
    {
        "ten_dang_nhap": "thanhhai",
        "ho_ten": "Thẩm Thanh Hải",
        "chuc_vu": "Phó Giám đốc",
        "don_vi_ma": "BAN_BT",
        "so_dien_thoai": "0972433503",
        "email": None,
        "loai_quyen": "BIEN_TAP",
    },
]
