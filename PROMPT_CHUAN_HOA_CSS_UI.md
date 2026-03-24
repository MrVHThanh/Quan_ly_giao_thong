# PROMPT: Chuẩn hóa toàn bộ Giao diện & CSS — Dự án Quản lý Đường bộ Lào Cai
# Dán toàn bộ nội dung dưới đây vào Claude Code (VSCode) và nhấn Enter.
# ─────────────────────────────────────────────────────────────────────────────

---

## YÊU CẦU TỔNG QUAN

Hãy chuẩn hóa toàn bộ giao diện web của dự án Quản lý Đường bộ Lào Cai theo
một Design System thống nhất. Dự án dùng **FastAPI + Jinja2**, static files
phục vụ tại `/static/`, templates tại `templates/`.

**Phạm vi công việc gồm 5 phần, thực hiện theo đúng thứ tự:**

---

## PHẦN 1 — KHẢO SÁT TRƯỚC KHI LÀM

Trước khi viết bất kỳ dòng code nào, hãy đọc và liệt kê:

1. Đọc toàn bộ file `templates/base.html` — ghi nhận: thư viện CSS đang dùng
   (Bootstrap phiên bản nào?), cấu trúc sidebar, topbar, main-content.
2. Đọc `static/css/style.css` (nếu tồn tại) — ghi nhận các class/variable đã có.
3. Liệt kê tất cả file trong `templates/` (kể cả thư mục con auth/, tuyen_duong/,
   doan_tuyen/) — ghi nhận pattern HTML đang dùng.
4. Đọc `static/js/app.js` (nếu tồn tại).
5. Báo cáo ngắn gọn những gì tìm thấy trước khi bắt tay thực hiện.

---

## PHẦN 2 — TẠO DESIGN SYSTEM (Design Tokens)

Tạo file `static/css/design-system.css` với nội dung sau đây.
**Đây là nguồn sự thật duy nhất cho toàn bộ màu sắc, font, spacing.**
Mọi file CSS khác phải import file này, không được hardcode giá trị trực tiếp.

### 2.1 CSS Custom Properties (Variables)

