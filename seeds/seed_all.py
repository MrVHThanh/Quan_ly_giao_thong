from seeds.seed_cap_quan_ly import seed_cap_quan_ly
from seeds.seed_cap_duong import seed_cap_duong
from seeds.seed_don_vi import seed_don_vi
from seeds.seed_tinh_trang import seed_tinh_trang
from seeds.seed_tuyen_duong import seed_tuyen_duong
from seeds.seed_doan_tuyen import seed_doan_tuyen
from seeds.seed_doan_di_chung import seed_doan_di_chung


def seed_all():
    ds_cap_quan_ly  = seed_cap_quan_ly()
    ds_cap          = seed_cap_duong()
    ds_don_vi       = seed_don_vi()
    ds_tinh_trang   = seed_tinh_trang()
    ds_tuyen_duong  = seed_tuyen_duong()
    ds_doan_tuyen   = seed_doan_tuyen()
    ds_doan_di_chung = seed_doan_di_chung() 

    return {
        "cap_quan_ly":      ds_cap_quan_ly,
        "cap_duong":        ds_cap,
        "don_vi":           ds_don_vi,
        "tinh_trang":       ds_tinh_trang,
        "tuyen_duong":      ds_tuyen_duong,
        "doan_tuyen":       ds_doan_tuyen,
        "doan_di_chung":    ds_doan_di_chung
    }