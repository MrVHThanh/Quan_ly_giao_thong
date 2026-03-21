"""
Service: ThongTinTuyen — Thông tin mô tả bổ sung của tuyến đường  [MỚI]
Toàn bộ validation + business logic tập trung ở đây.
Quan hệ 1-1 với tuyen_duong: mỗi tuyến có tối đa 1 bản ghi.
"""

import sqlite3
from typing import Optional

import models.thong_tin_tuyen as thong_tin_tuyen_model
import repositories.thong_tin_tuyen_repository as thong_tin_tuyen_repo
import repositories.tuyen_duong_repository as tuyen_duong_repo


class ThongTinTuyenServiceError(Exception):
    pass


def lay_theo_tuyen_id(
    conn: sqlite3.Connection, tuyen_id: int
) -> Optional[thong_tin_tuyen_model.ThongTinTuyen]:
    return thong_tin_tuyen_repo.lay_theo_tuyen_id(conn, tuyen_id)


def lay_theo_id(
    conn: sqlite3.Connection, id: int
) -> thong_tin_tuyen_model.ThongTinTuyen:
    obj = thong_tin_tuyen_repo.lay_theo_id(conn, id)
    if obj is None:
        raise ThongTinTuyenServiceError(f"Không tìm thấy thông tin tuyến id={id}.")
    return obj


def them_hoac_cap_nhat(
    conn: sqlite3.Connection,
    tuyen_id: int,
    mo_ta: Optional[str] = None,
    ly_do_xay_dung: Optional[str] = None,
    dac_diem_dia_ly: Optional[str] = None,
    lich_su_hinh_thanh: Optional[str] = None,
    y_nghia_kinh_te: Optional[str] = None,
    ghi_chu: Optional[str] = None,
) -> thong_tin_tuyen_model.ThongTinTuyen:
    """
    Nếu tuyến chưa có thông tin → INSERT.
    Nếu đã có → UPDATE.
    """
    _validate_tuyen_ton_tai(conn, tuyen_id)

    obj = thong_tin_tuyen_repo.lay_theo_tuyen_id(conn, tuyen_id)
    if obj is None:
        obj = thong_tin_tuyen_model.ThongTinTuyen(
            tuyen_id=tuyen_id,
            mo_ta=mo_ta,
            ly_do_xay_dung=ly_do_xay_dung,
            dac_diem_dia_ly=dac_diem_dia_ly,
            lich_su_hinh_thanh=lich_su_hinh_thanh,
            y_nghia_kinh_te=y_nghia_kinh_te,
            ghi_chu=ghi_chu,
        )
        obj.id = thong_tin_tuyen_repo.them(conn, obj)
    else:
        obj.mo_ta = mo_ta
        obj.ly_do_xay_dung = ly_do_xay_dung
        obj.dac_diem_dia_ly = dac_diem_dia_ly
        obj.lich_su_hinh_thanh = lich_su_hinh_thanh
        obj.y_nghia_kinh_te = y_nghia_kinh_te
        obj.ghi_chu = ghi_chu
        thong_tin_tuyen_repo.sua(conn, obj)
    return obj


def xoa(conn: sqlite3.Connection, tuyen_id: int) -> None:
    obj = thong_tin_tuyen_repo.lay_theo_tuyen_id(conn, tuyen_id)
    if obj is None:
        raise ThongTinTuyenServiceError(
            f"Tuyến id={tuyen_id} chưa có thông tin mô tả để xóa."
        )
    thong_tin_tuyen_repo.xoa(conn, obj.id)


# ── Validation nội bộ ──────────────────────────────────────────────────────

def _validate_tuyen_ton_tai(conn: sqlite3.Connection, tuyen_id: int) -> None:
    if tuyen_duong_repo.lay_theo_id(conn, tuyen_id) is None:
        raise ThongTinTuyenServiceError(f"Tuyến đường id={tuyen_id} không tồn tại.")
