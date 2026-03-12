class ThongKeCapKyThuat:
    """
    Model kết quả thống kê một dòng:
    (cap_quan_ly × cap_ky_thuat → chieu_dai)
    """

    def __init__(
        self,
        ma_cap_quan_ly,
        ten_cap_quan_ly,
        thu_tu_cap_quan_ly,
        ma_cap_ky_thuat,
        ten_cap_ky_thuat,
        thu_tu_cap_ky_thuat,
        tong_chieu_dai
    ):
        self.ma_cap_quan_ly      = ma_cap_quan_ly
        self.ten_cap_quan_ly     = ten_cap_quan_ly
        self.thu_tu_cap_quan_ly  = thu_tu_cap_quan_ly
        self.ma_cap_ky_thuat     = ma_cap_ky_thuat
        self.ten_cap_ky_thuat    = ten_cap_ky_thuat
        self.thu_tu_cap_ky_thuat = thu_tu_cap_ky_thuat
        self.tong_chieu_dai      = round(tong_chieu_dai, 3)

    def __repr__(self):
        return (
            f"<ThongKeCapKyThuat "
            f"[{self.ma_cap_quan_ly}] {self.ten_cap_quan_ly} | "
            f"[{self.ma_cap_ky_thuat}] {self.ten_cap_ky_thuat} | "
            f"{self.tong_chieu_dai} km>"
        )

    def to_dict(self):
        return {
            "ma_cap_quan_ly":      self.ma_cap_quan_ly,
            "ten_cap_quan_ly":     self.ten_cap_quan_ly,
            "ma_cap_ky_thuat":     self.ma_cap_ky_thuat,
            "ten_cap_ky_thuat":    self.ten_cap_ky_thuat,
            "tong_chieu_dai":      self.tong_chieu_dai,
        }

class ThongKeCapKyThuatTheoTuyen:
    """Tổng chiều dài theo cấp kỹ thuật của một tuyến."""

    def __init__(
        self,
        tuyen_id,
        ma_cap_ky_thuat,
        ten_cap_ky_thuat,
        thu_tu_cap_ky_thuat,
        tong_chieu_dai
    ):
        self.tuyen_id            = tuyen_id
        self.ma_cap_ky_thuat     = ma_cap_ky_thuat
        self.ten_cap_ky_thuat    = ten_cap_ky_thuat
        self.thu_tu_cap_ky_thuat = thu_tu_cap_ky_thuat
        self.tong_chieu_dai      = round(tong_chieu_dai, 3)

    def __repr__(self):
        return (
            f"<ThongKeCapKyThuatTheoTuyen "
            f"tuyen_id={self.tuyen_id} | "
            f"[{self.ma_cap_ky_thuat}] {self.ten_cap_ky_thuat} | "
            f"{self.tong_chieu_dai} km>"
        )


class ChiTietDoanTheoTuyen:
    """Thông tin chi tiết một đoạn (chính hoặc đi chung) thuộc tuyến."""

    def __init__(
        self,
        tuyen_id,
        ma_doan,
        ly_trinh_dau,
        ly_trinh_cuoi,
        chieu_dai,
        ten_cap_ky_thuat,
        ten_tinh_trang,
        loai          # "CHINH" | "DI CHUNG"
    ):
        self.tuyen_id        = tuyen_id
        self.ma_doan         = ma_doan
        self.ly_trinh_dau    = ly_trinh_dau
        self.ly_trinh_cuoi   = ly_trinh_cuoi
        self.chieu_dai       = round(chieu_dai, 3) if chieu_dai else None
        self.ten_cap_ky_thuat = ten_cap_ky_thuat
        self.ten_tinh_trang  = ten_tinh_trang or "Chưa xác định"
        self.loai            = loai

    def __repr__(self):
        return (
            f"<ChiTietDoan {self.ma_doan} | "
            f"Km{self.ly_trinh_dau}→Km{self.ly_trinh_cuoi} | "
            f"{self.chieu_dai} km | {self.loai}>"
        )