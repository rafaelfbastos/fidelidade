<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Building2, Check, LogOut } from 'lucide-vue-next'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const companies = computed(() => authStore.user?.companies ?? [])

const handleSelect = (companyUuid: string) => {
  const company = companies.value.find((item) => item.company.uuid === companyUuid)
  if (!company) return
  authStore.setCompany(company)
  router.push({ name: 'dashboard' })
}

const handleLogout = () => {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#F5F7FB]">
    <header class="flex items-center justify-between px-6 py-5">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.4em] text-muted-foreground">Fidelidade+</p>
        <h1 class="text-2xl font-semibold text-foreground">Escolha a empresa</h1>
        <p class="text-sm text-muted-foreground">Selecione qual operação deseja administrar agora.</p>
      </div>
      <Button variant="outline" class="gap-2 rounded-full" @click="handleLogout">
        <LogOut class="h-4 w-4" />
        Sair
      </Button>
    </header>

    <main class="flex flex-1 items-center justify-center px-6 pb-12">
      <div class="grid w-full max-w-5xl gap-6 md:grid-cols-2">
        <Card
          v-for="company in companies"
          :key="company.company.uuid"
          class="cursor-pointer border border-border/70 transition hover:-translate-y-1 hover:border-primary/60 hover:shadow-xl"
          @click="handleSelect(company.company.uuid)"
        >
          <CardHeader class="space-y-1">
            <CardTitle class="flex items-center gap-3 text-xl">
              <img
                v-if="company.company.logo"
                :src="company.company.logo"
                alt=""
                class="h-12 w-12 rounded-2xl border border-border/60 bg-white object-contain p-1"
              />
              <div
                v-else
                class="flex h-12 w-12 items-center justify-center rounded-2xl border border-border/60 bg-muted text-muted-foreground"
              >
                <Building2 class="h-5 w-5" />
              </div>
              <span>{{ company.company.trade_name }}</span>
            </CardTitle>
            <CardDescription>{{ company.company.legal_name }}</CardDescription>
          </CardHeader>
          <CardContent class="space-y-3 text-sm text-muted-foreground">
            <div class="flex items-center justify-between text-xs uppercase tracking-wide text-muted-foreground">
              <span>Papel</span>
              <span class="rounded-full bg-muted px-3 py-1 text-[11px] font-semibold text-foreground">{{ company.role_display }}</span>
            </div>
            <div class="rounded-2xl bg-muted/60 p-4">
              <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Status</p>
              <div class="mt-2 flex items-center gap-2 text-foreground">
                <Check class="h-4 w-4 text-emerald-500" />
                {{ company.is_active ? 'Empresa ativa' : 'Empresa inativa' }}
              </div>
            </div>
            <p class="text-xs text-muted-foreground">
              Último acesso registrado para {{ company.company.trade_name }}: <strong>{{ company.created_at.split('T')[0] }}</strong>
            </p>
          </CardContent>
        </Card>
      </div>
    </main>
  </div>
</template>
