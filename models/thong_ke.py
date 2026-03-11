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