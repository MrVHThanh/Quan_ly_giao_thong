class DoanTuyen:
    def __init__(
        self,
        id=None,
        ma_doan=None,
        tuyen_id=None,
        cap_duong_id=None,
        ly_trinh_dau=None,
        ly_trinh_cuoi=None,
        tinh_trang_id=None,
        chieu_dai_thuc_te=None,
        chieu_rong_mat_max=None,
        chieu_rong_mat_min=None,
        chieu_rong_nen_max=None,
        chieu_rong_nen_min=None,
        don_vi_bao_duong_id=None,
        ghi_chu=None,
        created_at=None
    ):
        self.id = id
        self.ma_doan = ma_doan
        self.tuyen_id = tuyen_id
        self.cap_duong_id = cap_duong_id
        self.ly_trinh_dau = ly_trinh_dau
        self.ly_trinh_cuoi = ly_trinh_cuoi
        self.tinh_trang_id = tinh_trang_id
        self.chieu_dai_thuc_te = chieu_dai_thuc_te
        self.chieu_rong_mat_max = chieu_rong_mat_max
        self.chieu_rong_mat_min = chieu_rong_mat_min
        self.chieu_rong_nen_max = chieu_rong_nen_max
        self.chieu_rong_nen_min = chieu_rong_nen_min
        self.don_vi_bao_duong_id = don_vi_bao_duong_id
        self.ghi_chu = ghi_chu
        self.created_at = created_at

        self._validate()

    # ==========================
    # PROPERTY CHIỀU DÀI
    # ==========================

    @property
    def chieu_dai(self):
        if self.ly_trinh_dau is None or self.ly_trinh_cuoi is None:
            return None
        return self.ly_trinh_cuoi - self.ly_trinh_dau

    @property
    def chieu_dai_tinh(self):
        return self.chieu_dai_thuc_te or self.chieu_dai

    # ==========================
    # VALIDATION
    # ==========================

    def _validate(self):
        if (
            self.ly_trinh_dau is not None
            and self.ly_trinh_cuoi is not None
        ):
            if self.ly_trinh_cuoi <= self.ly_trinh_dau:
                raise ValueError("Ly trinh cuoi phai lon hon ly trinh dau.")

        if (
            self.chieu_rong_mat_max is not None
            and self.chieu_rong_mat_min is not None
        ):
            if self.chieu_rong_mat_max < self.chieu_rong_mat_min:
                raise ValueError("Rong mat max phai >= rong mat min.")

        if (
            self.chieu_rong_nen_max is not None
            and self.chieu_rong_nen_min is not None
        ):
            if self.chieu_rong_nen_max < self.chieu_rong_nen_min:
                raise ValueError("Rong nen max phai >= rong nen min.")

    # ==========================
    # HIỂN THỊ
    # ==========================

    def __repr__(self):
        return (
            f"<DoanTuyen {self.ma_doan} | "
            f"{self.ly_trinh_dau}-{self.ly_trinh_cuoi} | "
            f"{self.chieu_dai_tinh:.2f} km>"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "ma_doan": self.ma_doan,
            "tuyen_id": self.tuyen_id,
            "cap_duong_id": self.cap_duong_id,
            "ly_trinh_dau": self.ly_trinh_dau,
            "ly_trinh_cuoi": self.ly_trinh_cuoi,
            "tinh_trang_id": self.tinh_trang_id,
            "chieu_rong_mat_max": self.chieu_rong_mat_max,
            "chieu_rong_mat_min": self.chieu_rong_mat_min,
            "chieu_rong_nen_max": self.chieu_rong_nen_max,
            "chieu_rong_nen_min": self.chieu_rong_nen_min,
            "don_vi_bao_duong_id": self.don_vi_bao_duong_id,
            "ghi_chu": self.ghi_chu
        }