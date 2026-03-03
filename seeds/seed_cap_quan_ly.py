from models.cap_quan_ly import CapQuanLy
from services.cap_quan_ly_service import get_or_create_cap_quan_ly


def seed_cap_quan_ly():
    ds_cap = [
        ("CT", "Đường cao tốc",      "Bộ Xây dựng quản lý",           1),
        ("QL", "Đường quốc lộ",      "UBND tỉnh quản lý",                       2),
        ("DT", "Đường tỉnh",         "UBND tỉnh quản lý",                       3),
        ("NT", "Đường đô thị",       "UBND phường quản lý",          4),
        ("DX", "Đường xã",           "Xã, phường quản lý",                      5),
        ("TX", "Đường thôn, xóm",    "Xã, phường quản lý",                      6),
        ("CD", "Đường chuyên dùng",  "Đơn vị trực tiếp khai thác quản lý",      7),
        ("DK", "Đường khác",         "",                                         8),
    ]

    result = {}

    for ma, ten, mo_ta, thu_tu in ds_cap:
        cap = get_or_create_cap_quan_ly(
            CapQuanLy(
                ma_cap=ma,
                ten_cap=ten,
                mo_ta=mo_ta,
                thu_tu_hien_thi=thu_tu
            )
        )
        result[ma] = cap

    print("Seed cap_quan_ly hoan thanh!")
    return result