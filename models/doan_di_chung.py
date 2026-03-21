"""
Model: DoanDiChung — Đoạn đi chung giữa các tuyến
Plain object thuần túy. KHÔNG logic nghiệp vụ, KHÔNG gọi DB.

Cấu trúc mới hoàn toàn:
- Mỗi bản ghi tham chiếu đúng 1 đoạn vật lý (doan_id)
- Nếu đoạn đi chung vắt qua nhiều đoạn vật lý → tách thành nhiều bản ghi riêng
- Lưu lý trình 2 chiều: theo tuyến đi nhờ VÀ theo tuyến chủ
- chieu_dai_di_chung KHÔNG lưu — tính từ ly_trinh_cuoi - ly_trinh_dau

Ví dụ mã: DDC-DT159-QL4E-01-001
  → DT159 đi nhờ trên đoạn QL4E-01 (đoạn vật lý số 001)
"""

from typing import Optional


class DoanDiChung:
    def __init__(
        self,
        id: Optional[int] = None,
        ma_doan_di_chung: Optional[str] = None,          # VD: DDC-DT159-QL4E-01-001
        tuyen_di_chung_id: Optional[int] = None,         # FK→tuyen_duong (tuyến đi nhờ: DT159)
        tuyen_chinh_id: Optional[int] = None,            # FK→tuyen_duong (tuyến chủ: QL4E)
        doan_id: Optional[int] = None,                   # FK→doan_tuyen (đoạn vật lý: QL4E-01)
        ly_trinh_dau_di_chung: Optional[float] = None,   # lý trình theo tuyến đi nhờ
        ly_trinh_cuoi_di_chung: Optional[float] = None,  # lý trình theo tuyến đi nhờ
        ly_trinh_dau_tuyen_chinh: Optional[float] = None, # lý trình theo tuyến chủ
        ly_trinh_cuoi_tuyen_chinh: Optional[float] = None, # lý trình theo tuyến chủ
        ghi_chu: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        self.id = id
        self.ma_doan_di_chung = ma_doan_di_chung
        self.tuyen_di_chung_id = tuyen_di_chung_id
        self.tuyen_chinh_id = tuyen_chinh_id
        self.doan_id = doan_id
        self.ly_trinh_dau_di_chung = ly_trinh_dau_di_chung
        self.ly_trinh_cuoi_di_chung = ly_trinh_cuoi_di_chung
        self.ly_trinh_dau_tuyen_chinh = ly_trinh_dau_tuyen_chinh
        self.ly_trinh_cuoi_tuyen_chinh = ly_trinh_cuoi_tuyen_chinh
        self.ghi_chu = ghi_chu
        self.created_at = created_at

    @property
    def chieu_dai_di_chung(self) -> Optional[float]:
        """Chiều dài đoạn đi chung theo tuyến đi nhờ (km)."""
        if self.ly_trinh_dau_di_chung is not None and self.ly_trinh_cuoi_di_chung is not None:
            return round(self.ly_trinh_cuoi_di_chung - self.ly_trinh_dau_di_chung, 3)
        return None

    @property
    def chieu_dai_tuyen_chinh(self) -> Optional[float]:
        """Chiều dài đoạn đi chung theo tuyến chủ (km)."""
        if self.ly_trinh_dau_tuyen_chinh is not None and self.ly_trinh_cuoi_tuyen_chinh is not None:
            return round(self.ly_trinh_cuoi_tuyen_chinh - self.ly_trinh_dau_tuyen_chinh, 3)
        return None

    def __repr__(self) -> str:
        return (
            f"<DoanDiChung id={self.id} ma={self.ma_doan_di_chung} "
            f"tuyen_di_chung_id={self.tuyen_di_chung_id} doan_id={self.doan_id}>"
        )
