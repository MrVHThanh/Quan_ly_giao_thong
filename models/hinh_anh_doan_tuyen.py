"""
Model: HinhAnhDoanTuyen — Hình ảnh hiện trạng đoạn tuyến  [MỚI]
Plain object thuần túy. KHÔNG logic nghiệp vụ, KHÔNG gọi DB.

Tọa độ lat/lng trích từ EXIF ảnh (NULL nếu ảnh không có GPS).
ly_trinh_anh tính từ lat/lng + đường tâm tuyến (Giai đoạn 2 — hiện để NULL).
"""

from typing import Optional


class HinhAnhDoanTuyen:
    def __init__(
        self,
        id: Optional[int] = None,
        doan_id: Optional[int] = None,
        duong_dan_file: Optional[str] = None,
        mo_ta: Optional[str] = None,
        ngay_chup: Optional[str] = None,
        nguoi_chup: Optional[str] = None,
        lat: Optional[float] = None,           # tọa độ trích từ EXIF (NULL nếu không có)
        lng: Optional[float] = None,           # tọa độ trích từ EXIF (NULL nếu không có)
        ly_trinh_anh: Optional[float] = None,  # tính từ lat/lng + đường tâm (Giai đoạn 2)
        created_at: Optional[str] = None,
    ):
        self.id = id
        self.doan_id = doan_id
        self.duong_dan_file = duong_dan_file
        self.mo_ta = mo_ta
        self.ngay_chup = ngay_chup
        self.nguoi_chup = nguoi_chup
        self.lat = lat
        self.lng = lng
        self.ly_trinh_anh = ly_trinh_anh
        self.created_at = created_at

    @property
    def co_toa_do_gps(self) -> bool:
        """Ảnh có tọa độ GPS hợp lệ."""
        return self.lat is not None and self.lng is not None

    def __repr__(self) -> str:
        return f"<HinhAnhDoanTuyen id={self.id} doan_id={self.doan_id} file={self.duong_dan_file}>"
