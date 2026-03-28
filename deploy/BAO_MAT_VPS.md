# BAO_MAT_VPS.md — Hướng dẫn Bảo mật và Gắn Tên miền VPS

> Tài liệu này ghi lại toàn bộ các bước đã thực hiện để gắn tên miền và bảo mật VPS
> cho hệ thống Quản lý Đường bộ Lào Cai.
> Thực hiện: 2026-03-29
> Domain: `soxaydunglaocai.vn` — VPS IP: `171.244.140.146`

---

## TỔNG QUAN CÁC BƯỚC ĐÃ THỰC HIỆN

| Bước | Nội dung | Kết quả |
|---|---|---|
| 1 | Trỏ DNS domain về IP VPS | ✓ |
| 2 | Cài Certbot, cấp chứng chỉ SSL Let's Encrypt | ✓ |
| 3 | Cập nhật nginx.conf với domain thực tế và security headers | ✓ |
| 4 | Cập nhật `.env`: DEBUG=false, ALLOWED_ORIGINS | ✓ |
| 5 | Cài UFW firewall, chỉ mở port 22/80/443 | ✓ |
| 6 | Cài Fail2ban chống brute force SSH | ✓ |
| 7 | Cài backup DB tự động 2h sáng hàng ngày | ✓ |
| 8 | Reboot VPS để load kernel mới | ✓ |

---

## BƯỚC 1 — TRỎ DNS

### Thực hiện trên trang quản lý tên miền

Tạo 2 bản ghi A trỏ domain về IP VPS:

| Type | Host | Value | TTL |
|---|---|---|---|
| A | `@` | `171.244.140.146` | 3600 |
| A | `www` | `171.244.140.146` | 3600 |

### Kiểm tra DNS đã lan truyền

```bash
nslookup soxaydunglaocai.vn 8.8.8.8
nslookup www.soxaydunglaocai.vn 8.8.8.8
```

**Ý nghĩa:** `nslookup` hỏi DNS server của Google (8.8.8.8) xem domain đang trỏ về IP nào.
Kết quả phải hiện `171.244.140.146` — chứng tỏ DNS đã lan truyền toàn cầu.

---

## BƯỚC 2 — CÀI SSL (Let's Encrypt)

### Cài Certbot

```bash
sudo apt update && sudo apt install -y certbot python3-certbot-nginx
```

**Ý nghĩa:**
- `certbot` — công cụ tự động xin và gia hạn chứng chỉ SSL miễn phí từ Let's Encrypt
- `python3-certbot-nginx` — plugin giúp Certbot tự động cấu hình Nginx

### Tạo nginx.conf tạm (HTTP only) trước khi có SSL

```bash
sudo nano /etc/nginx/sites-available/giaothong
```

Nội dung tạm:
```nginx
server {
    listen 80;
    server_name soxaydunglaocai.vn www.soxaydunglaocai.vn;
    location / {
        proxy_pass http://127.0.0.1:8000;
        ...
    }
}
```

**Ý nghĩa:** Certbot cần xác minh quyền sở hữu domain bằng cách đặt file vào server qua
HTTP port 80. Nginx phải đang chạy và phục vụ domain trước khi chạy Certbot.

### Cấp chứng chỉ SSL

```bash
sudo certbot --nginx -d soxaydunglaocai.vn -d www.soxaydunglaocai.vn
```

**Ý nghĩa từng phần:**
- `--nginx` — dùng plugin Nginx, Certbot tự cấu hình file nginx
- `-d soxaydunglaocai.vn` — cấp cert cho domain chính
- `-d www.soxaydunglaocai.vn` — cấp cert cho subdomain www

Certbot tự động:
1. Xác minh quyền sở hữu domain qua HTTP
2. Tạo chứng chỉ tại `/etc/letsencrypt/live/soxaydunglaocai.vn/`
3. Cập nhật nginx.conf với đường dẫn cert

### Kiểm tra tự động gia hạn (cert hết hạn sau 90 ngày)

```bash
sudo certbot renew --dry-run
```

**Ý nghĩa:** `--dry-run` chạy thử không thay đổi cert thật — kiểm tra xem quá trình
gia hạn tự động có hoạt động không. Certbot đã đăng ký systemd timer để tự gia hạn.

---

## BƯỚC 3 — CẬU HÌNH NGINX CHÍNH THỨC

### Deploy nginx.conf với domain và bảo mật đầy đủ

```bash
sudo cp /home/giaothong/giaothong-app/deploy/nginx.conf /etc/nginx/sites-available/giaothong
sudo nginx -t && sudo systemctl reload nginx
```

