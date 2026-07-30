/**
 * DistaMate — Main Application
 * Router, state management, initialization
 */

import Config from './config.js';
import Auth from './auth.js';
import { toast } from './ui.js';
import { renderDashboard } from './components/dashboard.js';
import { renderEmailPanel } from './components/email-panel.js';
import { renderDrivePanel } from './components/drive-panel.js';
import { renderDocsPanel } from './components/doc-panel.js';
import { renderSheetsPanel } from './components/sheets-panel.js';
import { renderSettingsPanel } from './components/settings-panel.js';
import { initChat } from './components/chat.js';

// ── State ────────────────────────────────────────────────────────
let _currentPanel = 'dashboard';
let _panelLoaded = {};

// ── Panel registry ───────────────────────────────────────────────
const PANELS = {
  dashboard: { title: 'Dashboard',  render: renderDashboard,    container: 'dashboard-content' },
  email:     { title: 'Email',      render: renderEmailPanel,   container: 'email-content' },
  drive:     { title: 'Drive',      render: renderDrivePanel,   container: 'drive-content' },
  docs:      { title: 'Documents',  render: renderDocsPanel,    container: 'docs-content' },
  sheets:    { title: 'Sheets',     render: renderSheetsPanel,  container: 'sheets-content' },
  settings:  { title: 'Settings',   render: renderSettingsPanel, container: 'settings-content' },
};

// ── Init ─────────────────────────────────────────────────────────
async function init() {
  Config.load();

  // Wire nav items
  document.querySelectorAll('.nav-item[data-panel]').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      switchPanel(item.dataset.panel);
    });
  });

  // Sidebar collapse
  document.getElementById('sidebar-toggle')?.addEventListener('click', () => {
    document.getElementById('sidebar')?.classList.toggle('collapsed');
  });

  // Mobile menu
  document.getElementById('mobile-menu-btn')?.addEventListener('click', () => {
    document.getElementById('sidebar')?.classList.toggle('mobile-open');
  });

  // Refresh
  document.getElementById('refresh-btn')?.addEventListener('click', () => {
    _panelLoaded = {};
    switchPanel(_currentPanel, true);
    toast.info('Refreshing...');
  });

  // Initialize Auth (wires auth UI and restores saved Client ID)
  await Auth.init(onAuthSuccess);
}

// ── Auth success ──────────────────────────────────────────────────
function onAuthSuccess(userProfile) {
  // Hide auth screen
  const authScreen = document.getElementById('auth-screen');
  if (authScreen) authScreen.style.display = 'none';

  // Show app
  document.getElementById('app')?.classList.remove('hidden');

  // Update user info
  updateUserInfo(userProfile);

  // Mode badge
  const badge = document.getElementById('mode-badge');
  if (badge) {
    if (Auth.isDemoMode()) {
      badge.textContent = '🎭 Demo Mode';
      badge.className = 'mode-badge demo';
      badge.classList.remove('hidden');
    } else {
      badge.textContent = '🟢 Live';
      badge.className = 'mode-badge live';
      badge.classList.remove('hidden');
    }
  }

  // Init chat
  initChat(userProfile);

  // Load dashboard
  switchPanel('dashboard');

  if (Auth.isDemoMode()) {
    toast.info('Demo Mode: Showing sample data. Add your Google Client ID in Settings for live data.', 7000);
  } else {
    const firstName = (userProfile?.name || '').split(' ')[0] || 'there';
    toast.success(`Welcome, ${firstName}! Connected to Google Workspace ✓`);
  }
}

// ── Panel Router ──────────────────────────────────────────────────
async function switchPanel(panelId, forceReload = false) {
  if (!PANELS[panelId]) return;

  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.toggle('active', item.dataset.panel === panelId);
  });

  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById(`panel-${panelId}`)?.classList.add('active');
  document.getElementById('topbar-title').textContent = PANELS[panelId].title;

  _currentPanel = panelId;

  if (!_panelLoaded[panelId] || forceReload) {
    const container = document.getElementById(PANELS[panelId].container);
    if (container) {
      try {
        await PANELS[panelId].render(container);
        _panelLoaded[panelId] = true;
      } catch (e) {
        console.error(`Panel ${panelId} error:`, e);
        container.innerHTML = `
          <div class="empty-state">
            <div class="empty-icon">⚠️</div>
            <h3>Error loading panel</h3>
            <p>${e.message}</p>
            <button class="btn btn-primary" onclick="window.location.reload()">Reload App</button>
          </div>`;
      }
    }
  }

  // Close mobile sidebar
  document.getElementById('sidebar')?.classList.remove('mobile-open');
}

// ── Update user info in sidebar ───────────────────────────────────
function updateUserInfo(profile) {
  if (!profile) return;
  const nameEl   = document.getElementById('user-name');
  const emailEl  = document.getElementById('user-email');
  const avatarEl = document.getElementById('user-avatar');

  if (nameEl)  nameEl.textContent  = profile.name  || 'User';
  if (emailEl) emailEl.textContent = profile.email || '';

  if (avatarEl) {
    if (profile.picture) {
      avatarEl.innerHTML = `<img src="${profile.picture}" alt="${profile.name || 'User'}" style="width:100%;height:100%;object-fit:cover;border-radius:50%" referrerpolicy="no-referrer" />`;
    } else {
      const initials = (profile.name || 'U').trim().split(/\s+/).map(n => n[0]).join('').substring(0, 2).toUpperCase();
      avatarEl.textContent = initials;
    }
  }
}

// ── Expose switchPanel for components ────────────────────────────
window._app = { switchPanel };

// ── Start ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', init);