```css
/* static/css/design-system.css */

:root {
  /* ── Brand Colors ── */
  --color-primary:        #1a3a5c;   /* Navy — màu chủ đạo (sidebar, header) */
  --color-primary-dark:   #122840;   /* Navy đậm hơn — hover sidebar */
  --color-primary-light:  #2a5298;   /* Navy nhạt — accent */
  --color-accent:         #e8a020;   /* Vàng cam — highlight, badge quan trọng */
  --color-accent-light:   #fef3dc;   /* Vàng cam nhạt — background badge */

  /* ── Semantic Colors ── */
  --color-success:        #28a745;
  --color-success-bg:     #d4edda;
  --color-warning:        #ffc107;
  --color-warning-bg:     #fff3cd;
  --color-danger:         #dc3545;
  --color-danger-bg:      #f8d7da;
  --color-info:           #17a2b8;
  --color-info-bg:        #d1ecf1;

  /* ── Tình trạng mặt đường (dùng trên badge + bản đồ) ── */
  --color-tt-tot:         #28a745;   /* TOT — Tốt */
  --color-tt-tb:          #ffc107;   /* TB — Trung bình */
  --color-tt-kem:         #fd7e14;   /* KEM — Kém */
  --color-tt-hh-nang:     #dc3545;   /* HH_NANG — Hư hỏng nặng */
  --color-tt-thi-cong:    #6f42c1;   /* THI_CONG — Đang thi công */
  --color-tt-bao-tri:     #20c997;   /* BAO_TRI — Bảo trì */
  --color-tt-chua-xd:     #adb5bd;   /* CHUA_XD — Chưa xây dựng */

  /* ── Neutral Colors ── */
  --color-bg-page:        #f0f4f8;   /* Nền trang */
  --color-bg-card:        #ffffff;   /* Nền card/bảng */
  --color-bg-hover:       #f8fafc;   /* Hover row bảng */
  --color-border:         #e2e8f0;   /* Đường kẻ */
  --color-border-strong:  #cbd5e0;
  --color-text-primary:   #1a202c;   /* Chữ chính */
  --color-text-secondary: #4a5568;   /* Chữ phụ */
  --color-text-muted:     #718096;   /* Chữ mờ */
  --color-text-disabled:  #a0aec0;

  /* ── Typography ── */
  --font-family-base:     'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
  --font-family-mono:     'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  --font-size-xs:         0.75rem;   /* 12px */
  --font-size-sm:         0.8125rem; /* 13px */
  --font-size-base:       0.875rem;  /* 14px — base toàn trang */
  --font-size-md:         0.9375rem; /* 15px */
  --font-size-lg:         1rem;      /* 16px */
  --font-size-xl:         1.125rem;  /* 18px */
  --font-size-2xl:        1.25rem;   /* 20px */
  --font-size-3xl:        1.5rem;    /* 24px */
  --font-weight-normal:   400;
  --font-weight-medium:   500;
  --font-weight-semibold: 600;
  --font-weight-bold:     700;
  --line-height-tight:    1.3;
  --line-height-base:     1.6;
  --line-height-loose:    1.8;

  /* ── Spacing Scale (bội số 4px) ── */
  --space-1:   0.25rem;   /*  4px */
  --space-2:   0.5rem;    /*  8px */
  --space-3:   0.75rem;   /* 12px */
  --space-4:   1rem;      /* 16px */
  --space-5:   1.25rem;   /* 20px */
  --space-6:   1.5rem;    /* 24px */
  --space-8:   2rem;      /* 32px */
  --space-10:  2.5rem;    /* 40px */
  --space-12:  3rem;      /* 48px */

  /* ── Border Radius ── */
  --radius-sm:  4px;
  --radius-md:  8px;
  --radius-lg:  12px;
  --radius-xl:  16px;
  --radius-full: 9999px;

  /* ── Shadows ── */
  --shadow-xs:  0 1px 2px rgba(0,0,0,.05);
  --shadow-sm:  0 1px 4px rgba(0,0,0,.08);
  --shadow-md:  0 4px 12px rgba(0,0,0,.10);
  --shadow-lg:  0 8px 24px rgba(0,0,0,.12);
  --shadow-xl:  0 16px 48px rgba(0,0,0,.16);

  /* ── Layout ── */
  --sidebar-width:       230px;
  --sidebar-collapsed:    64px;
  --topbar-height:        56px;
  --content-max-width:  1400px;

  /* ── Transitions ── */
  --transition-fast:  150ms ease;
  --transition-base:  250ms ease;
  --transition-slow:  400ms ease;

  /* ── Z-index Stack ── */
  --z-sidebar:  100;
  --z-topbar:   200;
  --z-dropdown: 300;
  --z-modal:    400;
  --z-toast:    500;
}
```

### 2.2 Utility Classes và Reset

Thêm vào cuối `design-system.css`:

