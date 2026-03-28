# Hướng dẫn Deploy Code từ GitHub lên VPS

> Cập nhật: 2026-03-27
> Dự án: Quản lý Đường bộ Lào Cai — Sở Xây dựng

---

## Thông tin hệ thống

| Thông tin | Giá trị |
|---|---|
| **VPS user** | `giaothong` |
| **Thư mục dự án** | `/home/giaothong/giaothong-app/` |
| **Thư mục dữ liệu** | `/home/giaothong/data/` ← DB nằm đây, ngoài repo |
| **Database** | `/home/giaothong/data/giao_thong.db` |
| **Python (venv)** | `/home/giaothong/giaothong-app/venv/bin/python3` |
| **Service name** | `giaothong` |
| **Nhánh production** | `main` |
| **Nhánh phát triển** | `develop` |
| **GitHub repo** | `https://github.com/MrVHThanh/Quan_ly_giao_thong.git` |

> **Tại sao DB nằm ngoài thư mục dự án?**
> Khi clone mới (`rm -rf giaothong-app`), DB không bị xóa theo.
> File `.env` trên local và VPS có `DB_PATH` khác nhau — mỗi môi trường tự cấu hình.

---

## PHẦN 0 — CHUYỂN DB RA NGOÀI THƯ MỤC DỰ ÁN (chỉ làm 1 lần)

> Thực hiện nếu VPS hiện đang để DB trong thư mục dự án (`giaothong-app/giao_thong.db`).

```bash
# 1. Tạo thư mục data
mkdir -p /home/giaothong/data

# 2. Chuyển DB sang thư mục mới
cp /home/giaothong/giaothong-app/giao_thong.db /home/giaothong/data/giao_thong.db

# 3. Xác nhận file đã copy đúng (kiểm tra dung lượng tương đương)
ls -lh /home/giaothong/data/

# 4. Sửa DB_PATH trong .env
nano /home/giaothong/giaothong-app/.env
# Đổi dòng: DB_PATH=giao_thong.db
# Thành:    DB_PATH=/home/giaothong/data/giao_thong.db

# 5. Restart service và kiểm tra
sudo systemctl restart giaothong
sudo systemctl status giaothong
```

> Sau khi xác nhận service chạy bình thường, có thể xóa DB cũ trong thư mục dự án:
> ```bash
> rm /home/giaothong/giaothong-app/giao_thong.db
> ```

---

## PHẦN 1 — CLONE DỰ ÁN MỚI HOÀN TOÀN LÊN VPS

> Dùng khi VPS chưa có dự án hoặc cần cài lại từ đầu.

### Bước 1 — SSH vào VPS

```bash
ssh giaothong@<IP_VPS>
```

### Bước 2 — Tạo thư mục dữ liệu (nếu chưa có)

```bash
mkdir -p /home/giaothong/data
```

### Bước 3 — Dừng service (nếu đang chạy)

```bash
sudo systemctl stop giaothong
```

### Bước 4 — Sao lưu DB (quan trọng!)

```bash
cp /home/giaothong/data/giao_thong.db /home/giaothong/data/giao_thong_backup_$(date +%Y%m%d).db
```

### Bước 5 — Xóa thư mục dự án cũ và clone mới

```bash
cd /home/giaothong
rm -rf giaothong-app
git clone -b main https://github.com/MrVHThanh/Quan_ly_giao_thong.git giaothong-app
cd giaothong-app
```

> DB **không bị xóa** vì nằm tại `/home/giaothong/data/`, ngoài thư mục dự án.

### Bước 6 — Tạo môi trường ảo và cài dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Bước 7 — Tạo file `.env`

```bash
nano .env
```

Nội dung file `.env`:
```env
SESSION_SECRET=<chuỗi ngẫu nhiên 64 ký tự>
DEBUG=false
DB_PATH=/home/giaothong/data/giao_thong.db
ALLOWED_ORIGINS=https://<domain_hoac_IP_VPS>
```

