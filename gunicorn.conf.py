"""
gunicorn.conf.py — Cấu hình Gunicorn cho production
Chạy: gunicorn api.main:app -c gunicorn.conf.py
"""

import multiprocessing

# Bind vào localhost — Nginx đứng phía trước làm reverse proxy
bind = "127.0.0.1:8000"

# Số worker = (CPU * 2) + 1, phù hợp workload I/O-bound
workers = multiprocessing.cpu_count() * 2 + 1

# UvicornWorker để chạy ASGI app (FastAPI)
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout request (giây)
timeout = 120
keepalive = 5

# Tự restart worker sau N request để tránh memory leak
max_requests = 1000
max_requests_jitter = 100

# Log
accesslog = "logs/access.log"
errorlog  = "logs/error.log"
loglevel  = "info"
