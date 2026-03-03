class DonVi:
    def __init__(
        self,
        id=None,
        ma_don_vi=None,
        ten_don_vi=None,
        loai=None,
        parent_id=None,
        is_active=1,
        created_at=None
    ):
        self.id = id
        self.ma_don_vi = ma_don_vi
        self.ten_don_vi = ten_don_vi
        self.loai = loai
        self.parent_id = parent_id
        self.is_active = is_active
        self.created_at = created_at

    def __repr__(self):
        return f"<DonVi {self.id} - {self.ten_don_vi} - Mã {self.ma_don_vi}>"