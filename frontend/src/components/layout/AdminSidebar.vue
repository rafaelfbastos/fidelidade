<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { Gift, LayoutDashboard, Settings2, Sparkles, Users } from 'lucide-vue-next'

import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth'

interface NavItem {
  label: string
  icon: any
  to?: string
  badge?: string
}

const props = defineProps<{
  isOpen: boolean
  isCollapsed: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const route = useRoute()
const authStore = useAuthStore()

const primaryNav: NavItem[] = [
  { label: 'Dashboard', icon: LayoutDashboard, to: '/' },
  { label: 'Clientes', icon: Users, badge: 'em breve' },
  { label: 'Recompensas', icon: Gift, badge: 'beta' },
  { label: 'Campanhas', icon: Sparkles },
]

const secondaryNav: NavItem[] = [{ label: 'Ajustes visuais', icon: Settings2, to: '/settings/layout' }]

const brandName = computed(() => authStore.selectedCompany?.company.trade_name || 'Painel Admin')
const brandSubtitle = computed(() => 'Fidelidade+')
const brandLogo = computed(() => {
  const theme = authStore.selectedCompany?.theme
  const override =
    theme?.extra_config && typeof theme.extra_config['logo_url_override'] === 'string'
      ? (theme.extra_config['logo_url_override'] as string)
      : null
  return override ?? theme?.logos?.light ?? authStore.selectedCompany?.company.logo ?? null
})

const sidebarBackgroundColor = computed(() => authStore.selectedCompany?.theme?.background?.primary ?? '#ffffff')
const sidebarDividerColor = computed(() => authStore.selectedCompany?.theme?.background?.secondary ?? '#eceff5')

const sidebarStyle = computed(() => ({
  backgroundColor: sidebarBackgroundColor.value,
  borderColor: sidebarDividerColor.value,
}))

const sectionDividerStyle = computed(() => ({
  backgroundColor: sidebarDividerColor.value,
}))

const handleClose = () => emit('close')
</script>

<template>
  <aside
    :class="[
      'fixed inset-y-0 left-0 z-40 flex flex-col border-r shadow-lg backdrop-blur-lg transition-[transform,width] duration-200 md:sticky md:top-0 md:h-screen md:self-start md:translate-x-0',
      props.isCollapsed ? 'w-20' : 'w-72',
      props.isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
    ]"
    :style="sidebarStyle"
  >
    <div class="flex h-16 items-center gap-3 border-b px-4" :style="{ borderColor: sidebarDividerColor }">
      <div class="flex h-11 w-11 items-center justify-center overflow-hidden rounded-2xl bg-primary/15 text-lg font-semibold text-primary">
        <img v-if="brandLogo" :src="brandLogo" alt="Logo" class="h-full w-full object-cover" />
        <span v-else>F+</span>
      </div>
      <transition name="fade">
        <div v-if="!props.isCollapsed" class="min-w-0">
          <p class="truncate text-xs uppercase tracking-wide text-muted-foreground">
            {{ brandSubtitle }}
          </p>
          <p class="truncate text-base font-semibold">{{ brandName }}</p>
        </div>
      </transition>
    </div>
    <ScrollArea class="flex-1 px-2 py-6">
      <p
        v-if="!props.isCollapsed"
        class="px-2 text-xs font-medium uppercase tracking-wide text-muted-foreground"
      >
        Menu principal
      </p>
      <div class="mt-3 space-y-1">
        <template v-for="item in primaryNav" :key="item.label">
          <RouterLink
            v-if="item.to"
            :to="item.to"
            :class="[
              'group flex items-center rounded-xl py-2 text-sm font-medium transition',
              props.isCollapsed ? 'justify-center px-2' : 'justify-between px-3',
              route.path === item.to
                ? 'bg-primary/90 text-white shadow-sm'
                : 'text-muted-foreground hover:bg-muted/70 hover:text-foreground',
            ]"
            @click="handleClose"
          >
            <span class="flex items-center gap-2" :class="{ 'justify-center': props.isCollapsed }">
              <component :is="item.icon" class="h-4 w-4" />
              <span v-if="!props.isCollapsed">{{ item.label }}</span>
            </span>
            <Badge v-if="item.badge && !props.isCollapsed" variant="outline" class="text-[10px] uppercase">
              {{ item.badge }}
            </Badge>
          </RouterLink>
          <button
            v-else
            type="button"
            :class="[
              'flex w-full items-center rounded-xl py-2 text-sm font-medium text-muted-foreground transition hover:bg-muted/70 hover:text-foreground',
              props.isCollapsed ? 'justify-center px-2' : 'justify-between px-3',
            ]"
          >
            <span class="flex items-center gap-2" :class="{ 'justify-center': props.isCollapsed }">
              <component :is="item.icon" class="h-4 w-4" />
              <span v-if="!props.isCollapsed">{{ item.label }}</span>
            </span>
            <Badge v-if="item.badge && !props.isCollapsed" variant="outline" class="text-[10px] uppercase">
              {{ item.badge }}
            </Badge>
          </button>
        </template>
      </div>

      <Separator class="my-6" :style="sectionDividerStyle" />

      <p
        v-if="!props.isCollapsed"
        class="px-2 text-xs font-medium uppercase tracking-wide text-muted-foreground"
      >
        Configurações
      </p>
      <div class="mt-3 space-y-1">
        <template v-for="item in secondaryNav" :key="item.label">
          <RouterLink
            v-if="item.to"
            :to="item.to"
            :class="[
              'group flex items-center rounded-xl py-2 text-sm font-medium transition',
              props.isCollapsed ? 'justify-center px-2' : 'justify-between px-3',
              route.path === item.to
                ? 'bg-primary/90 text-white shadow-sm'
                : 'text-muted-foreground hover:bg-muted/70 hover:text-foreground',
            ]"
            @click="handleClose"
          >
            <span class="flex items-center gap-2" :class="{ 'justify-center': props.isCollapsed }">
              <component :is="item.icon" class="h-4 w-4" />
              <span v-if="!props.isCollapsed">{{ item.label }}</span>
            </span>
          </RouterLink>
          <button
            v-else
            type="button"
            :class="[
              'flex w-full items-center gap-2 rounded-xl py-2 text-sm font-medium text-muted-foreground transition hover:bg-muted/70 hover:text-foreground',
              props.isCollapsed ? 'justify-center px-2' : 'px-3',
            ]"
          >
            <span class="flex items-center gap-2" :class="{ 'justify-center': props.isCollapsed }">
              <component :is="item.icon" class="h-4 w-4" />
              <span v-if="!props.isCollapsed">{{ item.label }}</span>
            </span>
          </button>
        </template>
      </div>
    </ScrollArea>
    <div class="border-t px-4 py-4" :style="{ borderColor: sidebarDividerColor }">
      <slot name="footer" />
    </div>
  </aside>
</template>
