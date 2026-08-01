/**
 * DistaAiEmployee — FX Engine
 * Particle network background + 3D mouse-reactive card tilt
 */

const FX = {
  canvas: null,
  ctx: null,
  particles: [],
  mouse: { x: -9999, y: -9999 },
  animId: null,
  W: 0, H: 0,

  init() {
    this._setupCanvas();
    this._spawnParticles(90);
    this._animate();
    this._trackMouse();
    this._initCardTilt();
    window.addEventListener('resize', () => this._resize());

    // Re-apply tilt to newly rendered cards (panels load async)
    const observer = new MutationObserver(() => this._initCardTilt());
    observer.observe(document.getElementById('main-content') || document.body, {
      childList: true, subtree: true,
    });
  },

  // ── Canvas setup ─────────────────────────────────────────────
  _setupCanvas() {
    this.canvas = document.getElementById('bg-canvas');
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this._resize();
  },

  _resize() {
    if (!this.canvas) return;
    this.W = this.canvas.width  = window.innerWidth;
    this.H = this.canvas.height = window.innerHeight;
  },

  // ── Particles ────────────────────────────────────────────────
  _spawnParticles(n) {
    this.particles = Array.from({ length: n }, () => this._newParticle());
  },

  _newParticle() {
    return {
      x: Math.random() * this.W,
      y: Math.random() * this.H,
      vx: (Math.random() - 0.5) * 0.28,
      vy: (Math.random() - 0.5) * 0.28,
      r:  Math.random() * 1.4 + 0.3,
      a:  Math.random() * 0.45 + 0.08,
      phase: Math.random() * Math.PI * 2,
      speed: Math.random() * 0.018 + 0.006,
    };
  },

  // ── Main animation loop ──────────────────────────────────────
  _animate() {
    const { canvas, ctx, particles, W, H, mouse } = this;
    if (!ctx) { this.animId = requestAnimationFrame(() => this._animate()); return; }

    ctx.clearRect(0, 0, W, H);

    for (const p of particles) {
      // Move
      p.x += p.vx;
      p.y += p.vy;
      p.phase += p.speed;

      // Wrap
      if (p.x < -5)   p.x = W + 5;
      if (p.x > W + 5) p.x = -5;
      if (p.y < -5)   p.y = H + 5;
      if (p.y > H + 5) p.y = -5;

      // Draw soft glow
      const alpha = p.a * (0.65 + 0.35 * Math.sin(p.phase));
      const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 5);
      gradient.addColorStop(0, `rgba(0,229,255,${alpha})`);
      gradient.addColorStop(1, 'rgba(0,229,255,0)');
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r * 5, 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.fill();

      // Core dot
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(0,229,255,${alpha})`;
      ctx.fill();
    }

    // Connections between nearby particles
    const MAX_DIST = 130;
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const d  = Math.sqrt(dx * dx + dy * dy);
        if (d < MAX_DIST) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(0,229,255,${(1 - d / MAX_DIST) * 0.07})`;
          ctx.lineWidth = 0.6;
          ctx.stroke();
        }
      }
    }

    // Mouse web — purple tendrils from cursor to nearby particles
    for (const p of particles) {
      const dx = p.x - mouse.x;
      const dy = p.y - mouse.y;
      const d  = Math.sqrt(dx * dx + dy * dy);
      if (d < 110) {
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(mouse.x, mouse.y);
        ctx.strokeStyle = `rgba(124,58,237,${(1 - d / 110) * 0.25})`;
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }
    }

    this.animId = requestAnimationFrame(() => this._animate());
  },

  _trackMouse() {
    window.addEventListener('mousemove', (e) => {
      this.mouse.x = e.clientX;
      this.mouse.y = e.clientY;
    });
    window.addEventListener('mouseleave', () => {
      this.mouse.x = -9999;
      this.mouse.y = -9999;
    });
  },

  // ── 3D Card Tilt ─────────────────────────────────────────────
  _tiltTargets: new WeakSet(),

  _initCardTilt() {
    const SELECTORS = [
      '.section-card', '.stat-card', '.settings-card',
      '.file-card', '.auth-card', '.email-item',
    ].join(',');

    document.querySelectorAll(SELECTORS).forEach(el => {
      if (this._tiltTargets.has(el)) return;
      this._tiltTargets.add(el);

      el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width  - 0.5;
        const y = (e.clientY - r.top)  / r.height - 0.5;
        el.style.transition = 'none';
        el.style.transform  =
          `perspective(700px) rotateY(${x * 9}deg) rotateX(${-y * 9}deg) translateZ(8px) scale(1.008)`;
      });

      el.addEventListener('mouseleave', () => {
        el.style.transition = 'transform 0.55s cubic-bezier(0.4,0,0.2,1)';
        el.style.transform  =
          'perspective(700px) rotateY(0deg) rotateX(0deg) translateZ(0px) scale(1)';
      });
    });
  },
};

export default FX;
