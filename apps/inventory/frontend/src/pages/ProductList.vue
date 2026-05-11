<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Product List</h1>
      <router-link 
        :to="{ name: '{{ model_name.lower() }}_create' }"
        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
      >
        Add New Product
      </router-link>
    </div>

    <!-- Search & Filters -->
    <div class="bg-white p-4 rounded-lg shadow-sm border mb-6 flex gap-4">
      <input 
        type="text" 
        placeholder="Search..." 
        class="border rounded px-4 py-2 w-full focus:ring-2 focus:ring-blue-500"
      />
    </div>

    <!-- Data Table -->
    <div class="bg-white rounded-lg shadow-sm border overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b">
          <tr>
            
            <th class="px-6 py-3 text-sm font-semibold text-gray-600 uppercase">
              title
            </th>
            
            <th class="px-6 py-3 text-sm font-semibold text-gray-600 uppercase">
              price
            </th>
            
            <th class="px-6 py-3 text-sm font-semibold text-gray-600 uppercase">
              stock
            </th>
            
            <th class="px-6 py-3 text-sm font-semibold text-gray-600 uppercase">
              category
            </th>
            
            <th class="px-6 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50 transition">
            
            <td class="px-6 py-4 text-sm text-gray-700">
              {{ item['title'] }}
            </td>
            
            <td class="px-6 py-4 text-sm text-gray-700">
              {{ item['price'] }}
            </td>
            
            <td class="px-6 py-4 text-sm text-gray-700">
              {{ item['stock'] }}
            </td>
            
            <td class="px-6 py-4 text-sm text-gray-700">
              {{ item['category'] }}
            </td>
            
            <td class="px-6 py-4 text-right space-x-3">
              <router-link :to="{ name: '{{ model_name.lower() }}_edit', params: { id: item.id } }" class="text-blue-600 hover:underline">Edit</router-link>
              <button @click="deleteItem(item.id)" class="text-red-600 hover:underline">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useProductStore } from '@/stores/{{ model_name.lower() }}Store';

const store = useProductStore();
const { items } = store;

onMounted(() => {
  store.fetchProducts();
});

const deleteItem = async (id) => {
  if (confirm('Are you sure you want to delete this Product?')) {
    await store.deleteProduct(id);
  }
};
</script>