```css
/* ── Base Reset ── */
*, *::before, *::after { box-sizing: border-box; }

html { font-size: 16px; scroll-behavior: smooth; }

body {
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background: var(--color-bg-page);
  line-height: var(--line-height-base);
  -webkit-font-smoothing: antialiased;
}

/* ── Typography Utilities ── */
.text-xs      { font-size: var(--font-size-xs); }
.text-sm      { font-size: var(--font-size-sm); }
.text-base    { font-size: var(--font-size-base); }
.text-lg      { font-size: var(--font-size-lg); }
.text-xl      { font-size: var(--font-size-xl); }
.text-muted   { color: var(--color-text-muted); }
.text-secondary { color: var(--color-text-secondary); }
.font-mono    { font-family: var(--font-family-mono); }
.font-medium  { font-weight: var(--font-weight-medium); }
.font-semibold { font-weight: var(--font-weight-semibold); }
.font-bold    { font-weight: var(--font-weight-bold); }

/* ── Badge Tình trạng mặt đường ── */
.badge-tt { display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 8px; border-radius: var(--radius-full);
  font-size: var(--font-size-xs); font-weight: var(--font-weight-semibold); }
.badge-tt-TOT      { background: var(--color-success-bg); color: var(--color-success); }
.badge-tt-TB       { background: var(--color-warning-bg); color: #856404; }
.badge-tt-KEM      { background: #ffe5d0; color: #c05621; }
.badge-tt-HH_NANG  { background: var(--color-danger-bg); color: var(--color-danger); }
.badge-tt-THI_CONG { background: #e8d8ff; color: #553c9a; }
.badge-tt-BAO_TRI  { background: #d0fff4; color: #0d6b54; }
.badge-tt-CHUA_XD  { background: #f1f3f5; color: #6c757d; }
.badge-tt-TAM_DONG { background: #f1f3f5; color: #6c757d; }
.badge-tt-NGUNG    { background: #f1f3f5; color: #6c757d; }

/* ── Badge Cấp quản lý ── */
.badge-cap-ql { display: inline-block; padding: 2px 8px; border-radius: var(--radius-full);
  font-size: var(--font-size-xs); font-weight: var(--font-weight-bold); letter-spacing: .03em; }
.badge-cap-QL  { background: #dbeafe; color: #1d4ed8; }
.badge-cap-DT  { background: #dcfce7; color: #16a34a; }
.badge-cap-DX  { background: #fef9c3; color: #854d0e; }
.badge-cap-DD  { background: #f3e8ff; color: #7e22ce; }

/* ── Lý trình ── */
.ly-trinh {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  color: var(--color-primary);
  font-weight: var(--font-weight-medium);
}

/* ── Số liệu km ── */
.chieu-dai {
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

/* ── Card chuẩn ── */
.card-gt {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.card-gt-header {
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--color-border);
  display: flex; align-items: center; justify-content: space-between;
}
.card-gt-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}
.card-gt-body { padding: var(--space-6); }

/* ── Stat Card (Dashboard) ── */
.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-base), transform var(--transition-base);
}
.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.stat-card-icon {
  width: 48px; height: 48px; border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem; margin-bottom: var(--space-3);
}
.stat-card-value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  line-height: 1;
  margin-bottom: var(--space-1);
}
.stat-card-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

/* ── Bảng dữ liệu chuẩn ── */
.table-gt { width: 100%; border-collapse: collapse; }
.table-gt thead th {
  padding: var(--space-2) var(--space-4);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: .06em;
  color: var(--color-text-muted);
  background: var(--color-bg-page);
  border-bottom: 1px solid var(--color-border-strong);
  white-space: nowrap;
}
.table-gt tbody td {
  padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border);
  vertical-align: middle;
}
.table-gt tbody tr { transition: background var(--transition-fast); }
.table-gt tbody tr:hover { background: var(--color-bg-hover); }
.table-gt tbody tr:last-child td { border-bottom: none; }

/* ── Nút bấm chuẩn ── */
.btn-gt {
  display: inline-flex; align-items: center; gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  border: 1px solid transparent;
  cursor: pointer; text-decoration: none;
  transition: all var(--transition-fast);
  white-space: nowrap;
}
.btn-gt-primary {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}
.btn-gt-primary:hover {
  background: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
  color: #fff; text-decoration: none;
}
.btn-gt-outline {
  background: transparent;
  color: var(--color-primary);
  border-color: var(--color-primary);
}
.btn-gt-outline:hover {
  background: var(--color-primary);
  color: #fff; text-decoration: none;
}
.btn-gt-danger { background: var(--color-danger); color: #fff; border-color: var(--color-danger); }
.btn-gt-danger:hover { background: #b91c1c; border-color: #b91c1c; color: #fff; }
.btn-gt-sm { padding: var(--space-1) var(--space-3); font-size: var(--font-size-xs); }
.btn-gt-icon { padding: var(--space-2); }

/* ── Form controls ── */
.form-gt-label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-1);
}
.form-gt-input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-family: var(--font-family-base);
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}
.form-gt-input:focus {
  outline: none;
  border-color: var(--color-primary-light);
  box-shadow: 0 0 0 3px rgba(42, 82, 152, .15);
}
.form-gt-input::placeholder { color: var(--color-text-disabled); }

/* ── Alert/Flash messages ── */
.alert-gt {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  border: 1px solid transparent;
  display: flex; align-items: flex-start; gap: var(--space-3);
}
.alert-gt-error   { background: var(--color-danger-bg);  border-color: #f5c6cb; color: #721c24; }
.alert-gt-success { background: var(--color-success-bg); border-color: #c3e6cb; color: #155724; }
.alert-gt-warning { background: var(--color-warning-bg); border-color: #ffeeba; color: #856404; }
.alert-gt-info    { background: var(--color-info-bg);    border-color: #bee5eb; color: #0c5460; }

/* ── Empty state ── */
.empty-state {
  text-align: center;
  padding: var(--space-12) var(--space-8);
  color: var(--color-text-muted);
}
.empty-state-icon { font-size: 3rem; margin-bottom: var(--space-4); opacity: .5; }
.empty-state-text { font-size: var(--font-size-md); margin-bottom: var(--space-2); }
.empty-state-hint { font-size: var(--font-size-sm); }
```

