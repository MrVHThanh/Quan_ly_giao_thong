class CapQuanLy:
    def __init__(
        self,
        id=None,
        ma_cap=None,
        ten_cap=None,
        mo_ta=None,
        thu_tu_hien_thi=0,
        is_active=1
    ):
        self.id = id
        self.ma_cap = ma_cap
        self.ten_cap = ten_cap
        self.mo_ta = mo_ta
        self.thu_tu_hien_thi = thu_tu_hien_thi
        self.is_active = is_active

    def __repr__(self):
        return f"{self.id}. {self.ten_cap} - Mã {self.ma_cap}"