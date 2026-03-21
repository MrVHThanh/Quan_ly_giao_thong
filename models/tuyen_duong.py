"""
Model: TuyenDuong — Tuyến đường
Plain object thuần túy. KHÔNG logic nghiệp vụ, KHÔNG gọi DB.

Lưu ý thiết kế:
- KHÔNG có cột chieu_dai — chỉ có chieu_dai_thuc_te và chieu_dai_quan_ly
- Chiều dài được SQLite trigger tự động cập nhật khi thêm/sửa/xóa doan_tuyen và doan_di_chung
- KHÔNG gọi cap_nhat_chieu_dai thủ công
"""

from typing import Optional


class TuyenDuong:
    def __init__(
        self,
        id: Optional[int] = None,
        ma_tuyen: Optional[str] = None,
        ten_tuyen: Optional[str] = None,
        cap_quan_ly_id: Optional[int] = None,
        don_vi_quan_ly_id: Optional[int] = None,
        diem_dau: Optional[str] = None,
        diem_cuoi: Optional[str] = None,
        lat_dau: Optional[float] = None,
        lng_dau: Optional[float] = None,
        lat_cuoi: Optional[float] = None,
        lng_cuoi: Optional[float] = None,
        chieu_dai_thuc_te: Optional[float] = None,   # tổng đoạn chính + đoạn đi chung (trigger)
        chieu_dai_quan_ly: Optional[float] = None,   # chỉ tổng đoạn chính (trigger)
        nam_xay_dung: Optional[int] = None,
        nam_hoan_thanh: Optional[int] = None,
        ghi_chu: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        self.id = id
        self.ma_tuyen = ma_tuyen
        self.ten_tuyen = ten_tuyen
        self.cap_quan_ly_id = cap_quan_ly_id
        self.don_vi_quan_ly_id = don_vi_quan_ly_id
        self.diem_dau = diem_dau
        self.diem_cuoi = diem_cuoi
        self.lat_dau = lat_dau
        self.lng_dau = lng_dau
        self.lat_cuoi = lat_cuoi
        self.lng_cuoi = lng_cuoi
        self.chieu_dai_thuc_te = chieu_dai_thuc_te
        self.chieu_dai_quan_ly = chieu_dai_quan_ly
        self.nam_xay_dung = nam_xay_dung
        self.nam_hoan_thanh = nam_hoan_thanh
        self.ghi_chu = ghi_chu
        self.created_at = created_at

    @property
    def chieu_dai_di_chung(self) -> Optional[float]:
        """Tổng chiều dài đoạn đi chung (= thực tế - quản lý)."""
        if self.chieu_dai_thuc_te is not None and self.chieu_dai_quan_ly is not None:
            return round(self.chieu_dai_thuc_te - self.chieu_dai_quan_ly, 3)
        return None

    def __repr__(self) -> str:
        return f"<TuyenDuong id={self.id} ma={self.ma_tuyen} ten={self.ten_tuyen}>"
