from models.don_vi import DonVi
from repositories import don_vi_repository as repo
import sqlite3



# ================= LẤY TẤT CẢ (CHỈ HOẠT ĐỘNG) =================
def lay_tat_ca():
    rows = repo.lay_tat_ca()
    return [DonVi(*row) for row in rows]


# ================= LẤY TẤT CẢ KỂ CẢ ĐÃ XOÁ =================
def lay_tat_ca_ke_ca_da_xoa():
    rows = repo.lay_tat_ca_ke_ca_da_xoa()
    return [DonVi(*row) for row in rows]


# ================= LẤY THEO ID =================
def lay_theo_id(id):
    row = repo.lay_theo_id(id)
    if row:
        return DonVi(*row)
    return None

# ================= LẤY THEO ID (CHỈ HOẠT ĐỘNG) =================
def lay_theo_id_hoat_dong(id):
    row = repo.lay_theo_id_hoat_dong(id)
    if row:
        return DonVi(*row)
    return None

# ================= LẤY THEO MÃ ĐƠN VỊ =================
def lay_theo_ma_hoat_dong(ma_don_vi):
    row = repo.lay_theo_ma_hoat_dong(ma_don_vi)
    if row:
        return DonVi(*row)
    return None

# ================= LẤY ĐƠN VỊ CON (CHỈ HOẠT ĐỘNG) =================
def lay_con(parent_id):
    rows = repo.lay_con(parent_id)
    return [DonVi(*row) for row in rows]


# ================= THÊM =================
def them_don_vi(don_vi: DonVi):
    try:
        last_id = repo.them_don_vi(
            don_vi.ma_don_vi,
            don_vi.ten_don_vi,
            don_vi.loai,
            don_vi.parent_id,
            don_vi.is_active
        )
        don_vi.id = last_id

    except sqlite3.IntegrityError as e:
        raise ValueError("Ma don vi da ton tai!") from e

    return don_vi


# ================= CẬP NHẬT =================
def cap_nhat_don_vi(don_vi: DonVi):
    existing = lay_theo_id(don_vi.id)
    if not existing:
        raise ValueError("Don vi khong ton tai!")

    repo.cap_nhat_don_vi(
        don_vi.id,
        don_vi.ma_don_vi,
        don_vi.ten_don_vi,
        don_vi.loai,
        don_vi.parent_id,
        don_vi.is_active
    )


# ================= XOÁ AN TOÀN =================
def xoa_don_vi(id):
    don_vi = lay_theo_id(id)
    if not don_vi:
        raise ValueError("Don vi khong ton tai!")

    repo.xoa_don_vi(id)


# ================= KHÔI PHỤC =================
def khoi_phuc_don_vi(id):
    don_vi = lay_theo_id(id)
    if not don_vi:
        raise ValueError("Don vi khong ton tai!")

    repo.khoi_phuc_don_vi(id)

# ================= GET OR CREATE =================
def get_or_create_don_vi(don_vi: DonVi):
    # 1. Kiểm tra tồn tại theo mã
    existing = lay_theo_ma_hoat_dong(don_vi.ma_don_vi)

    if existing:
        return existing  # Đã tồn tại → trả về luôn

    # 2. Nếu chưa tồn tại → thêm mới
    return them_don_vi(don_vi)

# ================= LẤY THEO MÃ (KỂ CẢ ĐÃ XOÁ) =================
def lay_theo_ma(ma_don_vi):
    row = repo.lay_theo_ma(ma_don_vi)
    if row:
        return DonVi(*row)
    return None

# ================= GET OR CREATE =================
def get_or_create_don_vi(don_vi: DonVi):
    existing = lay_theo_ma(don_vi.ma_don_vi)

    if existing:
        # Nếu tồn tại nhưng đã bị soft delete → khôi phục
        if existing.is_active == 0:
            khoi_phuc_don_vi(existing.id)
            existing.is_active = 1

        return existing

    return them_don_vi(don_vi)