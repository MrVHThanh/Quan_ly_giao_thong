"""
Service: DoanTuyen — Đoạn tuyến
Toàn bộ validation + business logic tập trung ở đây.
Validation đã được chuyển ra khỏi model hoàn toàn.
"""

import sqlite3
from typing import Optional, List

import models.doan_tuyen as doan_tuyen_model
import repositories.doan_tuyen_repository as doan_tuyen_repo
import repositories.tuyen_duong_repository as tuyen_duong_repo


class DoanTuyenServiceError(Exception):
    pass


def lay_theo_tuyen_id(
    conn: sqlite3.Connection, tuyen_id: int
) -> List[doan_tuyen_model.DoanTuyen]:
    return doan_tuyen_repo.lay_theo_tuyen_id(conn, tuyen_id)


def lay_theo_id(conn: sqlite3.Connection, id: int) -> doan_tuyen_model.DoanTuyen:
    obj = doan_tuyen_repo.lay_theo_id(conn, id)
    if obj is None:
        raise DoanTuyenServiceError(f"Không tìm thấy đoạn tuyến id={id}.")
    return obj


def lay_theo_ma(conn: sqlite3.Connection, ma_doan: str) -> doan_tuyen_model.DoanTuyen:
    obj = doan_tuyen_repo.lay_theo_ma(conn, ma_doan)
    if obj is None:
        raise DoanTuyenServiceError(f"Không tìm thấy đoạn tuyến mã '{ma_doan}'.")
    return obj


def lay_theo_tinh_trang(
    conn: sqlite3.Connection, tinh_trang_id: int
) -> List[doan_tuyen_model.DoanTuyen]:
    return doan_tuyen_repo.lay_theo_tinh_trang(conn, tinh_trang_id)


def lay_theo_ket_cau_mat(
    conn: sqlite3.Connection, ket_cau_mat_id: int
) -> List[doan_tuyen_model.DoanTuyen]:
    return doan_tuyen_repo.lay_theo_ket_cau_mat(conn, ket_cau_mat_id)


def lay_co_loc(
    conn: sqlite3.Connection,
    tuyen_id:       Optional[int] = None,
    tinh_trang_id:  Optional[int] = None,
    cap_duong_id:   Optional[int] = None,
    ket_cau_mat_id: Optional[int] = None,
) -> List[doan_tuyen_model.DoanTuyen]:
    """
    Lọc kết hợp nhiều tiêu chí (AND).
    Truyền None cho tiêu chí nào để bỏ qua tiêu chí đó.
    Không có tiêu chí nào → trả về toàn bộ danh sách.
    Được gọi từ router thay cho chuỗi if/elif riêng lẻ.
    """
    return doan_tuyen_repo.lay_co_loc(
        conn,
        tuyen_id=tuyen_id,
        tinh_trang_id=tinh_trang_id,
        cap_duong_id=cap_duong_id,
        ket_cau_mat_id=ket_cau_mat_id,
    )


def them(
    conn: sqlite3.Connection,
    ma_doan: str,
    tuyen_id: int,
    cap_duong_id: int,
    tinh_trang_id: int,
    ly_trinh_dau: float,
    ly_trinh_cuoi: float,
    ket_cau_mat_id: Optional[int] = None,
    chieu_dai_thuc_te: Optional[float] = None,
    chieu_rong_mat_min: Optional[float] = None,
    chieu_rong_mat_max: Optional[float] = None,
    chieu_rong_nen_min: Optional[float] = None,
    chieu_rong_nen_max: Optional[float] = None,
    don_vi_bao_duong_id: Optional[int] = None,
    nam_lam_moi: Optional[int] = None,
    ngay_cap_nhat_tinh_trang: Optional[str] = None,
    ghi_chu: Optional[str] = None,
    updated_by_id: Optional[int] = None,
) -> doan_tuyen_model.DoanTuyen:
    _validate_ma(ma_doan)
    _validate_tuyen_ton_tai(conn, tuyen_id)
    _validate_ly_trinh(ly_trinh_dau, ly_trinh_cuoi)
    _validate_chieu_rong(chieu_rong_mat_min, chieu_rong_mat_max, "mặt")
    _validate_chieu_rong(chieu_rong_nen_min, chieu_rong_nen_max, "nền")
    _validate_nam_lam_moi(nam_lam_moi)
    _kiem_tra_ma_doan_trung(conn, ma_doan)

    obj = doan_tuyen_model.DoanTuyen(
        ma_doan=ma_doan.strip().upper(),
        tuyen_id=tuyen_id,
        cap_duong_id=cap_duong_id,
        tinh_trang_id=tinh_trang_id,
        ket_cau_mat_id=ket_cau_mat_id,
        ly_trinh_dau=ly_trinh_dau,
        ly_trinh_cuoi=ly_trinh_cuoi,
        chieu_dai_thuc_te=chieu_dai_thuc_te,
        chieu_rong_mat_min=chieu_rong_mat_min,
        chieu_rong_mat_max=chieu_rong_mat_max,
        chieu_rong_nen_min=chieu_rong_nen_min,
        chieu_rong_nen_max=chieu_rong_nen_max,
        don_vi_bao_duong_id=don_vi_bao_duong_id,
        nam_lam_moi=nam_lam_moi,
        ngay_cap_nhat_tinh_trang=ngay_cap_nhat_tinh_trang,
        ghi_chu=ghi_chu,
        updated_by_id=updated_by_id,
    )
    obj.id = doan_tuyen_repo.them(conn, obj)
    return obj


