from models.tuyen_duong import TuyenDuong
from services.cap_quan_ly_service import lay_theo_id_hoat_dong as lay_cap_quan_ly
from services.don_vi_service import lay_theo_id_hoat_dong as lay_don_vi
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

# ================= THONG KE THEO CAP QUAN LY =================
def thong_ke_theo_cap_quan_ly(ds_ma_cap):
    """
    Thống kê tuyến đường theo một hoặc nhiều mã cấp quản lý.

    Args:
        ds_ma_cap (str | list): Một mã hoặc list mã cấp.
                                Ví dụ: "QL" hoặc ["QL", "DT"]

    Returns:
        list[dict] với các key:
            ma_cap, ten_cap, so_tuyen,
            tong_chieu_dai_quan_ly, tong_chieu_dai_thuc_te,
            ds_tuyen

    Raises:
        ValueError: Nếu ds_ma_cap rỗng.
    """
    # Chuẩn hóa: cho phép truyền string đơn hoặc list
    if isinstance(ds_ma_cap, str):
        ds_ma_cap = [ds_ma_cap]

    if not ds_ma_cap:
        raise ValueError("Phai truyen it nhat mot ma cap quan ly!")

    return repo.thong_ke_theo_cap_quan_ly(ds_ma_cap)