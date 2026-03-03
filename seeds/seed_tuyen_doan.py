"""
Seed TuyenDuong, DoanTuyen, DoanDiChung.
Dữ liệu được import từ thư mục data/ — chỉnh sửa số liệu ở đó, không sửa file này.
"""

from data.tuyen_duong_data import TUYEN_CONFIG
from data.doan_tuyen_data import DOAN_CONFIG
from data.doan_di_chung_data import DOAN_DI_CHUNG_CONFIG

from models.tuyen_duong import TuyenDuong
from models.doan_tuyen import DoanTuyen
from models.doan_di_chung import DoanDiChung

from services.tuyen_duong_service import get_or_create_tuyen_duong
from services.doan_tuyen_service import get_or_create_doan_tuyen
from services.doan_di_chung_service import get_or_create_doan_di_chung

from services.cap_quan_ly_service import lay_theo_ma as lay_cap_quan_ly
from services.cap_duong_service import lay_theo_ma as lay_cap_duong
from services.don_vi_service import lay_theo_ma_hoat_dong as lay_don_vi
from services.tuyen_duong_service import lay_theo_ma as lay_tuyen
from services.doan_tuyen_service import lay_theo_ma as lay_doan


def seed_tuyen_duong():
    for data in TUYEN_CONFIG:
        cap_quan_ly = lay_cap_quan_ly(data["ma_cap_quan_ly"])
        if not cap_quan_ly:
            print(f"❌ Khong tim thay cap quan ly: {data['ma_cap_quan_ly']}")
            continue

        dv_quan_ly = lay_don_vi(data["ma_don_vi_quan_ly"]) if data["ma_don_vi_quan_ly"] else None

        tuyen = TuyenDuong(
            ma_tuyen          = data["ma_tuyen"],
            ten_tuyen         = data["ten_tuyen"],
            cap_quan_ly_id    = cap_quan_ly.id,
            don_vi_quan_ly_id = dv_quan_ly.id if dv_quan_ly else None,
            diem_dau          = data["diem_dau"],
            diem_cuoi         = data["diem_cuoi"],
            lat_dau           = data["lat_dau"],
            lng_dau           = data["lng_dau"],
            lat_cuoi          = data["lat_cuoi"],
            lng_cuoi          = data["lng_cuoi"],
            chieu_dai_thuc_te = data["chieu_dai_thuc_te"],
            chieu_dai_quan_ly = data["chieu_dai_quan_ly"],
            nam_xay_dung      = data["nam_xay_dung"],
            nam_hoan_thanh    = data["nam_hoan_thanh"],
            ghi_chu           = data["ghi_chu"],
        )
        get_or_create_tuyen_duong(tuyen)
    print("✅ Seed tuyen_duong hoan thanh!")


def seed_doan_tuyen():
    for data in DOAN_CONFIG:
        tuyen = lay_tuyen(data["ma_tuyen"])
        if not tuyen:
            print(f"❌ Khong tim thay tuyen: {data['ma_tuyen']}")
            continue

        cap_duong = lay_cap_duong(data["ma_cap_duong"])
        if not cap_duong:
            print(f"❌ Khong tim thay cap duong: {data['ma_cap_duong']} (doan {data['ma_doan']})")
            continue

        don_vi_bd = lay_don_vi(data["ma_don_vi_bao_duong"]) if data["ma_don_vi_bao_duong"] else None

        doan = DoanTuyen(
            ma_doan             = data["ma_doan"],
            tuyen_id            = tuyen.id,
            cap_duong_id        = cap_duong.id,
            ly_trinh_dau        = data["ly_trinh_dau"],
            ly_trinh_cuoi       = data["ly_trinh_cuoi"],
            chieu_dai_thuc_te   = data["chieu_dai_thuc_te"],
            chieu_rong_mat_min  = data["chieu_rong_mat_min"],
            chieu_rong_mat_max  = data["chieu_rong_mat_max"],
            chieu_rong_nen_min  = data["chieu_rong_nen_min"],
            chieu_rong_nen_max  = data["chieu_rong_nen_max"],
            don_vi_bao_duong_id = don_vi_bd.id if don_vi_bd else None,
            ghi_chu             = data["ghi_chu"],
        )
        get_or_create_doan_tuyen(doan)
    print("✅ Seed doan_tuyen hoan thanh!")


def seed_doan_di_chung():
    for data in DOAN_DI_CHUNG_CONFIG:
        tuyen = lay_tuyen(data["ma_tuyen_di_chung"])
        if not tuyen:
            print(f"❌ Khong tim thay tuyen: {data['ma_tuyen_di_chung']}")
            continue

        doan = lay_doan(data["ma_doan"])
        if not doan:
            print(f"❌ Khong tim thay doan: {data['ma_doan']}")
            continue

        ddc = DoanDiChung(
            tuyen_id      = tuyen.id,
            doan_id       = doan.id,
            ly_trinh_dau  = data["ly_trinh_dau"],
            ly_trinh_cuoi = data["ly_trinh_cuoi"],
            ghi_chu       = data["ghi_chu"],
        )
        get_or_create_doan_di_chung(ddc)
    print("✅ Seed doan_di_chung hoan thanh!")


def seed_all_tuyen_doan():
    seed_tuyen_duong()
    seed_doan_tuyen()
    seed_doan_di_chung()