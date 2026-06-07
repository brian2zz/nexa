<template>
  <div class="admin-dashboard">
    <header class="dashboard-header">
      <div class="header-left">
        <span class="badge">Dynamic Encap Mode</span>
        <h1 class="title">Nexa Admin <em>Central</em></h1>
      </div>
      <div class="header-right">
        <router-link to="/" class="btn-ghost">← Kembali ke Beranda</router-link>
      </div>
    </header>

    <main class="dashboard-content">
      <div class="info-banner">
        <div class="banner-icon">🛡️</div>
        <div class="banner-text">
          <p class="banner-title">Runtime Reflection Aktif</p>
          <p class="banner-desc">Memindai metadata Doctrine secara dinamis. Modul di bawah ini otomatis ter-generate dari Models Anda.</p>
        </div>
      </div>

      <div class="cards">
        <router-link 
          v-for="model in schema" 
          :key="model.class"
          :to="{ name: 'dynamic_list', params: { entity: model.class } }" 
          class="card"
        >
          <div class="card-icon">⚡</div>
          <div class="card-title">{{ model.model }} Module</div>
          <div class="card-desc">Kelola seluruh entitas data tabel {{ model.model.toLowerCase() }} dengan antarmuka yang terenkapsulasi aman.</div>
          <span class="card-arrow">→</span>
        </router-link>
      </div>

      <div v-if="schema.length === 0" class="empty-state">
        <div class="loader"></div>
        <p>Mensintesis modul dari backend...</p>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      schema: []
    }
  },
  async mounted() {
    try {
      const response = await fetch('/nexa-admin/api/schema');
      const data = await response.json();
      if (data.data) {
        this.schema = data.data;
        localStorage.setItem('nexa_schema', JSON.stringify(data.data));
      }
    } catch (e) {
      console.error('Failed to load schema', e);
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  padding: 4rem 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
  padding-bottom: 1.5rem;
  margin-bottom: 3rem;
  animation: fadeDown 0.6s ease both;
}

.badge {
  background: var(--green-glow);
  color: var(--green);
  border: 1px solid var(--border);
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  display: inline-block;
  margin-bottom: 0.8rem;
}

.title {
  font-family: var(--serif);
  font-size: clamp(2rem, 4vw, 2.8rem);
  font-weight: 300;
  color: var(--text);
  margin: 0;
}

.title em {
  font-style: italic;
  color: var(--green);
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
  font-size: 12px;
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: all 0.2s;
}

.btn-ghost:hover {
  border-color: var(--green);
  color: var(--green);
}

.info-banner {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-left: 4px solid var(--green);
  border-radius: 6px;
  padding: 1.5rem;
  display: flex;
  gap: 1.2rem;
  align-items: flex-start;
  margin-bottom: 3rem;
  animation: fadeUp 0.8s ease 0.2s both;
}

.banner-icon {
  font-size: 1.5rem;
}

.banner-title {
  margin: 0 0 0.4rem 0;
  color: var(--green);
  font-weight: 500;
  font-size: 14px;
  letter-spacing: 0.02em;
}

.banner-desc {
  margin: 0;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.6;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  animation: fadeUp 0.8s ease 0.4s both;
}

.card {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1.8rem;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.25s;
  position: relative;
  overflow: hidden;
  display: block;
}

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
  width: 40px;
  height: 40px;
  background: var(--green-glow);
  border: 1px solid var(--border);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.2rem;
  font-size: 18px;
  color: var(--green);
}

.card-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 8px;
  letter-spacing: 0.02em;
}

.card-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.7;
}

.card-arrow {
  position: absolute;
  bottom: 1.5rem;
  right: 1.5rem;
  font-size: 16px;
  color: var(--green);
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.2s;
}

.card:hover .card-arrow {
  opacity: 1;
  transform: translateX(0);
}

.empty-state {
  text-align: center;
  padding: 4rem;
  color: var(--text-muted);
  font-size: 13px;
  letter-spacing: 0.05em;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loader {
  width: 30px;
  height: 30px;
  border: 2px solid var(--border);
  border-top-color: var(--green);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin { 100% { transform: rotate(360deg); } }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