**Ý nghĩa:**
- `nginx -t` — kiểm tra cú pháp file config TRƯỚC khi áp dụng (tránh nginx bị crash)
- `systemctl reload nginx` — tải lại config mà không ngắt kết nối đang có

### Nội dung nginx.conf sau khi hoàn thiện

```nginx
# Block 1: HTTP → HTTPS redirect
server {
    listen 80;
    server_name soxaydunglaocai.vn www.soxaydunglaocai.vn;
    server_tokens off;
    return 301 https://soxaydunglaocai.vn$request_uri;
}

# Block 2: www HTTPS → non-www HTTPS redirect
server {
    listen 443 ssl;
    server_name www.soxaydunglaocai.vn;
    ...
    return 301 https://soxaydunglaocai.vn$request_uri;
}

# Block 3: HTTPS chính
server {
    listen 443 ssl;
    server_name soxaydunglaocai.vn;
    ssl_protocols TLSv1.2 TLSv1.3;         # Chỉ dùng TLS mới, bỏ TLS 1.0/1.1 cũ yếu
    ssl_session_cache shared:SSL:10m;       # Cache session SSL để tăng tốc
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    ...
}
```

**Ý nghĩa các security header:**

| Header | Ý nghĩa |
|---|---|
| `Strict-Transport-Security` (HSTS) | Bắt trình duyệt luôn dùng HTTPS trong 1 năm, không cho phép HTTP |
| `X-Frame-Options: DENY` | Chặn website bị nhúng vào iframe — ngăn clickjacking |
| `X-Content-Type-Options: nosniff` | Ngăn trình duyệt đoán sai loại file — tránh XSS |
| `Referrer-Policy` | Kiểm soát thông tin referrer khi click link ra ngoài |
| `server_tokens off` | Ẩn phiên bản Nginx khỏi response header — giảm lộ thông tin |

---

## BƯỚC 4 — CẬP NHẬT FILE .ENV

```bash
nano /home/giaothong/giaothong-app/.env
```

Thay đổi:
```env
DEBUG=false
ALLOWED_ORIGINS=https://soxaydunglaocai.vn
```

```bash
sudo systemctl restart giaothong
```

**Ý nghĩa:**
- `DEBUG=false` — ẩn Swagger API docs (`/api/docs`), ẩn stack trace lỗi khỏi người dùng
- `ALLOWED_ORIGINS` — chỉ cho phép request từ domain HTTPS chính thức, chặn CORS từ
  nguồn khác (bảo vệ API khỏi bị gọi từ website lạ)

---

## BƯỚC 5 — CÀI UFW FIREWALL

### Các lệnh đã chạy

```bash
sudo apt install -y ufw                  # Cài UFW nếu chưa có
sudo ufw default deny incoming           # Mặc định: chặn TẤT CẢ kết nối vào
sudo ufw default allow outgoing          # Mặc định: cho phép TẤT CẢ kết nối ra
sudo ufw allow 22/tcp                    # Mở port SSH
sudo ufw allow 80/tcp                    # Mở port HTTP (để redirect và Certbot)
sudo ufw allow 443/tcp                   # Mở port HTTPS
sudo ufw enable                          # Bật firewall (tự động bật sau reboot)
```

### Kiểm tra trạng thái

```bash
sudo ufw status verbose
```

**Ý nghĩa từng lệnh:**
- `default deny incoming` — chính sách mặc định: từ chối mọi kết nối từ ngoài vào,
  trừ những port được `allow` rõ ràng
- `default allow outgoing` — server có thể kết nối ra ngoài (cài package, DNS, API...)
- Port 22 (SSH) — để quản trị server từ xa
- Port 80 (HTTP) — Certbot cần để xác minh domain; Nginx dùng để redirect sang HTTPS
- Port 443 (HTTPS) — cổng chính của ứng dụng web

> **Quan trọng:** Luôn `allow 22` TRƯỚC khi `ufw enable` — nếu quên sẽ bị mất kết nối SSH.

### Kết quả sau khi cài

```
Status: active
To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
80/tcp                     ALLOW IN    Anywhere
443/tcp                    ALLOW IN    Anywhere
```

---

## BƯỚC 6 — CÀI FAIL2BAN

