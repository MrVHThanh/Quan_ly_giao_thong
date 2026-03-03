from models.cap_quan_ly import CapQuanLy
from repositories import cap_quan_ly_repository as repo


def lay_tat_ca():
    rows = repo.lay_tat_ca()
    return [CapQuanLy(*row) for row in rows]


def lay_theo_ma(ma_cap):
    row = repo.lay_theo_ma(ma_cap)
    return CapQuanLy(*row) if row else None


def lay_theo_ma_hoat_dong(ma_cap):
    row = repo.lay_theo_ma_hoat_dong(ma_cap)
    return CapQuanLy(*row) if row else None


def lay_theo_id_hoat_dong(id):
    row = repo.lay_theo_id_hoat_dong(id)
    return CapQuanLy(*row) if row else None


def them_cap_quan_ly(cap: CapQuanLy):
    try:
        last_id = repo.them_cap_quan_ly(
            cap.ma_cap,
            cap.ten_cap,
            cap.mo_ta,
            cap.thu_tu_hien_thi,
            cap.is_active
        )
        cap.id = last_id
    except Exception:
        raise ValueError("Ma cap quan ly da ton tai!")
    return cap


def get_or_create_cap_quan_ly(cap: CapQuanLy):
    existing = lay_theo_ma(cap.ma_cap)

    if existing:
        # Nếu tồn tại nhưng bị soft delete → khôi phục
        if existing.is_active == 0:
            repo.khoi_phuc_cap_quan_ly(existing.id)
            existing.is_active = 1
        return existing

    return them_cap_quan_ly(cap)


def khoi_phuc_cap_quan_ly(id):
    repo.khoi_phuc_cap_quan_ly(id)