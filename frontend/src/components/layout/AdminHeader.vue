<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Bell, ChevronDown, Menu } from 'lucide-vue-next'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  isSidebarCollapsed: boolean
}>()

const emit = defineEmits<{
  toggleSidebar: []
  toggleCollapse: []
  logout: []
}>()

const authStore = useAuthStore()
const router = useRouter()

const initials = computed(() => {
  const first = authStore.user?.first_name?.[0] ?? ''
  const last = authStore.user?.last_name?.[0] ?? ''
  const fallback = (first + last).trim()
  return fallback || 'FS'
})

const handleCompanySwitch = () => {
  router.push({ name: 'company-select' })
}

const handleProfileClick = () => {
  router.push({ name: 'user-profile' })
}
</script>

<template>
  <header class="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border/70 bg-white/80 px-4 shadow-sm backdrop-blur">
    <div class="flex items-center gap-2">
      <Button variant="outline" size="icon" class="md:hidden rounded-full" @click="emit('toggleSidebar')">
        <Menu class="h-5 w-5" />
      </Button>
      <Button
        variant="outline"
        size="icon"
        class="hidden rounded-full md:flex"
        @click="emit('toggleCollapse')"
      >
        <ChevronDown
          :class="[
            'h-5 w-5 transition-transform',
            props.isSidebarCollapsed ? '-rotate-90' : 'rotate-90',
          ]"
        />
      </Button>
    </div>
    <div class="flex flex-1 items-center gap-3" />
    <div class="flex items-center gap-3">
      <Button
        variant="outline"
        size="icon"
        class="rounded-full border border-border/60 text-muted-foreground transition hover:text-foreground"
      >
        <Bell class="h-5 w-5" />
      </Button>
      <DropdownMenu>
        <DropdownMenuTrigger class="flex items-center gap-2 rounded-full border px-3 py-1 text-sm font-semibold">
          <Avatar class="h-8 w-8">
            <AvatarImage v-if="authStore.user?.avatar" :src="authStore.user.avatar" alt="Avatar" />
            <AvatarFallback>{{ initials }}</AvatarFallback>
          </Avatar>
          <div class="hidden text-left leading-tight md:block">
            <p>{{ authStore.user?.full_name ?? 'Fidelidade+' }}</p>
            <span class="text-xs text-muted-foreground">
              {{ authStore.selectedCompany?.role_display ?? 'Admin' }}
            </span>
          </div>
          <ChevronDown class="h-4 w-4 text-muted-foreground" />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" class="w-56">
          <DropdownMenuLabel>Conta</DropdownMenuLabel>
          <DropdownMenuItem @click="handleProfileClick">Perfil</DropdownMenuItem>
          <DropdownMenuItem @click="handleCompanySwitch">Trocar empresa</DropdownMenuItem>
          <DropdownMenuItem>Integrações</DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem @click="emit('logout')">Sair</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  </header>
</template>
