"""
Service: ThongKe — Thống kê tổng hợp
Toàn bộ business logic tập trung ở đây.
Chuyển kết quả dict thô từ Repository sang Model ThongKe.
Cập nhật: bổ sung thống kê theo ket_cau_mat_duong.
"""

import sqlite3
from typing import List

import models.thong_ke as thong_ke_model
import repositories.thong_ke_repository as thong_ke_repo


def lay_thong_ke_toan_tinh(conn: sqlite3.Connection) -> thong_ke_model.ThongKeToanTinh:
    """Thống kê tổng hợp toàn tỉnh Lào Cai."""
    tong_hop = thong_ke_repo.thong_ke_toan_tinh(conn)
    theo_cap = thong_ke_repo.thong_ke_theo_cap_quan_ly(conn)
    theo_tt = thong_ke_repo.thong_ke_theo_tinh_trang(conn)
    theo_kcm = thong_ke_repo.thong_ke_theo_ket_cau_mat(conn)
    theo_cd = thong_ke_repo.thong_ke_theo_cap_duong(conn)

    chieu_dai_tt = tong_hop.get("tong_chieu_dai_thuc_te") or 0
    chieu_dai_ql = tong_hop.get("tong_chieu_dai_quan_ly") or 0

    return thong_ke_model.ThongKeToanTinh(
        tong_so_tuyen=tong_hop.get("tong_so_tuyen"),
        tong_so_doan=tong_hop.get("tong_so_doan"),
        tong_so_doan_di_chung=tong_hop.get("tong_so_doan_di_chung"),
        tong_chieu_dai_quan_ly=chieu_dai_ql,
        tong_chieu_dai_thuc_te=chieu_dai_tt,
        tong_chieu_dai_di_chung=round(chieu_dai_tt - chieu_dai_ql, 3),
        theo_cap_quan_ly=theo_cap,
        theo_tinh_trang=theo_tt,
        theo_ket_cau_mat=theo_kcm,
        theo_cap_duong=theo_cd,
    )


def lay_thong_ke_mot_tuyen(
    conn: sqlite3.Connection, tuyen_id: int
) -> thong_ke_model.ThongKeTuyen:
    """Thống kê chi tiết cho một tuyến: theo tình trạng và kết cấu mặt."""
    raw = thong_ke_repo.thong_ke_mot_tuyen(conn, tuyen_id)
    tong = raw.get("tong_hop", {})
    theo_tt = {r["ma_tinh_trang"]: r["chieu_dai"] for r in raw.get("theo_tinh_trang", [])}
    theo_kcm = {r["ma_ket_cau"]: r["chieu_dai"] for r in raw.get("theo_ket_cau_mat", [])}

    return thong_ke_model.ThongKeTuyen(
        tuyen_id=tuyen_id,
        ma_tuyen=tong.get("ma_tuyen"),
        ten_tuyen=tong.get("ten_tuyen"),
        tong_so_doan=tong.get("tong_so_doan"),
        chieu_dai_quan_ly=tong.get("chieu_dai_quan_ly"),
        chieu_dai_thuc_te=tong.get("chieu_dai_thuc_te"),
        # Tình trạng
        chieu_dai_tot=theo_tt.get("TOT"),
        chieu_dai_tb=theo_tt.get("TB"),
        chieu_dai_kem=theo_tt.get("KEM"),
        chieu_dai_hu_hong_nang=theo_tt.get("HH_NANG"),
        chieu_dai_thi_cong=theo_tt.get("THI_CONG"),
        # Kết cấu mặt
        chieu_dai_btn=theo_kcm.get("BTN"),
        chieu_dai_btxm=theo_kcm.get("BTXM"),
        chieu_dai_hh=theo_kcm.get("HH"),
        chieu_dai_ln=theo_kcm.get("LN"),
        chieu_dai_cp=theo_kcm.get("CP"),
        chieu_dai_dat=theo_kcm.get("DAT"),
        chieu_dai_btn_ln=theo_kcm.get("BTN+LN"),
        chieu_dai_btxm_ln=theo_kcm.get("BTXM+LN"),
    )


def lay_thong_ke_tat_ca_tuyen(
    conn: sqlite3.Connection,
) -> List[thong_ke_model.ThongKeTuyen]:
    """Thống kê chi tiết cho từng tuyến (dùng cho bảng tổng hợp toàn tỉnh)."""
    theo_cap = thong_ke_repo.thong_ke_theo_cap_quan_ly(conn)
    danh_sach_tuyen_id: List[int] = []

    # Lấy danh sách tuyen_id từ bảng thống kê theo cap_quan_ly
    from repositories.tuyen_duong_repository import lay_tat_ca
    tat_ca = lay_tat_ca(conn)
    return [lay_thong_ke_mot_tuyen(conn, t.id) for t in tat_ca]


def lay_thong_ke_theo_don_vi_bao_duong(conn: sqlite3.Connection) -> List[dict]:
    return thong_ke_repo.thong_ke_theo_don_vi_bao_duong(conn)


def lay_thong_ke_theo_ket_cau_mat(conn: sqlite3.Connection) -> List[dict]:
    return thong_ke_repo.thong_ke_theo_ket_cau_mat(conn)


def lay_thong_ke_theo_tinh_trang(conn: sqlite3.Connection) -> List[dict]:
    return thong_ke_repo.thong_ke_theo_tinh_trang(conn)
