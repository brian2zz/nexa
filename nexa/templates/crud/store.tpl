import { defineStore } from 'pinia';
import service from '@/services/{{ model_name.lower() }}';

export const use{{ class_name }}Store = defineStore('{{ model_name.lower() }}', {
  state: () => ({
    items: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetch{{ plural_name }}() {
      this.loading = true;
      try {
        const response = await service.list();
        this.items = response.data;
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },

    async get{{ class_name }}(id) {
      const response = await service.get(id);
      return response.data;
    },

    async create{{ class_name }}(data) {
      const response = await service.create(data);
      this.items.push(response.data);
      return response.data;
    },

    async update{{ class_name }}(id, data) {
      const response = await service.update(id, data);
      const index = this.items.findIndex(item => item.id === id);
      if (index !== -1) {
        this.items[index] = response.data;
      }
      return response.data;
    },

    async delete{{ class_name }}(id) {
      await service.delete(id);
      this.items = this.items.filter(item => item.id !== id);
    }
  }
});
