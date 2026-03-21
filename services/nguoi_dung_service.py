"""
Service: NguoiDung — Tài khoản người dùng  [MỚI]
Toàn bộ validation + business logic tập trung ở đây.

Yêu cầu: pip install bcrypt
Phân quyền: ADMIN (toàn quyền) / BIEN_TAP (thêm/sửa) / XEM (chỉ xem)
Đăng ký → chờ ADMIN duyệt (is_approved=0) mới được dùng.
"""

import re
import sqlite3
from typing import Optional, List

import bcrypt

import models.nguoi_dung as nguoi_dung_model
import repositories.nguoi_dung_repository as nguoi_dung_repo

LOAI_QUYEN_HOP_LE = {
    nguoi_dung_model.NguoiDung.LOAI_QUYEN_ADMIN,
    nguoi_dung_model.NguoiDung.LOAI_QUYEN_BIEN_TAP,
    nguoi_dung_model.NguoiDung.LOAI_QUYEN_XEM,
}


class NguoiDungServiceError(Exception):
    pass


class DangNhapThatBaiError(Exception):
    pass


def dang_ky(
    conn: sqlite3.Connection,
    ten_dang_nhap: str,
    mat_khau: str,
    ho_ten: str,
    chuc_vu: Optional[str] = None,
    don_vi_id: Optional[int] = None,
    so_dien_thoai: Optional[str] = None,
    email: Optional[str] = None,
) -> nguoi_dung_model.NguoiDung:
    """
    Tạo tài khoản mới. Mặc định loai_quyen=XEM, is_approved=0.
    Phải chờ ADMIN duyệt trước khi đăng nhập được.
    """
    _validate_ten_dang_nhap(ten_dang_nhap)
    _validate_mat_khau(mat_khau)
    _validate_ho_ten(ho_ten)
    if email:
        _validate_email(email)

    if nguoi_dung_repo.lay_theo_ten_dang_nhap(conn, ten_dang_nhap) is not None:
        raise NguoiDungServiceError(f"Tên đăng nhập '{ten_dang_nhap}' đã được sử dụng.")
    if email and nguoi_dung_repo.lay_theo_email(conn, email) is not None:
        raise NguoiDungServiceError(f"Email '{email}' đã được sử dụng.")

    mat_khau_hash = _hash_mat_khau(mat_khau)
    obj = nguoi_dung_model.NguoiDung(
        ten_dang_nhap=ten_dang_nhap.strip(),
        mat_khau_hash=mat_khau_hash,
        ho_ten=ho_ten.strip(),
        chuc_vu=chuc_vu,
        don_vi_id=don_vi_id,
        so_dien_thoai=so_dien_thoai,
        email=email.strip().lower() if email else None,
        loai_quyen=nguoi_dung_model.NguoiDung.LOAI_QUYEN_XEM,
        is_active=0,
        is_approved=0,
    )
    obj.id = nguoi_dung_repo.them(conn, obj)
    return obj


def dang_nhap(
    conn: sqlite3.Connection,
    ten_dang_nhap: str,
    mat_khau: str,
) -> nguoi_dung_model.NguoiDung:
    """
    Xác thực và trả về NguoiDung nếu hợp lệ.
    Ném DangNhapThatBaiError nếu sai hoặc chưa được duyệt.
    """
    nguoi_dung = nguoi_dung_repo.lay_theo_ten_dang_nhap(conn, ten_dang_nhap)
    mat_khau_hash = nguoi_dung_repo.lay_hash_de_xac_thuc(conn, ten_dang_nhap)

    if nguoi_dung is None or mat_khau_hash is None:
        raise DangNhapThatBaiError("Tên đăng nhập hoặc mật khẩu không đúng.")
    if not _kiem_tra_mat_khau(mat_khau, mat_khau_hash):
        raise DangNhapThatBaiError("Tên đăng nhập hoặc mật khẩu không đúng.")
    if not nguoi_dung.is_approved:
        raise DangNhapThatBaiError("Tài khoản chưa được quản trị viên duyệt.")
    if not nguoi_dung.is_active:
        raise DangNhapThatBaiError("Tài khoản đã bị vô hiệu hóa.")

    nguoi_dung_repo.cap_nhat_lan_dang_nhap(conn, nguoi_dung.id)
    return nguoi_dung


def duyet_tai_khoan(
    conn: sqlite3.Connection,
    id: int,
    approved_by_id: int,
    loai_quyen: Optional[str] = None,
) -> nguoi_dung_model.NguoiDung:
    """
    ADMIN duyệt tài khoản. Có thể đặt loại quyền lúc duyệt.
    Nếu không chỉ định loai_quyen thì giữ nguyên quyền XEM mặc định.
    """
    obj = _lay_theo_id_noi_bo(conn, id)
    if loai_quyen is not None:
        _validate_quyen(loai_quyen)
        obj.loai_quyen = loai_quyen
        nguoi_dung_repo.sua(conn, obj)
    nguoi_dung_repo.duyet_tai_khoan(conn, id, approved_by_id)
    return _lay_theo_id_noi_bo(conn, id)


