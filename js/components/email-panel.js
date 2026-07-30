/**
 * DistaMate — Email Panel Component
 */

import Gmail from '../gmail.js';
import AI from '../ai.js';
import { toast, modal, formatDate, escapeHtml, avatarInitials } from '../ui.js';
import { renderEmailRow } from './dashboard.js';

let _emails = [];
let _filter = 'all';
let _currentThread = null;

export async function renderEmailPanel(container) {
  container.innerHTML = `
    <div class="page-header">
      <div>
        <h1 class="page-title">Email</h1>
        <p class="page-subtitle" id="email-subtitle">Loading...</p>
      </div>
      <button class="btn btn-primary btn-sm" id="compose-btn">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Compose
      </button>
    </div>

    <div class="section-card" style="margin-bottom: 20px">
      <div class="filter-bar" id="email-filter-bar">
        <button class="filter-btn active" data-filter="all">All</button>
        <button class="filter-btn" data-filter="urgent">🚨 Urgent</button>
        <button class="filter-btn" data-filter="action">⚡ Action</button>
        <button class="filter-btn" data-filter="info">ℹ️ Info</button>
        <button class="filter-btn" data-filter="unread">● Unread</button>
      </div>
      <div id="email-list-container">
        <div class="loading-state"><div class="spinner"></div><p>Fetching emails & running AI analysis...</p></div>
      </div>
    </div>
  `;

  document.getElementById('email-filter-bar')?.addEventListener('click', (e) => {
    const btn = e.target.closest('.filter-btn');
    if (!btn) return;
    document.querySelectorAll('#email-filter-bar .filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    _filter = btn.dataset.filter;
    renderEmailList();
  });

  document.getElementById('compose-btn')?.addEventListener('click', showComposeModal);

  await loadEmails(container);
}

async function loadEmails(container) {
  try {
    _emails = await Gmail.listMessages(20);

    // AI classify in batches
    const toClassify = _emails.filter(e => !e.priority);
    await Promise.allSettled(
      toClassify.map(e =>
        AI.classifyEmail({ subject: e.subject, snippet: e.snippet, sender: e.from })
          .then(p => { e.priority = p; })
      )
    );

    const unread = _emails.filter(e => e.isUnread).length;
    document.getElementById('email-subtitle').textContent =
      `${_emails.length} emails · ${unread} unread`;

    // Update nav badge
    const badge = document.getElementById('badge-email');
    if (badge && unread > 0) badge.textContent = unread;

    renderEmailList();
  } catch (e) {
    document.getElementById('email-list-container').innerHTML =
      `<div class="empty-state"><div class="empty-icon">⚠️</div><h3>Unable to load emails</h3><p>${escapeHtml(e.message)}</p></div>`;
  }
}

function renderEmailList() {
  const container = document.getElementById('email-list-container');
  if (!container) return;

  const filtered = _emails.filter(e => {
    if (_filter === 'all')    return true;
    if (_filter === 'unread') return e.isUnread;
    return e.priority?.priority === _filter;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">📭</div><h3>No emails</h3><p>No ${_filter === 'all' ? '' : _filter + ' '}emails found.</p></div>`;
    return;
  }

  container.innerHTML = `<div class="email-list">${filtered.map(e => renderEmailRow(e)).join('')}</div>`;

  container.querySelectorAll('.email-item').forEach((el, i) => {
    el.addEventListener('click', () => openThread(filtered[i].threadId));
  });
}

export async function openThread(threadId) {
  const panelContent = document.getElementById('email-content');
  if (!panelContent) return;

  panelContent.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Loading thread...</p></div>`;

  try {
    const messages = await Gmail.getThread(threadId);
    _currentThread = messages;
    const first = messages[0];

    panelContent.innerHTML = `
      <div class="email-thread">
        <button class="btn btn-ghost btn-sm" id="back-to-inbox" style="margin-bottom:16px">
          ← Back to inbox
        </button>

        <div class="email-thread-header">
          <h2 class="email-thread-subject">${escapeHtml(first.subject)}</h2>
          <div class="thread-badges">
            ${first.priority ? renderPriorityBadge(first.priority) : ''}
          </div>
        </div>

        ${messages.map(m => renderThreadMessage(m)).join('')}

        <div class="email-actions">
          <button class="btn btn-primary" id="ai-draft-btn">
            ✨ AI Draft Reply
          </button>
          <button class="btn btn-secondary" id="manual-reply-btn">
            ✏️ Manual Reply
          </button>
        </div>

        <div id="draft-area"></div>
      </div>
    `;

    document.getElementById('back-to-inbox')?.addEventListener('click', () => renderEmailPanel(panelContent));
    document.getElementById('ai-draft-btn')?.addEventListener('click', () => generateDraft('ai'));
    document.getElementById('manual-reply-btn')?.addEventListener('click', () => generateDraft('manual'));

  } catch (e) {
    panelContent.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div><h3>Error loading thread</h3><p>${escapeHtml(e.message)}</p></div>`;
  }
}

function renderThreadMessage(msg) {
  const initials = avatarInitials(msg.from);
  return `
    <div class="thread-msg">
      <div class="thread-msg-header">
        <div class="email-sender-avatar" style="width:30px;height:30px;font-size:11px">${initials}</div>
        <div>
          <div class="thread-msg-from">${escapeHtml(msg.from)}</div>
          <div style="font-size:11px;color:var(--color-text-muted)">${escapeHtml(msg.fromEmail)}</div>
        </div>
        <div class="thread-msg-date">${formatDate(msg.date)}</div>
      </div>
      <div class="thread-msg-body">${escapeHtml(msg.body || msg.snippet || '(no content)')}</div>
    </div>
  `;
}

function renderPriorityBadge(p) {
  const cls = p.priority === 'urgent' ? 'priority-urgent' : p.priority === 'action' ? 'priority-action' : 'priority-info';
  const label = p.priority === 'urgent' ? '🚨 Urgent' : p.priority === 'action' ? '⚡ Action Required' : 'ℹ️ Informational';
  return `<span class="priority-badge ${cls}">${label}</span> ${p.reason ? `<span class="tag">${escapeHtml(p.reason)}</span>` : ''}`;
}

async function generateDraft(mode) {
  const draftArea = document.getElementById('draft-area');
  if (!draftArea || !_currentThread) return;

  let draftText = '';

  if (mode === 'ai') {
    draftArea.innerHTML = `
      <div class="draft-box">
        <div class="draft-box-header">
          <div class="draft-box-title">
            <div class="spinner" style="width:14px;height:14px;border-width:2px"></div>
            Generating AI draft...
          </div>
        </div>
        <div style="padding:20px;color:var(--color-text-muted);font-size:13px">Analyzing thread and crafting reply...</div>
      </div>
    `;

    try {
      draftText = await AI.draftReply({
        thread: _currentThread.map(m => ({ from: m.from, body: m.body || m.snippet }))
      });
    } catch (e) {
      toast.error('AI draft failed: ' + e.message);
      draftText = '';
    }
  }

  const last = _currentThread[_currentThread.length - 1];
  showDraftBox(draftArea, draftText, {
    to: last.fromEmail,
    subject: 'Re: ' + last.subject,
    threadId: last.threadId,
  });
}

function showDraftBox(draftArea, initialText, meta) {
  draftArea.innerHTML = `
    <div class="draft-box" style="margin-top:20px">
      <div class="draft-box-header">
        <div class="draft-box-title">
          ✨ Draft Reply
          <span style="font-weight:400;color:var(--color-text-muted);font-size:12px">To: ${escapeHtml(meta.to)}</span>
        </div>
        <button class="btn btn-ghost btn-sm" id="regenerate-btn">↺ Regenerate</button>
      </div>
      <textarea class="draft-textarea" id="draft-text" placeholder="Type your reply...">${escapeHtml(initialText)}</textarea>
      <div class="draft-footer">
        <div class="draft-warning">⚠️ Review before sending — AI drafts may need editing</div>
        <div style="display:flex;gap:8px">
          <button class="btn btn-ghost btn-sm" id="save-draft-btn">💾 Save Draft</button>
          <button class="btn btn-primary btn-sm" id="send-email-btn">📤 Send Email</button>
        </div>
      </div>
    </div>
  `;

  document.getElementById('regenerate-btn')?.addEventListener('click', () => generateDraft('ai'));

  document.getElementById('save-draft-btn')?.addEventListener('click', async () => {
    const body = document.getElementById('draft-text')?.value;
    try {
      await Gmail.createDraft({ to: meta.to, subject: meta.subject, body, threadId: meta.threadId });
      toast.success('Draft saved to Gmail!');
    } catch (e) {
      toast.error(e.message);
    }
  });

  document.getElementById('send-email-btn')?.addEventListener('click', async () => {
    const body = document.getElementById('draft-text')?.value?.trim();
    if (!body) { toast.warning('Email body is empty.'); return; }

    const confirmed = await modal.confirm({
      title: '📤 Send Email?',
      body: `<p>You're about to send this email to <strong>${escapeHtml(meta.to)}</strong>.</p><p style="margin-top:8px;color:var(--color-text-subtle)">This action cannot be undone.</p>`,
      confirmLabel: 'Send Now',
      confirmClass: 'btn-primary',
    });

    if (!confirmed) return;

    try {
      await Gmail.sendMessage({ to: meta.to, subject: meta.subject, body, threadId: meta.threadId });
      toast.success('Email sent successfully! ✉️');
      document.getElementById('draft-area').innerHTML = `<div style="color:var(--color-accent);padding:12px;font-size:13px;font-weight:500">✅ Email sent!</div>`;
    } catch (e) {
      toast.error('Failed to send: ' + e.message);
    }
  });
}

function showComposeModal() {
  modal.show({
    title: '✉️ Compose Email',
    width: '560px',
    body: `
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="form-group">
          <label class="form-label">To</label>
          <input class="form-input" id="compose-to" type="email" placeholder="recipient@email.com" />
        </div>
        <div class="form-group">
          <label class="form-label">Subject</label>
          <input class="form-input" id="compose-subject" type="text" placeholder="Email subject" />
        </div>
        <div class="form-group">
          <label class="form-label">Body</label>
          <textarea class="form-input" id="compose-body" rows="6" placeholder="Write your message..."></textarea>
        </div>
        <div style="display:flex;gap:8px">
          <button class="btn btn-secondary btn-sm" id="ai-compose-btn">✨ AI Assist</button>
        </div>
      </div>
    `,
    buttons: [
      { label: 'Cancel', class: 'btn-ghost' },
      { label: '📤 Send', class: 'btn-primary', keepOpen: true, action: async () => {
        const to = document.getElementById('compose-to')?.value?.trim();
        const subject = document.getElementById('compose-subject')?.value?.trim();
        const body = document.getElementById('compose-body')?.value?.trim();
        if (!to || !subject || !body) { toast.warning('Please fill in all fields.'); return; }

        try {
          await Gmail.sendMessage({ to, subject, body });
          toast.success('Email sent! ✉️');
          modal.close();
        } catch (e) {
          toast.error('Failed to send: ' + e.message);
        }
      }},
    ]
  });

  document.getElementById('ai-compose-btn')?.addEventListener('click', async () => {
    const subject = document.getElementById('compose-subject')?.value?.trim();
    const existing = document.getElementById('compose-body')?.value?.trim();
    const bodyEl = document.getElementById('compose-body');
    if (!bodyEl) return;

    bodyEl.value = 'Generating...';
    try {
      const draft = await AI.draftReply({
        thread: [{ from: 'User', body: `Subject: ${subject}\n${existing}` }],
        userInstruction: `Write a professional email about: ${subject || existing}`
      });
      bodyEl.value = draft;
    } catch (e) {
      toast.error('AI assist failed: ' + e.message);
      bodyEl.value = existing;
    }
  });
}

// Export for external use
window.emailPanel = { openThread };
