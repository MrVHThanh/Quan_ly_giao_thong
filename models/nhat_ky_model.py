"""models/nhat_ky_model.py — Plain Object cho nhật ký hệ thống."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DangNhapLog:
    ten_dang_nhap: str
    thanh_cong: int = 0
    id: Optional[int] = None
    nguoi_dung_id: Optional[int] = None
    ip_address: Optional[str] = None
    vi_tri: Optional[str] = None
    user_agent: Optional[str] = None
    ghi_chu: Optional[str] = None
    thoi_gian: Optional[str] = None


@dataclass
class NhatKyHoatDong:
    hanh_dong: str
    nguoi_dung_id: Optional[int] = None
    ho_ten: Optional[str] = None
    doi_tuong: Optional[str] = None
    doi_tuong_id: Optional[int] = None
    mo_ta: Optional[str] = None
    ip_address: Optional[str] = None
    id: Optional[int] = None
    thoi_gian: Optional[str] = None
