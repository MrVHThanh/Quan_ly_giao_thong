"""
Model: KetCauMatDuong — Kết cấu mặt đường  [MỚI]
Plain object thuần túy. KHÔNG logic nghiệp vụ, KHÔNG gọi DB.

Các mã hợp lệ: BTN, BTXM, HH, LN, CP, DAT, BTN+LN, BTXM+LN
"""

from typing import Optional


class KetCauMatDuong:
    def __init__(
        self,
        id: Optional[int] = None,
        ma_ket_cau: Optional[str] = None,
        ten_ket_cau: Optional[str] = None,
        mo_ta: Optional[str] = None,
        thu_tu_hien_thi: Optional[int] = None,
        is_active: Optional[int] = 1,
    ):
        self.id = id
        self.ma_ket_cau = ma_ket_cau
        self.ten_ket_cau = ten_ket_cau
        self.mo_ta = mo_ta
        self.thu_tu_hien_thi = thu_tu_hien_thi
        self.is_active = is_active

    def __repr__(self) -> str:
        return f"<KetCauMatDuong id={self.id} ma={self.ma_ket_cau} ten={self.ten_ket_cau}>"
