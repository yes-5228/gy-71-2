<template>
  <nav class="tabs" aria-label="业务导航">
    <button
      v-for="item in items"
      :key="item.key"
      type="button"
      :class="{ active: modelValue === item.key }"
      @click="$emit('update:modelValue', item.key)"
    >
      {{ item.label }}
    </button>
  </nav>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true
  },
  items: {
    type: Array,
    required: true
  }
})

defineEmits(['update:modelValue'])
</script>
