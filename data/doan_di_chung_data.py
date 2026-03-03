"""
Dữ liệu đoạn đi chung — chỉ chỉnh sửa file này khi cập nhật đoạn đi chung.

Lưu ý:
- ma_doan trỏ đến đoạn vật lý của TUYẾN CHỦ (tuyến sở hữu đoạn đó).
- ly_trinh_dau/cuoi là lý trình theo TUYẾN ĐI CHUNG (không phải tuyến chủ).
- Các mục TODO cần bổ sung ma_doan thủ công khi tuyến chủ được nhập vào hệ thống.
"""

DOAN_DI_CHUNG_CONFIG = [
    # QL4D đi chung QL70 → đoạn QL70-05
    {
        "ma_tuyen_di_chung": "QL4D",
        "ma_doan":           "QL70-05",
        "ly_trinh_dau":      140.893,
        "ly_trinh_cuoi":     149,
        "ghi_chu":           "QL4D di chung qua doan QL70-05 (tuyen chu QL70)",
    },
    # QL4E đi chung QL70 → đoạn QL70-01
    {
        "ma_tuyen_di_chung": "QL4E",
        "ma_doan":           "QL70-01",
        "ly_trinh_dau":      35.6,
        "ly_trinh_cuoi":     36.975,
        "ghi_chu":           "QL4E di chung qua doan QL70-01 (tuyen chu QL70)",
    },
    # TODO: QL4E đi chung QL4D Km79.757→Km82.957
    # Chưa match được đoạn của tuyến chủ QL4D (tuyến chủ thuộc tỉnh khác quản lý).
    # Bổ sung ma_doan sau khi có dữ liệu tuyến QL4D trong hệ thống.
    # {
    #     "ma_tuyen_di_chung": "QL4E",
    #     "ma_doan":           "???",
    #     "ly_trinh_dau":      79.757,
    #     "ly_trinh_cuoi":     82.957,
    #     "ghi_chu":           "QL4E di chung QL4D Km79.757-Km82.957",
    # },
    # TODO: QL32 đi chung QL37 Km162.0→Km172.0
    # Chưa match được đoạn của tuyến chủ QL37 (tuyến chủ thuộc tỉnh khác quản lý).
    # Bổ sung ma_doan sau khi có dữ liệu tuyến QL37 trong hệ thống.
    # {
    #     "ma_tuyen_di_chung": "QL32",
    #     "ma_doan":           "???",
    #     "ly_trinh_dau":      162,
    #     "ly_trinh_cuoi":     172,
    #     "ghi_chu":           "QL32 di chung QL37 Km162.0-Km172.0",
    # },
    # DT153 đi chung QL4E → đoạn QL4E-04
    {
        "ma_tuyen_di_chung": "DT153",
        "ma_doan":           "QL4E-04",
        "ly_trinh_dau":      18.3,
        "ly_trinh_cuoi":     21.1,
        "ghi_chu":           "DT153 di chung qua doan QL4E-04 (tuyen chu QL4E)",
    },
    # TODO: DT155 đi chung QL4D Km43.5→Km47.1
    # Chưa match được đoạn của tuyến chủ QL4D (tuyến chủ thuộc tỉnh khác quản lý).
    # Bổ sung ma_doan sau khi có dữ liệu tuyến QL4D trong hệ thống.
    # {
    #     "ma_tuyen_di_chung": "DT155",
    #     "ma_doan":           "???",
    #     "ly_trinh_dau":      43.5,
    #     "ly_trinh_cuoi":     47.1,
    #     "ghi_chu":           "DT155 di chung QL4D Km43.5-Km47.1",
    # },
    # TODO: DT159 đi chung QL4 Km12.0→Km13.24
    # Chưa match được đoạn của tuyến chủ QL4 (tuyến chủ thuộc tỉnh khác quản lý).
    # Bổ sung ma_doan sau khi có dữ liệu tuyến QL4 trong hệ thống.
    # {
    #     "ma_tuyen_di_chung": "DT159",
    #     "ma_doan":           "???",
    #     "ly_trinh_dau":      12,
    #     "ly_trinh_cuoi":     13.24,
    #     "ghi_chu":           "DT159 di chung QL4 Km12.0-Km13.24",
    # },
    # DT159 đi chung QL4E → đoạn QL4E-08
    {
        "ma_tuyen_di_chung": "DT159",
        "ma_doan":           "QL4E-08",
        "ly_trinh_dau":      49.42,
        "ly_trinh_cuoi":     61.02,
        "ghi_chu":           "DT159 di chung qua doan QL4E-08 (tuyen chu QL4E)",
    },
    # DT159 đi chung QL4E → đoạn QL4E-09
    {
        "ma_tuyen_di_chung": "DT159",
        "ma_doan":           "QL4E-09",
        "ly_trinh_dau":      49.42,
        "ly_trinh_cuoi":     61.02,
        "ghi_chu":           "DT159 di chung qua doan QL4E-09 (tuyen chu QL4E)",
    },
    # DT159 đi chung QL4E → đoạn QL4E-10
    {
        "ma_tuyen_di_chung": "DT159",
        "ma_doan":           "QL4E-10",
        "ly_trinh_dau":      49.42,
        "ly_trinh_cuoi":     61.02,
        "ghi_chu":           "DT159 di chung qua doan QL4E-10 (tuyen chu QL4E)",
    },
    # DT159 đi chung QL4E → đoạn QL4E-11
    {
        "ma_tuyen_di_chung": "DT159",
        "ma_doan":           "QL4E-11",
        "ly_trinh_dau":      49.42,
        "ly_trinh_cuoi":     61.02,
        "ghi_chu":           "DT159 di chung qua doan QL4E-11 (tuyen chu QL4E)",
    },
    # TODO: DT159 đi chung QL4 Km61.02→Km67.75
    # Chưa match được đoạn của tuyến chủ QL4 (tuyến chủ thuộc tỉnh khác quản lý).
    # Bổ sung ma_doan sau khi có dữ liệu tuyến QL4 trong hệ thống.
    # {
    #     "ma_tuyen_di_chung": "DT159",
    #     "ma_doan":           "???",
    #     "ly_trinh_dau":      61.02,
    #     "ly_trinh_cuoi":     67.75,
    #     "ghi_chu":           "DT159 di chung QL4 Km61.02-Km67.75",
    # },
    # DT160 đi chung QL279 → đoạn QL279-11
    {
        "ma_tuyen_di_chung": "DT160",
        "ma_doan":           "QL279-11",
        "ly_trinh_dau":      81,
        "ly_trinh_cuoi":     88,
        "ghi_chu":           "DT160 di chung qua doan QL279-11 (tuyen chu QL279)",
    },
    # DT160 đi chung QL279 → đoạn QL279-12
    {
        "ma_tuyen_di_chung": "DT160",
        "ma_doan":           "QL279-12",
        "ly_trinh_dau":      81,
        "ly_trinh_cuoi":     88,
        "ghi_chu":           "DT160 di chung qua doan QL279-12 (tuyen chu QL279)",
    },
    # DT160 đi chung QL279 → đoạn QL279-13
    {
        "ma_tuyen_di_chung": "DT160",
        "ma_doan":           "QL279-13",
        "ly_trinh_dau":      81,
        "ly_trinh_cuoi":     88,
        "ghi_chu":           "DT160 di chung qua doan QL279-13 (tuyen chu QL279)",
    },
    # DT162 đi chung DT151 → đoạn DT151-03
    {
        "ma_tuyen_di_chung": "DT162",
        "ma_doan":           "DT151-03",
        "ly_trinh_dau":      32.6,
        "ly_trinh_cuoi":     33,
        "ghi_chu":           "DT162 di chung qua doan DT151-03 (tuyen chu DT151)",
    },
    # DX02 đi chung DT173 → đoạn DT173-01
    {
        "ma_tuyen_di_chung": "DX02",
        "ma_doan":           "DT173-01",
        "ly_trinh_dau":      6.814,
        "ly_trinh_cuoi":     8.09,
        "ghi_chu":           "DX02 di chung qua doan DT173-01 (tuyen chu DT173)",
    },
]