> Tạo SESSION_SECRET ngẫu nhiên:
> ```bash
> python3 -c "import secrets; print(secrets.token_hex(32))"
> ```

### Bước 8 — Chạy migration

```bash
python migrate.py
```

### Bước 9 — Khởi động service

```bash
sudo systemctl start giaothong
sudo systemctl status giaothong
```

Kết quả mong đợi: `Active: active (running)`

---

## PHẦN 2 — CẬP NHẬT CODE KHI VPS ĐÃ CÓ DỰ ÁN

> Dùng mỗi khi có code mới cần đưa lên VPS.

### Bước 1 — Trên máy local: Gộp code vào nhánh main

```bash
# Chuyển sang nhánh main
git checkout main

# Merge code từ develop vào main
git merge develop

# Push lên GitHub
git push origin main

# Quay lại develop để tiếp tục làm việc
git checkout develop
```

### Bước 2 — SSH vào VPS

```bash
ssh giaothong@<IP_VPS>
```

### Bước 3 — Vào thư mục dự án và kéo code mới

```bash
cd /home/giaothong/giaothong-app && git pull origin main
```

### Bước 4 — Chạy migration (nếu có bảng/cột mới)

```bash
python migrate.py
```

> Nếu không có thay đổi DB, lệnh tự báo `Không có migration mới` và bỏ qua.

### Bước 5 — Khởi động lại service

```bash
sudo systemctl restart giaothong
sudo systemctl status giaothong
```

### Bước 6 — Người dùng đăng xuất & đăng nhập lại (nếu cần)

> Chỉ cần khi có thay đổi liên quan đến session hoặc thông tin người dùng.

- Vào trang web → click **Đăng xuất** → **Đăng nhập lại**

---

## TÓM TẮT NHANH — Cập nhật VPS (không có migration)

```bash
# === MÁY LOCAL ===
git checkout main && git merge develop && git push origin main && git checkout develop

# === TRÊN VPS ===
cd /home/giaothong/giaothong-app && git pull origin main && sudo systemctl restart giaothong
```

---

## TÓM TẮT NHANH — Cập nhật VPS (có migration)

```bash
# === MÁY LOCAL ===
git checkout main && git merge develop && git push origin main && git checkout develop

# === TRÊN VPS ===
cd /home/giaothong/giaothong-app && git pull origin main
python migrate.py
sudo systemctl restart giaothong && sudo systemctl status giaothong
```

---

## CẤU HÌNH DB_PATH THEO MÔI TRƯỜNG

| Môi trường | `DB_PATH` trong `.env` | Ghi chú |
|---|---|---|
| **Local (máy phát triển)** | `DB_PATH=giao_thong.db` | Đường dẫn tương đối, DB trong thư mục dự án |
| **VPS (production)** | `DB_PATH=/home/giaothong/data/giao_thong.db` | Đường dẫn tuyệt đối, DB ngoài thư mục dự án |

> File `.env` được gitignore — mỗi môi trường tự cấu hình riêng, không ảnh hưởng nhau.

---

## BACKUP DB ĐỊNH KỲ

```bash
# Backup thủ công
cp /home/giaothong/data/giao_thong.db /home/giaothong/data/giao_thong_backup_$(date +%Y%m%d_%H%M).db

# Xem danh sách backup
ls -lh /home/giaothong/data/

# Xóa backup cũ hơn 30 ngày (tùy chọn)
find /home/giaothong/data/ -name "giao_thong_backup_*.db" -mtime +30 -delete
```

---

## QUẢN LÝ PHIÊN BẢN (Version)

### Tạo phiên bản mới

```bash
# 1. Sửa số version trên máy local
echo "1.0.2" > VERSION

# 2. Cập nhật CHANGELOG.md

# 3. Commit + push
git add VERSION CHANGELOG.md
git commit -m "v1.0.2 - Mo ta ngan gon"
git checkout main && git merge develop && git push origin main && git checkout develop

# 4. Tạo tag trên GitHub
git tag -a v1.0.2 -m "v1.0.2 - Mo ta ngan gon"
git push origin v1.0.2
```

