<template>
  <div class="admin-layout">
    <div class="grid-bg"></div>
    <div class="glow-orb"></div>
    <main class="main-content">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
export default {
  name: 'MainLayout'
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;1,9..144,300&display=swap');

.admin-layout {
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

.main-content {
  position: relative;
  z-index: 1;
  width: 100%;
  padding: 0;
}
</style>
