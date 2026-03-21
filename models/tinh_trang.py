"""
Model: TinhTrang — Tình trạng đường
Plain object thuần túy. KHÔNG logic nghiệp vụ, KHÔNG gọi DB.

Các mã hợp lệ: TOT, TB, KEM, HH_NANG, THI_CONG, BAO_TRI, TAM_DONG, NGUNG, CHUA_XD
"""

from typing import Optional


class TinhTrang:
    def __init__(
        self,
        id: Optional[int] = None,
        ma_tinh_trang: Optional[str] = None,
        ten_tinh_trang: Optional[str] = None,
        mo_ta: Optional[str] = None,
        mau_hien_thi: Optional[str] = None,
        thu_tu_hien_thi: Optional[int] = None,
        is_active: Optional[int] = 1,
    ):
        self.id = id
        self.ma_tinh_trang = ma_tinh_trang
        self.ten_tinh_trang = ten_tinh_trang
        self.mo_ta = mo_ta
        self.mau_hien_thi = mau_hien_thi       # Mã màu hex để hiển thị trên bản đồ
        self.thu_tu_hien_thi = thu_tu_hien_thi
        self.is_active = is_active

    def __repr__(self) -> str:
        return f"<TinhTrang id={self.id} ma={self.ma_tinh_trang} ten={self.ten_tinh_trang}>"
