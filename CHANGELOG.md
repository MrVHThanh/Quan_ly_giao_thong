# Changelog — Hệ thống Quản lý Đường bộ Lào Cai

Mọi thay đổi quan trọng của dự án được ghi lại tại đây.
Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/).
Versioning theo [Semantic Versioning](https://semver.org/).

---

## [v1.0.2] — 2026-03-27

### Thêm mới
- Script `tools/import_tai_khoan.py` — import danh sách tài khoản từ file Excel vào DB, idempotent
- File `Danh_sach_tai_khoan_sxd.xlsx` — mẫu danh sách tài khoản chuẩn (có header, ghi chú mặc định)
- Hướng dẫn deploy VPS đầy đủ (`deploy/HUONG_DAN_DEPLOY_VPS.md`): Clone mới, Cập nhật, backup DB, rollback

### Cải thiện
- DB trên VPS tách ra ngoài thư mục dự án: `/home/giaothong/data/giao_thong.db` — tránh mất dữ liệu khi clone mới
- `config/database.py`: `DB_PATH` đọc từ biến môi trường `.env` thay vì hardcode; fix lỗi `makedirs` với đường dẫn tương đối
- Logo sidebar nhỏ hơn trên điện thoại nhỏ (≤576px): 24px
- Sidebar mobile: `z-index` tăng lên 1000 — không bị bản đồ Leaflet che khuất

### Sửa lỗi
- Sidebar bị bản đồ Leaflet đè lên trên mobile (Leaflet dùng z-index 400–700)
- Logo hiển thị quá to trên điện thoại nhỏ
- `DB_PATH` hardcode khiến VPS tạo DB rỗng trong thư mục dự án thay vì dùng đường dẫn trong `.env`

---

## [v1.0.1] — 2026-03-27

### Thêm mới
- Nhật ký hệ thống: ghi log đăng nhập (IP, vị trí, trình duyệt, thành công/thất bại)
- Nhật ký hoạt động: tự động ghi các thao tác THÊM/SỬA/XÓA/XUẤT EXCEL qua middleware
- Tra vị trí địa lý từ IP đăng nhập (ip-api.com), nhận biết mạng nội bộ
- Mật khẩu tạm thời: ADMIN có thể tạo mật khẩu ngẫu nhiên và copy thông báo cho người dùng
- Form đăng ký: placeholder, hướng dẫn định dạng, validate realtime, giữ dữ liệu khi lỗi
- Sidebar thu gọn: nhóm "Dữ liệu" và "Hệ thống" có nút đóng/mở
- Bảng dữ liệu: cuộn ngang trên mobile, cột đầu tiên cố định (sticky)
- Logo Sở Xây dựng Lào Cai hiển thị trên sidebar
- `migrate.py`: công cụ chạy migration tự động, có theo dõi lịch sử
- `deploy/HUONG_DAN_DEPLOY_VPS.md`: tài liệu hướng dẫn deploy lên VPS

### Cải thiện
- Sidebar hiển thị Họ tên và Quyền (Quản trị viên/Biên tập/Xem) thay vì ID
- Topbar hiển thị Họ tên thay vì ID
- Tăng độ tương phản chữ trên mobile (đạt chuẩn WCAG AA)
- Logo responsive: layout ngang trên mobile, dọc trên desktop
- Sidebar mobile: z-index cao hơn topbar, không bị che khuất
- Session token lưu thêm `ho_ten` để hiển thị ngay sau đăng nhập
- Dashboard (`/`) truyền `user` vào template, sidebar load đầy đủ ngay khi đăng nhập

### Sửa lỗi
- Sidebar không load hết menu khi mới đăng nhập vào trang chủ
- Chữ cột đầu bị chồng lên khi cuộn ngang bảng
- Sidebar mobile bị topbar che khuất phần trên

---

## [v1.0.0] — 2026-03-22

### Thêm mới
- Hệ thống quản lý tuyến đường (49 tuyến: QL, DT, DX)
- Quản lý đoạn tuyến (222 đoạn)
- Quản lý đoạn đi chung (15 đoạn)
- Thống kê tổng hợp và chi tiết theo cấp quản lý
- Bản đồ Leaflet tích hợp GeoJSON
- Quản lý người dùng: đăng ký, duyệt tài khoản, phân quyền (ADMIN/BIEN_TAP/XEM)
- Xuất dữ liệu ra Excel
- Giao diện chuẩn hóa CSS Design System
- Triển khai lên VPS với Gunicorn + Nginx + Systemd

---

## Quy tắc versioning

| Loại thay đổi | Tăng phần nào |
|---|---|
| Thêm tính năng lớn | MINOR (1.**1**.0) |
| Sửa lỗi, cải thiện nhỏ | PATCH (1.0.**1**) |
| Thay đổi cấu trúc lớn, không tương thích | MAJOR (**2**.0.0) |
