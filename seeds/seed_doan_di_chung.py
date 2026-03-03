"""
Seed dữ liệu mẫu cho đoạn đi chung.

Ví dụ: QL279 đi chung qua đoạn QL4D-01 (đoạn 1 của QL4D)
với lý trình riêng theo QL279.
"""

from models.doan_di_chung import DoanDiChung
from services.doan_di_chung_service import get_or_create_doan_di_chung
from services.tuyen_duong_service import lay_theo_ma as lay_tuyen
from services.doan_tuyen_service import lay_theo_ma as lay_doan


def seed_doan_di_chung():

    DS_DOAN_DI_CHUNG = [
        {
            # QL279 đi chung qua đoạn QL4D-01
            # (đoạn QL4D-01 thuộc tuyến chủ QL4D)
            # Lý trình bên dưới là lý trình theo QL279
            "ma_tuyen_di_chung": "QL279",
            "ma_doan": "QL4D-01",
            "ly_trinh_dau": 20.0,
            "ly_trinh_cuoi": 29.5,
            "ghi_chu": "QL279 di chung qua doan QL4D-01 tu Km20 den Km29.5"
        }
    ]

    for item in DS_DOAN_DI_CHUNG:

        tuyen = lay_tuyen(item["ma_tuyen_di_chung"])
        if not tuyen:
            print(f"❌ Khong tim thay tuyen: {item['ma_tuyen_di_chung']}")
            continue

        doan = lay_doan(item["ma_doan"])
        if not doan:
            print(f"❌ Khong tim thay doan: {item['ma_doan']}")
            continue

        ddc = DoanDiChung(
            tuyen_id=tuyen.id,
            doan_id=doan.id,
            ly_trinh_dau=item["ly_trinh_dau"],
            ly_trinh_cuoi=item["ly_trinh_cuoi"],
            ghi_chu=item["ghi_chu"]
        )

        get_or_create_doan_di_chung(ddc)

    print("Seed doan_di_chung hoan thanh!")