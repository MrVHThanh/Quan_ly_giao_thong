from models.tuyen_duong import TuyenDuong
from services.cap_quan_ly_service import lay_theo_id_hoat_dong as lay_cap_quan_ly
from services.don_vi_service import lay_theo_id_hoat_dong as lay_don_vi
from services.tinh_trang_service import lay_theo_id_hoat_dong as lay_tinh_trang
from repositories import tuyen_duong_repository as repo


# ================= LẤY TẤT CẢ =================
def lay_tat_ca():
    return repo.lay_tat_ca()


# ================= LẤY THEO MÃ =================
def lay_theo_ma(ma_tuyen):
    return repo.lay_theo_ma(ma_tuyen)


# ================= LẤY THEO ID =================
def lay_theo_id(id):
    return repo.lay_theo_id(id)


# ================= THÊM =================
def them_tuyen_duong(tuyen: TuyenDuong):

    if tuyen.cap_quan_ly_id:
        if not lay_cap_quan_ly(tuyen.cap_quan_ly_id):
            raise ValueError("Cap quan ly khong hop le!")

    if tuyen.don_vi_quan_ly_id:
        if not lay_don_vi(tuyen.don_vi_quan_ly_id):
            raise ValueError("Don vi quan ly khong hop le!")

    if tuyen.tinh_trang_id:
        if not lay_tinh_trang(tuyen.tinh_trang_id):
            raise ValueError("Tinh trang khong hop le!")

    return repo.them_tuyen_duong(tuyen)


# ================= CẬP NHẬT CHIỀU DÀI =================
def cap_nhat_chieu_dai_tuyen(tuyen_id):
    repo.cap_nhat_chieu_dai_tuyen(tuyen_id)


# ================= GET OR CREATE =================
def get_or_create_tuyen_duong(tuyen: TuyenDuong):
    existing = lay_theo_ma(tuyen.ma_tuyen)

    if existing:
        return existing

    return them_tuyen_duong(tuyen)