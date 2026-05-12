<template>
  <div class="welcome-container">
    <div class="grid-bg"></div>
    <div class="glow-orb"></div>

    <div class="page">
      <nav>
        <div class="nav-logo">
          <svg class="vue-hex" viewBox="0 0 32 32" fill="none">
            <polygon points="16,2 29,9.5 29,22.5 16,30 3,22.5 3,9.5" fill="rgba(66,184,131,0.12)" stroke="rgba(66,184,131,0.4)" stroke-width="1"/>
            <path d="M16 7 L22 19 H10 Z" fill="#42b883" opacity="0.9"/>
            <path d="M16 11 L19.5 17 H12.5 Z" fill="#35495e"/>
          </svg>
          <span class="nav-title">Nexa Framework</span>
          <span class="nav-badge">v1.0 Enterprise</span>
        </div>
        <ul class="nav-links">
          <li><a href="/nexa-admin">Admin Portal</a></li>
          <li><a href="#">API Docs</a></li>
          <li><a href="#">Engine</a></li>
          <li><a href="#">GitHub</a></li>
        </ul>
      </nav>

      <div class="hero">
        <div class="hero-left">
          <div class="tag-line">
            <span class="tag-dot"></span>
            Workspace: Active Module
          </div>
          <h1 class="hero-title">
            Sistem<br>berhasil<br><em>disintesis.</em>
          </h1>
          <p class="hero-sub">
            Nexa Engine + Vue 3 siap digunakan. Mulai kembangkan antarmuka kustom pengguna pada direktori <code style="color:var(--green);font-size:11px">src/pages/</code> secara aman dan terisolasi.
          </p>
          <div class="btn-group">
            <a href="/nexa-admin" class="btn-primary" style="text-decoration:none">▶ Buka Portal Admin</a>
            <a href="#fitur" class="btn-ghost" style="text-decoration:none">📖 Eksplorasi Fitur</a>
          </div>
        </div>

        <div class="hero-right">
          <div class="code-window">
            <div class="window-bar">
              <div class="dot dot-red"></div>
              <div class="dot dot-yellow"></div>
              <div class="dot dot-green"></div>
              <span class="window-title">Struktur Arsitektur</span>
            </div>
            <div class="code-body">
              <div><span class="c-cmt">// Auto-Encapsulation USP Aktif</span></div>
              <div><span class="c-kw">import</span> { <span class="c-fn">createWorkspace</span> } <span class="c-kw">from</span> <span class="c-str">'nexa-engine'</span></div>
              <div>&nbsp;</div>
              <div><span class="c-kw">export default</span> <span class="c-fn">createWorkspace</span>({</div>
              <div>&nbsp;&nbsp;<span class="c-attr">appName</span>: <span class="c-str">'{{ app_name }}'</span>,</div>
              <div>&nbsp;&nbsp;<span class="c-attr">adminCrudLayer</span>: <span class="c-str">'admin-nexa/'</span>,</div>
              <div>&nbsp;&nbsp;<span class="c-attr">userCustomPages</span>: <span class="c-str">'pages/'</span></div>
              <div>})<span class="type-cursor"></span></div>
            </div>
          </div>
        </div>
      </div>

      <div class="stats-bar">
        <div class="stat">
          <span class="stat-num">Vue 3</span>
          <span class="stat-label">Frontend Engine</span>
        </div>
        <div class="stat">
          <span class="stat-num">Django</span>
          <span class="stat-label">Backend Bridge</span>
        </div>
        <div class="stat">
          <span class="stat-num">Secure</span>
          <span class="stat-label">Admin USP Status</span>
        </div>
      </div>

      <div id="fitur" class="section-header">
        <div class="section-line"></div>
        <span class="section-label">Fitur Unggulan Nexa Framework</span>
        <div class="section-line"></div>
      </div>

      <div class="cards">
        <div class="card">
          <div class="card-icon">🛡️</div>
          <div class="card-title">Isolated Admin USP</div>
          <div class="card-desc">Seluruh logika CRUD, layanan API, dan rute otomatis terenkapsulasi rapi di dalam admin-nexa/ tanpa mencemari kode pengguna.</div>
          <span class="card-arrow">→</span>
        </div>
        <div class="card">
          <div class="card-icon">⚡</div>
          <div class="card-title">Vite Hot Reload</div>
          <div class="card-desc">Perubahan antarmuka kustom langsung ter-render dalam hitungan milidetik dengan integrasi modul ES native ultra-cepat.</div>
          <span class="card-arrow">→</span>
        </div>
        <div class="card">
          <div class="card-icon">🔗</div>
          <div class="card-title">Seamless Django Bridge</div>
          <div class="card-desc">Koneksi mulus antara backend web server Django dan frontend SPA menggunakan sistem perutean ganda yang cerdas.</div>
          <span class="card-arrow">→</span>
        </div>
        <div class="card">
          <div class="card-icon">📦</div>
          <div class="card-title">State Management</div>
          <div class="card-desc">Didukung penuh oleh Pinia store terintegrasi untuk pengelolaan state aplikasi yang terpusat dan reaktif.</div>
          <span class="card-arrow">→</span>
        </div>
        <div class="card">
          <div class="card-icon">🎨</div>
          <div class="card-title">Premium Rich Aesthetics</div>
          <div class="card-desc">Antarmuka modern bergaya glassmorphism dengan palet warna terkurasi dan animasi halus untuk pengalaman visual terbaik.</div>
          <span class="card-arrow">→</span>
        </div>
        <div class="card">
          <div class="card-icon">🚀</div>
          <div class="card-title">Enterprise Scaffolding</div>
          <div class="card-desc">Siap dikembangkan untuk skala produksi dengan dukungan multi-tenant dan arsitektur modular mandiri.</div>
          <span class="card-arrow">→</span>
        </div>
      </div>

      <div class="section-header" style="animation-delay: 1s">
        <div class="section-line"></div>
        <span class="section-label">Operasi Otomatisasi CLI</span>
        <div class="section-line"></div>
      </div>

      <div class="terminal-section">
        <div class="terminal">
          <div class="terminal-bar">
            <div class="dot dot-red"></div>
            <div class="dot dot-yellow"></div>
            <div class="dot dot-green"></div>
            <span class="terminal-title">bash — Nexa CLI Operations</span>
          </div>
          <div class="terminal-body">
            <div><span class="t-prompt">$</span> <span class="t-cmd">nexa generate nexa.yaml</span></div>
            <div><span class="t-out">✔ Validating project schema...</span></div>
            <div><span class="t-out">✔ Synthesizing backend models & APIs...</span></div>
            <div><span class="t-out">✔ Encapsulating admin UI components...</span></div>
            <div><span class="t-success">✔ Scaffolding complete! Workspace ready.</span></div>
            <div>&nbsp;</div>
            <div><span class="t-prompt">$</span> <span class="t-cmd">nexa run</span></div>
            <div><span class="t-success">  DJANGO Engine running smoothly</span></div>
            <div><span class="t-out">  ➜  Portal Admin: http://127.0.0.1:8000/nexa-admin</span></div>
          </div>
        </div>
      </div>

      <footer>
        <span class="footer-text">© 2026 Nexa Framework Enterprise — Scaffolding the future of SaaS</span>
        <div class="footer-links">
          <a href="#">Docs</a>
          <a href="#">Engine</a>
          <a href="#">GitHub</a>
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;1,9..144,300&display=swap');

