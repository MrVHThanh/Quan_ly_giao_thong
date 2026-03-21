"""
Model: ThongKe — Kết quả thống kê tổng hợp
Plain object thuần túy. KHÔNG logic nghiệp vụ, KHÔNG gọi DB.

Dùng để truyền kết quả thống kê từ Service/Repository lên tầng trên.
Cập nhật: thêm thống kê theo ket_cau_mat_duong.
"""

from typing import Optional, List, Dict


class ThongKeTuyen:
    """Thống kê tổng hợp cho một tuyến đường."""

    def __init__(
        self,
        tuyen_id: Optional[int] = None,
        ma_tuyen: Optional[str] = None,
        ten_tuyen: Optional[str] = None,
        tong_so_doan: Optional[int] = None,
        chieu_dai_quan_ly: Optional[float] = None,
        chieu_dai_thuc_te: Optional[float] = None,
        chieu_dai_di_chung: Optional[float] = None,
        # Theo tình trạng
        chieu_dai_tot: Optional[float] = None,
        chieu_dai_tb: Optional[float] = None,
        chieu_dai_kem: Optional[float] = None,
        chieu_dai_hu_hong_nang: Optional[float] = None,
        chieu_dai_thi_cong: Optional[float] = None,
        # Theo kết cấu mặt
        chieu_dai_btn: Optional[float] = None,
        chieu_dai_btxm: Optional[float] = None,
        chieu_dai_hh: Optional[float] = None,
        chieu_dai_ln: Optional[float] = None,
        chieu_dai_cp: Optional[float] = None,
        chieu_dai_dat: Optional[float] = None,
        chieu_dai_btn_ln: Optional[float] = None,
        chieu_dai_btxm_ln: Optional[float] = None,
    ):
        self.tuyen_id = tuyen_id
        self.ma_tuyen = ma_tuyen
        self.ten_tuyen = ten_tuyen
        self.tong_so_doan = tong_so_doan
        self.chieu_dai_quan_ly = chieu_dai_quan_ly
        self.chieu_dai_thuc_te = chieu_dai_thuc_te
        self.chieu_dai_di_chung = chieu_dai_di_chung
        # Tình trạng
        self.chieu_dai_tot = chieu_dai_tot
        self.chieu_dai_tb = chieu_dai_tb
        self.chieu_dai_kem = chieu_dai_kem
        self.chieu_dai_hu_hong_nang = chieu_dai_hu_hong_nang
        self.chieu_dai_thi_cong = chieu_dai_thi_cong
        # Kết cấu mặt
        self.chieu_dai_btn = chieu_dai_btn
        self.chieu_dai_btxm = chieu_dai_btxm
        self.chieu_dai_hh = chieu_dai_hh
        self.chieu_dai_ln = chieu_dai_ln
        self.chieu_dai_cp = chieu_dai_cp
        self.chieu_dai_dat = chieu_dai_dat
        self.chieu_dai_btn_ln = chieu_dai_btn_ln
        self.chieu_dai_btxm_ln = chieu_dai_btxm_ln

    def __repr__(self) -> str:
        return (
            f"<ThongKeTuyen ma={self.ma_tuyen} "
            f"ql={self.chieu_dai_quan_ly}km tt={self.chieu_dai_thuc_te}km>"
        )


class ThongKeToanTinh:
    """Thống kê tổng hợp toàn tỉnh Lào Cai."""

    def __init__(
        self,
        tong_so_tuyen: Optional[int] = None,
        tong_so_doan: Optional[int] = None,
        tong_so_doan_di_chung: Optional[int] = None,
        tong_chieu_dai_quan_ly: Optional[float] = None,
        tong_chieu_dai_thuc_te: Optional[float] = None,
        tong_chieu_dai_di_chung: Optional[float] = None,
        # Thống kê theo cấp quản lý
        theo_cap_quan_ly: Optional[List[Dict]] = None,
        # Thống kê theo tình trạng
        theo_tinh_trang: Optional[List[Dict]] = None,
        # Thống kê theo kết cấu mặt
        theo_ket_cau_mat: Optional[List[Dict]] = None,
        # Thống kê theo cấp đường
        theo_cap_duong: Optional[List[Dict]] = None,
    ):
        self.tong_so_tuyen = tong_so_tuyen
        self.tong_so_doan = tong_so_doan
        self.tong_so_doan_di_chung = tong_so_doan_di_chung
        self.tong_chieu_dai_quan_ly = tong_chieu_dai_quan_ly
        self.tong_chieu_dai_thuc_te = tong_chieu_dai_thuc_te
        self.tong_chieu_dai_di_chung = tong_chieu_dai_di_chung
        self.theo_cap_quan_ly = theo_cap_quan_ly or []
        self.theo_tinh_trang = theo_tinh_trang or []
        self.theo_ket_cau_mat = theo_ket_cau_mat or []
        self.theo_cap_duong = theo_cap_duong or []

    def __repr__(self) -> str:
        return (
            f"<ThongKeToanTinh tuyen={self.tong_so_tuyen} "
            f"doan={self.tong_so_doan} ql={self.tong_chieu_dai_quan_ly}km>"
        )
