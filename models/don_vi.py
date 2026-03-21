"""
Model: DonVi — Đơn vị quản lý / bảo dưỡng
Plain object thuần túy. KHÔNG logic nghiệp vụ, KHÔNG gọi DB.

Cây cha-con: TINH → SXD → BAN_BT, và 13 Công ty con (parent_id = NULL)
"""

from typing import Optional


class DonVi:
    def __init__(
        self,
        id: Optional[int] = None,
        ma_don_vi: Optional[str] = None,
        ten_don_vi: Optional[str] = None,
        ten_viet_tat: Optional[str] = None,
        parent_id: Optional[int] = None,
        cap_don_vi: Optional[str] = None,
        dia_chi: Optional[str] = None,
        so_dien_thoai: Optional[str] = None,
        email: Optional[str] = None,
        is_active: Optional[int] = 1,
        created_at: Optional[str] = None,
    ):
        self.id = id
        self.ma_don_vi = ma_don_vi
        self.ten_don_vi = ten_don_vi
        self.ten_viet_tat = ten_viet_tat
        self.parent_id = parent_id
        self.cap_don_vi = cap_don_vi
        self.dia_chi = dia_chi
        self.so_dien_thoai = so_dien_thoai
        self.email = email
        self.is_active = is_active
        self.created_at = created_at

    @property
    def la_don_vi_goc(self) -> bool:
        """Trả về True nếu đây là đơn vị gốc (không có cha)."""
        return self.parent_id is None

    def __repr__(self) -> str:
        return f"<DonVi id={self.id} ma={self.ma_don_vi} ten={self.ten_don_vi}>"
