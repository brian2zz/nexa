<template>
  <div class="admin-dashboard">
    <header class="dashboard-header">
      <div class="header-left">
        <span class="badge">USP Framework Portal</span>
        <h1 class="title">Nexa Admin Central</h1>
      </div>
      <div class="header-right">
        <router-link to="/" class="btn-back">← Kembali ke Beranda</router-link>
      </div>
    </header>

    <main class="dashboard-content">
      <div class="info-banner">
        <div class="banner-icon">ℹ️</div>
        <div class="banner-text">
          <p class="banner-title">Mode Enkapsulasi Aktif</p>
          <p class="banner-desc">Pilih modul di bawah ini untuk mengelola rekaman data database secara langsung tanpa mengganggu antarmuka pengguna.</p>
        </div>
      </div>

      <div class="module-grid">
        <!-- ADMIN_MODULE_LINKS -->
      </div>
    </main>
  </div>
</template>

<style scoped>
.admin-dashboard {
  background: #0f172a;
  color: #f8fafc;
  min-height: 100vh;
  padding: 3rem 2rem;
  font-family: 'Inter', system-ui, sans-serif;
}

.dashboard-header {
  max-width: 1200px;
  margin: 0 auto 3rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding-bottom: 1.5rem;
}

.badge {
  background: rgba(56, 189, 248, 0.1);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: inline-block;
  margin-bottom: 0.5rem;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  color: #f8fafc;
  margin: 0;
}

.btn-back {
  background: rgba(255,255,255,0.05);
  color: #cbd5e1;
  text-decoration: none;
  padding: 0.6rem 1.2rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid rgba(255,255,255,0.1);
  transition: all 0.2s;
}

.btn-back:hover {
  background: rgba(255,255,255,0.1);
  color: #f8fafc;
}

.dashboard-content {
  max-width: 1200px;
  margin: 0 auto;
}

.info-banner {
  background: linear-gradient(to right, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.8));
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-left: 4px solid #38bdf8;
  padding: 1.25rem 1.5rem;
  border-radius: 0.5rem;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 2.5rem;
}

.banner-icon {
  font-size: 1.5rem;
}

.banner-title {
  font-weight: 600;
  color: #f8fafc;
  margin: 0 0 0.25rem;
  font-size: 1rem;
}

.banner-desc {
  color: #94a3b8;
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.5;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* Dynamically injected links style */
:deep(.admin-card) {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 0.75rem;
  padding: 1.5rem;
  display: block;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;
  position: relative;
}

:deep(.admin-card:hover) {
  background: rgba(30, 41, 59, 0.8);
  border-color: #38bdf8;
  transform: translateY(-2px);
}

:deep(.admin-card-title) {
  font-size: 1.125rem;
  font-weight: 600;
  color: #f8fafc;
  margin: 0 0 0.5rem;
}

:deep(.admin-card-desc) {
  font-size: 0.875rem;
  color: #94a3b8;
  margin: 0;
}
</style>
