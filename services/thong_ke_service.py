from repositories import thong_ke_repository as repo
from services.tuyen_duong_service import lay_tat_ca as lay_tat_ca_tuyen


# ==========================
# THỐNG KÊ TỔNG HỢP
# ==========================

def lay_thong_ke_cap_ky_thuat():
    """
    Trả về dict nhóm theo cap_quan_ly:
    {
        "QL": {
            "ten_cap_quan_ly": "Đường quốc lộ",
            "tong_chieu_dai":  75.4,
            "chi_tiet": [ThongKeCapKyThuat, ...]
        }, ...
    }
    """
    rows = repo.lay_thong_ke_cap_ky_thuat_theo_cap_quan_ly()

    result = {}
    for item in rows:
        ma = item.ma_cap_quan_ly
        if ma not in result:
            result[ma] = {
                "ten_cap_quan_ly": item.ten_cap_quan_ly,
                "tong_chieu_dai":  0.0,
                "chi_tiet":        []
            }
        result[ma]["tong_chieu_dai"] = round(
            result[ma]["tong_chieu_dai"] + item.tong_chieu_dai, 3
        )
        result[ma]["chi_tiet"].append(item)

    return result


def in_thong_ke_cap_ky_thuat():
    """In bảng thống kê tổng hợp ra console."""
    data = lay_thong_ke_cap_ky_thuat()

    print("\n" + "=" * 60)
    print("  THỐNG KÊ CHIỀU DÀI ĐƯỜNG THEO CẤP KỸ THUẬT")
    print("=" * 60)

    if not data:
        print("  Không có dữ liệu.")
        return

    for ma_cql, nhom in data.items():
        tong = nhom["tong_chieu_dai"]
        print(f"\n  [{ma_cql}] {nhom['ten_cap_quan_ly']}  —  Tổng: {tong:.3f} km")
        print(f"  {'─'*50}")
        print(f"  {'Cấp kỹ thuật':<20} {'Chiều dài (km)':>15}  {'Tỷ lệ':>8}")
        print(f"  {'─'*50}")

        for item in nhom["chi_tiet"]:
            ty_le = (item.tong_chieu_dai / tong * 100) if tong else 0
            print(
                f"  {item.ten_cap_ky_thuat:<20} "
                f"{item.tong_chieu_dai:>15.3f}  "
                f"{ty_le:>7.1f}%"
            )

        print(f"  {'─'*50}")
        print(f"  {'TỔNG CỘNG':<20} {tong:>15.3f}  {'100.0%':>8}")

    print("\n" + "=" * 60)


# ==========================
# THỐNG KÊ CHI TIẾT TỪNG TUYẾN
# ==========================

def lay_thong_ke_chi_tiet_tung_tuyen():
    """
    Trả về dict nhóm theo tuyen_id:
    {
        tuyen_id: {
            "tuyen":        TuyenDuong,
            "cap_ky_thuat": [ThongKeCapKyThuatTheoTuyen, ...],
            "doan_chinh":   [ChiTietDoanTheoTuyen, ...],
            "doan_di_chung":[ChiTietDoanTheoTuyen, ...],
        }, ...
    }
    """
    ds_tuyen    = lay_tat_ca_tuyen()
    ds_cap_kt   = repo.lay_thong_ke_cap_ky_thuat_theo_tung_tuyen()
    ds_chi_tiet = repo.lay_chi_tiet_doan_theo_tung_tuyen()

    result = {t.id: {
        "tuyen":         t,
        "cap_ky_thuat":  [],
        "doan_chinh":    [],
        "doan_di_chung": []
    } for t in ds_tuyen}

    for item in ds_cap_kt:
        if item.tuyen_id in result:
            result[item.tuyen_id]["cap_ky_thuat"].append(item)

    for doan in ds_chi_tiet:
        if doan.tuyen_id in result:
            key = "doan_chinh" if doan.loai == "CHINH" else "doan_di_chung"
            result[doan.tuyen_id][key].append(doan)

    return result


def in_thong_ke_chi_tiet_tung_tuyen():
    """In báo cáo chi tiết từng tuyến ra console."""
    data = lay_thong_ke_chi_tiet_tung_tuyen()

    for tuyen_id, nhom in data.items():
        tuyen        = nhom["tuyen"]
        cap_kts      = nhom["cap_ky_thuat"]
        ds_chinh     = nhom["doan_chinh"]
        ds_di_chung  = nhom["doan_di_chung"]

        cd_ql = f"{tuyen.chieu_dai_quan_ly:.3f}" if tuyen.chieu_dai_quan_ly else "N/A"
        cd_tt = f"{tuyen.chieu_dai_thuc_te:.3f}"  if tuyen.chieu_dai_thuc_te  else "N/A"

        print(f"\n{'='*75}")
        print(f"  {tuyen.ten_tuyen}  ({tuyen.ma_tuyen})")
        print(f"{'='*75}")
        print(f"  Chiều dài quản lý : {cd_ql} km   |   Chiều dài thực tế: {cd_tt} km")
        print(f"  Điểm đầu          : {tuyen.diem_dau  or 'N/A'}")
        print(f"  Điểm cuối         : {tuyen.diem_cuoi or 'N/A'}")

        # --- Thống kê cấp kỹ thuật ---
        tong = tuyen.chieu_dai_quan_ly or 0
        print(f"\n  {'─'*65}")
        print(f"  {'Cấp kỹ thuật':<25} {'Chiều dài (km)':>15}  {'Tỷ lệ':>8}")
        print(f"  {'─'*65}")
        for item in cap_kts:
            ty_le = (item.tong_chieu_dai / tong * 100) if tong else 0
            print(
                f"  {item.ten_cap_ky_thuat:<25} "
                f"{item.tong_chieu_dai:>15.3f}  "
                f"{ty_le:>7.1f}%"
            )
        print(f"  {'─'*65}")
        print(f"  {'TỔNG CỘNG':<25} {tong:>15.3f}  {'100.0%':>8}")

        # --- Chi tiết đoạn ---
        ds_tat_ca = ds_chinh + sorted(ds_di_chung, key=lambda x: x.ly_trinh_dau)
        print(f"\n  Chi tiết các đoạn: Tổng {len(ds_tat_ca)} đoạn "
              f"({len(ds_chinh)} đoạn chính, {len(ds_di_chung)} đoạn đi chung)")
        print(f"\n  {'Tên đoạn':<14} | {'Lý trình đầu – cuối':^25} | "
              f"{'CD (km)':>9} | {'Cấp đường':<12} | {'Tình trạng':<18} | Loại")
        print(f"  {'─'*100}")

        for doan in ds_tat_ca:
            ly_trinh = f"{doan.ly_trinh_dau:6.1f} → {doan.ly_trinh_cuoi:6.1f} km"
            cd       = f"{doan.chieu_dai:.3f}" if doan.chieu_dai else "N/A"
            print(
                f"  {doan.ma_doan:<14} | "
                f"{ly_trinh:^25} | "
                f"{cd:>9} | "
                f"{doan.ten_cap_ky_thuat:<12} | "
                f"{doan.ten_tinh_trang:<18} | "
                f"{doan.loai}"
            )

    print(f"\n{'='*75}\n")