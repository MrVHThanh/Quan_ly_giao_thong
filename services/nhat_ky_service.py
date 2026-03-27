"""services/nhat_ky_service.py — Ghi & truy vấn nhật ký hệ thống."""

import sqlite3
import urllib.request
import urllib.error
import json
import ipaddress
from typing import Optional

import repositories.nhat_ky_repository as nhat_ky_repo
import models.nhat_ky_model as nhat_ky_model


def _tra_vi_tri_ip(ip: str) -> Optional[str]:
    """Tra vị trí địa lý từ IP qua ip-api.com (miễn phí, không cần key).
    IP nội bộ → trả 'Mạng nội bộ'. Lỗi → trả None.
    """
    if not ip:
        return None
    try:
        addr = ipaddress.ip_address(ip)
        if addr.is_private or addr.is_loopback:
            return "Mạng nội bộ"
    except ValueError:
        return None
    try:
        url = f"http://ip-api.com/json/{ip}?lang=vi&fields=status,country,regionName,city,isp"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
        if data.get("status") != "success":
            return None
        parts = [data.get("city"), data.get("regionName"), data.get("country")]
        return ", ".join(p for p in parts if p)
    except Exception:
        return None

# Mapping URL path → (hành động, đối tượng) để tự động mô tả
_ROUTE_MAP = {
    "/tuyen-duong/them":       ("THÊM",    "Tuyến đường"),
    "/tuyen-duong/":           ("SỬA",     "Tuyến đường"),   # /tuyen-duong/{id}/sua
    "/doan-tuyen/them":        ("THÊM",    "Đoạn tuyến"),
    "/doan-tuyen/":            ("SỬA",     "Đoạn tuyến"),
    "/doan-di-chung/them":     ("THÊM",    "Đoạn đi chung"),
    "/doan-di-chung/":         ("SỬA",     "Đoạn đi chung"),
    "/he-thong/nguoi-dung/them": ("THÊM",  "Người dùng"),
    "/he-thong/nguoi-dung/":   ("SỬA",     "Người dùng"),
    "/danh-muc/":              ("SỬA",     "Danh mục"),
}


def ghi_dang_nhap(
    conn: sqlite3.Connection,
    ten_dang_nhap: str,
    thanh_cong: bool,
    nguoi_dung_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    ghi_chu: Optional[str] = None,
) -> None:
    """Ghi log mỗi lần đăng nhập (thành công hoặc thất bại)."""
    try:
        vi_tri = _tra_vi_tri_ip(ip_address)
        nhat_ky_repo.ghi_dang_nhap(
            conn,
            ten_dang_nhap=ten_dang_nhap,
            thanh_cong=1 if thanh_cong else 0,
            nguoi_dung_id=nguoi_dung_id,
            ip_address=ip_address,
            vi_tri=vi_tri,
            user_agent=user_agent,
            ghi_chu=ghi_chu,
        )
    except Exception:
        pass  # Không để lỗi log ảnh hưởng luồng chính


def ghi_hoat_dong(
    conn: sqlite3.Connection,
    hanh_dong: str,
    nguoi_dung_id: Optional[int] = None,
    ho_ten: Optional[str] = None,
    doi_tuong: Optional[str] = None,
    doi_tuong_id: Optional[int] = None,
    mo_ta: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> None:
    """Ghi log một thao tác của người dùng."""
    try:
        nhat_ky_repo.ghi_hoat_dong(
            conn,
            hanh_dong=hanh_dong,
            nguoi_dung_id=nguoi_dung_id,
            ho_ten=ho_ten,
            doi_tuong=doi_tuong,
            doi_tuong_id=doi_tuong_id,
            mo_ta=mo_ta,
            ip_address=ip_address,
        )
    except Exception:
        pass


def tu_dong_ghi_hoat_dong(
    conn: sqlite3.Connection,
    method: str,
    path: str,
    user: Optional[dict],
    ip_address: Optional[str],
) -> None:
    """Tự động ghi log dựa vào method + path URL.
    Gọi từ middleware sau mỗi POST thành công.
    """
    if method != "POST":
        return

    hanh_dong = "THAO TÁC"
    doi_tuong = None

    # Xác định hành động từ URL path
    if path.endswith("/them"):
        hanh_dong = "THÊM"
    elif path.endswith("/sua"):
        hanh_dong = "SỬA"
    elif path.endswith("/xoa"):
        hanh_dong = "XÓA"
    elif path.endswith("/doi-mk"):
        hanh_dong = "ĐỔI MẬT KHẨU"
    elif path.endswith("/duyet"):
        hanh_dong = "DUYỆT"
    elif path.endswith("/khoi-phuc"):
        hanh_dong = "KHÔI PHỤC"
    elif "/dang-ky" in path:
        hanh_dong = "ĐĂNG KÝ"

    # Xác định đối tượng từ URL path
    if "/tuyen-duong" in path:
        doi_tuong = "Tuyến đường"
    elif "/doan-di-chung" in path:
        doi_tuong = "Đoạn đi chung"
    elif "/doan-tuyen" in path:
        doi_tuong = "Đoạn tuyến"
    elif "/nguoi-dung" in path:
        doi_tuong = "Người dùng"
    elif "/danh-muc" in path:
        doi_tuong = "Danh mục"
    elif "/ban-do" in path:
        doi_tuong = "Bản đồ"
    elif "/auth" in path:
        return  # Đăng nhập/đăng xuất đã log riêng

    nguoi_dung_id = user.get("id") if user else None
    ho_ten = user.get("ho_ten") if user else None

    ghi_hoat_dong(
        conn,
        hanh_dong=hanh_dong,
        nguoi_dung_id=nguoi_dung_id,
        ho_ten=ho_ten,
        doi_tuong=doi_tuong,
        mo_ta=path,
        ip_address=ip_address,
    )


def lay_dang_nhap_log(
    conn: sqlite3.Connection,
    limit: int = 200,
) -> list[nhat_ky_model.DangNhapLog]:
    return nhat_ky_repo.lay_dang_nhap_log(conn, limit=limit)


def lay_nhat_ky(
    conn: sqlite3.Connection,
    limit: int = 200,
) -> list[nhat_ky_model.NhatKyHoatDong]:
    return nhat_ky_repo.lay_nhat_ky(conn, limit=limit)
