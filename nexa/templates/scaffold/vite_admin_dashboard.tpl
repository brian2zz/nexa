<template>
  <div class="admin-dashboard">
    <header class="admin-header">
      <div class="header-content">
        <h1>Nexa Admin Dashboard</h1>
        <p>Control Panel & System Management</p>
      </div>
    </header>
    <main class="admin-main">
      <div class="admin-grid">
<!-- ADMIN_MODULE_LINKS -->
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'Dashboard'
}
</script>

<style scoped>
/* Admin Header */
.admin-header {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  color: white;
  padding: 3rem 2rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.header-content h1 {
  font-size: 2.5rem;
  margin: 0 0 0.5rem 0;
  font-weight: 700;
}

.header-content p {
  margin: 0;
  opacity: 0.9;
  font-size: 1.1rem;
}

/* Admin Grid */
.admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

/* Admin Card */
:deep(.admin-card) {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  text-decoration: none;
  color: var(--text-color);
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  display: block;
}

:deep(.admin-card::before) {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--primary-color);
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

:deep(.admin-card:hover) {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.05);
  border-color: var(--primary-color);
}

:deep(.admin-card:hover::before) {
  transform: scaleY(1);
}

:deep(.admin-card-title) {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  color: var(--primary-color);
}

:deep(.admin-card-desc) {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.5;
}
</style>
