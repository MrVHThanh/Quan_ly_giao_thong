class TuyenDuong:
    def __init__(
        self,
        id=None,
        ma_tuyen=None,
        ten_tuyen=None,
        cap_quan_ly_id=None,
        don_vi_quan_ly_id=None,
        diem_dau=None,
        diem_cuoi=None,
        lat_dau=None,
        lng_dau=None,
        lat_cuoi=None,
        lng_cuoi=None,
        chieu_dai_thuc_te=None,
        chieu_dai_quan_ly=None,
        nam_xay_dung=None,
        nam_hoan_thanh=None,
        tinh_trang_id=None,
        ghi_chu=None,
        created_at=None
    ):
        self.id = id
        self.ma_tuyen = ma_tuyen
        self.ten_tuyen = ten_tuyen
        self.cap_quan_ly_id = cap_quan_ly_id
        self.don_vi_quan_ly_id = don_vi_quan_ly_id
        self.diem_dau = diem_dau
        self.diem_cuoi = diem_cuoi
        self.lat_dau = lat_dau
        self.lng_dau = lng_dau
        self.lat_cuoi = lat_cuoi
        self.lng_cuoi = lng_cuoi
        self.chieu_dai_thuc_te = chieu_dai_thuc_te     # tổng quãng đường (kể đoạn đi chung)
        self.chieu_dai_quan_ly = chieu_dai_quan_ly     # chỉ đoạn chính (phục vụ bảo trì)
        self.nam_xay_dung = nam_xay_dung
        self.nam_hoan_thanh = nam_hoan_thanh
        self.tinh_trang_id = tinh_trang_id
        self.ghi_chu = ghi_chu
        self.created_at = created_at

    # ==========================
    # PROPERTY TỌA ĐỘ
    # ==========================

    @property
    def toa_do_dau(self):
        if self.lat_dau is None or self.lng_dau is None:
            return None
        return [self.lat_dau, self.lng_dau]

    @property
    def toa_do_cuoi(self):
        if self.lat_cuoi is None or self.lng_cuoi is None:
            return None
        return [self.lat_cuoi, self.lng_cuoi]

    # ==========================
    # HIỂN THỊ
    # ==========================

    def __repr__(self):
        thuc_te_str  = f"{self.chieu_dai_thuc_te:.2f}km"  if self.chieu_dai_thuc_te  else "N/A"
        quan_ly_str  = f"{self.chieu_dai_quan_ly:.2f}km"  if self.chieu_dai_quan_ly  else "N/A"
        return (
            f"{self.id}. {self.ma_tuyen} - {self.ten_tuyen} "
            f"| Thực tế: {thuc_te_str} | Quản lý: {quan_ly_str} "
            f"| {self.diem_dau or '?'} → {self.diem_cuoi or '?'}"
        )