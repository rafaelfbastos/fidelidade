<script setup lang="ts">
import { Hammer } from 'lucide-vue-next'
</script>

<template>
  <main class="flex min-h-[70vh] flex-col items-center justify-center px-4 py-10 text-center">
    <div class="space-y-4">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
        <Hammer class="h-8 w-8" />
      </div>
      <h1 class="text-3xl font-semibold tracking-tight text-foreground">Dashboard em construção</h1>
      <p class="text-sm text-muted-foreground">
        Estamos finalizando integrações e métricas principais. Assim que estiver tudo pronto, o painel será liberado para
        uso.
      </p>
    </div>
  </main>
</template>
