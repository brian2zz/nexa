<template>
  <div class="crud-form-wrapper">
    <!-- Top Back Navigation -->
    <header class="page-header">
      <div class="header-left">
        <router-link :to="{ name: '{{ model_name.lower() }}_list' }" class="btn-back">← Batal & Kembali</router-link>
        <span class="separator">/</span>
        <span class="current-module">{{ isEdit ? 'Formulir Edit' : 'Formulir Pembuatan' }} {{ class_name }}</span>
      </div>
    </header>

    <!-- Main Form Container -->
    <main class="form-container">
      <div class="form-card">
        <div class="card-header">
          <div class="header-indicator"></div>
          <div class="header-titles">
            <h1 class="form-title">{{ class_name }} Entity Management</h1>
            <p class="form-subtitle">Zona enkapsulasi pengisian atribut database secara aman</p>
          </div>
          <span class="mode-badge">{{ isEdit ? 'Mode Edit' : 'Mode Buat Baru' }}</span>
        </div>

        <form @submit.prevent="saveRecord" class="form-body">
          <div class="fields-grid">
            <!-- Dynamic Form Fields Loop -->
            [loop:fields]
            <div class="form-group">
              <label :for="'field_{{ item.name }}'" class="form-label">
                <span class="label-text">{{ item.name }}</span>
                <span class="type-badge" title="Tipe Data Kolom DB">{{ item.type }}</span>
              </label>
              
              <!-- Dynamic Field Typing mapped from database meta -->
              <input 
                v-model="form['{{ item.name }}']"
                :type="getInputType('{{ item.type }}')"
                :step="isDecimal('{{ item.type }}') ? 'any' : undefined"
                :id="'field_{{ item.name }}'"
                class="form-input"
                :class="{ 'input-checkbox': getInputType('{{ item.type }}') === 'checkbox' }"
                placeholder="Spesifikasikan nilai {{ item.name }}..."
                required
              />
            </div>
            [/loop]
          </div>

          <footer class="form-actions">
            <button type="submit" class="btn-save" :disabled="isSaving">
              <span class="save-icon">💾</span> 
              {{ isSaving ? 'Menyimpan Entitas...' : 'Simpan Perubahan Rekaman' }}
            </button>
            <router-link 
              :to="{ name: '{{ model_name.lower() }}_list' }" 
              class="btn-cancel"
            >
              Batalkan
            </router-link>
          </footer>
        </form>
      </div>
    </main>
  </div>
</template>

<style scoped>
.crud-form-wrapper {
  background: #0b0f17;
  color: #e2e8f0;
  min-height: 100vh;
  padding: 2.5rem 2rem;
  font-family: 'Inter', system-ui, sans-serif;
}

/* HEADER */
.page-header {
  max-width: 800px;
  margin: 0 auto 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-back {
  background: rgba(255,255,255,0.05);
  color: #94a3b8;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid rgba(255,255,255,0.08);
  transition: all 0.2s;
}

.btn-back:hover {
  background: rgba(255,255,255,0.1);
  color: #f8fafc;
  border-color: rgba(56, 189, 248, 0.3);
}

.separator { color: #475569; font-size: 0.875rem; }

.current-module {
  font-size: 1.125rem;
  font-weight: 600;
  color: #f8fafc;
}

/* FORM CARD */
.form-container {
  max-width: 800px;
  margin: 0 auto;
}

.form-card {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(56, 189, 248, 0.15);
  border-radius: 1rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(12px);
  overflow: hidden;
}

.card-header {
  background: rgba(11, 15, 23, 0.5);
  padding: 1.5rem 2rem;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  position: relative;
}

.header-indicator {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 4px;
  background: #38bdf8;
  box-shadow: 0 0 10px #38bdf8;
}

.header-titles { margin-left: 0.5rem; }

.form-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f8fafc;
  margin: 0 0 0.25rem;
  letter-spacing: 0.02em;
}

.form-subtitle {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

.mode-badge {
  background: rgba(56, 189, 248, 0.1);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

/* FORM BODY */
.form-body { padding: 2rem; }

.fields-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.875rem;
  font-weight: 500;
  color: #cbd5e1;
}

.type-badge {
  font-family: 'DM Mono', monospace;
  font-size: 0.65rem;
  background: rgba(255,255,255,0.05);
  color: #64748b;
  padding: 0.1rem 0.4rem;
  border-radius: 0.25rem;
  border: 1px solid rgba(255,255,255,0.08);
  text-transform: uppercase;
}

.form-input {
  background: rgba(11, 15, 23, 0.8);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  color: #f8fafc;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.15);
  background: rgba(11, 15, 23, 0.95);
}

.input-checkbox {
  width: 20px;
  height: 20px;
  accent-color: #38bdf8;
  cursor: pointer;
}

/* FOOTER ACTIONS */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  border-top: 1px solid rgba(255,255,255,0.06);
  padding-top: 1.5rem;
}

.btn-save {
  background: #38bdf8;
  color: #0b0f17;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
  transition: all 0.2s;
}

.btn-save:hover:not(:disabled) {
  background: #7dd3fc;
  transform: translateY(-1px);
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-cancel {
  background: rgba(255,255,255,0.05);
  color: #94a3b8;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid rgba(255,255,255,0.08);
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
}

.btn-cancel:hover {
  background: rgba(255,255,255,0.1);
  color: #f8fafc;
}
</style>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { use{{ class_name }}Store } from '@/admin-nexa/stores/{{ model_name.lower() }}Store';

const route = useRoute();
const router = useRouter();
const store = use{{ class_name }}Store();

const isEdit = computed(() => !!route.params.id);
const isSaving = ref(false);
const form = ref({});

onMounted(async () => {
  if (isEdit.value) {
    try {
      const data = await store.get{{ class_name }}(route.params.id);
      form.value = data ? { ...data } : {};
    } catch (err) {
      // safe load
    }
  }
});

// Save Handler
const saveRecord = async () => {
  isSaving.value = true;
  try {
    if (isEdit.value) {
      await store.update{{ class_name }}(route.params.id, form.value);
    } else {
      await store.create{{ class_name }}(form.value);
    }
    router.push({ name: '{{ model_name.lower() }}_list' });
  } catch (error) {
    alert('Gagal menyimpan rekaman {{ class_name }} database');
  } finally {
    isSaving.value = false;
  }
};

// Dynamic database type evaluator
const getInputType = (typeStr) => {
  if (!typeStr) return 'text';
  const t = String(typeStr).toLowerCase();
  if (t.includes('datetime') || t.includes('timestamp')) return 'datetime-local';
  if (t.includes('date')) return 'date';
  if (t.includes('time')) return 'time';
  if (t.includes('int') || t.includes('num') || t.includes('decimal') || t.includes('float') || t.includes('double')) return 'number';
  if (t.includes('bool')) return 'checkbox';
  return 'text';
};

const isDecimal = (typeStr) => {
  if (!typeStr) return false;
  const t = String(typeStr).toLowerCase();
  return t.includes('decimal') || t.includes('float') || t.includes('double') || t.includes('numeric');
};
</script>
