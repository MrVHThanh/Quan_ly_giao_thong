class TinhTrang:
    def __init__(
        self,
        id=None,
        ma=None,
        ten=None,
        mo_ta=None,
        mau_hien_thi=None,
        thu_tu_hien_thi=0,
        is_active=1
    ):
        self.id = id
        self.ma = ma
        self.ten = ten
        self.mo_ta = mo_ta
        self.mau_hien_thi = mau_hien_thi
        self.thu_tu_hien_thi = thu_tu_hien_thi
        self.is_active = is_active

    def __repr__(self):
        return f"{self.id}. {self.ten} (Mã: {self.ma}) - Màu: {self.mau_hien_thi}"