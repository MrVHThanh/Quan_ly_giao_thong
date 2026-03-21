"""
Model: CapDuong — Cấp đường
Plain object thuần túy. KHÔNG logic nghiệp vụ, KHÔNG gọi DB.
"""

from typing import Optional


class CapDuong:
    def __init__(
        self,
        id: Optional[int] = None,
        ma_cap: Optional[str] = None,
        ten_cap: Optional[str] = None,
        mo_ta: Optional[str] = None,
        thu_tu_hien_thi: Optional[int] = None,
        is_active: Optional[int] = 1,
    ):
        self.id = id
        self.ma_cap = ma_cap
        self.ten_cap = ten_cap
        self.mo_ta = mo_ta
        self.thu_tu_hien_thi = thu_tu_hien_thi
        self.is_active = is_active

    def __repr__(self) -> str:
        return f"<CapDuong id={self.id} ma={self.ma_cap} ten={self.ten_cap}>"
