from models.cap_duong import CapDuong
from services.cap_duong_service import get_or_create_cap_duong


def seed_cap_duong():
    ds_cap = [
        ("I", "Cấp I", "Đường cấp I", 1),
        ("II", "Cấp II", "Đường cấp II", 2),
        ("III", "Cấp III", "Đường cấp III - Miền núi", 3),
        ("IV", "Cấp IV", "Đường cấp IV - Miền núi", 4),
        ("V", "Cấp V", "Đường cấp V - Miền núi", 5),
        ("VI", "Cấp VI", "Đường cấp VI - Miền núi", 6),
        ("NO", "Chưa vào cấp", "Đường chưa vào cấp", 7),
    ]

    result = {}

    for ma, ten, mo_ta, thu_tu in ds_cap:
        cap = get_or_create_cap_duong(
            CapDuong(
                ma_cap=ma,
                ten_cap=ten,
                mo_ta=mo_ta,
                thu_tu_hien_thi=thu_tu
            )
        )
        result[ma] = cap

    return result