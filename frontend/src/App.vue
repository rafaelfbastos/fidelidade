<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'

import AdminLayout from '@/components/layout/AdminLayout.vue'
import AuthLayout from '@/components/layout/AuthLayout.vue'

const route = useRoute()

const layoutComponent = computed(() => {
  return route.meta.layout === 'auth' ? AuthLayout : AdminLayout
})
</script>

<template>
  <component :is="layoutComponent">
    <RouterView />
  </component>
</template>
