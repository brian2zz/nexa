<template>
  <div class="crud-container">
    <header class="crud-header">
      <div class="header-left">
        <router-link to="/nexa-admin" class="btn-ghost">← Kembali</router-link>
        <h2 class="title">{{ entityName }} <em>Management</em></h2>
      </div>
      <button @click="showForm = true" class="btn-primary">+ Add New Record</button>
    </header>

    <div class="table-wrapper">
      <table class="nexa-table">
        <thead>
          <tr>
            <th v-for="field in columns" :key="field.name">{{ field.name.toUpperCase() }}</th>
            <th>ACTIONS</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in data" :key="row.id">
            <td v-for="field in columns" :key="field.name">{{ row[field.name] }}</td>
            <td class="actions-cell">
              <button @click="deleteRecord(row.id)" class="btn-danger">Delete</button>
            </td>
          </tr>
          <tr v-if="data.length === 0">
            <td :colspan="columns.length + 1" class="text-center empty-state">No records found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Form -->
    <div v-if="showForm" class="modal-overlay">
      <div class="modal-content">
        <h3 class="modal-title">New {{ entityName }}</h3>
        <form @submit.prevent="saveRecord">
          <div v-for="field in formFields" :key="field.name" class="form-group">
            <label>{{ field.name }}</label>
            <input v-if="field.type === 'integer' || field.type === 'decimal'" type="number" v-model="formData[field.name]" class="form-control" required />
            <input v-else-if="field.type === 'date' || field.type === 'datetime'" type="datetime-local" v-model="formData[field.name]" class="form-control" required />
            <input v-else type="text" v-model="formData[field.name]" class="form-control" required />
          </div>
          <div class="modal-actions">
            <button type="button" @click="showForm = false" class="btn-ghost">Cancel</button>
            <button type="submit" class="btn-primary">Save Record</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DynamicList',
  data() {
    return {
      entityClass: this.$route.params.entity,
      schema: null,
      data: [],
      showForm: false,
      formData: {}
    }
  },
  computed: {
    entityName() {
      return this.schema ? this.schema.model : this.entityClass;
    },
    columns() {
      return this.schema ? this.schema.fields : [];
    },
    formFields() {
      return this.columns.filter(f => !f.identifier);
    }
  },
  async mounted() {
    await this.loadSchema();
    await this.fetchData();
  },
  watch: {
    '$route.params.entity'(newVal) {
      this.entityClass = newVal;
      this.loadSchema();
      this.fetchData();
    }
  },
  methods: {
    async loadSchema() {
      const stored = localStorage.getItem('nexa_schema');
      let schemas = [];
      if (stored) {
        schemas = JSON.parse(stored);
      } else {
        const res = await fetch('/nexa-admin/api/schema');
        const d = await res.json();
        schemas = d.data;
      }
      this.schema = schemas.find(s => s.class === this.entityClass);
    },
    async fetchData() {
      try {
        const res = await fetch(`/nexa-admin/api/data/${this.entityClass}`);
        const d = await res.json();
        this.data = d.data || [];
      } catch (e) {
        console.error('Failed to fetch data', e);
      }
    },
    async saveRecord() {
      try {
        const res = await fetch(`/nexa-admin/api/data/${this.entityClass}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.formData)
        });
        if (res.ok) {
          this.showForm = false;
          this.formData = {};
          await this.fetchData();
        }
      } catch (e) {
        console.error('Save failed', e);
      }
    },
    async deleteRecord(id) {
      if (!confirm('Are you sure you want to delete this record?')) return;
      try {
        const res = await fetch(`/nexa-admin/api/data/${this.entityClass}/${id}`, {
          method: 'DELETE'
        });
        if (res.ok) {
          await this.fetchData();
        }
      } catch (e) {
        console.error('Delete failed', e);
      }
    }
  }
}
</script>

<style scoped>
.crud-container {
  padding: 4rem 2rem;
  max-width: 1000px;
  margin: 0 auto;
  animation: fadeUp 0.6s ease both;
}

.crud-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 1px solid var(--border);
  padding-bottom: 1.5rem;
  margin-bottom: 2rem;
}

.header-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1rem;
}

.title {
  font-family: var(--serif);
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  font-weight: 300;
  color: var(--text);
  margin: 0;
}

.title em {
  font-style: italic;
  color: var(--green);
}

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
  padding: 8px 18px;
  border-radius: 4px;
  font-family: var(--mono);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-decoration: none;
}

.btn-ghost:hover {
  border-color: var(--green);
  color: var(--green);
}

.btn-danger {
  background: rgba(255, 95, 87, 0.1);
  color: #ff5f57;
  border: 1px solid rgba(255, 95, 87, 0.3);
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: var(--mono);
  text-transform: uppercase;
}

.btn-danger:hover {
  background: #ff5f57;
  color: #0a0e12;
}

.table-wrapper {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: auto;
}

.nexa-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.nexa-table th {
  background: var(--bg3);
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.08em;
  padding: 1rem 1.4rem;
  border-bottom: 1px solid var(--border);
}

.nexa-table td {
  padding: 1rem 1.4rem;
  font-size: 13px;
  color: var(--text);
  border-bottom: 1px solid rgba(66, 184, 131, 0.05);
}

.nexa-table tbody tr:hover {
  background: rgba(66, 184, 131, 0.02);
}

.empty-state {
  color: var(--text-muted) !important;
  font-style: italic;
  padding: 3rem !important;
}

/* Modal Form */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 14, 18, 0.85);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background: var(--bg2);
  border: 1px solid var(--border);
  padding: 2.5rem;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.4);
  animation: slideUp 0.3s ease;
}

.modal-title {
  margin: 0 0 2rem 0;
  font-family: var(--serif);
  font-weight: 300;
  font-size: 1.8rem;
  color: var(--text);
  border-bottom: 1px solid var(--border);
  padding-bottom: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--green);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.form-control {
  width: 100%;
  padding: 0.8rem 1rem;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text);
  font-family: var(--mono);
  font-size: 13px;
  transition: all 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: var(--green);
  box-shadow: 0 0 0 2px var(--green-glow);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2.5rem;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
</style>
