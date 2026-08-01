/**
 * DistaAiEmployee — FX Engine v2 (Tony Stark / 4D Edition)
 * True 4D rotating tesseract + arc reactor scanner + gold particle network + 3D card tilt
 */

// ══════════════════════════════════════════════════════════════
// 4D HYPERCUBE (TESSERACT) — Genuine 4D→3D→2D double projection
// ══════════════════════════════════════════════════════════════
class Tesseract {
  constructor() {
    // 16 vertices: all (±1, ±1, ±1, ±1) combinations
    this.verts = [];
    for (let x = -1; x <= 1; x += 2)
      for (let y = -1; y <= 1; y += 2)
        for (let z = -1; z <= 1; z += 2)
          for (let w = -1; w <= 1; w += 2)
            this.verts.push([x, y, z, w]);

    // 32 edges: connect vertices differing in exactly 1 coordinate
    this.edges = [];
    for (let i = 0; i < 16; i++)
      for (let j = i + 1; j < 16; j++) {
        const diffs = this.verts[i].filter((v, k) => v !== this.verts[j][k]).length;
        if (diffs === 1) this.edges.push([i, j]);
      }

    // Rotation angles in all 6 rotation planes of 4D space
    this.a = { xy: 0, xz: 0, xw: 0, yz: 0, yw: 0, zw: 0 };
  }

  // Apply 4D rotation in plane (i,j)
  _rot(v, i, j, angle) {
    const c = Math.cos(angle), s = Math.sin(angle);
    const r = [...v];
    r[i] = v[i] * c - v[j] * s;
    r[j] = v[i] * s + v[j] * c;
    return r;
  }

  // Rotate vertex through all 4D planes
  _rotate(v) {
    v = this._rot(v, 0, 1, this.a.xy);
    v = this._rot(v, 0, 2, this.a.xz);
    v = this._rot(v, 0, 3, this.a.xw); // ← THE 4D ROTATION (most visually striking)
    v = this._rot(v, 1, 2, this.a.yz);
    v = this._rot(v, 1, 3, this.a.yw);
    v = this._rot(v, 2, 3, this.a.zw);
    return v;
  }

  // Double perspective: 4D→3D→2D
  _project(v, cx, cy, scale) {
    // 4D → 3D (w-axis perspective)
    const d4 = 3.5;
    const f4 = 1 / (d4 - v[3]);
    const x3 = v[0] * f4, y3 = v[1] * f4, z3 = v[2] * f4;

    // 3D → 2D (z-axis perspective)
    const d3 = 4.0;
    const f3 = 1 / (d3 - z3);
    return {
      x: x3 * f3 * scale + cx,
      y: y3 * f3 * scale + cy,
      depth: (z3 - v[3]) * 0.5,
      w: v[3],
    };
  }

  // Advance rotation — asymmetric speeds = continuous unique motion
  update() {
    this.a.xy += 0.0022;
    this.a.xz += 0.0038;
    this.a.xw += 0.0055; // Main 4D fold
    this.a.yz += 0.0016;
    this.a.yw += 0.0031;
    this.a.zw += 0.0047;
  }

