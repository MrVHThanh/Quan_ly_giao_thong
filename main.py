import os
import sqlite3

# ================= DATABASE =================
from config.database import create_tables, DB_PATH

# ================= SEED =================
from seeds.seed_all import seed_all

# ================= IMPORT MODEL =================
import models.cap_quan_ly as cap_quan_ly_model
import models.cap_duong as cap_duong_model
import models.don_vi as don_vi_model
import models.tinh_trang as tinh_trang_model
import models.tuyen_duong as tuyen_duong_model
import models.doan_tuyen as doan_tuyen_model

# ================= IMPORT SERVICE =================
import services.cap_quan_ly_service as cap_quan_ly_service
import services.cap_duong_service as cap_duong_service
import services.don_vi_service as don_vi_service
import services.tinh_trang_service as tinh_trang_service
import services.tuyen_duong_service as tuyen_duong_service
import services.doan_tuyen_service as doan_tuyen_service
import services.doan_di_chung_service as doan_di_chung_service


# ================= IN CÂY ĐƠN VỊ =================
def in_cay_don_vi(parent_id=None, level=0):
    if parent_id is None:
        ds = [dv for dv in don_vi_service.lay_tat_ca() if dv.parent_id is None]
    else:
        ds = don_vi_service.lay_con(parent_id)

    for dv in ds:
        print("   " * level + dv.ten_don_vi)
        in_cay_don_vi(dv.id, level + 1)


# ================= IN CHI TIẾT TUYẾN + ĐOẠN =================
def in_chi_tiet_tuyen(tuyen):
    """
    In thông tin tuyến đường và toàn bộ danh sách đoạn (chính + đi chung),
    sắp xếp theo ly_trinh_dau, có đánh dấu loại đoạn.
    """

    # --- Tiêu đề tuyến ---
    print(f"\n{'='*60}")
    print(f"  {tuyen.ma_tuyen} - {tuyen.ten_tuyen}")
    # print(f"{'='*60}")
    print(f"  Điểm đầu     : {tuyen.diem_dau or 'N/A'}")
    print(f"  Điểm cuối    : {tuyen.diem_cuoi or 'N/A'}")
    cd_ql = f"{tuyen.chieu_dai_quan_ly:.2f} km" if tuyen.chieu_dai_quan_ly else "N/A"
    cd_tt = f"{tuyen.chieu_dai_thuc_te:.2f} km" if tuyen.chieu_dai_thuc_te else "N/A"
    print(f"  CD quản lý   : {cd_ql}   (chỉ đoạn chính)")
    print(f"  CD thực tế   : {cd_tt}   (kể cả đoạn đi chung)")

    # --- Lấy đoạn chính ---
    ds_chinh = doan_tuyen_service.lay_theo_tuyen(tuyen.id)

    # --- Lấy đoạn đi chung ---
    ds_di_chung = doan_di_chung_service.lay_theo_tuyen(tuyen.id)

    # --- Gộp lại, đánh tag, sắp xếp theo ly_trinh_dau ---
    ds_tat_ca = []

    for doan in ds_chinh:
        ds_tat_ca.append({
            "ly_trinh_dau":  doan.ly_trinh_dau,
            "ly_trinh_cuoi": doan.ly_trinh_cuoi,
            "chieu_dai":     doan.chieu_dai_tinh,
            "ma_doan":       doan.ma_doan,
            "loai":          "CHINH",
            "ghi_chu":       doan.ghi_chu or ""
        })

    for ddc in ds_di_chung:
        # Lấy thông tin đoạn gốc để biết mã đoạn
        doan_goc = doan_tuyen_service.lay_theo_id(ddc.doan_id)
        ma_doan  = doan_goc.ma_doan if doan_goc else f"doan_id={ddc.doan_id}"
        ds_tat_ca.append({
            "ly_trinh_dau":  ddc.ly_trinh_dau,
            "ly_trinh_cuoi": ddc.ly_trinh_cuoi,
            "chieu_dai":     ddc.chieu_dai,
            "ma_doan":       ma_doan,
            "loai":          "DI CHUNG",
            "ghi_chu":       ddc.ghi_chu or ""
        })

    ds_tat_ca.sort(key=lambda x: x["ly_trinh_dau"])

    # --- In bảng đoạn ---
    print(f"\n  {'STT':<4} {'Mã đoạn':<12} {'Lý trình':<20} {'CD (km)':<10} {'Loại':<10} Ghi chú")
    print(f"  {'-'*4} {'-'*12} {'-'*20} {'-'*10} {'-'*10} {'-'*20}")

    for i, d in enumerate(ds_tat_ca, 1):
        ly_trinh = f"Km{d['ly_trinh_dau']} → Km{d['ly_trinh_cuoi']}"
        cd       = f"{d['chieu_dai']:.1f}" if d['chieu_dai'] else "N/A"
        print(f"  {i:<4} {d['ma_doan']:<12} {ly_trinh:<20} {cd:<10} {d['loai']:<10} {d['ghi_chu']}")

    print(f"\n  Tổng số đoạn : {len(ds_tat_ca)} "
          f"({len(ds_chinh)} đoạn chính, {len(ds_di_chung)} đoạn đi chung)")


# ========================== MAIN ========================
# ========================================================

if __name__ == "__main__":

    print("\n===== KHOI TAO DATABASE =====")

    # 🔥 DEV MODE: Xóa DB nếu tồn tại
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Da xoa database cu!")

    # Tạo lại bảng
    create_tables()

    # =========================
    # SEED TOÀN BỘ DỮ LIỆU
    # =========================
    print("\n===== SEED DU LIEU =====")
    seed_all()

    # =========================
    # KIỂM TRA CAP_QUAN_LY
    # =========================
    print("\n===== DANH SACH CAP_QUAN_LY =====")
    for capql in cap_quan_ly_service.lay_tat_ca():
        print(capql)

    # =========================
    # KIỂM TRA CAP_DUONG
    # =========================
    print("\n===== DANH SACH CAP_DUONG =====")
    for cap in cap_duong_service.lay_tat_ca():
        print(cap)

    # =========================
    # KIỂM TRA DON_VI
    # =========================
    print("\n===== CAY DON_VI =====")
    in_cay_don_vi()

    # =========================
    # KIỂM TRA TINH_TRANG
    # =========================
    print("\n===== DANH SACH TINH_TRANG =====")
    for tt in tinh_trang_service.lay_tat_ca():
        print(tt)

    # =========================
    # CHI TIẾT TỪNG TUYẾN + ĐOẠN
    # =========================
    print("\n\n===== CHI TIET TUYEN DUONG VA DOAN TUYEN =====")
    for tuyen in tuyen_duong_service.lay_tat_ca():
        in_chi_tiet_tuyen(tuyen)

    print("\n\n===== HOAN THANH =====")





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
  