.welcome-container {
  --green: #42b883;
  --green-dark: #2d8f5e;
  --green-glow: rgba(66, 184, 131, 0.15);
  --vue-navy: #35495e;
  --bg: #0a0e12;
  --bg2: #111820;
  --bg3: #1a2535;
  --text: #e8f0f7;
  --text-muted: #6e8ba8;
  --border: rgba(66, 184, 131, 0.18);
  --mono: 'DM Mono', monospace;
  --serif: 'Fraunces', serif;

  background: var(--bg);
  color: var(--text);
  font-family: var(--mono);
  min-height: 100vh;
  width: 100%;
  position: relative;
  overflow-x: hidden;
  padding-bottom: 2rem;
}

.grid-bg {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(66,184,131,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(66,184,131,0.04) 1px, transparent 1px);
  background-size: 48px 48px;
  pointer-events: none;
  z-index: 0;
}

.glow-orb {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(66,184,131,0.08) 0%, transparent 70%);
  top: -100px;
  right: -100px;
  pointer-events: none;
  z-index: 0;
  animation: orbFloat 8s ease-in-out infinite;
}

@keyframes orbFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-30px); }
}

.page {
  position: relative;
  z-index: 1;
  max-width: 960px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* NAV */
nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 0;
  border-bottom: 1px solid var(--border);
  animation: fadeDown 0.6s ease both;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.vue-hex {
  width: 32px;
  height: 32px;
}

.nav-title {
  font-family: var(--serif);
  font-size: 1.1rem;
  font-weight: 300;
  color: var(--text);
  letter-spacing: 0.02em;
}

.nav-badge {
  font-size: 11px;
  background: var(--green-glow);
  border: 1px solid var(--border);
  color: var(--green);
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.08em;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-links a {
  font-size: 12px;
  color: var(--text-muted);
  text-decoration: none;
  letter-spacing: 0.05em;
  transition: color 0.2s;
  text-transform: uppercase;
}

.nav-links a:hover { color: var(--green); }

/* HERO */
.hero {
  padding: 6rem 0 4rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}

.hero-left { animation: fadeUp 0.8s ease 0.1s both; }

.tag-line {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: var(--green);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 1.5rem;
}

.tag-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--green);
  animation: pulse 2s ease infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.hero-title {
  font-family: var(--serif);
  font-size: clamp(2.5rem, 5vw, 3.5rem);
  font-weight: 300;
  line-height: 1.1;
  color: var(--text);
  margin-bottom: 1rem;
}

.hero-title em {
  font-style: italic;
  color: var(--green);
}

.hero-sub {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.8;
  max-width: 380px;
  margin-bottom: 2.5rem;
}

.btn-group { display: flex; gap: 12px; flex-wrap: wrap; }

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--green);
  color: #0a0e12;
  border: none;
  padding: 10px 22px;
  border-radius: 4px;
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.2s;
  text-transform: uppercase;
}

