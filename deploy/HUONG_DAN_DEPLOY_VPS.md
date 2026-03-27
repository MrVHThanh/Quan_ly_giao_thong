# Hướng dẫn Deploy Code từ GitHub lên VPS

> Cập nhật: 2026-03-27
> Dự án: Quản lý Đường bộ Lào Cai — Sở Xây dựng

---

## Thông tin hệ thống

| Thông tin | Giá trị |
|---|---|
| **VPS user** | `giaothong` |
| **Thư mục dự án** | `/home/giaothong/giaothong-app/` |
| **Python (venv)** | `/home/giaothong/giaothong-app/venv/bin/python3` |
| **Service name** | `giaothong` |
| **Nhánh production** | `main` |
| **Nhánh phát triển** | `develop` |
| **GitHub repo** | `https://github.com/MrVHThanh/Quan_ly_giao_thong.git` |

---

## PHẦN 1 — CLONE DỰ ÁN MỚI HOÀN TOÀN LÊN VPS

> Dùng khi VPS chưa có dự án hoặc cần cài lại từ đầu.

### Bước 1 — SSH vào VPS

```bash
ssh giaothong@<IP_VPS>
```

### Bước 2 — Dừng service (nếu đang chạy)

```bash
sudo systemctl stop giaothong
```

### Bước 3 — Sao lưu DB trước khi làm gì (quan trọng!)

```bash
cp /home/giaothong/giaothong-app/giao_thong.db /home/giaothong/giao_thong_backup_$(date +%Y%m%d).db
```

### Bước 4 — Xóa thư mục cũ và clone mới

```bash
cd /home/giaothong
rm -rf giaothong-app
git clone -b main https://github.com/MrVHThanh/Quan_ly_giao_thong.git giaothong-app
cd giaothong-app
```

### Bước 5 — Tạo môi trường ảo và cài dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Bước 6 — Tạo file `.env`

```bash
nano .env
```

Nội dung file `.env`:
```env
SESSION_SECRET=<chuỗi ngẫu nhiên 64 ký tự>
DEBUG=false
DB_PATH=giao_thong.db
ALLOWED_ORIGINS=https://<domain_hoac_IP_VPS>
```

> Tạo SESSION_SECRET ngẫu nhiên:
> ```bash
> python3 -c "import secrets; print(secrets.token_hex(32))"
> ```

### Bước 7 — Khôi phục DB từ backup

```bash
cp /home/giaothong/giao_thong_backup_<ngày>.db /home/giaothong/giaothong-app/giao_thong.db
```

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
| Mất dữ liệu sau clone | Quên khôi phục DB | Restore từ file backup |

---

## XEM LOG KHI CÓ LỖI

```bash
# Xem 50 dòng log gần nhất
sudo journalctl -u giaothong -n 50

# Xem log realtime
sudo journalctl -u giaothong -f
```
