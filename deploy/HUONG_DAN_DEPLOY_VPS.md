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

---

## QUY TRÌNH HOÀN CHỈNH

### BƯỚC 1 — Trên máy local: Gộp code vào nhánh main

```bash
# 1. Đảm bảo đang ở nhánh develop và code đã commit đầy đủ
git status

# 2. Chuyển sang nhánh main
git checkout main

# 3. Merge code từ develop vào main
git merge develop

# 4. Push main lên GitHub
git push origin main

# 5. Quay lại develop để tiếp tục làm việc
git checkout develop
```

---

### BƯỚC 2 — Trên VPS: Kéo code mới về

```bash
# SSH vào VPS rồi chạy:
cd /home/giaothong/giaothong-app && git pull origin main
```

---

### BƯỚC 3 — Trên VPS: Chạy migration (nếu có bảng/cột mới)

> Chỉ cần chạy khi có thêm bảng hoặc cột mới trong DB.
> Nếu chỉ sửa giao diện/logic thì bỏ qua bước này.

```bash
# Ví dụ chạy migration m002
/home/giaothong/giaothong-app/venv/bin/python3 -c "from config.database import get_connection; from migrations.m002_nhat_ky import up; conn = get_connection(); up(conn); conn.close(); print('Migration OK')"
```

**Cú pháp chung cho migration bất kỳ:**
```bash
/home/giaothong/giaothong-app/venv/bin/python3 -c "from config.database import get_connection; from migrations.TEN_MIGRATION import up; conn = get_connection(); up(conn); conn.close(); print('OK')"
```

---

### BƯỚC 4 — Trên VPS: Khởi động lại service

```bash
sudo systemctl restart giaothong
```

---

### BƯỚC 5 — Kiểm tra service đang chạy

```bash
sudo systemctl status giaothong
```

Kết quả mong đợi: `Active: active (running)`

---

### BƯỚC 6 — Người dùng đăng xuất & đăng nhập lại

> Cần thực hiện khi có thay đổi liên quan đến **session / thông tin người dùng**
> (ví dụ: thêm trường `ho_ten` vào session token).

- Mỗi người dùng vào trang web → click **Đăng xuất** → **Đăng nhập lại**
- Cookie cũ sẽ được thay bằng cookie mới có đầy đủ thông tin

---

## TÓM TẮT NHANH (không có migration)

```bash
# === MÁY LOCAL ===
git checkout main
git merge develop
git push origin main
git checkout develop

# === TRÊN VPS ===
cd /home/giaothong/giaothong-app && git pull origin main
sudo systemctl restart giaothong
sudo systemctl status giaothong
```

---

## TÓM TẮT NHANH (có migration)

```bash
# === MÁY LOCAL ===
git checkout main
git merge develop
git push origin main
git checkout develop

# === TRÊN VPS ===
cd /home/giaothong/giaothong-app && git pull origin main

# Chạy migration (thay TEN_MIGRATION cho đúng)
/home/giaothong/giaothong-app/venv/bin/python3 -c "from config.database import get_connection; from migrations.TEN_MIGRATION import up; conn = get_connection(); up(conn); conn.close(); print('OK')"

sudo systemctl restart giaothong
sudo systemctl status giaothong
```

---

## XỬ LÝ LỖI THƯỜNG GẶP

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| Trang web không cập nhật | Trình duyệt cache | Bấm `Ctrl + Shift + R` |
| Thông tin người dùng không đổi | Session cũ | Đăng xuất → đăng nhập lại |
| `IndentationError` khi chạy python -c | Copy có dấu cách đầu dòng | Dùng dấu `;` thay xuống dòng |
| Service không start | Lỗi code Python | Chạy `sudo journalctl -u giaothong -n 50` để xem log |
| `Migration OK` không in ra | Lỗi import | Kiểm tra tên file migration |

---

## XEM LOG KHI CÓ LỖI

```bash
# Xem 50 dòng log gần nhất
sudo journalctl -u giaothong -n 50

# Xem log realtime
sudo journalctl -u giaothong -f
```
