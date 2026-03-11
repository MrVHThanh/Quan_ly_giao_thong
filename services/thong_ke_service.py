from repositories import thong_ke_repository as repo


def lay_thong_ke_cap_ky_thuat():
    """
    Trả về dict nhóm theo cap_quan_ly:
    {
        "QL": {
            "ten_cap_quan_ly": "Đường quốc lộ",
            "tong_chieu_dai":  75.4,
            "chi_tiet": [ThongKeCapKyThuat, ...]
        },
        ...
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
    """In bảng thống kê ra console."""
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