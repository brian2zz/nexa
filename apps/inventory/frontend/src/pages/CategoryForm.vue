<template>
  <div class="p-6 max-w-2xl mx-auto">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">{{ isEdit ? 'Edit' : 'Create' }} Category</h1>
    </div>

    <form @submit.prevent="save" class="bg-white p-6 rounded-lg shadow-sm border space-y-4">
      <!-- Dynamic Form Fields -->
      
      <div>
        <label :for="'name'" class="block text-sm font-medium text-gray-700 mb-1">name</label>
        <input 
          v-model="form['name']"
          :type="'string' === 'integer' ? 'number' : 'text'"
          :id="'name'"
          class="w-full border rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 transition"
          required
        />
      </div>
      

      <div class="pt-4 flex gap-3">
        <button 
          type="submit" 
          class="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition"
        >
          Save Category
        </button>
        <router-link 
          :to="{ name: '{{ model_name.lower() }}_list' }"
          class="bg-gray-100 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-200 transition"
        >
          Cancel
        </router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useCategoryStore } from '@/stores/{{ model_name.lower() }}Store';

const route = useRoute();
const router = useRouter();
const store = useCategoryStore();

const isEdit = computed(() => !!route.params.id);
const form = ref({});

onMounted(async () => {
  if (isEdit.value) {
    form.value = await store.getCategory(route.params.id);
  }
});

const save = async () => {
  try {
    if (isEdit.value) {
      await store.updateCategory(route.params.id, form.value);
    } else {
      await store.createCategory(form.value);
    }
    router.push({ name: '{{ model_name.lower() }}_list' });
  } catch (error) {
    alert('Failed to save Category');
  }
};
</script>
