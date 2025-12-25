<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronDown, LogOut } from 'lucide-vue-next'

import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth'
import AdminSidebar from './AdminSidebar.vue'
import AdminHeader from './AdminHeader.vue'

const authStore = useAuthStore()
const router = useRouter()

const SIDEBAR_COLLAPSED_KEY = 'sidebar_collapsed'
const AUTH_PERSIST_KEY = 'keep_signed_in'

const isSidebarOpen = ref(false)
const isSidebarCollapsed = ref(localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === 'true')

const closeSidebar = () => {
  isSidebarOpen.value = false
}

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const toggleSidebarCollapse = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

watch(
  isSidebarCollapsed,
  (value) => {
    localStorage.setItem(SIDEBAR_COLLAPSED_KEY, value ? 'true' : 'false')
  },
  { immediate: true },
)

const handleLogout = () => {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="flex min-h-screen bg-[#F5F7FB] text-foreground">
    <div
      v-if="isSidebarOpen"
      class="fixed inset-0 z-30 bg-background/70 backdrop-blur-sm md:hidden"
      @click="closeSidebar"
    />

    <AdminSidebar
      :is-open="isSidebarOpen"
      :is-collapsed="isSidebarCollapsed"
      @close="closeSidebar"
    >
      <template #footer>
        <Button
          variant="ghost"
          class="w-full justify-between"
          size="sm"
          @click="handleLogout"
        >
          <span class="flex items-center gap-2 text-sm">
            <LogOut class="h-4 w-4" />
            <span v-if="!isSidebarCollapsed">Sair</span>
          </span>
          <ChevronDown v-if="!isSidebarCollapsed" class="h-4 w-4 text-muted-foreground" />
        </Button>
      </template>
    </AdminSidebar>

    <div class="flex flex-1 flex-col">
      <AdminHeader
        :is-sidebar-collapsed="isSidebarCollapsed"
        @toggle-sidebar="toggleSidebar"
        @toggle-collapse="toggleSidebarCollapse"
        @logout="handleLogout"
      />
      <main class="flex-1 overflow-y-auto bg-muted/30 px-4 py-8">
        <slot />
      </main>
    </div>
  </div>
</template>
