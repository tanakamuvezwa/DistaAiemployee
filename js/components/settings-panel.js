/**
 * DistaMate — Settings Panel Component
 */

import Config from '../config.js';
import Auth from '../auth.js';
import AI from '../ai.js';
import { toast, escapeHtml } from '../ui.js';

export function renderSettingsPanel(container) {
  const clientIdStatus = Config.GOOGLE_CLIENT_ID ? 'connected' : 'disconnected';
  const aiKeyStatus = Config.OPENROUTER_API_KEY ? 'connected' : 'disconnected';

  container.innerHTML = `
    <div class="page-header">
      <div>
        <h1 class="page-title">Settings</h1>
        <p class="page-subtitle">Configure API keys and preferences</p>
      </div>
    </div>

    <div class="settings-grid">

      <!-- Gemini AI Settings -->
      <div class="settings-card">
        <div class="settings-card-header">
          <div class="settings-card-icon" style="background:rgba(108,99,255,0.12)">✨</div>
          <div>
            <div class="settings-card-title">AI Engine (Google Gemini)</div>
            <div class="settings-card-desc">Powers email drafts, summaries &amp; smart chat</div>
          </div>
        </div>
        <div class="settings-card-body">
          <div class="form-group">
            <label class="form-label">Status</label>
            <div style="display:flex;align-items:center">
              <span class="status-dot ${aiKeyStatus}" id="ai-status-dot"></span>
              <span class="status-text" id="ai-status-text">${aiKeyStatus === 'connected' ? 'Gemini API key configured' : 'Not configured'}</span>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Gemini API Key</label>
            <div class="form-input-group">
              <input class="form-input" id="ai-key-input" type="password"
                value="${Config.GEMINI_API_KEY || ''}"
                placeholder="AIzaSy..." />
              <button class="btn btn-icon btn-secondary" id="toggle-ai-key" title="Show/hide key">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              </button>
            </div>
            <p class="form-hint">Get a key at <a href="https://aistudio.google.com/app/apikey" target="_blank">aistudio.google.com</a>. Stored locally in browser only.</p>
          </div>
          <div class="form-group">
            <label class="form-label">Gemini Model</label>
            <select class="form-input" id="ai-model-select">
              <option value="gemini-2.0-flash" ${Config.AI_MODEL === 'gemini-2.0-flash' ? 'selected' : ''}>Gemini 2.0 Flash (Recommended — Next-Gen, Fast)</option>
              <option value="gemini-1.5-flash" ${Config.AI_MODEL === 'gemini-1.5-flash' ? 'selected' : ''}>Gemini 1.5 Flash (Fast &amp; Multimodal)</option>
              <option value="gemini-1.5-pro" ${Config.AI_MODEL === 'gemini-1.5-pro' ? 'selected' : ''}>Gemini 1.5 Pro (Reasoning &amp; Deep Analysis)</option>
            </select>
          </div>
          <div style="display:flex;gap:8px">
            <button class="btn btn-primary btn-sm" id="save-ai-btn">💾 Save Gemini Settings</button>
            <button class="btn btn-secondary btn-sm" id="test-ai-btn">🧪 Test Gemini AI</button>
          </div>
        </div>
      </div>

      <!-- Google OAuth Settings -->
      <div class="settings-card">
        <div class="settings-card-header">
          <div class="settings-card-icon" style="background:rgba(66,133,244,0.12)">
            <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
          </div>
          <div>
            <div class="settings-card-title">Google Workspace</div>
            <div class="settings-card-desc">Gmail, Drive, Docs &amp; Sheets access</div>
          </div>
        </div>
        <div class="settings-card-body">
          <div class="form-group">
            <label class="form-label">Status</label>
            <div style="display:flex;align-items:center;gap:8px">
              <span class="status-dot ${Auth.isAuthenticated() && !Auth.isDemoMode() ? 'connected' : Auth.isDemoMode() ? 'error' : 'disconnected'}"></span>
              <span class="status-text">
                ${Auth.isDemoMode()
                  ? '🎭 Demo Mode — no live data'
                  : Auth.isAuthenticated() && Auth.userProfile
                    ? `✅ Signed in as <strong>${escapeHtml(Auth.userProfile.name)}</strong> (${escapeHtml(Auth.userProfile.email)})`
                    : 'Not connected'}
              </span>
            </div>
          </div>
          ${Auth.isAuthenticated() && !Auth.isDemoMode() ? `
          <button class="btn btn-danger btn-sm" id="signout-settings-btn" style="margin-bottom:12px">Sign Out of Google</button>
          <div class="divider"></div>` : ''}
          <div class="form-group">
            <label class="form-label">${Auth.isAuthenticated() && !Auth.isDemoMode() ? 'Change' : 'Enter'} Google OAuth2 Client ID</label>
            <input class="form-input" id="client-id-input" type="text"
              value="${Config.GOOGLE_CLIENT_ID || ''}"
              placeholder="xxxxxxxxxxxx-xxxx.apps.googleusercontent.com" />
            <p class="form-hint">Get from <a href="https://console.cloud.google.com/apis/credentials" target="_blank">Google Cloud Console</a> → Credentials → OAuth 2.0 Client IDs.<br/>
            Add <code style="color:var(--color-accent)">${location.origin}</code> to Authorized JavaScript Origins.</p>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <button class="btn btn-primary btn-sm" id="save-google-btn">💾 Save &amp; Sign In</button>
            <button class="btn btn-secondary btn-sm" id="demo-mode-btn">🎭 Demo Mode</button>
          </div>
        </div>
      </div>

      <!-- About / Help -->
      <div class="settings-card">
        <div class="settings-card-header">
          <div class="settings-card-icon" style="background:rgba(0,212,170,0.12)">📖</div>
          <div>
            <div class="settings-card-title">Setup Guide</div>
            <div class="settings-card-desc">How to configure Google Workspace access</div>
          </div>
        </div>
        <div class="settings-card-body">
          <ol style="font-size:13px;color:var(--color-text-muted);padding-left:18px;line-height:2">
            <li>Go to <a href="https://console.cloud.google.com/" target="_blank">Google Cloud Console</a></li>
            <li>Create or select a project</li>
            <li>Enable these APIs: Gmail, Drive, Docs, Sheets</li>
            <li>Go to <strong>Credentials → Create OAuth2 Client ID</strong></li>
            <li>Choose <strong>Web Application</strong></li>
            <li>Add your URL to <strong>Authorized JavaScript Origins</strong></li>
            <li>Paste the Client ID above and click Save</li>
          </ol>
          <div style="background:rgba(108,99,255,0.06);border:1px solid rgba(108,99,255,0.2);border-radius:var(--radius-md);padding:12px;margin-top:8px;font-size:12px;color:var(--color-text-muted)">
            💡 Serve this app via <code style="color:var(--color-accent)">npx serve .</code> or a local HTTP server — OAuth requires an HTTP(S) origin, not <code>file://</code>.
          </div>
        </div>
      </div>

      <!-- Data & Privacy -->
      <div class="settings-card">
        <div class="settings-card-header">
          <div class="settings-card-icon" style="background:rgba(255,92,122,0.12)">🔒</div>
          <div>
            <div class="settings-card-title">Privacy &amp; Data</div>
            <div class="settings-card-desc">Your data stays in your browser</div>
          </div>
        </div>
        <div class="settings-card-body">
          <p style="font-size:13px;color:var(--color-text-muted);line-height:1.7">
            DistaMate is a <strong>100% client-side app</strong>. No data is ever stored on any server.
          </p>
          <ul style="font-size:12px;color:var(--color-text-muted);padding-left:16px;line-height:2;list-style:disc;margin-top:8px">
            <li>API keys stored in browser <code>localStorage</code> only</li>
            <li>All Google API calls go directly to Google's servers</li>
            <li>AI requests go directly to OpenRouter</li>
            <li>No analytics, no tracking, no telemetry</li>
          </ul>
          <button class="btn btn-danger btn-sm" id="clear-data-btn" style="margin-top:12px">🗑️ Clear All Stored Data</button>
        </div>
      </div>

    </div>
  `;

  // Toggle API key visibility
  document.getElementById('toggle-ai-key')?.addEventListener('click', () => {
    const input = document.getElementById('ai-key-input');
    if (input) input.type = input.type === 'password' ? 'text' : 'password';
  });

  // Save AI settings
  document.getElementById('save-ai-btn')?.addEventListener('click', () => {
    const key = document.getElementById('ai-key-input')?.value?.trim();
    const model = document.getElementById('ai-model-select')?.value;
    if (!key) { toast.warning('Please enter an API key.'); return; }
    Config.GEMINI_API_KEY = key;
    Config.AI_MODEL = model;
    Config.save();
    document.getElementById('ai-status-dot').className = 'status-dot connected';
    document.getElementById('ai-status-text').textContent = 'Gemini key saved';
    toast.success('Gemini settings saved!');
  });

  // Test AI
  document.getElementById('test-ai-btn')?.addEventListener('click', async () => {
    const btn = document.getElementById('test-ai-btn');
    btn.textContent = '...testing';
    btn.disabled = true;
    try {
      const result = await AI._call(
        [{ role: 'user', content: 'Say "DistaMate AI is working!" in exactly those words.' }],
        'You are a test bot. Reply exactly as instructed.'
      );
      toast.success('✅ AI Test: ' + result.substring(0, 60));
    } catch (e) {
      toast.error('AI Test failed: ' + e.message);
    } finally {
      btn.textContent = '🧪 Test AI';
      btn.disabled = false;
    }
  });

  // Save Google Client ID
  document.getElementById('save-google-btn')?.addEventListener('click', () => {
    const clientId = document.getElementById('client-id-input')?.value?.trim();
    if (!clientId) { toast.warning('Please enter your Google Client ID.'); return; }
    if (!clientId.includes('.apps.googleusercontent.com')) {
      toast.warning('That doesn\'t look like a valid Client ID.');
      return;
    }
    Config.GOOGLE_CLIENT_ID = clientId;
    Config.save();
    toast.success('Client ID saved! Starting sign-in...');
    setTimeout(() => Auth.signIn(), 800);
  });

  // Demo mode
  document.getElementById('demo-mode-btn')?.addEventListener('click', () => {
    Auth._demoMode();
    toast.info('Switched to Demo mode — showing sample data');
    setTimeout(() => window._app?.switchPanel('dashboard'), 200);
  });

  // Sign out from settings
  document.getElementById('signout-settings-btn')?.addEventListener('click', () => {
    Auth.signOut();
  });
  document.getElementById('clear-data-btn')?.addEventListener('click', async () => {
    const { modal } = await import('../ui.js');
    const confirmed = await modal.confirm({
      title: '🗑️ Clear All Data?',
      body: 'This will remove your stored API keys and settings. You will need to reconfigure DistaMate.',
      confirmLabel: 'Clear All',
      confirmClass: 'btn-danger',
    });
    if (confirmed) {
      Object.values(Config.STORAGE_KEYS).forEach(k => localStorage.removeItem(k));
      toast.success('All data cleared. Reloading...');
      setTimeout(() => location.reload(), 1500);
    }
  });
}