def sua(
    conn: sqlite3.Connection,
    id: int,
    cap_duong_id: int,
    tinh_trang_id: int,
    ly_trinh_dau: float,
    ly_trinh_cuoi: float,
    ket_cau_mat_id: Optional[int] = None,
    chieu_dai_thuc_te: Optional[float] = None,
    chieu_rong_mat_min: Optional[float] = None,
    chieu_rong_mat_max: Optional[float] = None,
    chieu_rong_nen_min: Optional[float] = None,
    chieu_rong_nen_max: Optional[float] = None,
    don_vi_bao_duong_id: Optional[int] = None,
    nam_lam_moi: Optional[int] = None,
    ngay_cap_nhat_tinh_trang: Optional[str] = None,
    ghi_chu: Optional[str] = None,
    updated_by_id: Optional[int] = None,
) -> doan_tuyen_model.DoanTuyen:
    obj = lay_theo_id(conn, id)
    _validate_ly_trinh(ly_trinh_dau, ly_trinh_cuoi)
    _validate_chieu_rong(chieu_rong_mat_min, chieu_rong_mat_max, "mặt")
    _validate_chieu_rong(chieu_rong_nen_min, chieu_rong_nen_max, "nền")
    _validate_nam_lam_moi(nam_lam_moi)

    obj.cap_duong_id = cap_duong_id
    obj.tinh_trang_id = tinh_trang_id
    obj.ket_cau_mat_id = ket_cau_mat_id
    obj.ly_trinh_dau = ly_trinh_dau
    obj.ly_trinh_cuoi = ly_trinh_cuoi
    obj.chieu_dai_thuc_te = chieu_dai_thuc_te
    obj.chieu_rong_mat_min = chieu_rong_mat_min
    obj.chieu_rong_mat_max = chieu_rong_mat_max
    obj.chieu_rong_nen_min = chieu_rong_nen_min
    obj.chieu_rong_nen_max = chieu_rong_nen_max
    obj.don_vi_bao_duong_id = don_vi_bao_duong_id
    obj.nam_lam_moi = nam_lam_moi
    obj.ngay_cap_nhat_tinh_trang = ngay_cap_nhat_tinh_trang
    obj.ghi_chu = ghi_chu
    obj.updated_by_id = updated_by_id
    doan_tuyen_repo.sua(conn, obj)
    return obj


def cap_nhat_tinh_trang(
    conn: sqlite3.Connection,
    id: int,
    tinh_trang_id: int,
    ngay_cap_nhat: str,
    updated_by_id: int,
) -> None:
    """Cập nhật nhanh tình trạng sau đợt khảo sát hiện trường."""
    lay_theo_id(conn, id)  # kiểm tra tồn tại
    doan_tuyen_repo.cap_nhat_tinh_trang(conn, id, tinh_trang_id, ngay_cap_nhat, updated_by_id)


def xoa(conn: sqlite3.Connection, id: int) -> None:
    lay_theo_id(conn, id)
    doan_tuyen_repo.xoa(conn, id)


# ── Validation nội bộ ──────────────────────────────────────────────────────

def _validate_ma(ma_doan: str) -> None:
    if not ma_doan or not ma_doan.strip():
        raise DoanTuyenServiceError("Mã đoạn không được để trống.")
    if len(ma_doan.strip()) > 30:
        raise DoanTuyenServiceError("Mã đoạn không được vượt quá 30 ký tự.")


def _validate_tuyen_ton_tai(conn: sqlite3.Connection, tuyen_id: int) -> None:
    if tuyen_duong_repo.lay_theo_id(conn, tuyen_id) is None:
        raise DoanTuyenServiceError(f"Tuyến đường id={tuyen_id} không tồn tại.")


def _validate_ly_trinh(dau: float, cuoi: float) -> None:
    if dau is None or cuoi is None:
        raise DoanTuyenServiceError("Lý trình đầu và cuối không được để trống.")
    if dau < 0 or cuoi < 0:
        raise DoanTuyenServiceError("Lý trình không được âm.")
    if cuoi <= dau:
        raise DoanTuyenServiceError(
            f"Lý trình cuối ({cuoi}) phải lớn hơn lý trình đầu ({dau})."
        )


def _validate_chieu_rong(
    gia_tri_min: Optional[float], gia_tri_max: Optional[float], loai: str
) -> None:
    if gia_tri_min is None and gia_tri_max is None:
        return
    if gia_tri_min is not None and gia_tri_min <= 0:
        raise DoanTuyenServiceError(f"Chiều rộng {loai} min phải lớn hơn 0.")
    if gia_tri_max is not None and gia_tri_max <= 0:
        raise DoanTuyenServiceError(f"Chiều rộng {loai} max phải lớn hơn 0.")
    if (gia_tri_min is not None and gia_tri_max is not None
            and gia_tri_max < gia_tri_min):
        raise DoanTuyenServiceError(
            f"Chiều rộng {loai} max không thể nhỏ hơn min."
        )


def _validate_nam_lam_moi(nam: Optional[int]) -> None:
    if nam is not None and not (1900 <= nam <= 2100):
        raise DoanTuyenServiceError("Năm làm mới không hợp lệ.")


def _kiem_tra_ma_doan_trung(conn: sqlite3.Connection, ma_doan: str) -> None:
    if doan_tuyen_repo.lay_theo_ma(conn, ma_doan) is not None:
        raise DoanTuyenServiceError(f"Mã đoạn '{ma_doan}' đã tồn tại.")