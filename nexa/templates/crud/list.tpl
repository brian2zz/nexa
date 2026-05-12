<template>
  <div class="crud-list-wrapper">
    <!-- Top Back Navigation -->
    <header class="page-header">
      <div class="header-left">
        <router-link :to="{ name: 'admin_dashboard' }" class="btn-back">← Admin Central Dashboard</router-link>
        <span class="separator">/</span>
        <span class="current-module">{{ class_name }} Staged Database Workspace</span>
      </div>
      <div class="header-right">
        <button 
          @click="addNewStagedRow" 
          class="btn-primary"
          title="Menambahkan baris hijau baru di tabel (menunggu disimpan)"
        >
          <span class="btn-icon">+</span> Tambah Baris Baru
        </button>
      </div>
    </header>

    <!-- Content Card Container -->
    <main class="crud-content-card">
      <!-- Master Staged Commit Toolbar -->
      <div v-if="hasStagedChanges" class="staged-commit-toolbar">
        <div class="toolbar-left">
          <span class="pulse-indicator"></span>
          <div class="staged-counts">
            <span class="toolbar-title">Perubahan Tertunda (Belum Disimpan):</span>
            <span v-if="pendingAdds.length" class="count-pill pill-add">{{ pendingAdds.length }} Baris Ditambah</span>
            <span v-if="Object.keys(pendingEdits).length" class="count-pill pill-edit">{{ Object.keys(pendingEdits).length }} Baris Diedit</span>
            <span v-if="Object.keys(pendingDeletes).length" class="count-pill pill-del">{{ Object.keys(pendingDeletes).length }} Baris Dihapus</span>
          </div>
        </div>
        <div class="toolbar-right">
          <button @click="commitAllChanges" class="btn-commit" :disabled="isSaving">
            <span class="btn-icon">🚀</span> {{ isSaving ? 'Menyinkronkan...' : 'Simpan Perubahan ke DB' }}
          </button>
          <button @click="discardAllChanges" class="btn-discard" :disabled="isSaving">Batalkan Semua</button>
        </div>
      </div>

      <!-- Search Bar & Limit Controls -->
      <div class="controls-bar">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Kueri DBeaver (misal: id = 53 and status = 'sukses') atau pencarian teks..."
            class="input-search"
          />
          <button v-if="searchQuery" @click="searchQuery = ''" class="btn-clear">✕</button>
        </div>

        <div class="limit-box">
          <span class="limit-label">Tampilkan:</span>
          <select v-model="pageSize" @change="currentPage = 1" class="select-limit">
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
          <span class="limit-label">entri</span>
        </div>
      </div>

      <!-- Filter Notice Banner -->
      <div v-if="isSqlFilter" class="sql-banner">
        <span class="banner-badge">Mode Kueri SQL Aktif</span>
        <span class="banner-text">Menerapkan filter ganda DBeaver: <strong>{{ searchQuery }}</strong></span>
      </div>

      <!-- Data Table Workspace -->
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              [loop:columns]
              <th @click="sortBy('{{ item }}')" class="sortable-header" title="Klik untuk mengurutkan">
                <div class="header-content">
                  <span>{{ item }}</span>
                  <span class="sort-indicator" :class="getSortClass('{{ item }}')">↕</span>
                </div>
              </th>
              [/loop]
              <th class="actions-header">Aksi Manajemen</th>
            </tr>
          </thead>
          <tbody>
            <!-- EMPTY STATE -->
            <tr v-if="combinedItems.length === 0">
              <td colspan="100%" class="empty-state">
                <div class="empty-content">
                  <span class="empty-icon">📂</span>
                  <p class="empty-text">Tidak ada rekaman data yang cocok di dalam pangkalan data.</p>
                </div>
              </td>
            </tr>

            <!-- COMBINED STAGED ADDS AND DATABASE ROWS -->
            <tr 
              v-for="(row, idx) in combinedItems" 
              :key="row.isPendingAdd ? 'add_' + idx : (row.id !== undefined ? row.id : 'idx_' + idx)" 
              class="data-row"
              :class="{
                'status-added': row.isPendingAdd,
                'status-deleted': !row.isPendingAdd && pendingDeletes[row.id],
                'status-edited': !row.isPendingAdd && pendingEdits[row.id] && !pendingDeletes[row.id],
                'editing-active': activeEditRowId === row.id && !row.isPendingAdd
              }"
              @dblclick="!row.isPendingAdd ? startDoubleClickEdit(row) : null"
            >
              [loop:columns]
              <td class="data-cell" :class="{ 'inline-edit-cell': activeEditRowId === row.id || row.isPendingAdd }">
                <!-- Staged Added Row Mode -->
                <template v-if="row.isPendingAdd">
                  <input 
                    v-model="pendingAdds[row.pendingAddIndex]['{{ item }}']"
                    :type="getInputType('{{ item }}')"
                    :step="isDecimalField('{{ item }}') ? 'any' : undefined"
                    class="spreadsheet-input staged-add-input"
                    :class="{ 'spreadsheet-checkbox': getInputType('{{ item }}') === 'checkbox' }"
                    :placeholder="'{{ item }}' === 'id' ? '[Auto / Manual]' : '{{ item }}...'"
                  />
                </template>

                <!-- Existing Database Row Mode -->
                <template v-else>
                  <!-- Active Inline Input via Double-Click -->
                  <template v-if="activeEditRowId === row.id">
                    <input 
                      v-if="'{{ item }}' !== 'id'"
                      v-model="pendingEdits[row.id]['{{ item }}']"
                      :type="getInputType('{{ item }}')"
                      :step="isDecimalField('{{ item }}') ? 'any' : undefined"
                      class="spreadsheet-input staged-edit-input"
                      :class="{ 'spreadsheet-checkbox': getInputType('{{ item }}') === 'checkbox' }"
                      @keyup.enter="confirmRowEdit(row.id)"
                    />
                    <span v-else class="cell-val read-only-id">{{ row['{{ item }}'] }}</span>
                  </template>
                  
                  <!-- Display Mode -->
                  <template v-else>
                    <span 
                      class="cell-val user-select-text" 
                      :class="{ 'line-through opacity-40': pendingDeletes[row.id] }"
                      title="Klik ganda (double-click) baris ini untuk mengedit nilainya"
                    >
                      {{ getDisplayValue(row, '{{ item }}') }}
                    </span>
                  </template>
                </template>
              </td>
              [/loop]
              
              <!-- ACTIONS CELL -->
              <td class="data-cell actions-cell" @dblclick.stop>
                <div class="action-buttons">
                  <!-- Actions for Staged Added Row -->
                  <template v-if="row.isPendingAdd">
                    <button @click="discardAdd(row.pendingAddIndex)" class="btn-act btn-del" title="Hapus sisipan baris ini">Batal</button>
                  </template>

                  <!-- Actions for Existing Database Row -->
                  <template v-else>
                    <template v-if="pendingDeletes[row.id]">
                      <button @click="restoreDelete(row.id)" class="btn-act btn-restore" title="Batalkan penghapusan baris ini">↩ Restore</button>
                    </template>
                    <template v-else>
                      <template v-if="activeEditRowId === row.id">
                        <button @click="confirmRowEdit(row.id)" class="btn-act btn-save" title="Selesai mengetik di baris ini">Selesai</button>
                      </template>
                      <template v-else>
                        <button v-if="pendingEdits[row.id]" @click="discardEdit(row.id)" class="btn-act btn-restore" title="Kembalikan ke nilai semula">↩ Reset</button>
                        <button 
                          v-if="row.id !== undefined && row.id !== null"
                          @click="stageDelete(row.id)" 
                          class="btn-act btn-del" 
                          title="Tandai baris ini untuk dihapus (merah)"
                        >
                          Hapus
                        </button>
                        <span v-else class="btn-act btn-del disabled-act" title="Rekaman tidak memiliki Primary Key ID">Hapus</span>
                      </template>
                    </template>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Footer -->
      <footer class="pagination-footer">
        <div class="footer-info">
          Menampilkan <span class="highlight">{{ startIndex + 1 }}</span> hingga 
          <span class="highlight">{{ Math.min(startIndex + pageSize, filteredItems.length) }}</span> dari 
          <span class="highlight">{{ filteredItems.length }}</span> total rekaman
        </div>

        <div class="footer-controls">
          <button 
            @click="currentPage--" 
            :disabled="currentPage === 1" 
            class="btn-page"
          >
            Prev
          </button>
          <div class="page-numbers">
            <button 
              v-for="p in totalPages" 
              :key="p" 
              @click="currentPage = p"
              class="btn-num" 
              :class="{ 'active': currentPage === p }"
            >
              {{ p }}
            </button>
          </div>
          <button 
            @click="currentPage++" 
            :disabled="currentPage >= totalPages" 
            class="btn-page"
          >
            Next
          </button>
        </div>
      </footer>
    </main>
  </div>
