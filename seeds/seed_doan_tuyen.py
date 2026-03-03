from models.doan_tuyen import DoanTuyen
from services.doan_tuyen_service import get_or_create_doan_tuyen
from services.tuyen_duong_service import lay_tat_ca as lay_tuyen
from services.cap_duong_service import lay_tat_ca as lay_cap
from services.don_vi_service import lay_tat_ca as lay_don_vi
from services.tinh_trang_service import lay_tat_ca as lay_tinh_trang


def seed_doan_tuyen():
    map_tuyen    = {t.ma_tuyen: t for t in lay_tuyen()}
    map_cap      = {c.ma_cap: c   for c in lay_cap()}
    map_don_vi   = {dv.ma_don_vi: dv for dv in lay_don_vi()}
    map_tt       = {tt.ma: tt     for tt in lay_tinh_trang()}

    DS_DOAN = [
        {
            "ma_doan":          "QL279-01",
            "ma_tuyen":         "QL279",
            "ma_cap":           "II",
            "ly_trinh_dau":     0,
            "ly_trinh_cuoi":    10,
            "chieu_dai_thuc_te": 10.0,
            "ma_don_vi":        "CTY_BT",
            "ma_tinh_trang":    "TOT",
            "ghi_chu":          "Doan 1 tuyen QL279"
        },
        {
            "ma_doan":          "QL279-02",
            "ma_tuyen":         "QL279",
            "ma_cap":           "III",
            "ly_trinh_dau":     10,
            "ly_trinh_cuoi":    29.5,
            "chieu_dai_thuc_te": 19.6,
            "ma_don_vi":        "CTY_BT",
            "ma_tinh_trang":    "TB",
            "ghi_chu":          "Doan 2 tuyen QL279"
        },
        {
            "ma_doan":          "QL4D-01",
            "ma_tuyen":         "QL4D",
            "ma_cap":           "III",
            "ly_trinh_dau":     0,
            "ly_trinh_cuoi":    35.5,
            "chieu_dai_thuc_te": 35.7,
            "ma_don_vi":        "CTY_MD",
            "ma_tinh_trang":    "KEM",
            "ghi_chu":          "Doan 1 tuyen QL4D"
        },
        {
            "ma_doan":          "QL4D-02",
            "ma_tuyen":         "QL4D",
            "ma_cap":           "IV",
            "ly_trinh_dau":     35.5,
            "ly_trinh_cuoi":    49.5,
            "chieu_dai_thuc_te": 14.1,
            "ma_don_vi":        "CTY_MD",
            "ma_tinh_trang":    "HH_NANG",
            "ghi_chu":          "Doan 2 tuyen QL4D"
        },
    ]

    for item in DS_DOAN:
        tuyen    = map_tuyen.get(item["ma_tuyen"])
        cap      = map_cap.get(item["ma_cap"])
        don_vi   = map_don_vi.get(item["ma_don_vi"])
        tt       = map_tt.get(item["ma_tinh_trang"])

        if not tuyen:
            print(f"❌ Khong tim thay tuyen: {item['ma_tuyen']}")
            continue
        if not cap:
            print(f"❌ Khong tim thay cap: {item['ma_cap']}")
            continue
        if not don_vi:
            print(f"❌ Khong tim thay don vi: {item['ma_don_vi']}")
            continue
        if not tt:
            print(f"❌ Khong tim thay tinh trang: {item['ma_tinh_trang']}")
            continue

        doan = DoanTuyen(
            ma_doan=item["ma_doan"],
            tuyen_id=tuyen.id,
            cap_duong_id=cap.id,
            ly_trinh_dau=item["ly_trinh_dau"],
            ly_trinh_cuoi=item["ly_trinh_cuoi"],
            chieu_dai_thuc_te=item["chieu_dai_thuc_te"],
            tinh_trang_id=tt.id,
            chieu_rong_mat_max=7.5,
            chieu_rong_mat_min=7.0,
            chieu_rong_nen_max=9.0,
            chieu_rong_nen_min=8.5,
            don_vi_bao_duong_id=don_vi.id,
            ghi_chu=item["ghi_chu"]
        )
        get_or_create_doan_tuyen(doan)

    print("Seed Doan tuyen hoan thanh!")