### Xem các phiên bản đã có

```bash
git tag -l
```

### Rollback về phiên bản cũ (khi có lỗi nghiêm trọng)

```bash
# Trên VPS — quay về phiên bản cũ
git checkout v1.0.0
sudo systemctl restart giaothong
```

---

## XỬ LÝ LỖI THƯỜNG GẶP

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| Trang web không cập nhật | Trình duyệt cache | Bấm `Ctrl + Shift + R` |
| Thông tin người dùng không đổi | Session cũ | Đăng xuất → đăng nhập lại |
| Service không start | Lỗi code Python | Chạy `sudo journalctl -u giaothong -n 50` |
| `Migration OK` không in ra | Lỗi import | Kiểm tra tên file migration |
| `unable to open database` | DB_PATH sai trong `.env` | Kiểm tra đường dẫn tuyệt đối trong `.env` |
| Mất dữ liệu sau clone | DB vẫn trong thư mục dự án | Thực hiện PHẦN 0 để chuyển DB ra ngoài |

---

## XEM LOG KHI CÓ LỖI

```bash
# Xem 50 dòng log gần nhất
sudo journalctl -u giaothong -n 50

# Xem log realtime
sudo journalctl -u giaothong -f
```

---

## PHẦN 3 — GẮN TÊN MIỀN VÀ CÀI SSL (chỉ làm 1 lần)

> Thực hiện khi đã có tên miền trỏ về IP VPS.
> Domain: `soxaydunglaocai.vn` — VPS IP: `171.244.140.146`

### Bước 1 — Tro DNS tren trang quan ly ten mien

Dang nhap trang quan ly ten mien, tao 2 ban ghi A:

| Type | Host | Value | TTL |
|---|---|---|---|
| A | `@` (hoac `soxaydunglaocai.vn`) | `171.244.140.146` | 3600 |
| A | `www` | `171.244.140.146` | 3600 |

> Doi 5–30 phut de DNS lan truyen. Kiem tra bang:
> ```bash
> ping soxaydunglaocai.vn
> # Ket qua phai hien IP: 171.244.140.146
> ```

### Bước 2 — Cài Certbot (Let's Encrypt)

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

### Bước 3 — Deploy nginx.conf mới với tên miền thực

```bash
# Copy file cau hinh moi len VPS
sudo cp /home/giaothong/giaothong-app/deploy/nginx.conf /etc/nginx/sites-available/giaothong

# Kiem tra cu phap nginx
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Bước 4 — Cấp chứng chỉ SSL

```bash
sudo certbot --nginx -d soxaydunglaocai.vn -d www.soxaydunglaocai.vn
```

> Certbot se hoi:
> - Email de thong bao het han cert → nhap email thuc
> - Dong y dieu khoan → nhap `Y`
> - Redirect HTTP → HTTPS → chon `2` (Redirect)

> Certbot **tu dong cap nhat** nginx.conf voi duong dan SSL. Kiem tra lai:
> ```bash
> sudo nginx -t && sudo systemctl reload nginx
> ```

### Bước 5 — Cập nhật file .env trên VPS

```bash
nano /home/giaothong/giaothong-app/.env
```

Sua cac dong sau:
```env
DEBUG=false
ALLOWED_ORIGINS=https://soxaydunglaocai.vn
```

Khoi dong lai service:
```bash
sudo systemctl restart giaothong
```

### Bước 6 — Kiểm tra chứng chỉ tự động gia hạn

```bash
# Kiem tra timer tu dong gia han
sudo systemctl status certbot.timer

# Thu gia han (khong thay doi cert that)
sudo certbot renew --dry-run
```

> Certbot tu dong gia han moi 90 ngay qua systemd timer — khong can lam thu cong.

### Bước 7 — Kiểm tra tổng thể

```bash
# Kiem tra HTTPS
curl -I https://soxaydunglaocai.vn

# Ket qua mong doi:
# HTTP/2 200
# strict-transport-security: max-age=31536000...
```

---

## PHẦN 4 — BẢO MẬT VPS

### 4.1 — Cấu hình Firewall (UFW)

```bash
# Cai UFW neu chua co
sudo apt install -y ufw

