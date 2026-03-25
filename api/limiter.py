"""
api/limiter.py — Shared rate limiter dùng chung toàn app.
Import module này ở main.py (gắn vào app.state) và ở các route cần giới hạn.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