---

## PHẦN 3 — VIẾT LẠI `static/css/style.css` (Layout chính)

Tạo/ghi đè `static/css/style.css`. File này chỉ chứa layout (sidebar, topbar,
main-content, responsive). **Không hardcode màu sắc — luôn dùng var(--...) từ design-system.css.**

```css
/* static/css/style.css — Layout System */
/* Phụ thuộc: design-system.css phải được load trước */

/* ═══════════════════════════════════════════════════════
   1. SIDEBAR
═══════════════════════════════════════════════════════ */
.sidebar {
  position: fixed;
  top: 0; left: 0;
  width: var(--sidebar-width);
  height: 100vh;
  background: var(--color-primary);
  display: flex; flex-direction: column;
  z-index: var(--z-sidebar);
  overflow-y: auto;
  overflow-x: hidden;
  transition: width var(--transition-base);
}

/* Thanh cuộn sidebar mỏng */
.sidebar::-webkit-scrollbar { width: 4px; }
.sidebar::-webkit-scrollbar-thumb { background: rgba(255,255,255,.2); border-radius: 2px; }

/* Brand / Logo */
.sidebar-brand {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid rgba(255,255,255,.1);
  text-decoration: none; flex-shrink: 0;
}
.sidebar-brand-icon {
  width: 36px; height: 36px; flex-shrink: 0;
  background: var(--color-accent);
  border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; color: #fff;
}
.sidebar-brand-text { color: #fff; font-weight: var(--font-weight-bold);
  font-size: var(--font-size-sm); line-height: 1.3; }
.sidebar-brand-sub  { color: rgba(255,255,255,.5); font-size: var(--font-size-xs); }

/* Navigation sections */
.sidebar-section {
  padding: var(--space-5) var(--space-3) var(--space-2);
  flex: 1;
}
.sidebar-section-label {
  padding: var(--space-4) var(--space-3) var(--space-1);
  color: rgba(255,255,255,.35);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: .1em;
  font-weight: var(--font-weight-semibold);
}

/* Nav links */
.sidebar-link {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  color: rgba(255,255,255,.7);
  border-radius: var(--radius-md);
  text-decoration: none;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
  margin-bottom: 2px;
  white-space: nowrap;
}
.sidebar-link:hover {
  background: rgba(255,255,255,.1);
  color: #fff; text-decoration: none;
}
.sidebar-link.active {
  background: rgba(255,255,255,.18);
  color: #fff;
  box-shadow: inset 3px 0 0 var(--color-accent);
}
.sidebar-link-icon {
  width: 20px; text-align: center; flex-shrink: 0;
  font-size: var(--font-size-base);
}
.sidebar-badge {
  margin-left: auto;
  background: var(--color-accent);
  color: #fff;
  font-size: 10px;
  font-weight: var(--font-weight-bold);
  padding: 1px 6px;
  border-radius: var(--radius-full);
}

/* User info bottom */
.sidebar-user {
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid rgba(255,255,255,.1);
  display: flex; align-items: center; gap: var(--space-3);
  flex-shrink: 0;
}
.sidebar-user-avatar {
  width: 32px; height: 32px; border-radius: var(--radius-full);
  background: var(--color-accent); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: var(--font-size-sm); font-weight: var(--font-weight-bold);
  flex-shrink: 0;
}
.sidebar-user-name  { color: #fff; font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium); }
.sidebar-user-role  { color: rgba(255,255,255,.5); font-size: var(--font-size-xs); }
.sidebar-user-logout { margin-left: auto; color: rgba(255,255,255,.5);
  text-decoration: none; font-size: var(--font-size-lg);
  transition: color var(--transition-fast); }
.sidebar-user-logout:hover { color: #fff; }

/* ═══════════════════════════════════════════════════════
   2. TOPBAR
═══════════════════════════════════════════════════════ */
.topbar {
  position: sticky; top: 0;
  height: var(--topbar-height);
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border);
  display: flex; align-items: center;
  padding: 0 var(--space-6);
  gap: var(--space-4);
  z-index: var(--z-topbar);
  margin-bottom: var(--space-6);
  box-shadow: var(--shadow-xs);
}
.topbar-breadcrumb {
  display: flex; align-items: center; gap: var(--space-2);
  font-size: var(--font-size-sm); color: var(--color-text-muted);
  flex: 1;
}
.topbar-breadcrumb a { color: var(--color-primary); text-decoration: none; }
.topbar-breadcrumb a:hover { text-decoration: underline; }
.topbar-breadcrumb .sep { color: var(--color-border-strong); }
.topbar-breadcrumb .current { color: var(--color-text-primary);
  font-weight: var(--font-weight-medium); }
.topbar-actions { display: flex; align-items: center; gap: var(--space-3); }

/* ═══════════════════════════════════════════════════════
   3. MAIN LAYOUT
═══════════════════════════════════════════════════════ */
.app-layout {
  display: flex;
  min-height: 100vh;
}
.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  min-width: 0;
  display: flex; flex-direction: column;
}
.page-body {
  flex: 1;
  padding: 0 var(--space-6) var(--space-8);
  max-width: var(--content-max-width);
  width: 100%;
}

/* Page header */
.page-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  flex-wrap: wrap;
}
.page-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1);
  line-height: var(--line-height-tight);
}
.page-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}
.page-actions { display: flex; gap: var(--space-3); flex-wrap: wrap; }

/* ═══════════════════════════════════════════════════════
   4. GRID SYSTEM
═══════════════════════════════════════════════════════ */
.grid { display: grid; gap: var(--space-6); }
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }
.grid-stat { grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }

/* ═══════════════════════════════════════════════════════
   5. RESPONSIVE — Mobile & Tablet
═══════════════════════════════════════════════════════ */
@media (max-width: 1200px) {
  .grid-4 { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 992px) {
  :root { --sidebar-width: 0px; }

  .sidebar {
    width: var(--sidebar-width);
    transform: translateX(-100%);
  }
  .sidebar.open {
    width: 230px;
    transform: translateX(0);
    box-shadow: var(--shadow-xl);
  }
  .main-content { margin-left: 0; }
  .grid-3 { grid-template-columns: repeat(2, 1fr); }
  .grid-2 { grid-template-columns: 1fr; }

  /* Nút hamburger hiện trên mobile */
  .sidebar-toggle { display: flex !important; }
}

@media (max-width: 768px) {
  .page-body { padding: 0 var(--space-4) var(--space-6); }
  .topbar    { padding: 0 var(--space-4); }
  .grid-3, .grid-4 { grid-template-columns: 1fr; }
  .grid-stat { grid-template-columns: repeat(2, 1fr); }
  .page-header { flex-direction: column; align-items: stretch; }

  /* Bảng scroll ngang trên mobile */
  .table-responsive-gt { overflow-x: auto; -webkit-overflow-scrolling: touch; }

  /* Ẩn cột phụ trên mobile */
  .col-hidden-mobile { display: none; }
}

@media (max-width: 480px) {
  .grid-stat { grid-template-columns: 1fr; }
  .topbar-breadcrumb .breadcrumb-long { display: none; }
}

/* ═══════════════════════════════════════════════════════
   6. OVERLAY (khi sidebar mở trên mobile)
═══════════════════════════════════════════════════════ */
.sidebar-overlay {
  display: none;
  position: fixed; inset: 0;
  background: rgba(0,0,0,.4);
  z-index: calc(var(--z-sidebar) - 1);
  opacity: 0; transition: opacity var(--transition-base);
}
.sidebar-overlay.visible { display: block; opacity: 1; }

/* ═══════════════════════════════════════════════════════
   7. ANIMATIONS
═══════════════════════════════════════════════════════ */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes slideInRight {
  from { opacity: 0; transform: translateX(20px); }
  to   { opacity: 1; transform: translateX(0); }
}
.animate-fade-in { animation: fadeIn var(--transition-base) both; }

/* Stagger children */
.stagger > * { animation: fadeIn var(--transition-base) both; }
.stagger > *:nth-child(1) { animation-delay: 0ms; }
.stagger > *:nth-child(2) { animation-delay: 60ms; }
.stagger > *:nth-child(3) { animation-delay: 120ms; }
.stagger > *:nth-child(4) { animation-delay: 180ms; }

/* ═══════════════════════════════════════════════════════
   8. LOADING / SKELETON
═══════════════════════════════════════════════════════ */
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.4s infinite;
  border-radius: var(--radius-sm);
}
@keyframes skeleton-loading {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ═══════════════════════════════════════════════════════
   9. PRINT
═══════════════════════════════════════════════════════ */
@media print {
  .sidebar, .topbar, .page-actions,
  .btn-gt, .sidebar-toggle { display: none !important; }
  .main-content { margin-left: 0 !important; }
  .page-body { padding: 0 !important; }
  .card-gt { box-shadow: none !important; border: 1px solid #ccc; }
}
```