def doi_mat_khau(
    conn: sqlite3.Connection,
    id: int,
    mat_khau_cu: str,
    mat_khau_moi: str,
) -> None:
    """Người dùng tự đổi mật khẩu, phải xác nhận mật khẩu cũ."""
    mat_khau_hash = nguoi_dung_repo.lay_hash_de_xac_thuc(
        conn, _lay_theo_id_noi_bo(conn, id).ten_dang_nhap
    )
    if not _kiem_tra_mat_khau(mat_khau_cu, mat_khau_hash):
        raise NguoiDungServiceError("Mật khẩu cũ không đúng.")
    _validate_mat_khau(mat_khau_moi)
    nguoi_dung_repo.cap_nhat_mat_khau(conn, id, _hash_mat_khau(mat_khau_moi))


def doi_mat_khau_admin(
    conn: sqlite3.Connection,
    id: int,
    mat_khau_moi: str,
) -> None:
    """ADMIN đặt lại mật khẩu, không cần xác nhận mật khẩu cũ."""
    _lay_theo_id_noi_bo(conn, id)
    _validate_mat_khau(mat_khau_moi)
    nguoi_dung_repo.cap_nhat_mat_khau(conn, id, _hash_mat_khau(mat_khau_moi))


def cap_nhat_quyen(
    conn: sqlite3.Connection,
    id: int,
    loai_quyen_moi: str,
) -> nguoi_dung_model.NguoiDung:
    obj = _lay_theo_id_noi_bo(conn, id)
    _validate_quyen(loai_quyen_moi)
    obj.loai_quyen = loai_quyen_moi
    nguoi_dung_repo.sua(conn, obj)
    return obj


def vo_hieu_hoa(conn: sqlite3.Connection, id: int) -> None:
    _lay_theo_id_noi_bo(conn, id)
    nguoi_dung_repo.vo_hieu_hoa(conn, id)


def lay_tat_ca(conn: sqlite3.Connection) -> List[nguoi_dung_model.NguoiDung]:
    return nguoi_dung_repo.lay_tat_ca(conn)


def lay_cho_duyet(conn: sqlite3.Connection) -> List[nguoi_dung_model.NguoiDung]:
    return nguoi_dung_repo.lay_cho_duyet(conn)


def lay_theo_id(conn: sqlite3.Connection, id: int) -> nguoi_dung_model.NguoiDung:
    return _lay_theo_id_noi_bo(conn, id)


# ── Helpers bcrypt ──────────────────────────────────────────────────────────

def _hash_mat_khau(mat_khau: str) -> str:
    return bcrypt.hashpw(mat_khau.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _kiem_tra_mat_khau(mat_khau: str, mat_khau_hash: str) -> bool:
    return bcrypt.checkpw(mat_khau.encode("utf-8"), mat_khau_hash.encode("utf-8"))


# ── Validation nội bộ ──────────────────────────────────────────────────────

def _lay_theo_id_noi_bo(conn: sqlite3.Connection, id: int) -> nguoi_dung_model.NguoiDung:
    obj = nguoi_dung_repo.lay_theo_id(conn, id)
    if obj is None:
        raise NguoiDungServiceError(f"Không tìm thấy người dùng id={id}.")
    return obj


def _validate_ten_dang_nhap(ten: str) -> None:
    if not ten or not ten.strip():
        raise NguoiDungServiceError("Tên đăng nhập không được để trống.")
    if not re.match(r'^[a-zA-Z0-9_]{4,50}$', ten.strip()):
        raise NguoiDungServiceError(
            "Tên đăng nhập chỉ được chứa chữ cái, chữ số và dấu gạch dưới, "
            "độ dài 4–50 ký tự."
        )


def _validate_mat_khau(mat_khau: str) -> None:
    if not mat_khau or len(mat_khau) < 8:
        raise NguoiDungServiceError("Mật khẩu phải có ít nhất 8 ký tự.")


def _validate_ho_ten(ho_ten: str) -> None:
    if not ho_ten or not ho_ten.strip():
        raise NguoiDungServiceError("Họ tên không được để trống.")


def _validate_email(email: str) -> None:
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email.strip()):
        raise NguoiDungServiceError(f"Email '{email}' không đúng định dạng.")


def _validate_quyen(loai_quyen: str) -> None:
    if loai_quyen not in LOAI_QUYEN_HOP_LE:
        raise NguoiDungServiceError(
            f"Loại quyền '{loai_quyen}' không hợp lệ. "
            f"Các quyền được phép: {', '.join(LOAI_QUYEN_HOP_LE)}."
        )
