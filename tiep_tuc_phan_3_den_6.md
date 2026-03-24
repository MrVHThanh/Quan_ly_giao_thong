# PROMPT: Tiếp tục chuẩn hóa UI — Phần 3 đến Phần 6
# Đặt file này vào: D:\Dropbox\@Giaothong2\prompts\tiep_tuc_phan_3_den_6.md
# Gọi trong Claude Code bằng: @prompts/tiep_tuc_phan_3_den_6.md

---

Phần 1 và Phần 2 đã hoàn thành với kết quả như sau:
- Bootstrap 5.3.2 + Bootstrap Icons 1.11.3 (CDN) — GIỮ NGUYÊN, không xóa
- static/css/design-system.css đã tạo đầy đủ và đã link vào base.html
- CSS cũ hoàn toàn inline trong <style> của base.html — cần chuyển ra file riêng
- 21 template files trong 6 thư mục: auth/, tuyen_duong/, doan_tuyen/ và các file gốc
- Sidebar hiện tại: 220px, navy #1a3a5c, đã có toggle

Hãy thực hiện tiếp Phần 3 → Phần 6 theo đúng thứ tự:

---

## PHẦN 3 — Tạo static/css/style.css

- Chuyển toàn bộ CSS inline đang có trong `<style>` của base.html ra file này
- Viết lại theo cấu trúc layout chuẩn (sidebar, topbar, main-content, responsive)
- Thay mọi màu hex cứng bằng `var(--...)` từ design-system.css
- Giữ nguyên các giá trị sidebar 220px và màu #1a3a5c nhưng ánh xạ sang
  `var(--sidebar-width)` và `var(--color-primary)`
- Xóa toàn bộ `<style>` inline khỏi base.html sau khi đã chuyển xong
- Báo cáo xong Phần 3 rồi tiếp tục ngay Phần 4

---

## PHẦN 4 — Tạo static/js/app.js

- Tạo file mới hoàn toàn theo spec trong `@prompts/chuan_hoa_css_ui.md` (Phần 4)
- Kiểm tra toggle sidebar hiện có trong base.html — nếu đã có JS inline thì
  hợp nhất vào app.js rồi xóa JS inline khỏi base.html
- Báo cáo xong Phần 4 rồi tiếp tục ngay Phần 5

---

## PHẦN 5 — Cập nhật base.html

- Thêm `<link>` load design-system.css TRƯỚC style.css, cả hai TRƯỚC Bootstrap
- Thêm Google Fonts Inter với `font-display:swap`
- Thêm `<script src="/static/js/app.js" defer>` cuối body
- Thêm `{% block extra_css %}{% endblock %}` trong `<head>`
- Thêm `{% block extra_js %}{% endblock %}` trước `</body>`
- Thêm `<div class="sidebar-overlay"></div>` ngay sau thẻ mở `<body>`
- GIỮ NGUYÊN toàn bộ logic Jinja2 `{% %}` và `{{ }}` hiện có — chỉ thay đổi HTML/class
- Báo cáo xong Phần 5 rồi tiếp tục ngay Phần 6

---

## PHẦN 6 — Cập nhật 21 templates

Xử lý theo nhóm, báo cáo tiến độ sau mỗi nhóm rồi tiếp tục nhóm tiếp theo:

**Nhóm A — Templates gốc** (dashboard.html, thong_ke.html, ban_do.html):
- Thay `class="card"` → `class="card-gt"`
- Thay `class="card-body"` → `class="card-gt-body"`
- Thay `class="card-header"` → `class="card-gt-header"`
- Thay `class="btn btn-primary"` → `class="btn-gt btn-gt-primary"`
- Thay `class="btn btn-sm btn-primary"` → `class="btn-gt btn-gt-primary btn-gt-sm"`
- Thay `class="btn btn-danger"` → `class="btn-gt btn-gt-danger"`
- Thay `class="btn btn-outline-*"` → `class="btn-gt btn-gt-outline"`

**Nhóm B — Auth** (auth/login.html, auth/dang_ky.html):
- Form input → `class="form-gt-input"`
- Form label → `class="form-gt-label"`
- Thông báo lỗi → `class="alert-gt alert-gt-error" data-auto-close="5000"`
- Thông báo thành công → `class="alert-gt alert-gt-success" data-auto-close="5000"`

**Nhóm C — Tuyến đường** (tuyen_duong/danh_sach.html, chi_tiet.html, form.html):
- `class="table table-hover"` → `class="table-gt"`
- Bọc bảng trong `<div class="table-responsive-gt">`
- Badge cấp quản lý → `class="badge-cap-ql badge-cap-{{ tuyen.ma_cap_quan_ly }}"`
- Ô lý trình → thêm `class="ly-trinh"` (giữ filter `| format_ly_trinh`)
- Ô chiều dài km → thêm `class="chieu-dai"`
- Ô tìm kiếm/lọc → thêm `data-table-filter="id-của-bảng"`

**Nhóm D — Đoạn tuyến** (doan_tuyen/danh_sach.html, chi_tiet.html, form.html):
- Tương tự Nhóm C cho bảng và form
- Badge tình trạng → `class="badge-tt badge-tt-{{ doan.ma_tinh_trang }}"`
- Badge kết cấu mặt → `class="badge-cap-ql"` với màu phù hợp

**Nhóm E — Còn lại** (doan_di_chung/, các template chưa xử lý):
- Áp dụng tương tự các nhóm trên theo từng loại phần tử

---

## YÊU CẦU BÁO CÁO CUỐI CÙNG

Sau khi hoàn thành toàn bộ Phần 3 → 6, lập báo cáo gồm:

1. **Danh sách file đã tạo mới** (tên file + mô tả ngắn)
2. **Danh sách file đã sửa** (tên file + những gì thay đổi)
3. **Template chưa cập nhật** (nếu có, lý do tại sao)
4. **Bootstrap utility class còn giữ** (d-flex, mb-3, col-md-...) — liệt kê để biết phụ thuộc
5. **Kết quả chạy thử** — chạy `uvicorn api.main:app --reload`, có lỗi nào không

---

## LƯU Ý KHI THỰC HIỆN

- KHÔNG xóa Bootstrap — chỉ thay thế component classes (card, btn, table, badge, alert)
- GIỮ NGUYÊN Bootstrap utility classes (d-flex, mb-3, col-md-6, gap-2, ...)
- KHÔNG hardcode màu hex trong file CSS mới — dùng var(--...)
- KHÔNG thêm `<style>` inline mới vào bất kỳ template nào
- Nếu template có CSS inline trong `{% block extra_css %}` — giữ nguyên, không xóa
