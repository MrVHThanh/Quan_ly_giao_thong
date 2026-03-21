"""
Helper: _auth_helper.py — Quản lý session đơn giản bằng cookie có ký HMAC.
Không dùng JWT để giảm dependency — chỉ cần Python stdlib.
"""

import hashlib
import hmac
import os
import time
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

# Secret key — trong production đặt vào biến môi trường
SECRET_KEY = os.environ.get("SESSION_SECRET", "laocai-giaothong-secret-2024")
SESSION_COOKIE = "gt_session"
SESSION_TTL = 86400 * 7  # 7 ngày


def tao_session_token(user_id: int, loai_quyen: str) -> str:
    """Tạo token: base64(user_id:quyen:timestamp):hmac_sig"""
    payload = f"{user_id}:{loai_quyen}:{int(time.time())}"
    sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    import base64
    b64 = base64.urlsafe_b64encode(payload.encode()).decode()
    return f"{b64}.{sig}"


def giai_ma_session_token(token: str) -> Optional[dict]:
    """Giải mã và xác thực token. Trả None nếu không hợp lệ hoặc hết hạn."""
    try:
        import base64
        parts = token.split(".")
        if len(parts) != 2:
            return None
        b64, sig = parts
        payload = base64.urlsafe_b64decode(b64.encode()).decode()
        expected = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        user_id_str, loai_quyen, ts_str = payload.split(":")
        if int(time.time()) - int(ts_str) > SESSION_TTL:
            return None
        return {"id": int(user_id_str), "loai_quyen": loai_quyen}
    except Exception:
        return None


def xoa_session_token():
    pass  # Cookie xóa phía client bằng delete_cookie


def lay_user_hien_tai(
    request: Request,
    gt_session: Optional[str] = Cookie(default=None),
) -> Optional[dict]:
    """Trả về dict user từ session cookie, hoặc None nếu chưa đăng nhập."""
    if not gt_session:
        return None
    return giai_ma_session_token(gt_session)


def yeu_cau_dang_nhap(
    user: Optional[dict] = Depends(lay_user_hien_tai),
) -> dict:
    """Dependency: yêu cầu đã đăng nhập. Redirect về login nếu chưa."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/auth/login"},
        )
    return user


def yeu_cau_quyen_admin(
    user: dict = Depends(yeu_cau_dang_nhap),
) -> dict:
    """Dependency: yêu cầu quyền ADMIN."""
    if user.get("loai_quyen") != "ADMIN":
        raise HTTPException(status_code=403, detail="Cần quyền ADMIN.")
    return user


def yeu_cau_quyen_bien_tap(
    user: dict = Depends(yeu_cau_dang_nhap),
) -> dict:
    """Dependency: yêu cầu quyền ADMIN hoặc BIEN_TAP."""
    if user.get("loai_quyen") not in ("ADMIN", "BIEN_TAP"):
        raise HTTPException(status_code=403, detail="Cần quyền BIEN_TAP trở lên.")
    return user