  draw(ctx, cx, cy, scale) {
    const pts = this.verts.map(v => this._project(this._rotate(v), cx, cy, scale));

    // Draw edges
    for (const [i, j] of this.edges) {
      const a = pts[i], b = pts[j];
      const avgW = (a.w + b.w) * 0.5;
      const avgD = (a.depth + b.depth) * 0.5;
      const t = (avgW + 1) * 0.5; // 0=blue, 0.5=white, 1=gold

      // Blue → White → Gold color shift based on 4th dimension position
      const R = Math.round(t > 0.5 ? 255 : t * 2 * 255);
      const G = Math.round(t > 0.5 ? 184 + (t - 0.5) * 2 * 71 : 130 + t * 2 * 54);
      const B = Math.round(t > 0.5 ? (1 - (t - 0.5) * 2) * 255 : 255);

      const alpha = Math.max(0.03, Math.min(0.55, 0.1 + (avgD + 2) * 0.08));
      const lineW = Math.max(0.4, 0.5 + (avgD + 2) * 0.35);

      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.strokeStyle = `rgba(${R},${G},${B},${alpha})`;
      ctx.lineWidth = lineW;
      ctx.stroke();
    }

    // Draw vertices as glowing nodes
    for (const p of pts) {
      const t = (p.w + 1) * 0.5;
      const R = Math.round(t > 0.5 ? 255 : t * 2 * 255);
      const G = Math.round(180);
      const B = Math.round(t > 0.5 ? (1 - (t - 0.5) * 2) * 255 : 255);
      const sz = Math.max(1, 1.5 + (p.depth + 2) * 0.9);
      const al = Math.max(0.2, 0.35 + (p.depth + 2) * 0.1);

      // Glow halo
      const grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, sz * 6);
      grd.addColorStop(0, `rgba(${R},${G},${B},${al * 0.5})`);
      grd.addColorStop(1, `rgba(${R},${G},${B},0)`);
      ctx.beginPath();
      ctx.arc(p.x, p.y, sz * 6, 0, Math.PI * 2);
      ctx.fillStyle = grd;
      ctx.fill();

      // Core dot
      ctx.beginPath();
      ctx.arc(p.x, p.y, sz, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${R},${G},${B},${al})`;
      ctx.fill();
    }
  }
}

// ══════════════════════════════════════════════════════════════
// ARC REACTOR SCANNER — Rotating sweeping beam (JARVIS-style)
// ══════════════════════════════════════════════════════════════
class ArcScanner {
  constructor() { this.angle = 0; }
  update()      { this.angle += 0.006; }

  draw(ctx, cx, cy, W, H) {
    const r = Math.hypot(W, H) * 0.55;
    const sweep = 0.45;

    // Sweeping sector glow
    const grd = ctx.createConicalGradient
      ? ctx.createConicalGradient(this.angle, cx, cy) // not standard, skip
      : null;

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, r, this.angle - sweep, this.angle);
    ctx.closePath();

    const radGrd = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
    radGrd.addColorStop(0, 'rgba(0,180,255,0.03)');
    radGrd.addColorStop(0.7, 'rgba(0,180,255,0.02)');
    radGrd.addColorStop(1, 'rgba(0,180,255,0)');
    ctx.fillStyle = radGrd;
    ctx.fill();

    // Leading edge bright line
    const ex = cx + Math.cos(this.angle) * r;
    const ey = cy + Math.sin(this.angle) * r;
    const lineGrd = ctx.createLinearGradient(cx, cy, ex, ey);
    lineGrd.addColorStop(0, 'rgba(0,180,255,0)');
    lineGrd.addColorStop(0.4, 'rgba(0,180,255,0.06)');
    lineGrd.addColorStop(1, 'rgba(0,200,255,0.18)');
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(ex, ey);
    ctx.strokeStyle = lineGrd;
    ctx.lineWidth = 1.2;
    ctx.stroke();
    ctx.restore();
  }
}

// ══════════════════════════════════════════════════════════════
// PARTICLE — Arc reactor blue + Stark gold variants
// ══════════════════════════════════════════════════════════════
class Particle {
  constructor(W, H) {
    this.W = W; this.H = H;
    this.reset();
  }
  reset() {
    this.x     = Math.random() * this.W;
    this.y     = Math.random() * this.H;
    this.vx    = (Math.random() - 0.5) * 0.24;
    this.vy    = (Math.random() - 0.5) * 0.24;
    this.r     = Math.random() * 1.3 + 0.2;
    this.a     = Math.random() * 0.4 + 0.07;
    this.phase = Math.random() * Math.PI * 2;
    this.spd   = Math.random() * 0.014 + 0.004;
    this.gold  = Math.random() < 0.18; // 18% Stark gold
  }
}

// ══════════════════════════════════════════════════════════════
// MAIN FX ENGINE
// ══════════════════════════════════════════════════════════════
const FX = {
  canvas: null, ctx: null,
  W: 0, H: 0,
  particles: [],
  tesseract: null,
  scanner: null,
  mouse: { x: -9999, y: -9999 },
  _tiltSet: new WeakSet(),

  init() {
    this.canvas = document.getElementById('bg-canvas');
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this._resize();
    window.addEventListener('resize', () => this._resize());

    this.tesseract = new Tesseract();
    this.scanner   = new ArcScanner();
    this._spawnParticles(65);
    this._loop();
    this._trackMouse();
    this._initCardTilt();

    // Re-apply tilt as panels render dynamically
    new MutationObserver(() => this._initCardTilt()).observe(
      document.getElementById('main-content') || document.body,
      { childList: true, subtree: true }
    );
  },

  _resize() {
    if (!this.canvas) return;
    this.W = this.canvas.width  = window.innerWidth;
    this.H = this.canvas.height = window.innerHeight;
  },

  _spawnParticles(n) {
    this.particles = Array.from({ length: n }, () => new Particle(this.W, this.H));
  },

  _loop() {
    const { ctx, W, H, particles, tesseract, scanner, mouse } = this;
    if (!ctx) { requestAnimationFrame(() => this._loop()); return; }

    ctx.clearRect(0, 0, W, H);

    // Layer 1: rolling 4D tesseract (background centerpiece)
    tesseract.update();
    tesseract.draw(ctx, W / 2, H / 2, Math.min(W, H) * 0.21);

    // Layer 2: JARVIS arc scanner beam
    scanner.update();
    scanner.draw(ctx, W / 2, H / 2, W, H);

    // Layer 3: particles
    for (const p of particles) {
      p.x += p.vx; p.y += p.vy;
      p.phase += p.spd;
      if (p.x < -5) p.x = W + 5; else if (p.x > W + 5) p.x = -5;
      if (p.y < -5) p.y = H + 5; else if (p.y > H + 5) p.y = -5;

      const al = p.a * (0.65 + 0.35 * Math.sin(p.phase));
      const [R, G, B] = p.gold ? [255, 184, 0] : [0, 180, 255];

      const grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 6);
      grd.addColorStop(0, `rgba(${R},${G},${B},${al * 0.4})`);
      grd.addColorStop(1, `rgba(${R},${G},${B},0)`);
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r * 6, 0, Math.PI * 2);
      ctx.fillStyle = grd; ctx.fill();

      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${R},${G},${B},${al})`; ctx.fill();
    }

