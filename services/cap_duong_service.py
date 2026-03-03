from models.cap_duong import CapDuong
from repositories import cap_duong_repository as repo


def lay_tat_ca():
    rows = repo.lay_tat_ca()
    return [CapDuong(*row) for row in rows]


def lay_theo_ma(ma_cap):
    row = repo.lay_theo_ma(ma_cap)
    return CapDuong(*row) if row else None


def lay_theo_id_hoat_dong(id):
    row = repo.lay_theo_id_hoat_dong(id)
    return CapDuong(*row) if row else None


def them_cap_duong(cap: CapDuong):
    try:
        last_id = repo.them_cap_duong(
            cap.ma_cap,
            cap.ten_cap,
            cap.mo_ta,
            cap.thu_tu_hien_thi,
            cap.is_active
        )
        cap.id = last_id
    except Exception:
        raise ValueError("Ma cap da ton tai!")
    return cap



def lay_theo_ma_hoat_dong(ma_cap):
    row = repo.lay_theo_ma_hoat_dong(ma_cap)
    return CapDuong(*row) if row else None

# ================= GET OR CREATE =================
def get_or_create_cap_duong(cap: CapDuong):
    existing = lay_theo_ma(cap.ma_cap)

    if existing:
        # Nếu tồn tại nhưng bị soft delete → khôi phục
        if existing.is_active == 0:
            repo.khoi_phuc_cap_duong(existing.id)
            existing.is_active = 1

        return existing

    return them_cap_duong(cap)


def khoi_phuc_cap_duong(id):
    repo.khoi_phuc_cap_duong(id)