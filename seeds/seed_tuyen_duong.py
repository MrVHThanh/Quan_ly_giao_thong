from models.tuyen_duong import TuyenDuong
from services.tuyen_duong_service import get_or_create_tuyen_duong
from services.cap_quan_ly_service import lay_theo_ma as lay_cap_quan_ly_theo_ma
from services.don_vi_service import lay_theo_ma_hoat_dong
from services.tinh_trang_service import lay_theo_ma_hoat_dong as lay_tinh_trang_theo_ma


# =========================
# CẤU HÌNH DỮ LIỆU TUYẾN
# =========================

TUYEN_CONFIG = [
    {
        "ma_tuyen":             "QL279",
        "ten_tuyen":            "Quốc lộ 279",
        "ma_cap_quan_ly":       "QL",
        "chieu_dai_thuc_te":    29.5,   # sẽ được tính lại sau khi nhập đoạn
        "chieu_dai_quan_ly":    27.0,   # sẽ được tính lại sau khi nhập đoạn
        "ma_don_vi_quan_ly":    "SXD",
        "diem_dau":             "Km0 - TP Lào Cai",
        "diem_cuoi":            "Km30 - Huyện Bắc Hà",
        "lat_dau":              22.3364,
        "lng_dau":              103.8438,
        "lat_cuoi":             22.5300,
        "lng_cuoi":             104.2200,
        "nam_xay_dung":         1990,
        "nam_hoan_thanh":       1995,
        "ma_tinh_trang":        "TB",
        "ghi_chu":              "Tuyến qua địa bàn tỉnh Lào Cai"
    },
    {
        "ma_tuyen":             "QL4D",
        "ten_tuyen":            "Quốc lộ 4D",
        "ma_cap_quan_ly":       "QL",
        "chieu_dai_thuc_te":    49.5,   # sẽ được tính lại sau khi nhập đoạn
        "chieu_dai_quan_ly":    45.0,   # sẽ được tính lại sau khi nhập đoạn
        "ma_don_vi_quan_ly":    "SXD",
        "diem_dau":             "Km0 - TP Lào Cai",
        "diem_cuoi":            "Km50 - Cửa khẩu Mường Khương",
        "lat_dau":              22.3364,
        "lng_dau":              103.8438,
        "lat_cuoi":             22.8000,
        "lng_cuoi":             104.1500,
        "nam_xay_dung":         1985,
        "nam_hoan_thanh":       1992,
        "ma_tinh_trang":        "KEM",
        "ghi_chu":              "Tuyến biên giới phía Bắc"
    }
]


# =========================
# SEED TUYẾN ĐƯỜNG
# =========================

def seed_tuyen_duong():
    for data in TUYEN_CONFIG:

        # 1️⃣ Cấp quản lý
        cap_quan_ly = lay_cap_quan_ly_theo_ma(data["ma_cap_quan_ly"])
        if not cap_quan_ly:
            raise ValueError(f"Khong tim thay cap quan ly: {data['ma_cap_quan_ly']}")

        # 2️⃣ Đơn vị quản lý
        dv_quan_ly = lay_theo_ma_hoat_dong(data["ma_don_vi_quan_ly"])
        if not dv_quan_ly:
            raise ValueError(f"Khong tim thay don vi quan ly: {data['ma_don_vi_quan_ly']}")

        # 3️⃣ Tình trạng
        tinh_trang = lay_tinh_trang_theo_ma(data["ma_tinh_trang"])
        if not tinh_trang:
            raise ValueError(f"Khong tim thay tinh trang: {data['ma_tinh_trang']}")

        # 4️⃣ Tạo tuyến
        tuyen = TuyenDuong(
            ma_tuyen=data["ma_tuyen"],
            ten_tuyen=data["ten_tuyen"],
            cap_quan_ly_id=cap_quan_ly.id,
            don_vi_quan_ly_id=dv_quan_ly.id,
            diem_dau=data["diem_dau"],
            diem_cuoi=data["diem_cuoi"],
            lat_dau=data["lat_dau"],
            lng_dau=data["lng_dau"],
            lat_cuoi=data["lat_cuoi"],
            lng_cuoi=data["lng_cuoi"],
            chieu_dai_thuc_te=data["chieu_dai_thuc_te"],
            chieu_dai_quan_ly=data["chieu_dai_quan_ly"],
            nam_xay_dung=data["nam_xay_dung"],
            nam_hoan_thanh=data["nam_hoan_thanh"],
            tinh_trang_id=tinh_trang.id,
            ghi_chu=data["ghi_chu"]
        )
        get_or_create_tuyen_duong(tuyen)

    print("Seed tuyen_duong thanh cong.")