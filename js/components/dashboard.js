/**
 * DistaMate — Dashboard Component
 */

import Gmail from '../gmail.js';
import Drive from '../drive.js';
import AI from '../ai.js';
import Auth from '../auth.js';
import { formatDate, formatBytes, getFileIcon, getFileIconBg, escapeHtml, avatarInitials } from '../ui.js';

export async function renderDashboard(container) {
  container.innerHTML = `
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">Your workspace at a glance</p>
      </div>
    </div>

    <!-- Stat Cards -->
    <div class="dashboard-grid" id="dash-stats">
      ${['','','',''].map(i => `
        <div class="stat-card" style="animation: fadeSlideUp 0.4s both">
          <div class="stat-icon" style="background:var(--color-surface2)"><div class="spinner" style="width:18px;height:18px"></div></div>
          <div class="stat-value" style="color:var(--color-text-subtle)">—</div>
          <div class="stat-label">Loading...</div>
        </div>`).join('')}
    </div>

    <div class="dashboard-sections">
      <!-- Recent Emails -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-title">📧 Recent Emails</span>
          <button class="section-action" id="view-all-emails-btn">View all</button>
        </div>
        <div id="dash-emails"><div class="loading-state"><div class="spinner"></div><p>Loading emails...</p></div></div>
      </div>

      <!-- Recent Files -->
      <div class="section-card">
        <div class="section-header">
          <span class="section-title">📁 Recent Files</span>
          <button class="section-action" id="view-all-files-btn">View all</button>
        </div>
        <div id="dash-files"><div class="loading-state"><div class="spinner"></div><p>Loading files...</p></div></div>
      </div>
    </div>
  `;

  document.getElementById('view-all-emails-btn')?.addEventListener('click', () => {
    document.querySelector('[data-panel="email"]')?.click();
  });
  document.getElementById('view-all-files-btn')?.addEventListener('click', () => {
    document.querySelector('[data-panel="drive"]')?.click();
  });

  await Promise.all([
    loadStats(),
    loadDashEmails(),
    loadDashFiles(),
  ]);
}

async function loadStats() {
  try {
    const [emails, quota] = await Promise.allSettled([
      Gmail.listMessages(50),
      Drive.getStorageQuota()
    ]);

    const emailList = emails.status === 'fulfilled' ? emails.value : [];
    const quotaData = quota.status === 'fulfilled' ? quota.value : {};

    const unread = emailList.filter(e => e.isUnread).length;
    const urgent = emailList.filter(e => e.priority?.priority === 'urgent').length;
    const used = parseInt(quotaData.usage || 0);
    const limit = parseInt(quotaData.limit || 16106127360);
    const pct = limit ? Math.round((used / limit) * 100) : 0;

    document.getElementById('dash-stats').innerHTML = `
      <div class="stat-card" style="animation: fadeSlideUp 0.3s both">
        <div class="stat-icon" style="background:rgba(108,99,255,0.12)">📧</div>
        <div class="stat-value">${unread}</div>
        <div class="stat-label">Unread Emails</div>
        ${unread > 0 ? `<span class="stat-change negative">needs attention</span>` : `<span class="stat-change positive">all clear</span>`}
      </div>
      <div class="stat-card" style="animation: fadeSlideUp 0.4s both">
        <div class="stat-icon" style="background:rgba(255,92,122,0.12)">🚨</div>
        <div class="stat-value">${urgent}</div>
        <div class="stat-label">Urgent Items</div>
        ${urgent > 0 ? `<span class="stat-change negative">action needed</span>` : `<span class="stat-change positive">none</span>`}
      </div>
      <div class="stat-card" style="animation: fadeSlideUp 0.5s both">
        <div class="stat-icon" style="background:rgba(0,212,170,0.12)">☁️</div>
        <div class="stat-value">${formatBytes(used)}</div>
        <div class="stat-label">Drive Storage Used</div>
        <div class="progress-bar-wrapper" style="margin-top:10px">
          <div class="progress-bar-fill" style="width:${pct}%"></div>
        </div>
      </div>
      <div class="stat-card" style="animation: fadeSlideUp 0.6s both">
        <div class="stat-icon" style="background:rgba(255,179,71,0.12)">✅</div>
        <div class="stat-value">${emailList.filter(e => e.priority?.actionItem).length}</div>
        <div class="stat-label">Pending Actions</div>
        <span class="stat-change ${urgent > 0 ? 'negative' : 'positive'}">${urgent > 0 ? 'review needed' : 'on track'}</span>
      </div>
    `;
  } catch (e) {
    console.error('Stats error:', e);
    document.getElementById('dash-stats').innerHTML = `<p style="color:var(--color-text-muted);font-size:13px;padding:12px">Unable to load stats.</p>`;
  }
}

