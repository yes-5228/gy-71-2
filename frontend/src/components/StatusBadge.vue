<template>
  <span class="status-badge" :class="`status-${value}`">{{ statusText(value) }}</span>
</template>

<script setup>
import { statusText } from '../utils/formatters'

defineProps({
  value: {
    type: String,
    required: true
  }
})
</script>
