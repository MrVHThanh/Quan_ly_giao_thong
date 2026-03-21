"""
Model: DoanTuyen — Đoạn tuyến
Plain object thuần túy. KHÔNG logic nghiệp vụ, KHÔNG gọi DB.

Thay đổi so với phiên bản cũ:
- Thêm 5 trường mới: ket_cau_mat_id, nam_lam_moi, ngay_cap_nhat_tinh_trang,
  updated_at, updated_by_id
- Bỏ hoàn toàn hàm _validate() — chuyển sang doan_tuyen_service.py
"""

from typing import Optional


class DoanTuyen:
    def __init__(
        self,
        id: Optional[int] = None,
        ma_doan: Optional[str] = None,
        tuyen_id: Optional[int] = None,
        cap_duong_id: Optional[int] = None,
        tinh_trang_id: Optional[int] = None,
        ket_cau_mat_id: Optional[int] = None,          # MỚI — FK→ket_cau_mat_duong
        ly_trinh_dau: Optional[float] = None,
        ly_trinh_cuoi: Optional[float] = None,
        chieu_dai_thuc_te: Optional[float] = None,
        chieu_rong_mat_min: Optional[float] = None,
        chieu_rong_mat_max: Optional[float] = None,
        chieu_rong_nen_min: Optional[float] = None,
        chieu_rong_nen_max: Optional[float] = None,
        don_vi_bao_duong_id: Optional[int] = None,
        nam_lam_moi: Optional[int] = None,             # MỚI — năm sửa chữa/nâng cấp gần nhất
        ngay_cap_nhat_tinh_trang: Optional[str] = None, # MỚI — ngày khảo sát tình trạng
        ghi_chu: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,              # MỚI — tự động cập nhật
        updated_by_id: Optional[int] = None,           # MỚI — FK→nguoi_dung
    ):
        self.id = id
        self.ma_doan = ma_doan
        self.tuyen_id = tuyen_id
        self.cap_duong_id = cap_duong_id
        self.tinh_trang_id = tinh_trang_id
        self.ket_cau_mat_id = ket_cau_mat_id
        self.ly_trinh_dau = ly_trinh_dau
        self.ly_trinh_cuoi = ly_trinh_cuoi
        self.chieu_dai_thuc_te = chieu_dai_thuc_te
        self.chieu_rong_mat_min = chieu_rong_mat_min
        self.chieu_rong_mat_max = chieu_rong_mat_max
        self.chieu_rong_nen_min = chieu_rong_nen_min
        self.chieu_rong_nen_max = chieu_rong_nen_max
        self.don_vi_bao_duong_id = don_vi_bao_duong_id
        self.nam_lam_moi = nam_lam_moi
        self.ngay_cap_nhat_tinh_trang = ngay_cap_nhat_tinh_trang
        self.ghi_chu = ghi_chu
        self.created_at = created_at
        self.updated_at = updated_at
        self.updated_by_id = updated_by_id

    @property
    def chieu_dai(self) -> Optional[float]:
        """Chiều dài tính từ lý trình (km). Ưu tiên dùng chieu_dai_thuc_te nếu có."""
        if self.chieu_dai_thuc_te is not None:
            return self.chieu_dai_thuc_te
        if self.ly_trinh_dau is not None and self.ly_trinh_cuoi is not None:
            return round(self.ly_trinh_cuoi - self.ly_trinh_dau, 3)
        return None

    @property
    def chieu_rong_mat_trung_binh(self) -> Optional[float]:
        """Chiều rộng mặt đường trung bình (m)."""
        if self.chieu_rong_mat_min is not None and self.chieu_rong_mat_max is not None:
            return round((self.chieu_rong_mat_min + self.chieu_rong_mat_max) / 2, 2)
        return None

    @property
    def chieu_rong_nen_trung_binh(self) -> Optional[float]:
        """Chiều rộng nền đường trung bình (m)."""
        if self.chieu_rong_nen_min is not None and self.chieu_rong_nen_max is not None:
            return round((self.chieu_rong_nen_min + self.chieu_rong_nen_max) / 2, 2)
        return None

    def __repr__(self) -> str:
        return f"<DoanTuyen id={self.id} ma={self.ma_doan} tuyen_id={self.tuyen_id}>"