    // Layer 4: particle connections
    const MAX = 115;
    for (let i = 0; i < particles.length; i++)
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const d  = Math.sqrt(dx * dx + dy * dy);
        if (d < MAX) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(0,180,255,${(1 - d / MAX) * 0.055})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }

    // Layer 5: gold mouse tendrils
    for (const p of particles) {
      const dx = p.x - mouse.x, dy = p.y - mouse.y;
      const d  = Math.sqrt(dx * dx + dy * dy);
      if (d < 100) {
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(mouse.x, mouse.y);
        ctx.strokeStyle = `rgba(255,184,0,${(1 - d / 100) * 0.22})`;
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }
    }

    requestAnimationFrame(() => this._loop());
  },

  _trackMouse() {
    window.addEventListener('mousemove', e => { this.mouse.x = e.clientX; this.mouse.y = e.clientY; });
    window.addEventListener('mouseleave', () => { this.mouse.x = -9999; this.mouse.y = -9999; });
  },

  _initCardTilt() {
    document.querySelectorAll('.section-card,.stat-card,.settings-card,.file-card,.auth-card,.email-item').forEach(el => {
      if (this._tiltSet.has(el)) return;
      this._tiltSet.add(el);
      el.addEventListener('mousemove', e => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width  - 0.5;
        const y = (e.clientY - r.top)  / r.height - 0.5;
        el.style.transition = 'none';
        el.style.transform  = `perspective(700px) rotateY(${x * 10}deg) rotateX(${-y * 10}deg) translateZ(8px)`;
      });
      el.addEventListener('mouseleave', () => {
        el.style.transition = 'transform 0.55s cubic-bezier(0.4,0,0.2,1)';
        el.style.transform  = 'perspective(700px) rotateY(0) rotateX(0) translateZ(0)';
      });
    });
  },
};

export default FX;
