"""
Model: TuyenDuongGeo — Dữ liệu tọa độ GeoJSON theo tuyến  [MỚI - Giai đoạn 1]
Plain object thuần túy. KHÔNG logic nghiệp vụ, KHÔNG gọi DB.

coordinates lưu dạng JSON string: [[lng, lat], [lng, lat], ...]
Tên file nguồn = mã tuyến: QL4E.geojson, DT158.geojson
"""

import json
from typing import Optional, List


class TuyenDuongGeo:
    def __init__(
        self,
        id: Optional[int] = None,
        tuyen_id: Optional[int] = None,
        coordinates: Optional[str] = None,    # JSON string: [[lng,lat],[lng,lat],...]
        so_diem: Optional[int] = None,
        chieu_dai_gps: Optional[float] = None, # km, tính từ tọa độ GPS
        nguon: Optional[str] = None,           # tên file nguồn, VD: QL4E.geojson
        updated_at: Optional[str] = None,
    ):
        self.id = id
        self.tuyen_id = tuyen_id
        self.coordinates = coordinates
        self.so_diem = so_diem
        self.chieu_dai_gps = chieu_dai_gps
        self.nguon = nguon
        self.updated_at = updated_at

    @property
    def coordinates_list(self) -> Optional[List[List[float]]]:
        """Parse coordinates JSON string thành list Python [[lng, lat], ...]."""
        if self.coordinates:
            try:
                return json.loads(self.coordinates)
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    def __repr__(self) -> str:
        return (
            f"<TuyenDuongGeo id={self.id} tuyen_id={self.tuyen_id} "
            f"so_diem={self.so_diem} nguon={self.nguon}>"
        )
