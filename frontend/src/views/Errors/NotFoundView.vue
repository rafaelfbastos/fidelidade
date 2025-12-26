<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Compass, Home } from 'lucide-vue-next'

import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const primaryCtaLabel = computed(() => (authStore.isAuthenticated ? 'Voltar ao dashboard' : 'Ir para o login'))

const handlePrimaryAction = () => {
  if (authStore.isAuthenticated) {
    router.push({ name: 'dashboard' })
  } else {
    router.push({ name: 'login' })
  }
}

const handleGoBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    handlePrimaryAction()
  }
}
</script>

<template>
  <main class="mx-auto flex min-h-[70vh] w-full max-w-4xl flex-col items-center justify-center gap-8 px-4 py-10 text-center">
    <div class="space-y-5 rounded-3xl border border-dashed border-primary/40 bg-white/80 p-10 shadow-lg">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
        <Compass class="h-8 w-8" />
      </div>
      <p class="text-xs font-semibold uppercase tracking-[0.4em] text-primary">Erro 404</p>
      <div class="space-y-3">
        <h1 class="text-3xl font-semibold tracking-tight text-foreground">Página não encontrada</h1>
        <p class="text-sm text-muted-foreground">
          O endereço acessado não existe ou foi movido. Utilize as ações abaixo para continuar navegando.
        </p>
      </div>
      <div class="flex flex-wrap items-center justify-center gap-3">
        <Button class="gap-2" @click="handlePrimaryAction">
          <Home class="h-4 w-4" />
          {{ primaryCtaLabel }}
        </Button>
        <Button variant="outline" class="gap-2" @click="handleGoBack">
          <ArrowLeft class="h-4 w-4" />
          Voltar
        </Button>
      </div>
    </div>
    <p class="text-xs uppercase tracking-[0.3em] text-muted-foreground">Suporte disponível via chat interno</p>
  </main>
</template>
