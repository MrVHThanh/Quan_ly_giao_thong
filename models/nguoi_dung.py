"""
Model: NguoiDung — Tài khoản người dùng hệ thống  [MỚI]
Plain object thuần túy. KHÔNG logic nghiệp vụ, KHÔNG gọi DB.

Phân quyền: ADMIN (toàn quyền) / BIEN_TAP (thêm/sửa) / XEM (chỉ xem)
Đăng ký → chờ ADMIN duyệt mới được dùng (is_approved = 0 mặc định).
Mật khẩu lưu dạng bcrypt hash — KHÔNG lưu rõ.
"""

from typing import Optional


class NguoiDung:
    LOAI_QUYEN_ADMIN = "ADMIN"
    LOAI_QUYEN_BIEN_TAP = "BIEN_TAP"
    LOAI_QUYEN_XEM = "XEM"

    def __init__(
        self,
        id: Optional[int] = None,
        ten_dang_nhap: Optional[str] = None,
        mat_khau_hash: Optional[str] = None,
        ho_ten: Optional[str] = None,
        chuc_vu: Optional[str] = None,
        don_vi_id: Optional[int] = None,
        so_dien_thoai: Optional[str] = None,
        email: Optional[str] = None,
        loai_quyen: Optional[str] = None,
        is_active: Optional[int] = 0,
        is_approved: Optional[int] = 0,
        approved_by_id: Optional[int] = None,
        approved_at: Optional[str] = None,
        created_at: Optional[str] = None,
        last_login: Optional[str] = None,
    ):
        self.id = id
        self.ten_dang_nhap = ten_dang_nhap
        self.mat_khau_hash = mat_khau_hash
        self.ho_ten = ho_ten
        self.chuc_vu = chuc_vu
        self.don_vi_id = don_vi_id
        self.so_dien_thoai = so_dien_thoai
        self.email = email
        self.loai_quyen = loai_quyen
        self.is_active = is_active
        self.is_approved = is_approved
        self.approved_by_id = approved_by_id
        self.approved_at = approved_at
        self.created_at = created_at
        self.last_login = last_login

    @property
    def co_the_dang_nhap(self) -> bool:
        """Tài khoản có thể đăng nhập khi đã được duyệt và đang hoạt động."""
        return bool(self.is_active) and bool(self.is_approved)

    @property
    def la_admin(self) -> bool:
        return self.loai_quyen == self.LOAI_QUYEN_ADMIN

    @property
    def co_quyen_bien_tap(self) -> bool:
        return self.loai_quyen in (self.LOAI_QUYEN_ADMIN, self.LOAI_QUYEN_BIEN_TAP)

    def __repr__(self) -> str:
        return f"<NguoiDung id={self.id} ten_dang_nhap={self.ten_dang_nhap} quyen={self.loai_quyen}>"
