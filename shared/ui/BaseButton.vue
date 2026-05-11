<template>
  <button 
    :type="type"
    :class="[
      'px-4 py-2 rounded transition font-medium',
      variant === 'primary' ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
    ]"
    @click="$emit('click')"
  >
    <slot />
  </button>
</template>

<script setup>
defineProps({
  type: { type: String, default: 'button' },
  variant: { type: String, default: 'primary' }
});
defineEmits(['click']);
</script>
