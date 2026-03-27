/* static/js/app.js — Global Interactions
 * Yêu cầu: Bootstrap 5.x đã load
 */

'use strict';

/* ── 1. Sidebar toggle ────────────────────────────────────── */
(function initSidebar() {
  const sidebar     = document.getElementById('sidebar');
  const mainContent = document.getElementById('mainContent');
  const overlay     = document.querySelector('.sidebar-overlay');
  const btn         = document.getElementById('btnToggleSidebar');
  const icon        = document.getElementById('iconToggle');
  if (!sidebar || !btn) return;

  const KEY         = 'sidebar_hidden';
  const isMobile    = () => window.innerWidth <= 992;

  // Desktop: ẩn/hiện sidebar với localStorage
  function applyDesktopState(hidden, animate) {
    if (!animate) {
      sidebar.style.transition     = 'none';
      mainContent.style.transition = 'none';
    }
    sidebar.classList.toggle('hidden', hidden);
    if (mainContent) mainContent.classList.toggle('expanded', hidden);
    if (icon) icon.className = hidden ? 'bi bi-layout-sidebar' : 'bi bi-list';
    btn.title = hidden ? 'Hiện menu' : 'Ẩn menu';
    if (!animate) {
      requestAnimationFrame(() => {
        sidebar.style.transition     = '';
        mainContent.style.transition = '';
      });
    }
    localStorage.setItem(KEY, hidden ? '1' : '0');
  }

  // Mobile: mở/đóng với overlay
  function openMobile()  {
    sidebar.classList.add('open');
    overlay?.classList.add('visible');
  }
  function closeMobile() {
    sidebar.classList.remove('open');
    overlay?.classList.remove('visible');
  }

  // Khởi tạo: khôi phục trạng thái desktop không animation
  if (!isMobile()) {
    applyDesktopState(localStorage.getItem(KEY) === '1', false);
  }

  btn.addEventListener('click', function() {
    if (isMobile()) {
      sidebar.classList.contains('open') ? closeMobile() : openMobile();
    } else {
      applyDesktopState(!sidebar.classList.contains('hidden'), true);
    }
  });

  overlay?.addEventListener('click', closeMobile);

  // Khi resize từ mobile → desktop, đóng mobile overlay
  window.addEventListener('resize', function() {
    if (!isMobile()) {
      closeMobile();
      applyDesktopState(localStorage.getItem(KEY) === '1', false);
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

/* ── 5. Bảng — filter phía client ───────────────────────── */
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

/* ── 6. Smooth number counter (dashboard stats) ─────────── */
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
        const p    = Math.min((now - start) / dur, 1);
        const ease = 1 - Math.pow(1 - p, 3);
        el.textContent = (end * ease).toFixed(dec);
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
      observer.unobserve(el);
    });
  }, { threshold: 0.3 });

  counters.forEach(el => observer.observe(el));
})();

/* ── 7. Toast notification ───────────────────────────────── */
window.showToast = function(message, type = 'info', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = [
      'position:fixed', 'bottom:1.5rem', 'right:1.5rem',
      'display:flex', 'flex-direction:column', 'gap:0.5rem',
      'z-index:9999', 'pointer-events:none'
    ].join(';');
    document.body.appendChild(container);
  }

  const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
  const toast = document.createElement('div');
  toast.className = `alert-gt alert-gt-${type}`;
  toast.style.cssText = 'pointer-events:all;min-width:260px;max-width:380px;box-shadow:var(--shadow-lg);animation:slideInRight 0.25s ease both;';
  toast.innerHTML = `<span>${icons[type] || 'ℹ'}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 0.3s, transform 0.3s';
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    setTimeout(() => toast.remove(), 300);
  }, duration);
};

/* ── 8. Sidebar group toggle (Dữ liệu / Hệ thống) ───────── */
(function initSidebarGroups() {
  document.querySelectorAll('.sidebar-group-toggle').forEach(btn => {
    const groupId = btn.dataset.group;
    const group   = document.getElementById('group-' + groupId);
    if (!group) return;

    // Khởi tạo: mở nếu có class open (server render active link)
    if (btn.classList.contains('open')) {
      group.classList.add('open');
    }

    btn.addEventListener('click', function() {
      const isOpen = group.classList.contains('open');
      group.classList.toggle('open', !isOpen);
      btn.classList.toggle('open', !isOpen);
    });
  });
})();
