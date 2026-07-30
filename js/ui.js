/**
 * DistaMate — UI Helpers
 * Toast notifications, modals, loaders
 */

// ── Toast Notifications ──────────────────────────────────────────
export const toast = {
  show(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toast-container');
    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };

    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.innerHTML = `
      <span class="toast-icon">${icons[type] || '💬'}</span>
      <span class="toast-msg">${message}</span>
    `;
    container.appendChild(t);

    setTimeout(() => {
      t.classList.add('removing');
      setTimeout(() => t.remove(), 250);
    }, duration);
  },
  success: (msg, dur) => toast.show(msg, 'success', dur),
  error:   (msg, dur) => toast.show(msg, 'error', dur),
  warning: (msg, dur) => toast.show(msg, 'warning', dur),
  info:    (msg, dur) => toast.show(msg, 'info', dur),
};

// ── Modal ────────────────────────────────────────────────────────
export const modal = {
  _resolve: null,

  show({ title, body, buttons = [], width = '520px' }) {
    const overlay = document.getElementById('modal-overlay');
    const container = document.getElementById('modal-container');
    const titleEl = document.getElementById('modal-title');
    const bodyEl  = document.getElementById('modal-body');
    const footerEl = document.getElementById('modal-footer');

    titleEl.textContent = title;
    if (typeof body === 'string') {
      bodyEl.innerHTML = body;
    } else {
      bodyEl.innerHTML = '';
      bodyEl.appendChild(body);
    }

    footerEl.innerHTML = '';
    buttons.forEach(btn => {
      const b = document.createElement('button');
      b.className = `btn ${btn.class || 'btn-secondary'}`;
      b.textContent = btn.label;
      b.id = btn.id || '';
      b.onclick = () => {
        if (btn.action) btn.action();
        if (!btn.keepOpen) this.close();
      };
      footerEl.appendChild(b);
    });

    container.style.maxWidth = width;
    overlay.classList.remove('hidden');

    return new Promise(resolve => { this._resolve = resolve; });
  },

  close() {
    document.getElementById('modal-overlay').classList.add('hidden');
    if (this._resolve) { this._resolve(); this._resolve = null; }
  },

  confirm({ title, body, confirmLabel = 'Confirm', confirmClass = 'btn-primary', cancelLabel = 'Cancel' }) {
    return new Promise(resolve => {
      this.show({
        title,
        body,
        buttons: [
          { label: cancelLabel,   class: 'btn-ghost',   action: () => resolve(false) },
          { label: confirmLabel, class: confirmClass, action: () => resolve(true) },
        ]
      });
    });
  }
};

// Wire close button
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('modal-close-btn')?.addEventListener('click', () => modal.close());
  document.getElementById('modal-overlay')?.addEventListener('click', (e) => {
    if (e.target === document.getElementById('modal-overlay')) modal.close();
  });
});

// ── Loader ───────────────────────────────────────────────────────
export function setLoading(containerId, isLoading, message = 'Loading...') {
  const el = document.getElementById(containerId);
  if (!el) return;
  if (isLoading) {
    el.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>${message}</p></div>`;
  }
}

// ── Format Helpers ───────────────────────────────────────────────
export function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  const now = new Date();
  const diff = now - d;
  if (diff < 60000)        return 'just now';
  if (diff < 3600000)      return `${Math.floor(diff/60000)}m ago`;
  if (diff < 86400000)     return `${Math.floor(diff/3600000)}h ago`;
  if (diff < 604800000)    return `${Math.floor(diff/86400000)}d ago`;
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export function formatBytes(bytes) {
  if (!bytes) return '0 B';
  const sizes = ['B','KB','MB','GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024,i)).toFixed(1)} ${sizes[i]}`;
}

export function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function avatarInitials(name) {
  if (!name) return '?';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return (parts[0][0] + parts[parts.length-1][0]).toUpperCase();
}

export function getFileIcon(mimeType, name) {
  if (!mimeType && name) {
    const ext = name.split('.').pop().toLowerCase();
    const extMap = { pdf:'📄', doc:'📝', docx:'📝', xls:'📊', xlsx:'📊', ppt:'📊', pptx:'📊', jpg:'🖼️', jpeg:'🖼️', png:'🖼️', mp4:'🎬', zip:'🗜️', txt:'📃' };
    return extMap[ext] || '📄';
  }
  if (mimeType?.includes('spreadsheet') || mimeType?.includes('excel')) return '📊';
  if (mimeType?.includes('document') || mimeType?.includes('word')) return '📝';
  if (mimeType?.includes('presentation') || mimeType?.includes('powerpoint')) return '📊';
  if (mimeType?.includes('pdf')) return '📄';
  if (mimeType?.includes('image')) return '🖼️';
  if (mimeType?.includes('video')) return '🎬';
  if (mimeType?.includes('audio')) return '🎵';
  if (mimeType?.includes('folder')) return '📁';
  if (mimeType?.includes('form')) return '📋';
  if (mimeType?.includes('drawing')) return '🎨';
  return '📄';
}

export function getFileIconBg(mimeType) {
  if (mimeType?.includes('spreadsheet')) return 'rgba(0,212,170,0.12)';
  if (mimeType?.includes('document'))    return 'rgba(108,99,255,0.12)';
  if (mimeType?.includes('presentation')) return 'rgba(255,179,71,0.12)';
  if (mimeType?.includes('pdf'))         return 'rgba(255,92,122,0.12)';
  if (mimeType?.includes('image'))       return 'rgba(0,212,170,0.10)';
  if (mimeType?.includes('folder'))      return 'rgba(108,99,255,0.10)';
  return 'rgba(255,255,255,0.06)';
}

// ── Debounce ─────────────────────────────────────────────────────
export function debounce(fn, delay = 300) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); };
}

// ── Auto-resize textarea ──────────────────────────────────────────
export function autoResizeTextarea(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 200) + 'px';
}