### Cài đặt và khởi động

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban      # Tự động chạy sau reboot
sudo systemctl start fail2ban       # Chạy ngay
sudo fail2ban-client status         # Kiểm tra
```

**Ý nghĩa:**
- `fail2ban` — theo dõi log hệ thống, tự động ban IP nếu có nhiều lần đăng nhập sai
- Mặc định bảo vệ SSH: sau 5 lần nhập sai password trong 10 phút → ban IP 10 phút
- Ngăn chặn tấn công brute force (dò mật khẩu SSH hàng nghìn lần)

### Kiểm tra jail đang hoạt động

```bash
sudo fail2ban-client status sshd
```

**Ý nghĩa:** Hiển thị danh sách IP đang bị ban và số lần thất bại.

---

## BƯỚC 7 — BACKUP DB TỰ ĐỘNG

### Tạo script backup

```bash
nano /home/giaothong/backup_db.sh
```

Nội dung:
```bash
#!/bin/bash
BACKUP_DIR="/home/giaothong/data/backups"
DB_FILE="/home/giaothong/data/giao_thong.db"
DATE=$(date +%Y%m%d_%H%M)
mkdir -p "$BACKUP_DIR"
cp "$DB_FILE" "$BACKUP_DIR/giao_thong_$DATE.db"
# Giữ lại 30 bản backup gần nhất, xóa cũ hơn
ls -t "$BACKUP_DIR"/giao_thong_*.db | tail -n +31 | xargs -r rm
```

```bash
chmod +x /home/giaothong/backup_db.sh   # Cấp quyền chạy
```

### Đăng ký chạy tự động lúc 2h sáng

```bash
crontab -e
```

Thêm dòng:
```
0 2 * * * /home/giaothong/backup_db.sh
```

**Ý nghĩa cú pháp crontab `0 2 * * *`:**
- `0` — phút 0
- `2` — giờ 2 (2h sáng)
- `* * *` — mọi ngày, mọi tháng, mọi thứ trong tuần

**Ý nghĩa script:**
- Sao chép DB vào thư mục backup với tên có ngày giờ
- Tự động xóa các bản backup cũ hơn bản thứ 30 — tránh đầy ổ cứng
- Backup lưu tại `/home/giaothong/data/backups/` — ngoài thư mục dự án

---

## BƯỚC 8 — REBOOT VPS

```bash
sudo reboot
```

**Ý nghĩa:** Trong quá trình cài package, hệ thống báo có kernel mới
(`6.8.0-79` → `6.8.0-106`). Reboot để load kernel mới với các bản vá bảo mật mới nhất.

### Kiểm tra sau reboot

```bash
sudo systemctl status giaothong    # App đang chạy
sudo systemctl status nginx        # Nginx đang chạy
sudo fail2ban-client status        # Fail2ban đang chạy
```

---

## KIỂM TRA TỔNG THỂ

```bash
# HTTPS hoạt động và có security headers
curl -I https://soxaydunglaocai.vn

# HTTP tự động redirect sang HTTPS
curl -I http://soxaydunglaocai.vn

# Chỉ 3 port được mở
sudo ufw status verbose

# Gunicorn KHÔNG expose ra ngoài (chỉ 127.0.0.1)
sudo ss -tlnp | grep 8000

# Cert SSL còn hạn và tự gia hạn được
sudo certbot renew --dry-run
```

---

## CÁC LỆNH QUẢN TRỊ THƯỜNG DÙNG SAU NÀY

```bash
# Xem log app
sudo journalctl -u giaothong -n 50 -f

# Xem log nginx
sudo tail -f /var/log/nginx/error.log

# Xem IP đang bị Fail2ban ban
sudo fail2ban-client status sshd

# Bỏ ban 1 IP (khi cần)
sudo fail2ban-client set sshd unbanip <IP>

# Gia hạn cert thủ công (nếu cần)
sudo certbot renew

# Xem danh sách backup DB
ls -lh /home/giaothong/data/backups/

# Backup DB thủ công ngay lập tức
/home/giaothong/backup_db.sh

# Kiểm tra cert còn bao nhiêu ngày
sudo certbot certificates
```

---

## CẤU TRÚC BẢO MẬT TỔNG THỂ

```
Internet
    │
    ↓ HTTPS port 443 (SSL/TLS 1.2/1.3)
  UFW Firewall (chỉ 22/80/443 được vào)
    │
    ↓
  Nginx (reverse proxy)
  ├── Security headers (HSTS, X-Frame-Options...)
  ├── Redirect HTTP → HTTPS
  ├── Serve /static/ trực tiếp
    │
    ↓ HTTP 127.0.0.1:8000 (nội bộ, không ra ngoài)
  Gunicorn (3 workers)
    │
    ↓
  FastAPI App
  ├── Rate limit đăng nhập (5 req/phút/IP)
  ├── Session HMAC-SHA256
  ├── bcrypt password hash
    │
    ↓
  SQLite DB (/home/giaothong/data/giao_thong.db)
  └── Backup tự động 2h sáng → /home/giaothong/data/backups/

Fail2ban: giám sát SSH log → tự ban IP brute force
```

---

*Cập nhật file này nếu có thay đổi cấu hình bảo mật.*
