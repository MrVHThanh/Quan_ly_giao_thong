from models.tinh_trang import TinhTrang
from services.tinh_trang_service import get_or_create_tinh_trang


def seed_tinh_trang():
    ds_tinh_trang = [
        ("TOT",      "Tốt",              "Mặt đường bằng phẳng, không hư hỏng đáng kể",          "#2ecc71", 1),
        ("TB",       "Trung bình",       "Có hư hỏng nhỏ, vẫn lưu thông bình thường",            "#f39c12", 2),
        ("KEM",      "Kém",              "Hư hỏng nhiều, cần sửa chữa trong thời gian tới",       "#e67e22", 3),
        ("HH_NANG",  "Hư hỏng nặng",    "Mất an toàn giao thông, cần xử lý khẩn cấp",           "#e74c3c", 4),
        ("THI_CONG", "Đang thi công",    "Đang trong quá trình xây dựng mới",                     "#3498db", 5),
        ("BAO_TRI",  "Đang bảo trì",     "Đang sửa chữa, bảo dưỡng định kỳ",                     "#9b59b6", 6),
        ("TAM_DONG", "Tạm đóng",         "Đóng cửa tạm thời do thiên tai hoặc sự cố",            "#7f8c8d", 7),
        ("NGUNG",    "Ngưng sử dụng",    "Không còn khai thác, chờ thanh lý hoặc cải tạo",       "#2c3e50", 8),
    ]

    result = {}

    for ma, ten, mo_ta, mau, thu_tu in ds_tinh_trang:
        tt = get_or_create_tinh_trang(
            TinhTrang(
                ma=ma,
                ten=ten,
                mo_ta=mo_ta,
                mau_hien_thi=mau,
                thu_tu_hien_thi=thu_tu
            )
        )
        result[ma] = tt

    print("Seed tinh_trang hoan thanh!")
    return result