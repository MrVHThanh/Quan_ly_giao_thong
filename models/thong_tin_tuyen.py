"""
Model: ThongTinTuyen — Thông tin mô tả bổ sung của tuyến đường  [MỚI]
Plain object thuần túy. KHÔNG logic nghiệp vụ, KHÔNG gọi DB.

Quan hệ: 1 tuyen_duong → 0..1 thong_tin_tuyen
Hiện có 9/49 tuyến đã có thông tin này. Phần còn lại bổ sung dần qua Web.
"""

from typing import Optional


class ThongTinTuyen:
    def __init__(
        self,
        id: Optional[int] = None,
        tuyen_id: Optional[int] = None,
        mo_ta: Optional[str] = None,
        ly_do_xay_dung: Optional[str] = None,
        dac_diem_dia_ly: Optional[str] = None,
        lich_su_hinh_thanh: Optional[str] = None,
        y_nghia_kinh_te: Optional[str] = None,
        ghi_chu: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.id = id
        self.tuyen_id = tuyen_id
        self.mo_ta = mo_ta
        self.ly_do_xay_dung = ly_do_xay_dung
        self.dac_diem_dia_ly = dac_diem_dia_ly
        self.lich_su_hinh_thanh = lich_su_hinh_thanh
        self.y_nghia_kinh_te = y_nghia_kinh_te
        self.ghi_chu = ghi_chu
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self) -> str:
        return f"<ThongTinTuyen id={self.id} tuyen_id={self.tuyen_id}>"
