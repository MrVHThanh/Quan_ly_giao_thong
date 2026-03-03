from seeds.seed_cap_quan_ly import seed_cap_quan_ly
from seeds.seed_cap_duong import seed_cap_duong
from seeds.seed_don_vi import seed_don_vi
from seeds.seed_tinh_trang import seed_tinh_trang
from seeds.seed_tuyen_doan import seed_tuyen_duong, seed_doan_tuyen, seed_doan_di_chung


def seed_all():
    ds_cap_quan_ly   = seed_cap_quan_ly()
    ds_cap           = seed_cap_duong()
    ds_don_vi        = seed_don_vi()
    ds_tinh_trang    = seed_tinh_trang()
    seed_tuyen_duong()
    seed_doan_tuyen()
    seed_doan_di_chung()

    return {
        "cap_quan_ly":      ds_cap_quan_ly,
        "cap_duong":        ds_cap,
        "don_vi":           ds_don_vi,
        "tinh_trang":       ds_tinh_trang,
        "tuyen_duong":      None,
        "doan_tuyen":       None,
        "doan_di_chung":    None,
    }