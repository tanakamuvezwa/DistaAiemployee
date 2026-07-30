/**
 * DistaMate — Google OAuth2 Authentication
 * Redesigned for real sign-in: GIS token flow, no GAPI dependency for API calls.
 */

import Config from './config.js';
import { toast } from './ui.js';

const Auth = {
  tokenClient: null,
  accessToken: null,
  tokenExpiry: null,
  userProfile: null,
  onAuthSuccess: null,

  // ── Initialize ──────────────────────────────────────────────────
  async init(onSuccess) {
    this.onAuthSuccess = onSuccess;
    Config.load();
    this._wireAuthUI();

    // Client ID is set (hardcoded or saved) — go straight to sign-in screen
    if (Config.GOOGLE_CLIENT_ID) {
      const field = document.getElementById('client-id-field');
      if (field) field.value = Config.GOOGLE_CLIENT_ID;
      this._showStep(2);
    }
  },

  // ── Wire all auth-screen interactions ──────────────────────────
  _wireAuthUI() {
    // Show current origin in setup guide
    const originEl = document.getElementById('current-origin');
    if (originEl) originEl.textContent = location.origin;

    // Setup guide toggle
    document.getElementById('setup-toggle-link')?.addEventListener('click', () => {
      const guide = document.getElementById('setup-guide');
      const link = document.getElementById('setup-toggle-link');
      if (guide.classList.contains('hidden')) {
        guide.classList.remove('hidden');
        link.textContent = ' Hide guide ▴';
      } else {
        guide.classList.add('hidden');
        link.textContent = ' Show setup guide ▸';
      }
    });

    // Step 1 Continue
    document.getElementById('step1-continue-btn')?.addEventListener('click', () => {
      const clientId = document.getElementById('client-id-field')?.value?.trim();
      if (!clientId) {
        this._shake('client-id-field');
        toast.warning('Please enter your Google Client ID.');
        return;
      }
      if (!clientId.includes('.apps.googleusercontent.com')) {
        toast.warning('That doesn\'t look like a valid Client ID. It should end with .apps.googleusercontent.com');
        return;
      }
      Config.GOOGLE_CLIENT_ID = clientId;
      Config.save();
      this._showStep(2);
    });

    // Demo mode
    document.getElementById('demo-mode-btn')?.addEventListener('click', () => {
      this._demoMode();
    });

    // Step 2: Sign in
    document.getElementById('google-signin-btn')?.addEventListener('click', () => {
      this.signIn();
    });

    // Back to step 1
    document.getElementById('back-to-step1')?.addEventListener('click', () => {
      this._showStep(1);
    });

    // Allow Enter key on client-id-field
    document.getElementById('client-id-field')?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') document.getElementById('step1-continue-btn')?.click();
    });

    // Sign-out button
    document.getElementById('signout-btn')?.addEventListener('click', () => this.signOut());
  },

  _showStep(step) {
    document.getElementById('auth-step-1')?.classList.toggle('hidden', step !== 1);
    document.getElementById('auth-step-2')?.classList.toggle('hidden', step !== 2);
    document.getElementById('auth-signing-in')?.classList.add('hidden');

    // Step dots
    document.getElementById('step-1-dot')?.classList.toggle('active', step >= 1);
    document.getElementById('step-2-dot')?.classList.toggle('active', step >= 2);
  },

  _setSigningIn(msg = 'Signing in...') {
    document.getElementById('auth-step-1')?.classList.add('hidden');
    document.getElementById('auth-step-2')?.classList.add('hidden');
    document.getElementById('auth-signing-in')?.classList.remove('hidden');
    const msgEl = document.getElementById('auth-signing-msg');
    if (msgEl) msgEl.textContent = msg;
  },

  _shake(inputId) {
    const el = document.getElementById(inputId);
    if (!el) return;
    el.style.animation = 'none';
    el.offsetHeight; // reflow
    el.style.animation = 'shake 0.4s ease';
  },

  // ── Google Sign-In (GIS token flow) ────────────────────────────
  signIn() {
    if (!Config.GOOGLE_CLIENT_ID) {
      this._showStep(1);
      toast.warning('Please enter your Google Client ID first.');
      return;
    }

    // Wait for GIS to be ready
    this._waitForGIS().then(() => {
      try {
        this.tokenClient = window.google.accounts.oauth2.initTokenClient({
          client_id: Config.GOOGLE_CLIENT_ID,
          scope: Config.GOOGLE_SCOPES,
          callback: (response) => this._handleTokenResponse(response),
          error_callback: (err) => {
            console.error('GIS error:', err);
            toast.error('Sign-in failed: ' + (err.message || err.type || 'Unknown error'));
            this._showStep(2);
          },
        });
        this.tokenClient.requestAccessToken({ prompt: '' });
      } catch (e) {
        toast.error('Could not start sign-in: ' + e.message);
        this._showStep(2);
      }
    });
  },

  _waitForGIS() {
    return new Promise((resolve, reject) => {
      if (window.google?.accounts?.oauth2) { resolve(); return; }
      let attempts = 0;
      const check = setInterval(() => {
        attempts++;
        if (window.google?.accounts?.oauth2) {
          clearInterval(check);
          resolve();
        } else if (attempts > 50) { // 5 seconds
          clearInterval(check);
          reject(new Error('Google Identity Services failed to load. Check your internet connection.'));
        }
      }, 100);
    });
  },

  async _handleTokenResponse(response) {
    if (response.error) {
      // access_denied = user cancelled, not an error
      if (response.error === 'access_denied') {
        toast.info('Sign-in cancelled.');
        this._showStep(2);
      } else {
        toast.error(`Authentication failed: ${response.error_description || response.error}`);
        this._showStep(2);
      }
      return;
    }

    this.accessToken = response.access_token;
    this.tokenExpiry = Date.now() + (response.expires_in || 3600) * 1000;

    this._setSigningIn('Loading your profile...');

    try {
      await this._fetchUserProfile();
      this._setSigningIn('Connecting to your workspace...');

      // Small delay for UX
      await new Promise(r => setTimeout(r, 600));

      if (this.onAuthSuccess) this.onAuthSuccess(this.userProfile);
    } catch (e) {
      toast.error('Failed after sign-in: ' + e.message);
      this._showStep(2);
    }
  },

  async _fetchUserProfile() {
    const res = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
      headers: { Authorization: `Bearer ${this.accessToken}` }
    });
    if (!res.ok) throw new Error('Could not fetch user profile (HTTP ' + res.status + ')');
    this.userProfile = await res.json();
  },

  signOut() {
    // Revoke token
    if (this.accessToken && window.google?.accounts?.oauth2) {
      window.google.accounts.oauth2.revoke(this.accessToken, () => {});
    }
    this.accessToken = null;
    this.tokenExpiry = null;
    this.userProfile = null;

    // Show auth screen
    const app = document.getElementById('app');
    const authScreen = document.getElementById('auth-screen');
    app?.classList.add('hidden');
    authScreen?.style.removeProperty('display');
    authScreen?.style.setProperty('display', 'flex');

    // Reset to step that makes sense
    if (Config.GOOGLE_CLIENT_ID) {
      this._showStep(2);
    } else {
      this._showStep(1);
    }

    toast.info('Signed out successfully.');
  },

  // ── Demo Mode ───────────────────────────────────────────────────
  _demoMode() {
    this.accessToken = 'DEMO';
    this.userProfile = {
      name: 'Demo User',
      email: 'demo@distamate.app',
      picture: null,
    };
    if (this.onAuthSuccess) this.onAuthSuccess(this.userProfile);
  },

  // ── Helpers ─────────────────────────────────────────────────────
  isAuthenticated() { return !!this.accessToken; },
  isDemoMode()      { return this.accessToken === 'DEMO'; },
  isTokenExpired()  { return this.tokenExpiry && Date.now() > this.tokenExpiry; },

  // Make authenticated fetch requests to Google APIs
  async request(url, options = {}) {
    if (this.isDemoMode()) throw new Error('DEMO_MODE');
    if (this.isTokenExpired()) {
      toast.warning('Session expired. Please sign in again.');
      this.signOut();
      throw new Error('TOKEN_EXPIRED');
    }

    const res = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json',
        ...options.headers,
      }
    });

    if (res.status === 401) {
      toast.warning('Session expired. Please sign in again.');
      this.signOut();
      throw new Error('Unauthorized — please sign in again.');
    }

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      const msg = errBody.error?.message || errBody.error?.errors?.[0]?.message || `HTTP ${res.status} ${res.statusText}`;
      throw new Error(msg);
    }

    // Handle 204 No Content
    if (res.status === 204) return {};

    return res.json();
  }
};

export default Auth;
