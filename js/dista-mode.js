/**
 * DistaAiEmployee — DISTA MODE
 * Full-screen JARVIS-style AI conversation interface
 */

import AI from './ai.js';
import Voice from './voice.js';

const DistaMode = {
  isOpen: false,
  messages: [],
  _timers: [],

  // ── Init ──────────────────────────────────────────────────────
  init() {
    document.getElementById('dista-mode-btn')?.addEventListener('click',  () => this.open());
    document.getElementById('dm-close-btn')?.addEventListener('click',    () => this.close());
    document.getElementById('dm-send-btn')?.addEventListener('click',     () => this._handleSend());
    document.getElementById('dm-mic-btn')?.addEventListener('click',      () => this._triggerVoice());

    document.getElementById('dm-input')?.addEventListener('keydown', e => {
      if (e.key === 'Enter') this._handleSend();
    });

    document.querySelectorAll('.dm-quick-btn').forEach(btn =>
      btn.addEventListener('click', () => this._processMessage(btn.dataset.cmd))
    );

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && this.isOpen) this.close();
    });
  },

  // ── Open / Close ──────────────────────────────────────────────
  open() {
    this.isOpen = true;
    Voice.stopSpeaking?.();
    this.messages = [];
    this._clearChat();

    const el = document.getElementById('dista-mode');
    el?.classList.remove('hidden');
    requestAnimationFrame(() => el?.classList.add('visible'));

    this._startClock();
    this._startMetrics();
    this._startDataStream();

    setTimeout(() => {
      this._sendGreeting();
      document.getElementById('dm-input')?.focus();
    }, 700);
  },

  close() {
    this.isOpen = false;
    Voice.stopSpeaking?.();
    const el = document.getElementById('dista-mode');
    el?.classList.remove('visible');
    setTimeout(() => el?.classList.add('hidden'), 600);
    this._timers.forEach(clearInterval);
    this._timers = [];
  },

  // ── Voice (called from app.js Voice callback when in Dista Mode)
  async handleVoiceInput(text) {
    this._setOrb('listening', 'LISTENING');
    await new Promise(r => setTimeout(r, 200));
    await this._processMessage(text);
  },

  // ── Message handling ──────────────────────────────────────────
  async _handleSend() {
    const input = document.getElementById('dm-input');
    const text  = input?.value?.trim();
    if (!text) return;
    input.value = '';
    await this._processMessage(text);
  },

  async _processMessage(text) {
    if (!text) return;
    this._appendMessage('user', text);
    this._setOrb('thinking', 'PROCESSING');
    this._setStatus('◌ ANALYZING COMMAND...');

    const history = [
      ...this.messages.map(m => ({
        role: m.role === 'dista' ? 'assistant' : 'user',
        content: m.content,
      })),
      { role: 'user', content: text },
    ];

    const SYSTEM = `You are DISTA — a razor-sharp, highly intelligent AI system operating within a personal workspace assistant called DistaAiEmployee.
You have full integration with Gmail, Google Drive, Google Docs, and Google Sheets.
Your personality is modeled on JARVIS from Iron Man: supremely competent, precise, slightly dry in tone, always professional.
Always call the user "sir." Never use markdown, bullet points, or headers — speak in clean flowing sentences.
Keep responses under 3 sentences unless the user explicitly asks for detail.`;

    let reply = '';
    try {
      this._setOrb('speaking', 'RESPONDING');
      const msgEl  = this._appendMessage('dista', '');
      const textEl = msgEl?.querySelector('.dm-msg-text');

      const stream = AI.chatStream(history, SYSTEM);
      for await (const chunk of stream) {
        reply += chunk;
        if (textEl) textEl.textContent = reply;
        this._scrollChat();
      }

      this.messages.push({ role: 'user', content: text }, { role: 'dista', content: reply });
      Voice.speak(reply);
    } catch (e) {
      reply = `I encountered an error, sir. ${e.message}`;
      this._appendMessage('dista', reply);
      this.messages.push({ role: 'user', content: text }, { role: 'dista', content: reply });
    }

    this._setOrb('idle', 'STANDBY');
    this._setStatus('◉ AWAITING INPUT');
  },

  // ── Opening greeting ──────────────────────────────────────────
  async _sendGreeting() {
    this._setOrb('speaking', 'INITIALIZING');
    this._setStatus('◌ BOOTING SYSTEMS...');

    const greeting = 'All systems online, sir. Gemini AI is active and Google Workspace access is confirmed. I can manage your emails, search Drive, analyse documents and spreadsheets, draft replies, and handle any task you assign. What would you like me to do?';

    const msgEl  = this._appendMessage('dista', '');
    const textEl = msgEl?.querySelector('.dm-msg-text');
    if (!textEl) return;

    let i = 0;
    await new Promise(resolve => {
      const id = setInterval(() => {
        textEl.textContent = greeting.slice(0, ++i);
        this._scrollChat();
        if (i >= greeting.length) { clearInterval(id); resolve(); }
      }, 18);
    });

    this.messages = [{ role: 'dista', content: greeting }];
    Voice.speak(greeting);
    this._setOrb('idle', 'STANDBY');
    this._setStatus('◉ AWAITING INPUT');
  },

  // ── DOM helpers ───────────────────────────────────────────────
  _appendMessage(role, text) {
    const chat = document.getElementById('dm-chat');
    if (!chat) return null;
    const stamp = new Date().toLocaleTimeString('en-US', { hour12: false });
    const div   = document.createElement('div');
    div.className = `dm-msg dm-msg-${role}`;
    div.innerHTML = `
      <div class="dm-msg-header">
        <span class="dm-msg-label">${role === 'dista' ? '◈ DISTA' : '► INPUT'}</span>
        <span class="dm-msg-time">${stamp}</span>
      </div>
      <div class="dm-msg-text">${text}</div>`;
    chat.appendChild(div);
    this._scrollChat();
    return div;
  },

  _clearChat()  { const c = document.getElementById('dm-chat'); if (c) c.innerHTML = ''; },
  _scrollChat() { const c = document.getElementById('dm-chat'); if (c) c.scrollTop = c.scrollHeight; },

  _setOrb(state, label) {
    const orb = document.getElementById('dm-orb');
    if (orb) orb.dataset.state = state;
    const lbl = document.getElementById('dm-orb-label');
    if (lbl) lbl.textContent = label || state.toUpperCase();
  },
  _setStatus(t) { const el = document.getElementById('dm-footer-status'); if (el) el.textContent = t; },

  _triggerVoice() {
    // Fires the topbar mic button which routes back here via app.js
    document.getElementById('voice-btn')?.click();
  },

  // ── Ambient animations ────────────────────────────────────────
  _startClock() {
    const tick = () => {
      const el = document.getElementById('dm-clock');
      if (el) el.textContent = new Date().toLocaleTimeString('en-US', { hour12: false });
    };
    tick();
    this._timers.push(setInterval(tick, 1000));
  },

  _startMetrics() {
    const defs = [
      { fill: 'dm-ai-fill',  pct: 'dm-ai-pct',  base: 72, range: 25 },
      { fill: 'dm-cpu-fill', pct: 'dm-cpu-pct',  base: 55, range: 30 },
      { fill: 'dm-mem-fill', pct: 'dm-mem-pct',  base: 42, range: 22 },
      { fill: 'dm-net-fill', pct: 'dm-net-pct',  base: 60, range: 28 },
    ];
    this._timers.push(setInterval(() => {
      defs.forEach(m => {
        const v    = Math.min(99, Math.max(8, m.base + (Math.random() - 0.5) * m.range));
        const fill = document.getElementById(m.fill);
        const pct  = document.getElementById(m.pct);
        if (fill) fill.style.width = v.toFixed(0) + '%';
        if (pct)  pct.textContent  = v.toFixed(0) + '%';
      });
    }, 1400));
  },

  _startDataStream() {
    const el = document.getElementById('dm-stream');
    if (!el) return;
    const pool = [
      'TOKEN REFRESH: OK', 'GMAIL API: 200 OK', 'DRIVE MOUNTED: YES',
      'CONTEXT WINDOW: 128K', 'CACHE HIT: 94%', 'LATENCY: 12ms',
      'OAUTH SCOPE: GRANTED', 'TLS 1.3: ACTIVE', 'WORKERS: 4/4 ONLINE',
      'ENCRYPTION: AES-256', 'VECTOR INDEX: LOADED', 'PIPELINE: IDLE',
      'AUTH TOKEN: VALID', 'INBOX SYNC: OK', 'RATE LIMIT: OK',
      'GEMINI 2.0: READY', 'DRIVE QUOTA: 12.4 GB FREE', 'DOCS API: 200 OK',
    ];
    this._timers.push(setInterval(() => {
      const line  = document.createElement('div');
      line.className = 'dm-stream-line';
      line.textContent = `[${new Date().toLocaleTimeString('en-US', { hour12: false })}] ${pool[Math.floor(Math.random() * pool.length)]}`;
      el.prepend(line);
      while (el.children.length > 14) el.removeChild(el.lastChild);
    }, 900));
  },
};

export default DistaMode;
