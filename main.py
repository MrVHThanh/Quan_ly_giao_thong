import os
import sqlite3

from config.database import create_tables, DB_PATH
from seeds.seed_all import seed_all

import models.cap_quan_ly as cap_quan_ly_model
import models.cap_duong as cap_duong_model
import models.don_vi as don_vi_model
import models.tinh_trang as tinh_trang_model
import models.tuyen_duong as tuyen_duong_model
import models.doan_tuyen as doan_tuyen_model

import services.cap_quan_ly_service as cap_quan_ly_service
import services.cap_duong_service as cap_duong_service
import services.don_vi_service as don_vi_service
import services.tinh_trang_service as tinh_trang_service
import services.tuyen_duong_service as tuyen_duong_service
import services.doan_tuyen_service as doan_tuyen_service


def in_cay_don_vi(parent_id=None, level=0):
    if parent_id is None:
        ds = [dv for dv in don_vi_service.lay_tat_ca() if dv.parent_id is None]
    else:
        ds = don_vi_service.lay_con(parent_id)
    for dv in ds:
        print("   " * level + dv.ten_don_vi)
        in_cay_don_vi(dv.id, level + 1)


def in_thong_ke_tinh_trang(tuyen):
    tk = doan_tuyen_service.thong_ke_tinh_trang_tuyen(tuyen.id)
    print(f"\n  >> Thống kê tình trạng tuyến {tuyen.ma_tuyen} (tổng: {tk['tong_km']} km):")
    for doan in tk["chi_tiet"]:
        ten_tt = doan["ten_tinh_trang"] or "Chưa xác định"
        print(f"     - {doan['ma_doan']:12s} | {doan['ly_trinh_dau']:6.1f} → {doan['ly_trinh_cuoi']:6.1f} km"
              f" | {doan['chieu_dai_tinh']:6.2f} km | {ten_tt}")
    print(f"  >> Tổng hợp:")
    for ma, info in tk["tong_hop"].items():
        print(f"     {info['ten']:20s}: {info['tong_km']:.2f} km ({info['ty_le']}%)")


if __name__ == "__main__":

    print("\n===== KHOI TAO DATABASE =====")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Da xoa database cu!")
    create_tables()

    print("\n===== SEED DU LIEU =====")
    seed_all()

    print("\n===== DANH SACH CAP_QUAN_LY =====")
    for capql in cap_quan_ly_service.lay_tat_ca():
        print(capql)

    print("\n===== DANH SACH CAP_DUONG =====")
    for cap in cap_duong_service.lay_tat_ca():
        print(cap)

    print("\n===== CAY DON_VI =====")
    in_cay_don_vi()

    print("\n===== DANH SACH TINH_TRANG =====")
    for tt in tinh_trang_service.lay_tat_ca():
        print(tt)

    print("\n===== DANH SACH TUYEN_DUONG =====")
    for tuyen in tuyen_duong_service.lay_tat_ca():
        print(tuyen)
        print(f"   Toa do dau : {tuyen.toa_do_dau}")
        print(f"   Toa do cuoi: {tuyen.toa_do_cuoi}")
        in_thong_ke_tinh_trang(tuyen)

    print("\n===== DANH SACH DOAN_TUYEN =====")
    for doan in doan_tuyen_service.lay_tat_ca():
        print(doan)

    print("\n===== HOAN THANH =====")


# Thống kê các tuyến Quốc lộ
quoclo = tuyen_duong_service.thong_ke_theo_cap_quan_ly("QL")
# In kết quả
print("============DANH SÁCH CÁC TUYẾN QUỐC LỘ=======================")
for cap in quoclo:
    print(f"\n{cap['ma_cap']} - {cap['ten_cap']}")
    print(f"  Số tuyến        : {cap['so_tuyen']}")
    print(f"  CD quản lý      : {cap['tong_chieu_dai_quan_ly']} km")
    print(f"  CD thực tế      : {cap['tong_chieu_dai_thuc_te']} km")
    for tuyen in cap['ds_tuyen']:
        print(f"    - {tuyen}")

# Thống kê các tuyến Tỉnh lộ
tinhlo = tuyen_duong_service.thong_ke_theo_cap_quan_ly("DT")
print("============DANH SÁCH CÁC TUYẾN TỈNH LỘ=======================")
for cap in tinhlo:
    print(f"\n{cap['ma_cap']} - {cap['ten_cap']}")
    print(f"  Số tuyến        : {cap['so_tuyen']}")
    print(f"  CD quản lý      : {cap['tong_chieu_dai_quan_ly']} km")
    print(f"  CD thực tế      : {cap['tong_chieu_dai_thuc_te']} km")
    for tuyen in cap['ds_tuyen']:
        print(f"    - {tuyen}")

print("============DANH SÁCH CÁC TUYẾN QUỐC LỘ, TỈNH LỘ=======================")
# Thống kê quốc lộ và tỉnh lộ
quoclo_tinhlo = tuyen_duong_service.thong_ke_theo_cap_quan_ly(["QL", "DT"])
for cap in quoclo_tinhlo:
    print(f"\n{cap['ma_cap']} - {cap['ten_cap']}")
    print(f"  Số tuyến        : {cap['so_tuyen']}")
    print(f"  CD quản lý      : {cap['tong_chieu_dai_quan_ly']} km")
    print(f"  CD thực tế      : {cap['tong_chieu_dai_thuc_te']} km")
    for tuyen in cap['ds_tuyen']:
        print(f"    - {tuyen}")
print(quoclo_tinhlo)








'''
    ql279 = tuyen_duong_service.lay_theo_ma("QL279")

    print(ql279.chieu_dai)
    print(ql279.cap_duong_id)
    print(ql279.don_vi_quan_ly_id)
    print(ql279.don_vi_bao_duong_id)
    print(ql279.ten_tuyen)

    print(don_vi_service.lay_theo_id_hoat_dong(ql279.don_vi_quan_ly_id))
    print(don_vi_service.lay_theo_id_hoat_dong(ql279.don_vi_bao_duong_id))
    print(cap_duong_service.lay_theo_id_hoat_dong(ql279.cap_duong_id))
    print(ql279)

    print(tuyen_duong_service.lay_theo_ma("QL279").chieu_dai)
    print(cap_duong_service.lay_theo_id_hoat_dong(ql279.cap_duong_id))
'''
  
