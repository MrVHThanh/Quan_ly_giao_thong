from models.tinh_trang import TinhTrang
from repositories import tinh_trang_repository as repo


def lay_tat_ca():
    rows = repo.lay_tat_ca()
    return [TinhTrang(*row) for row in rows]


def lay_theo_ma(ma):
    row = repo.lay_theo_ma(ma)
    return TinhTrang(*row) if row else None


def lay_theo_ma_hoat_dong(ma):
    row = repo.lay_theo_ma_hoat_dong(ma)
    return TinhTrang(*row) if row else None


def lay_theo_id_hoat_dong(id):
    row = repo.lay_theo_id_hoat_dong(id)
    return TinhTrang(*row) if row else None


def them_tinh_trang(tt: TinhTrang):
    try:
        last_id = repo.them_tinh_trang(
            tt.ma,
            tt.ten,
            tt.mo_ta,
            tt.mau_hien_thi,
            tt.thu_tu_hien_thi,
            tt.is_active
        )
        tt.id = last_id
    except Exception:
        raise ValueError("Ma tinh trang da ton tai!")
    return tt


def get_or_create_tinh_trang(tt: TinhTrang):
    existing = lay_theo_ma(tt.ma)

    if existing:
        if existing.is_active == 0:
            repo.khoi_phuc_tinh_trang(existing.id)
            existing.is_active = 1
        return existing

    return them_tinh_trang(tt)


def khoi_phuc_tinh_trang(id):
    repo.khoi_phuc_tinh_trang(id)