# Mac dinh: chan het
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Chi mo 3 cong can thiet
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 80/tcp     # HTTP (de certbot va redirect)
sudo ufw allow 443/tcp    # HTTPS

# Bat firewall
sudo ufw enable

# Kiem tra trang thai
sudo ufw status verbose
```

> **Luu y:** Dam bao port 22 da mo TRUOC khi bat `ufw enable`, neu khong bi mat ket noi SSH.

### 4.2 — Cài Fail2ban (chống brute force)

```bash
# Cai dat
sudo apt install -y fail2ban

# Tao file cau hinh local (khong chinh sua file goc)
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

Tim va sua cac dong sau trong `[DEFAULT]`:
```ini
bantime  = 3600      # Ban 1 gio
findtime = 600       # Trong 10 phut
maxretry = 5         # Cho phep 5 lan that bai
```

Bat va kiem tra:
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

### 4.3 — Giới hạn truy cập SSH (tùy chọn nâng cao)

```bash
# Xem ai dang dang nhap
who

# Kiem tra cac lan dang nhap that bai gan day
sudo grep "Failed password" /var/log/auth.log | tail -20

# Doi port SSH (tuy chon — neu doi, phai them ufw allow <port>/tcp)
# sudo nano /etc/ssh/sshd_config
# Doi: Port 22 → Port <so_khac>
# sudo systemctl restart sshd
```

### 4.4 — Kiểm tra bảo mật tổng thể

```bash
# Kiem tra port dang mo
sudo ss -tlnp

# Ket qua mong doi chi thay:
# :22  (SSH)
# :80  (Nginx HTTP)
# :443 (Nginx HTTPS)
# :8000 ONLY 127.0.0.1 (Gunicorn — khong expose ra ngoai)

# Kiem tra Gunicorn khong expose ra ngoai internet
sudo ss -tlnp | grep 8000
# Phai hien: 127.0.0.1:8000 — KHONG duoc la 0.0.0.0:8000
```

### 4.5 — Backup DB tự động hàng ngày

```bash
# Tao script backup
sudo nano /home/giaothong/backup_db.sh
```

Noi dung file:
```bash
#!/bin/bash
BACKUP_DIR="/home/giaothong/data/backups"
DB_FILE="/home/giaothong/data/giao_thong.db"
DATE=$(date +%Y%m%d_%H%M)
mkdir -p "$BACKUP_DIR"
cp "$DB_FILE" "$BACKUP_DIR/giao_thong_$DATE.db"
# Giu lai 30 ban backup gan nhat
ls -t "$BACKUP_DIR"/giao_thong_*.db | tail -n +31 | xargs -r rm
```

```bash
# Phan quyen va cai cron
chmod +x /home/giaothong/backup_db.sh

# Them vao crontab — chay 2h sang moi ngay
crontab -e
# Them dong:
# 0 2 * * * /home/giaothong/backup_db.sh
```

---

## CHECKLIST SAU KHI GẮN TÊN MIỀN

```
[ ] DNS A record tro ve 171.244.140.146 (ca @ va www)
[ ] ping soxaydunglaocai.vn → hien IP VPS
[ ] nginx.conf da copy len /etc/nginx/sites-available/giaothong
[ ] sudo nginx -t → OK
[ ] Certbot cap cert thanh cong
[ ] https://soxaydunglaocai.vn mo duoc, o khoa xanh
[ ] http://soxaydunglaocai.vn tu dong redirect sang https
[ ] www.soxaydunglaocai.vn redirect ve soxaydunglaocai.vn
[ ] .env: DEBUG=false, ALLOWED_ORIGINS=https://soxaydunglaocai.vn
[ ] sudo systemctl restart giaothong → Active: running
[ ] UFW bat va chi cho 22/80/443
[ ] Fail2ban dang chay
[ ] sudo certbot renew --dry-run → OK
[ ] Backup DB tu dong da cai crontab
```
