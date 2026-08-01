/**
 * DistaAiEmployee — Voice Engine (Jarvis Mode)
 * Web Speech API: STT + TTS + Web Audio waveform visualization
 */

import AI from './ai.js';

const BEEP_ACTIVATE   = [880, 0.08, 'sine'];
const BEEP_DEACTIVATE = [440, 0.08, 'sine'];
const BEEP_ERROR      = [220, 0.15, 'sawtooth'];

const Voice = {
  // ── State ────────────────────────────────────────────────────
  state: 'idle', // idle | listening | thinking | speaking
  recognition: null,
  synthesis: window.speechSynthesis,
  audioCtx: null,
  analyser: null,
  micStream: null,
  animFrame: null,
  onResult: null,      // callback(text) set by app
  _spaceDown: false,
  _currentUtterance: null,

  // ── Init ─────────────────────────────────────────────────────
  init(onResultCallback) {
    this.onResult = onResultCallback;

    if (!('SpeechRecognition' in window) && !('webkitSpeechRecognition' in window)) {
      console.warn('SpeechRecognition not supported in this browser.');
      return false;
    }

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SR();
    this.recognition.continuous    = false;
    this.recognition.interimResults = true;
    this.recognition.lang          = 'en-US';
    this.recognition.maxAlternatives = 1;

    this.recognition.onstart  = () => this._onStart();
    this.recognition.onresult = (e) => this._onRecognitionResult(e);
    this.recognition.onend    = () => this._onEnd();
    this.recognition.onerror  = (e) => this._onError(e);

    // Hold-Space to talk
    document.addEventListener('keydown', (e) => {
      if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA' && !this._spaceDown) {
        this._spaceDown = true;
        this.startListening();
      }
    });
    document.addEventListener('keyup', (e) => {
      if (e.code === 'Space' && this._spaceDown) {
        this._spaceDown = false;
        if (this.state === 'listening') this.recognition.stop();
      }
    });

    // Mic button
    document.getElementById('voice-btn')?.addEventListener('click', () => {
      if (this.state === 'idle') {
        this.startListening();
      } else if (this.state === 'listening') {
        this.recognition.stop();
      } else if (this.state === 'speaking') {
        this.stopSpeaking();
      }
    });

    // Cancel button inside orb overlay
    document.getElementById('voice-cancel-btn')?.addEventListener('click', () => {
      this._cancel();
    });

    // Preload voices
    this.synthesis.getVoices();
    this.synthesis.onvoiceschanged = () => this.synthesis.getVoices();

    return true;
  },

  // ── Start Listening ──────────────────────────────────────────
  async startListening() {
    if (this.state !== 'idle') return;
    this._beep(...BEEP_ACTIVATE);
    this._setState('listening');
    this._showOrb();
    this._setTranscript('Listening...', false);

    try {
      this.micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this._startWaveform(this.micStream);
    } catch {
      // Waveform is optional — continue without it
    }

    try {
      this.recognition.start();
    } catch (e) {
      this._onError({ error: e.message });
    }
  },

  // ── Recognition Events ───────────────────────────────────────
  _onStart() {
    this._setState('listening');
  },

  _onRecognitionResult(event) {
    let interim = '';
    let final   = '';
    for (const result of event.results) {
      if (result.isFinal) final   += result[0].transcript;
      else                interim += result[0].transcript;
    }
    this._setTranscript(final || interim, !!final);
  },

  _onEnd() {
    this._stopWaveform();
    if (this.micStream) {
      this.micStream.getTracks().forEach(t => t.stop());
      this.micStream = null;
    }

    const transcript = document.getElementById('voice-transcript')?.dataset.final;
    if (transcript && transcript.trim()) {
      this._processCommand(transcript.trim());
    } else {
      this._beep(...BEEP_DEACTIVATE);
      this._setState('idle');
      this._hideOrb();
    }
  },

  _onError(e) {
    if (e.error === 'no-speech' || e.error === 'aborted') {
      this._setState('idle');
      this._hideOrb();
      return;
    }
    this._beep(...BEEP_ERROR);
    this._setTranscript('❌ ' + (e.error || 'Error'), false);
    setTimeout(() => { this._setState('idle'); this._hideOrb(); }, 2000);
  },

  // ── Process Command ──────────────────────────────────────────
  async _processCommand(text) {
    this._setState('thinking');
    this._setTranscript(`"${text}"`, false);

    // Check for panel-switching voice commands first
    const handled = this._handleLocalCommand(text.toLowerCase());
    if (handled) {
      await this._delayedIdle(1200);
      return;
    }

    // Route to AI
    try {
      if (this.onResult) {
        const reply = await this.onResult(text);
        if (reply) await this.speak(reply);
        else { this._setState('idle'); this._hideOrb(); }
      }
    } catch (e) {
      this._beep(...BEEP_ERROR);
      await this.speak('Sorry, something went wrong. ' + e.message);
    }
  },

  // ── Local Commands (no AI needed) ───────────────────────────
  _handleLocalCommand(text) {
    const cmds = [
      { triggers: ['open email', 'go to email', 'show email', 'check email'],  panel: 'email',    reply: 'Opening your emails.' },
      { triggers: ['open drive', 'go to drive', 'show drive', 'my drive'],     panel: 'drive',    reply: 'Opening Google Drive.' },
      { triggers: ['open doc', 'go to doc', 'show doc'],                        panel: 'docs',     reply: 'Opening Documents.' },
      { triggers: ['open sheet', 'go to sheet', 'show sheet'],                 panel: 'sheets',   reply: 'Opening Sheets.' },
      { triggers: ['dashboard', 'go home', 'home'],                             panel: 'dashboard',reply: 'Going to Dashboard.' },
      { triggers: ['open setting', 'go to setting', 'settings'],                panel: 'settings', reply: 'Opening Settings.' },
    ];

    for (const cmd of cmds) {
      if (cmd.triggers.some(t => text.includes(t))) {
        window._app?.switchPanel(cmd.panel);
        this.speak(cmd.reply);
        return true;
      }
    }

    // Stop speaking
    if (text.includes('stop') || text.includes('quiet') || text.includes('silence')) {
      this.stopSpeaking();
      this._setState('idle'); this._hideOrb();
      return true;
    }

    return false;
  },

  // ── Text-to-Speech ───────────────────────────────────────────
  async speak(text) {
    return new Promise((resolve) => {
      this.synthesis.cancel();
      this._setState('speaking');
      this._setTranscript(text.length > 120 ? text.slice(0, 120) + '…' : text, false);

      const utterance = new SpeechSynthesisUtterance(text);
      this._currentUtterance = utterance;

      // Pick best voice
      const voices = this.synthesis.getVoices();
      const preferred = voices.find(v =>
        (v.name.includes('Google') && v.lang.startsWith('en'))
        || (v.name.includes('Microsoft') && v.lang.startsWith('en'))
      ) || voices.find(v => v.lang.startsWith('en')) || voices[0];

      if (preferred) utterance.voice = preferred;
      utterance.rate  = 1.05;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      utterance.onend = () => {
        this._setState('idle');
        this._hideOrb();
        resolve();
      };
      utterance.onerror = () => {
        this._setState('idle');
        this._hideOrb();
        resolve();
      };

      this.synthesis.speak(utterance);
    });
  },

  stopSpeaking() {
    this.synthesis.cancel();
    this._setState('idle');
    this._hideOrb();
  },

  // ── Waveform Visualization ───────────────────────────────────
  _startWaveform(stream) {
    try {
      this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      this.analyser = this.audioCtx.createAnalyser();
      this.analyser.fftSize = 64;

      const source = this.audioCtx.createMediaStreamSource(stream);
      source.connect(this.analyser);

      const bars = document.querySelectorAll('.voice-bar');
      const data = new Uint8Array(this.analyser.frequencyBinCount);

      const draw = () => {
        this.animFrame = requestAnimationFrame(draw);
        this.analyser.getByteFrequencyData(data);
        bars.forEach((bar, i) => {
          const val = (data[i * 2] || 0) / 255;
          bar.style.height = Math.max(4, val * 60) + 'px';
          bar.style.opacity = 0.4 + val * 0.6;
        });
      };
      draw();
    } catch { /* skip viz */ }
  },

  _stopWaveform() {
    if (this.animFrame) { cancelAnimationFrame(this.animFrame); this.animFrame = null; }
    if (this.audioCtx)  { this.audioCtx.close().catch(() => {}); this.audioCtx = null; }
    document.querySelectorAll('.voice-bar').forEach(b => { b.style.height = '4px'; b.style.opacity = '0.3'; });
  },

  // ── Beep ─────────────────────────────────────────────────────
  _beep(freq, duration, type = 'sine') {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain); gain.connect(ctx.destination);
      osc.type = type;
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
      osc.start(); osc.stop(ctx.currentTime + duration);
    } catch { /* skip */ }
  },

  // ── UI State ─────────────────────────────────────────────────
  _setState(newState) {
    this.state = newState;
    const orb = document.getElementById('voice-orb');
    const btn = document.getElementById('voice-btn');
    const label = document.getElementById('voice-orb-state');

    if (orb) {
      orb.dataset.state = newState;
    }
    if (btn) {
      btn.dataset.state = newState;
      btn.title = {
        idle:      'Voice Command (Space)',
        listening: 'Listening — click to stop',
        thinking:  'Thinking...',
        speaking:  'Speaking — click to stop',
      }[newState] || 'Voice';
    }
    if (label) {
      label.textContent = {
        idle:      '',
        listening: 'Listening...',
        thinking:  'Thinking...',
        speaking:  'Speaking...',
      }[newState] || '';
    }
  },

  _setTranscript(text, isFinal) {
    const el = document.getElementById('voice-transcript');
    if (!el) return;
    el.textContent = text;
    el.dataset.final = isFinal ? text : '';
  },

  _showOrb() {
    const overlay = document.getElementById('voice-overlay');
    overlay?.classList.remove('hidden');
    requestAnimationFrame(() => overlay?.classList.add('visible'));
  },

  _hideOrb() {
    const overlay = document.getElementById('voice-overlay');
    overlay?.classList.remove('visible');
    setTimeout(() => overlay?.classList.add('hidden'), 400);
  },

  _cancel() {
    this.recognition?.abort();
    this.synthesis.cancel();
    this._stopWaveform();
    if (this.micStream) { this.micStream.getTracks().forEach(t => t.stop()); this.micStream = null; }
    this._setState('idle');
    this._hideOrb();
  },

  async _delayedIdle(ms) {
    await new Promise(r => setTimeout(r, ms));
    this._setState('idle');
    this._hideOrb();
  },

  isSupported() {
    return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
  },
};

export default Voice;