async function loadDashEmails() {
  try {
    const emails = await Gmail.listMessages(5);

    // Classify with AI (in parallel, up to 3)
    const toClassify = emails.slice(0, 3);
    await Promise.allSettled(toClassify.map(async e => {
      if (!e.priority) {
        e.priority = await AI.classifyEmail({ subject: e.subject, snippet: e.snippet, sender: e.from });
      }
    }));

    const container = document.getElementById('dash-emails');
    if (!container) return;

    if (emails.length === 0) {
      container.innerHTML = `<div class="empty-state"><div class="empty-icon">📭</div><p>No emails found</p></div>`;
      return;
    }

    container.innerHTML = `<div class="email-list">${emails.map(e => renderEmailRow(e, true)).join('')}</div>`;

    container.querySelectorAll('.email-item').forEach((el, i) => {
      el.addEventListener('click', () => {
        document.querySelector('[data-panel="email"]')?.click();
        setTimeout(() => window.emailPanel?.openThread?.(emails[i].threadId), 200);
      });
    });

    // Update badge
    const badge = document.getElementById('badge-dashboard');
    const unread = emails.filter(e => e.isUnread).length;
    if (badge && unread > 0) badge.textContent = unread;
  } catch (e) {
    document.getElementById('dash-emails').innerHTML = `<p style="color:var(--color-text-muted);font-size:13px;padding:16px">Unable to load emails. ${Auth.isDemoMode() ? '' : 'Check connection.'}</p>`;
  }
}

async function loadDashFiles() {
  try {
    const files = await Drive.getRecentFiles(6);
    const container = document.getElementById('dash-files');
    if (!container) return;

    if (files.length === 0) {
      container.innerHTML = `<div class="empty-state"><div class="empty-icon">📂</div><p>No recent files</p></div>`;
      return;
    }

    container.innerHTML = `
      <div class="activity-list">
        ${files.map(f => `
          <div class="activity-item" data-file-id="${f.id}" data-mime="${f.mimeType}">
            <div class="activity-icon" style="background:${getFileIconBg(f.mimeType)}">${getFileIcon(f.mimeType, f.name)}</div>
            <div class="activity-info">
              <div class="activity-name" title="${escapeHtml(f.name)}">${escapeHtml(f.name)}</div>
              <div class="activity-time">${formatDate(f.modifiedTime)}</div>
            </div>
          </div>
        `).join('')}
      </div>
    `;

    container.querySelectorAll('.activity-item').forEach((el, i) => {
      el.addEventListener('click', () => {
        const file = files[i];
        if (Drive.isDoc(file.mimeType)) {
          document.querySelector('[data-panel="docs"]')?.click();
          setTimeout(() => window.docsPanel?.openDoc?.(file.id), 200);
        } else if (Drive.isSheet(file.mimeType)) {
          document.querySelector('[data-panel="sheets"]')?.click();
          setTimeout(() => window.sheetsPanel?.openSheet?.(file.id, file.name), 200);
        } else {
          document.querySelector('[data-panel="drive"]')?.click();
        }
      });
    });
  } catch (e) {
    document.getElementById('dash-files').innerHTML = `<p style="color:var(--color-text-muted);font-size:13px;padding:16px">Unable to load files.</p>`;
  }
}

export function renderEmailRow(email, compact = false) {
  const p = email.priority;
  const pClass = p?.priority === 'urgent' ? 'priority-urgent' : p?.priority === 'action' ? 'priority-action' : 'priority-info';
  const pLabel = p?.priority === 'urgent' ? 'Urgent' : p?.priority === 'action' ? 'Action' : 'Info';
  const initials = avatarInitials(email.from);
  const colors = ['#6C63FF','#00D4AA','#FF5C7A','#FFB347','#A78BFA'];
  const color = colors[(email.from || '').charCodeAt(0) % colors.length];

  return `
    <div class="email-item ${email.isUnread ? 'unread' : ''}">
      <div class="email-sender-avatar" style="background:linear-gradient(135deg,${color},${color}aa)">${initials}</div>
      <div class="email-body">
        <div class="email-meta">
          <span class="email-sender">${escapeHtml(email.from)}</span>
          <span class="email-time">${formatDate(email.date)}</span>
        </div>
        <div class="email-subject">${escapeHtml(email.subject)}</div>
        ${!compact ? `<div class="email-snippet">${escapeHtml(email.snippet)}</div>` : ''}
        ${p ? `<div class="email-tags"><span class="priority-badge ${pClass}">${pLabel}</span>${p.actionItem ? `<span class="tag">📋 ${escapeHtml(p.actionItem.substring(0,40))}</span>` : ''}</div>` : ''}
      </div>
    </div>
  `;
}