.btn-primary:hover {
  background: #4dcf95;
  transform: translateY(-1px);
}

.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  color: var(--text-muted);
  border: 1px solid var(--border);
  padding: 10px 22px;
  border-radius: 4px;
  font-family: var(--mono);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.btn-ghost:hover {
  border-color: var(--green);
  color: var(--green);
}

/* CODE WINDOW */
.hero-right { animation: fadeUp 0.8s ease 0.3s both; }

.code-window {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  text-align: left;
}

.window-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: var(--bg3);
  border-bottom: 1px solid var(--border);
}

.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot-red { background: #ff5f57; }
.dot-yellow { background: #ffbd2e; }
.dot-green { background: #28c840; }

.window-title {
  font-size: 11px;
  color: var(--text-muted);
  margin-left: auto;
  letter-spacing: 0.05em;
}

.code-body {
  padding: 1.2rem 1.4rem;
  font-size: 12px;
  line-height: 1.8;
}

.c-tag { color: #e06c75; }
.c-attr { color: #d19a66; }
.c-str { color: #98c379; }
.c-kw { color: #c678dd; }
.c-fn { color: #61afef; }
.c-cmt { color: #5c6370; font-style: italic; }
.c-num { color: #e5c07b; }

.type-cursor {
  display: inline-block;
  width: 2px;
  height: 14px;
  background: var(--green);
  vertical-align: middle;
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* STATS BAR */
.stats-bar {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  margin: 4rem 0;
  animation: fadeUp 0.8s ease 0.4s both;
}

.stat {
  background: var(--bg);
  padding: 1.5rem;
  text-align: center;
}

.stat-num {
  font-family: var(--serif);
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--green);
  line-height: 1;
  margin-bottom: 6px;
  display: block;
}

.stat-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* CARDS GRID */
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1.5rem;
  animation: fadeUp 0.8s ease 0.5s both;
}

.section-line {
  flex: 1;
  height: 1px;
  background: var(--border);
}

.section-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  white-space: nowrap;
}

.cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 4rem;
  text-align: left;
}

.card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1.4rem;
  cursor: pointer;
  transition: all 0.25s;
  position: relative;
  overflow: hidden;
  animation: fadeUp 0.8s ease both;
}

.card:nth-child(1) { animation-delay: 0.55s; }
.card:nth-child(2) { animation-delay: 0.65s; }
.card:nth-child(3) { animation-delay: 0.75s; }
.card:nth-child(4) { animation-delay: 0.85s; }
.card:nth-child(5) { animation-delay: 0.95s; }
.card:nth-child(6) { animation-delay: 1.05s; }

.card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--green-glow) 0%, transparent 100%);
  opacity: 0;
  transition: opacity 0.25s;
}

.card:hover {
  border-color: rgba(66,184,131,0.4);
  transform: translateY(-2px);
}

.card:hover::before { opacity: 1; }

.card-icon {
  width: 36px;
  height: 36px;
  background: var(--green-glow);
  border: 1px solid var(--border);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  font-size: 16px;
}

.card-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 6px;
  letter-spacing: 0.02em;
}

.card-desc {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.7;
}

.card-arrow {
  position: absolute;
  bottom: 1.2rem;
  right: 1.2rem;
  font-size: 14px;
  color: var(--green);
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.2s;
}

.card:hover .card-arrow {
  opacity: 1;
  transform: translateX(0);
}

/* TERMINAL */
.terminal-section {
  margin-bottom: 4rem;
  animation: fadeUp 0.8s ease 1.1s both;
  text-align: left;
}

.terminal {
  background: #0d1117;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.terminal-bar {
  background: var(--bg3);
  padding: 8px 14px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 8px;
}

.terminal-title {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

.terminal-body {
  padding: 1.2rem 1.4rem;
  font-size: 12px;
  line-height: 2;
}

.t-prompt { color: var(--green); }
.t-cmd { color: var(--text); }
.t-out { color: var(--text-muted); }
.t-success { color: #28c840; }

/* FOOTER */
footer {
  border-top: 1px solid var(--border);
  padding: 2rem 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  animation: fadeUp 0.8s ease 1.2s both;
}

.footer-text {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

.footer-links {
  display: flex;
  gap: 1.5rem;
}

.footer-links a {
  font-size: 11px;
  color: var(--text-muted);
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  transition: color 0.2s;
}

.footer-links a:hover { color: var(--green); }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .hero { grid-template-columns: 1fr; gap: 2rem; padding-top: 4rem; }
  .cards { grid-template-columns: 1fr; }
  .stats-bar { grid-template-columns: 1fr; gap: 1px; }
  footer { flex-direction: column; gap: 1rem; text-align: center; }
}
</style>

<script setup>
// Pure High-Fidelity Static Welcome Page for Nexa Engine
</script>
