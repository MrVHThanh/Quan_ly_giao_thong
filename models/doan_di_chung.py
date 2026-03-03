class DoanDiChung:
    """
    Đoạn đi chung: một đoạn vật lý thuộc tuyến chủ sở hữu,
    nhưng được một tuyến khác đi chung với lý trình riêng.

    Ví dụ:
        doan_id = đoạn 3 (thuộc QL4D)
        tuyen_id = QL279 (tuyến đi chung)
        ly_trinh_dau/cuoi = lý trình theo QL279
    """

    def __init__(
        self,
        tuyen_id,
        doan_id,
        ly_trinh_dau,
        ly_trinh_cuoi,
        ghi_chu=None,
        id=None,
        created_at=None
    ):
        self.id = id
        self.tuyen_id = tuyen_id
        self.doan_id = doan_id
        self.ly_trinh_dau = ly_trinh_dau
        self.ly_trinh_cuoi = ly_trinh_cuoi
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

    # ==========================
    # HIỂN THỊ
    # ==========================

    def __repr__(self):
        return (
            f"<DoanDiChung tuyen_id={self.tuyen_id} | "
            f"doan_id={self.doan_id} | "
            f"Km{self.ly_trinh_dau}→Km{self.ly_trinh_cuoi} | "
            f"{self.chieu_dai} km>"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "tuyen_id": self.tuyen_id,
            "doan_id": self.doan_id,
            "ly_trinh_dau": self.ly_trinh_dau,
            "ly_trinh_cuoi": self.ly_trinh_cuoi,
            "chieu_dai": self.chieu_dai,
            "ghi_chu": self.ghi_chu,
            "created_at": self.created_at
        }