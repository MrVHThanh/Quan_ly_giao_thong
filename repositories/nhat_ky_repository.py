"""repositories/nhat_ky_repository.py — SQL nhật ký đăng nhập & hoạt động."""

import sqlite3
from typing import Optional
import models.nhat_ky_model as nhat_ky_model


# ── ĐĂNG NHẬP LOG ────────────────────────────────────────────────────────────

def ghi_dang_nhap(
    conn: sqlite3.Connection,
    ten_dang_nhap: str,
    thanh_cong: int,
    nguoi_dung_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    vi_tri: Optional[str] = None,
    user_agent: Optional[str] = None,
    ghi_chu: Optional[str] = None,
) -> None:
    conn.execute(
        """INSERT INTO dang_nhap_log
           (ten_dang_nhap, nguoi_dung_id, ip_address, vi_tri, user_agent, thanh_cong, ghi_chu)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (ten_dang_nhap, nguoi_dung_id, ip_address, vi_tri, user_agent, thanh_cong, ghi_chu),
    )
    conn.commit()


def lay_dang_nhap_log(
    conn: sqlite3.Connection,
    limit: int = 200,
) -> list[nhat_ky_model.DangNhapLog]:
    rows = conn.execute(
        """SELECT id, ten_dang_nhap, nguoi_dung_id, ip_address, vi_tri,
                  user_agent, thanh_cong, ghi_chu, thoi_gian
           FROM dang_nhap_log
           ORDER BY thoi_gian DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    return [_row_to_dang_nhap(r) for r in rows]


def _row_to_dang_nhap(row) -> nhat_ky_model.DangNhapLog:
    obj = nhat_ky_model.DangNhapLog(ten_dang_nhap=row["ten_dang_nhap"])
    obj.id             = row["id"]
    obj.nguoi_dung_id  = row["nguoi_dung_id"]
    obj.ip_address     = row["ip_address"]
    obj.vi_tri         = row["vi_tri"]
    obj.user_agent     = row["user_agent"]
    obj.thanh_cong     = row["thanh_cong"]
    obj.ghi_chu        = row["ghi_chu"]
    obj.thoi_gian      = row["thoi_gian"]
    return obj


# ── NHẬT KÝ HOẠT ĐỘNG ────────────────────────────────────────────────────────

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
    conn.execute(
        """INSERT INTO nhat_ky_hoat_dong
           (nguoi_dung_id, ho_ten, hanh_dong, doi_tuong, doi_tuong_id, mo_ta, ip_address)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (nguoi_dung_id, ho_ten, hanh_dong, doi_tuong, doi_tuong_id, mo_ta, ip_address),
    )
    conn.commit()


def lay_nhat_ky(
    conn: sqlite3.Connection,
    limit: int = 200,
) -> list[nhat_ky_model.NhatKyHoatDong]:
    rows = conn.execute(
        """SELECT id, nguoi_dung_id, ho_ten, hanh_dong, doi_tuong,
                  doi_tuong_id, mo_ta, ip_address, thoi_gian
           FROM nhat_ky_hoat_dong
           ORDER BY thoi_gian DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    return [_row_to_nhat_ky(r) for r in rows]


def _row_to_nhat_ky(row) -> nhat_ky_model.NhatKyHoatDong:
    obj = nhat_ky_model.NhatKyHoatDong(hanh_dong=row["hanh_dong"])
    obj.id            = row["id"]
    obj.nguoi_dung_id = row["nguoi_dung_id"]
    obj.ho_ten        = row["ho_ten"]
    obj.doi_tuong     = row["doi_tuong"]
    obj.doi_tuong_id  = row["doi_tuong_id"]
    obj.mo_ta         = row["mo_ta"]
    obj.ip_address    = row["ip_address"]
    obj.thoi_gian     = row["thoi_gian"]
    return obj