</template>

<style scoped>
.crud-list-wrapper {
  background: #0b0f17;
  color: #e2e8f0;
  min-height: 100vh;
  padding: 2.5rem 2rem;
  font-family: 'Inter', system-ui, sans-serif;
}

/* HEADER */
.page-header {
  max-width: 1400px;
  margin: 0 auto 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
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
  font-size: 1.25rem;
  font-weight: 600;
  color: #f8fafc;
  letter-spacing: 0.02em;
}

.btn-primary {
  background: #38bdf8;
  color: #0b0f17;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #7dd3fc;
  transform: translateY(-1px);
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
}

/* CONTENT CARD */
.crud-content-card {
  max-width: 1400px;
  margin: 0 auto;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(56, 189, 248, 0.15);
  border-radius: 1rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(12px);
  overflow: hidden;
}

/* MASTER STAGED COMMIT TOOLBAR */
.staged-commit-toolbar {
  background: rgba(15, 23, 42, 0.95);
  border-bottom: 1px solid rgba(56, 189, 248, 0.3);
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pulse-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #38bdf8;
  box-shadow: 0 0 10px #38bdf8;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.5; }
}

.staged-counts {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.toolbar-title { font-size: 0.875rem; font-weight: 600; color: #cbd5e1; }

.count-pill {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
}

.pill-add { background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
.pill-edit { background: rgba(234, 179, 8, 0.2); color: #eab308; border: 1px solid rgba(234, 179, 8, 0.3); }
.pill-del { background: rgba(244, 63, 94, 0.2); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); }

.toolbar-right { display: flex; gap: 0.75rem; }

.btn-commit {
  background: #38bdf8;
  color: #0b0f17;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
  transition: all 0.2s;
}

.btn-commit:hover:not(:disabled) { background: #7dd3fc; box-shadow: 0 0 20px rgba(56, 189, 248, 0.4); }
.btn-commit:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-discard {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: #94a3b8;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-discard:hover { background: rgba(244, 63, 94, 0.1); color: #f43f5e; border-color: rgba(244, 63, 94, 0.2); }

/* CONTROLS BAR */
.controls-bar {
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-wrap: wrap;
}

.search-box { flex: 1; min-width: 300px; position: relative; display: flex; align-items: center; }
.search-icon { position: absolute; left: 1rem; font-size: 0.875rem; color: #64748b; pointer-events: none; }
.input-search {
  width: 100%;
  background: rgba(11, 15, 23, 0.8);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 0.5rem;
  padding: 0.6rem 2.5rem;
  color: #f8fafc;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s;
  font-family: 'DM Mono', monospace;
}
.input-search:focus { border-color: #38bdf8; box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.15); }
.btn-clear { position: absolute; right: 0.75rem; background: transparent; border: none; color: #64748b; cursor: pointer; padding: 0.25rem; font-size: 0.75rem; }
.btn-clear:hover { color: #f8fafc; }

.limit-box { display: flex; align-items: center; gap: 0.5rem; }
.limit-label { font-size: 0.875rem; color: #64748b; }
.select-limit {
  background: rgba(11, 15, 23, 0.8);
  border: 1px solid rgba(255,255,255,0.1);
  color: #f8fafc;
  padding: 0.4rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  outline: none;
  cursor: pointer;
}
.select-limit:focus { border-color: #38bdf8; }

/* SQL BANNER */
.sql-banner {
  background: rgba(56, 189, 248, 0.05);
  border-bottom: 1px solid rgba(56, 189, 248, 0.15);
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.875rem;
}
.banner-badge { background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 0.15rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
.banner-text { color: #cbd5e1; }
.banner-text strong { color: #f8fafc; font-family: monospace; }

/* TABLE WORKSPACE */
.table-container { overflow-x: auto; width: 100%; }
.data-table { width: 100%; border-collapse: collapse; text-align: left; }
.sortable-header {
  background: rgba(11, 15, 23, 0.4);
  padding: 1rem 1.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}
.sortable-header:hover { background: rgba(255,255,255,0.03); color: #f8fafc; }
.header-content { display: flex; align-items: center; gap: 0.5rem; }
.sort-indicator { font-size: 0.875rem; color: #475569; transition: all 0.2s; }
.sort-indicator.active-asc { color: #38bdf8; content: '↑'; }
.sort-indicator.active-desc { color: #38bdf8; content: '↓'; }
.actions-header {
  background: rgba(11, 15, 23, 0.4);
  padding: 1rem 1.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  text-align: right;
  min-width: 140px;
}

/* ROW ENCODINGS */
.data-row {
  border-bottom: 1px solid rgba(255,255,255,0.04);
  transition: all 0.2s;
}
.data-row:hover { background: rgba(255,255,255,0.02); }

/* STAGED ADDED ROW (HIJAU) */
.data-row.status-added {
  background: rgba(16, 185, 129, 0.08);
  border-left: 4px solid #10b981;
}

/* STAGED EDITED ROW (KUNING) */
.data-row.status-edited {
  background: rgba(234, 179, 8, 0.08);
  border-left: 4px solid #eab308;
}

/* STAGED DELETED ROW (MERAH) */
.data-row.status-deleted {
  background: rgba(244, 63, 94, 0.08);
  border-left: 4px solid #f43f5e;
}

/* DOUBLE-CLICK ACTIVE INPUT ROW */
.data-row.editing-active {
  background: rgba(56, 189, 248, 0.08);
  box-shadow: inset 0 0 0 1px rgba(56, 189, 248, 0.2);
}

.data-cell {
  padding: 0.75rem 1.25rem;
  font-size: 0.875rem;
  color: #cbd5e1;
  vertical-align: middle;
}
.inline-edit-cell { padding: 0.4rem 1.25rem; }

.user-select-text {
  user-select: text;
  cursor: text;
}

.cell-val {
  display: inline-block;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: all 0.2s;
}

.read-only-id { color: #64748b; font-family: 'DM Mono', monospace; font-size: 0.8rem; }
.staged-badge {
  font-family: 'DM Mono', monospace;
  font-size: 0.65rem;
  padding: 0.15rem 0.4rem;
  border-radius: 0.25rem;
  font-weight: 600;
}
.badge-add { background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }

/* SPREADSHEET INPUTS */
.spreadsheet-input {
  width: 100%;
  background: #0b0f17;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 0.375rem;
  padding: 0.4rem 0.6rem;
  color: #f8fafc;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s;
}

.staged-add-input { border-color: rgba(16, 185, 129, 0.4); }
.staged-add-input:focus { border-color: #10b981; box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2); }

.staged-edit-input { border-color: rgba(234, 179, 8, 0.4); }
.staged-edit-input:focus { border-color: #eab308; box-shadow: 0 0 0 2px rgba(234, 179, 8, 0.2); }

.spreadsheet-checkbox { width: 18px; height: 18px; accent-color: #38bdf8; cursor: pointer; }

/* ACTIONS */
.actions-cell { text-align: right; }
.action-buttons { display: inline-flex; gap: 0.4rem; }
.btn-act {
  background: transparent;
  border: 1px solid transparent;
  padding: 0.35rem 0.6rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-save { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border-color: rgba(56, 189, 248, 0.3); }
.btn-save:hover { background: #38bdf8; color: #0b0f17; }

.btn-restore { background: rgba(234, 179, 8, 0.1); color: #eab308; border-color: rgba(234, 179, 8, 0.2); }
.btn-restore:hover { background: rgba(234, 179, 8, 0.2); color: #fff; }

.btn-del { background: rgba(244, 63, 94, 0.1); color: #f43f5e; border-color: rgba(244, 63, 94, 0.2); }
.btn-del:hover { background: rgba(244, 63, 94, 0.2); color: #fff; }

.disabled-act { opacity: 0.3; cursor: not-allowed; border-color: rgba(255,255,255,0.05); color: #64748b; }

.empty-state { padding: 4rem 2rem; text-align: center; }
.empty-content { display: flex; flex-direction: column; align-items: center; gap: 1rem; }
.empty-icon { font-size: 2.5rem; opacity: 0.6; }
.empty-text { color: #64748b; font-size: 0.875rem; margin: 0; }

/* FOOTER PAGINATION */
.pagination-footer {
  padding: 1.25rem 1.5rem;
  background: rgba(11, 15, 23, 0.3);
  border-top: 1px solid rgba(255,255,255,0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}
.footer-info { font-size: 0.875rem; color: #64748b; }
.highlight { color: #cbd5e1; font-weight: 600; }
.footer-controls { display: flex; align-items: center; gap: 0.5rem; }
.btn-page { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); color: #cbd5e1; padding: 0.35rem 0.75rem; border-radius: 0.375rem; font-size: 0.75rem; font-weight: 500; cursor: pointer; transition: all 0.2s; }
.btn-page:hover:not(:disabled) { background: rgba(255,255,255,0.1); color: #f8fafc; }
.btn-page:disabled { opacity: 0.4; cursor: not-allowed; }
.page-numbers { display: flex; gap: 0.25rem; }
.btn-num { background: transparent; border: 1px solid transparent; color: #64748b; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 0.375rem; font-size: 0.75rem; cursor: pointer; transition: all 0.2s; }
.btn-num:hover { color: #cbd5e1; }
.btn-num.active { background: rgba(56, 189, 248, 0.15); border-color: rgba(56, 189, 248, 0.3); color: #38bdf8; font-weight: 600; }
</style>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { use{{ class_name }}Store } from '@/admin-nexa/stores/{{ model_name.lower() }}Store';

const store = use{{ class_name }}Store();

// Schema Type Map injected by Generator Loops
const fieldTypes = {
  [loop:fields]
  "{{ item.name }}": "{{ item.type }}",
  [/loop]
};

// Reactive State
const searchQuery = ref('');
const pageSize = ref(10);
const currentPage = ref(1);
const sortColumn = ref('');
const sortDirection = ref('asc');
const isSaving = ref(false);

// Client-Side Staged Batch Processing Architecture
const pendingAdds = ref([]); // array of newly staged record objects
const pendingEdits = ref({}); // map of id -> staged modified record values
const pendingDeletes = ref({}); // map of id -> boolean pending delete flag
const activeEditRowId = ref(null); // tracking double-click active input box cell mode

// Mount action
onMounted(() => {
  store.fetch{{ plural_name }}();
});

// Dynamic Field Type Helpers
const getInputType = (colName) => {
  const typeStr = fieldTypes[colName] || 'text';
  const t = String(typeStr).toLowerCase();
  if (t.includes('datetime') || t.includes('timestamp')) return 'datetime-local';
  if (t.includes('date')) return 'date';
  if (t.includes('time')) return 'time';
  if (t.includes('int') || t.includes('num') || t.includes('decimal') || t.includes('float') || t.includes('double')) return 'number';
  if (t.includes('bool')) return 'checkbox';
  return 'text';
};

const isDecimalField = (colName) => {
  const typeStr = fieldTypes[colName] || '';
  const t = String(typeStr).toLowerCase();
  return t.includes('decimal') || t.includes('float') || t.includes('double') || t.includes('numeric');
};

// Staged Addition Handlers (GREEN)
const addNewStagedRow = () => {
  pendingAdds.value.unshift({});
};

const discardAdd = (idx) => {
  pendingAdds.value.splice(idx, 1);
};

// Staged Inline Editing Handlers via Double-Click (YELLOW)
const startDoubleClickEdit = (row) => {
  // Prevent edit if row is staged for deletion
  if (pendingDeletes.value[row.id]) return;

  activeEditRowId.value = row.id;
  if (!pendingEdits.value[row.id]) {
    pendingEdits.value[row.id] = { ...row };
  }
};

const confirmRowEdit = (id) => {
  activeEditRowId.value = null;
};

const discardEdit = (id) => {
  delete pendingEdits.value[id];
  if (activeEditRowId.value === id) {
    activeEditRowId.value = null;
  }
};

const getDisplayValue = (row, colName) => {
  if (pendingEdits.value[row.id] && pendingEdits.value[row.id][colName] !== undefined) {
    const val = pendingEdits.value[row.id][colName];
    return val !== null && val !== undefined ? String(val) : '-';
  }
  const val = row[colName];
  return val !== null && val !== undefined ? String(val) : '-';
};

// Staged Deletion Handlers (RED)
const stageDelete = (id) => {
  // If user was editing it, stop edit active box
  if (activeEditRowId.value === id) {
    activeEditRowId.value = null;
  }
  pendingDeletes.value[id] = true;
};

const restoreDelete = (id) => {
  delete pendingDeletes.value[id];
};

// Batch Commit / Synchronization Engine
const hasStagedChanges = computed(() => {
  return pendingAdds.value.length > 0 || 
         Object.keys(pendingEdits.value).length > 0 || 
         Object.keys(pendingDeletes.value).length > 0;
});

const commitAllChanges = async () => {
  isSaving.value = true;
  try {
    // 1. Process Staged Deletes
    for (const id of Object.keys(pendingDeletes.value)) {
      if (pendingDeletes.value[id]) {
        await store.delete{{ class_name }}(id);
      }
    }

    // 2. Process Staged Edits
    for (const id of Object.keys(pendingEdits.value)) {
      if (!pendingDeletes.value[id]) {
        await store.update{{ class_name }}(id, pendingEdits.value[id]);
      }
    }

    // 3. Process Staged Adds
    for (const addObj of pendingAdds.value) {
      const payload = { ...addObj };
      if (payload.id === '' || payload.id === null || payload.id === undefined) {
        delete payload.id;
      }
      await store.create{{ class_name }}(payload);
    }

    // Pull fresh normalized database state
    await store.fetch{{ plural_name }}();

    // Reset local staging mappings
    discardAllChanges();
  } catch (err) {
    alert('Terjadi anomali saat melakukan sinkronisasi batch pangkalan data.');
  } finally {
    isSaving.value = false;
  }
};

const discardAllChanges = () => {
  pendingAdds.value = [];
  pendingEdits.value = {};
  pendingDeletes.value = {};
  activeEditRowId.value = null;
};

// Powerful DBeaver SQL & Text Dual Filter
const isSqlFilter = computed(() => {
  const q = searchQuery.value.trim();
  return /[=><]/.test(q) || /\band\b/i.test(q) || /\bor\b/i.test(q);
});

const filteredItems = computed(() => {
  const list = store.items || [];
  if (!searchQuery.value.trim()) return list;

  const query = searchQuery.value.trim();

  if (isSqlFilter.value) {
    try {
      const conditions = query.split(/\band\b/i).map(c => c.trim());
      return list.filter(item => {
        return conditions.every(cond => {
          const match = cond.match(/^([a-zA-Z0-9_]+)\s*([=><]+|like)\s*(.+)$/i);
          if (!match) return false;
          const [, field, op, valRaw] = match;
          const val = valRaw.replace(/^["']|["']$/g, '');
          const itemVal = item[field];
          if (itemVal === undefined || itemVal === null) return false;

          if (op === '=') return String(itemVal).toLowerCase() === val.toLowerCase();
          if (op === '>') return Number(itemVal) > Number(val);
          if (op === '<') return Number(itemVal) < Number(val);
          if (op.toLowerCase() === 'like') return String(itemVal).toLowerCase().includes(val.toLowerCase());
          return false;
        });
      });
    } catch (e) {
      // safe fallback
    }
  }

  const q = query.toLowerCase();
  return list.filter(item => {
    return Object.values(item).some(val => 
      val !== null && val !== undefined && String(val).toLowerCase().includes(q)
    );
  });
});

// Sorting Logic
const sortBy = (col) => {
  if (sortColumn.value === col) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = col;
    sortDirection.value = 'asc';
  }
  currentPage.value = 1;
};

const getSortClass = (col) => {
  if (sortColumn.value !== col) return '';
  return sortDirection.value === 'asc' ? 'active-asc' : 'active-desc';
};

const sortedItems = computed(() => {
  const list = [...filteredItems.value];
  if (!sortColumn.value) return list;

  return list.sort((a, b) => {
    let valA = a[sortColumn.value];
    let valB = b[sortColumn.value];

    if (valA === null || valA === undefined) valA = '';
    if (valB === null || valB === undefined) valB = '';

    if (typeof valA === 'string') valA = valA.toLowerCase();
    if (typeof valB === 'string') valB = valB.toLowerCase();

    if (valA < valB) return sortDirection.value === 'asc' ? -1 : 1;
    if (valA > valB) return sortDirection.value === 'asc' ? 1 : -1;
    return 0;
  });
});

// Pagination Computation
const totalPages = computed(() => {
  return Math.max(1, Math.ceil(filteredItems.value.length / pageSize.value));
});

const startIndex = computed(() => {
  return (currentPage.value - 1) * pageSize.value;
});

const paginatedItems = computed(() => {
  return sortedItems.value.slice(startIndex.value, startIndex.value + pageSize.value);
});

// Combine Staged Adds with DB Paginated Rows directly in the flow view
const combinedItems = computed(() => {
  const baseList = paginatedItems.value.map(item => ({ ...item }));
  const addsList = pendingAdds.value.map((addItem, aIdx) => ({
    ...addItem,
    isPendingAdd: true,
    pendingAddIndex: aIdx
  }));
  return [...addsList, ...baseList];
});
</script>