---

## PHẦN 4 — VIẾT LẠI `static/js/app.js` (Interactions)

Tạo/ghi đè `static/js/app.js`:

```javascript
/* static/js/app.js — Global Interactions
 * Yêu cầu: Bootstrap 5.x đã load
 */

'use strict';

/* ── 1. Sidebar toggle (mobile) ───────────────────────────── */
(function initSidebar() {
  const sidebar  = document.querySelector('.sidebar');
  const overlay  = document.querySelector('.sidebar-overlay');
  const toggles  = document.querySelectorAll('[data-sidebar-toggle]');
  if (!sidebar) return;

  function open()  { sidebar.classList.add('open');    overlay?.classList.add('visible'); }
  function close() { sidebar.classList.remove('open'); overlay?.classList.remove('visible'); }

  toggles.forEach(btn => btn.addEventListener('click', () =>
    sidebar.classList.contains('open') ? close() : open()
  ));
  overlay?.addEventListener('click', close);

  // Đánh dấu link active theo URL hiện tại
  const path = window.location.pathname;
  document.querySelectorAll('.sidebar-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) {
      link.classList.add('active');
    } else if (href === '/' && path === '/') {
      link.classList.add('active');
    }
  });
})();

/* ── 2. Flash messages tự đóng ───────────────────────────── */
(function initAlerts() {
  document.querySelectorAll('.alert-gt[data-auto-close]').forEach(el => {
    const delay = parseInt(el.dataset.autoClose) || 4000;
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s ease';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, delay);
  });
})();

/* ── 3. Confirm xóa ──────────────────────────────────────── */
(function initConfirmDelete() {
  document.addEventListener('submit', function(e) {
    const form = e.target;
    if (!form.dataset.confirmDelete) return;
    const msg = form.dataset.confirmDelete || 'Bạn chắc chắn muốn xóa?';
    if (!confirm(msg)) e.preventDefault();
  });
  // Hỗ trợ button có data-confirm
  document.addEventListener('click', function(e) {
    const btn = e.target.closest('[data-confirm]');
    if (!btn) return;
    if (!confirm(btn.dataset.confirm)) e.preventDefault();
  });
})();

/* ── 4. Tooltip Bootstrap ────────────────────────────────── */
(function initTooltips() {
  if (typeof bootstrap === 'undefined') return;
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el, { trigger: 'hover', delay: { show: 300, hide: 100 } });
  });
})();

/* ── 5. Bảng — sort & filter phía client ────────────────── */
(function initTableFilter() {
  const input = document.querySelector('[data-table-filter]');
  if (!input) return;
  const targetId = input.dataset.tableFilter;
  const table = document.getElementById(targetId);
  if (!table) return;
  const rows = Array.from(table.querySelectorAll('tbody tr'));

  input.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase();
    rows.forEach(row => {
      row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
  });
})();

/* ── 6. Active nav highlight ─────────────────────────────── */
(function highlightActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('a[data-nav]').forEach(a => {
    if (path.startsWith(a.getAttribute('href'))) a.classList.add('active');
  });
})();

/* ── 7. Smooth number counter (dashboard stats) ─────────── */
(function initCounters() {
  const counters = document.querySelectorAll('[data-count-to]');
  if (!counters.length || !window.IntersectionObserver) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el    = entry.target;
      const end   = parseFloat(el.dataset.countTo);
      const dec   = el.dataset.decimals ? parseInt(el.dataset.decimals) : 0;
      const dur   = 800;
      const start = performance.now();

      function step(now) {
        const p = Math.min((now - start) / dur, 1);
        const ease = 1 - Math.pow(1 - p, 3); // ease-out cubic
        el.textContent = (end * ease).toFixed(dec);
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
      observer.unobserve(el);
    });
  }, { threshold: 0.3 });

  counters.forEach(el => observer.observe(el));
})();

/* ── 8. Toast notification ───────────────────────────────── */
window.showToast = function(message, type = 'info', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = `
      position: fixed; bottom: 1.5rem; right: 1.5rem;
      display: flex; flex-direction: column; gap: 0.5rem;
      z-index: 9999; pointer-events: none;
    `;
    document.body.appendChild(container);
  }

  const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
  const toast = document.createElement('div');
  toast.className = `alert-gt alert-gt-${type === 'error' ? 'error' : type}`;
  toast.style.cssText = `
    pointer-events: all; min-width: 260px; max-width: 380px;
    box-shadow: var(--shadow-lg); animation: slideInRight 0.25s ease both;
  `;
  toast.innerHTML = `<span>${icons[type] || 'ℹ'}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.3s, transform 0.3s';
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    setTimeout(() => toast.remove(), 300);
  }, duration);
};
```

---

## PHẦN 5 — CẬP NHẬT `templates/base.html`

Viết lại `templates/base.html` theo cấu trúc mới, sử dụng đúng các class từ
design-system.css và style.css vừa tạo. Template phải:

1. Load `design-system.css` TRƯỚC `style.css` — TRƯỚC Bootstrap
2. Load Google Fonts Inter (woff2) với `font-display: swap`
3. Sidebar có `brand`, `nav-section`, `sidebar-link` đúng cấu trúc
4. Topbar có breadcrumb `{% block breadcrumb %}` và actions `{% block topbar_actions %}`
5. `{% block page_header %}` — tiêu đề trang (page-title + page-subtitle + page-actions)
6. `{% block content %}` — nội dung chính
7. Nút hamburger `.sidebar-toggle` (hiển thị trên mobile, ẩn trên desktop)
8. `.sidebar-overlay` cho mobile
9. Load `app.js` ở cuối body với `defer`
10. Hỗ trợ `{% block extra_css %}` và `{% block extra_js %}` để trang con inject thêm

Cấu trúc Jinja2 context variables cần truyền: `user` (dict với `loai_quyen`, `ho_ten`).

---

## PHẦN 6 — CẬP NHẬT TẤT CẢ TEMPLATES CON

Sau khi `base.html` xong, duyệt qua **toàn bộ** các template sau và cập nhật
để sử dụng đúng class từ Design System mới (thay thế class Bootstrap raw bằng
class `.card-gt`, `.table-gt`, `.btn-gt-*`, `.badge-tt-*`, `.badge-cap-*`,
`.stat-card`, `.form-gt-*`, `.alert-gt-*`):

**Danh sách templates cần cập nhật:**
- `templates/dashboard.html`
- `templates/thong_ke.html`
- `templates/ban_do.html`
- `templates/auth/login.html`
- `templates/auth/dang_ky.html`
- `templates/tuyen_duong/danh_sach.html`
- `templates/tuyen_duong/chi_tiet.html`
- `templates/tuyen_duong/form.html`
- `templates/doan_tuyen/danh_sach.html`
- `templates/doan_tuyen/chi_tiet.html`
- `templates/doan_tuyen/form.html`

**Với mỗi template, thực hiện:**
1. Thay `class="card"` → `class="card-gt"`
2. Thay `class="table table-hover"` → `class="table-gt"`
3. Thay `class="btn btn-primary btn-sm"` → `class="btn-gt btn-gt-primary btn-gt-sm"`
4. Thay `class="badge bg-success"` theo tình trạng → `class="badge-tt badge-tt-{MA_TT}"`
5. Thay `class="badge"` cấp quản lý → `class="badge-cap-ql badge-cap-{MA_CAP}"`
6. Các ô lý trình → thêm `class="ly-trinh"` (dùng Jinja2 filter `| format_ly_trinh`)
7. Các form input → `class="form-gt-input"`, label → `class="form-gt-label"`
8. Các thông báo lỗi/thành công → `class="alert-gt alert-gt-{type}" data-auto-close="5000"`
9. Bảng bọc trong `<div class="table-responsive-gt">` nếu nhiều cột
10. Trang danh sách: thêm `data-table-filter="id-bảng"` vào ô tìm kiếm

---

## KIỂM TRA SAU KHI HOÀN THÀNH

Sau khi thực hiện xong toàn bộ 6 phần trên, hãy:

1. Chạy `uvicorn api.main:app --reload` và kiểm tra không có lỗi import
2. Liệt kê tất cả file đã tạo mới và đã sửa đổi
3. Báo cáo nếu có template nào chưa được cập nhật
4. Xác nhận `design-system.css` được load trên tất cả trang (qua `base.html`)
5. Ghi ngắn gọn class nào từ Bootstrap vẫn được dùng (override) để biết phụ thuộc

**Ưu tiên xử lý nếu gặp conflict Bootstrap:**
- Bootstrap utility class (`d-flex`, `mb-3`, `col-md-6`...) vẫn GIỮ NGUYÊN
- Chỉ thay thế Bootstrap component classes (card, table, btn, badge, alert, form-control)
  bằng class `.gt-*` tương ứng
- Không xóa Bootstrap — vẫn dùng grid (`row/col`) và modal của Bootstrap nếu có

---

## LƯU Ý QUAN TRỌNG

- **KHÔNG** tạo file CSS riêng cho từng trang — chỉ dùng `{% block extra_css %}`
  cho overrides tối thiểu nếu thật sự cần
- **KHÔNG** hardcode màu hex/rgb trực tiếp trong HTML style attribute
- **KHÔNG** xóa Bootstrap — bổ sung, không thay thế
- Mọi giá trị màu/spacing/font phải qua CSS variable `var(--...)`
- Khi sửa template Jinja2, **giữ nguyên** toàn bộ logic `{% for %}`, `{% if %}`,
  `{{ biến }}` — chỉ thay đổi phần HTML/class
