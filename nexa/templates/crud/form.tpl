<template>
  <div class="p-6 max-w-2xl mx-auto">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">{{ isEdit ? 'Edit' : 'Create' }} {{ class_name }}</h1>
    </div>

    <form @submit.prevent="save" class="bg-white p-6 rounded-lg shadow-sm border space-y-4">
      <!-- Dynamic Form Fields -->
      [loop:fields]
      <div>
        <label :for="'{{ item.name }}'" class="block text-sm font-medium text-gray-700 mb-1">{{ item.name }}</label>
        <input 
          v-model="form['{{ item.name }}']"
          :type="'{{ item.type }}' === 'integer' ? 'number' : 'text'"
          :id="'{{ item.name }}'"
          class="w-full border rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 transition"
          required
        />
      </div>
      [/loop]

      <div class="pt-4 flex gap-3">
        <button 
          type="submit" 
          class="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition"
        >
          Save {{ class_name }}
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
import { use{{ class_name }}Store } from '@/stores/{{ model_name.lower() }}Store';

const route = useRoute();
const router = useRouter();
const store = use{{ class_name }}Store();

const isEdit = computed(() => !!route.params.id);
const form = ref({});

onMounted(async () => {
  if (isEdit.value) {
    form.value = await store.get{{ class_name }}(route.params.id);
  }
});

const save = async () => {
  try {
    if (isEdit.value) {
      await store.update{{ class_name }}(route.params.id, form.value);
    } else {
      await store.create{{ class_name }}(form.value);
    }
    router.push({ name: '{{ model_name.lower() }}_list' });
  } catch (error) {
    alert('Failed to save {{ model_name }}');
  }
};
</script>
