<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, Eye, EyeOff, LineChart, ShieldCheck, Sparkles, UsersRound } from 'lucide-vue-next'

import { useAuthStore } from '@/stores/auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const keepSigned = ref(true)

const handleSubmit = async () => {
  if (authStore.loading) return
  const success = await authStore.login({
    email: email.value,
    password: password.value,
    persist: keepSigned.value,
  })

  if (success) {
    if ((authStore.user?.companies?.length ?? 0) > 1 && !authStore.selectedCompany) {
      router.push({ name: 'company-select' })
    } else {
      router.push({ name: 'dashboard' })
    }
  }
}

const currentYear = new Date().getFullYear()

const heroHighlights = [
  { label: 'Clientes ativos', value: '24.582', change: '+8% vs. mês anterior', icon: UsersRound },
  { label: 'Campanhas rodando', value: '312', change: '+18 este mês', icon: Sparkles },
  { label: 'Pontos emitidos', value: '3,2M', change: '+112k nesta semana', icon: LineChart },
]

const trustBadges = [
  { title: 'Segurança empresarial', description: 'Autenticação JWT e acesso por papéis.', icon: ShieldCheck },
  { title: 'Insights em tempo real', description: 'KPIs de clientes e campanhas sempre atualizados.', icon: LineChart },
]
</script>

<template>
  <div class="grid min-h-screen bg-[#F5F7FB] lg:grid-cols-2">
    <div class="relative hidden bg-gradient-to-b from-foreground to-foreground/80 px-10 py-12 text-white lg:flex lg:flex-col lg:justify-between">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.25),_transparent_45%)] opacity-60" />
      <div class="relative space-y-4">
        <p class="text-xs font-semibold uppercase tracking-[0.45em] text-white/70">Fidelidade+</p>
        <h1 class="text-4xl font-semibold leading-tight text-white">
          Fidelize clientes com experiências <span class="text-emerald-200">premium.</span>
        </h1>
        <p class="max-w-md text-base text-white/80">
          Centralize o relacionamento com seus clientes, acompanhe métricas em tempo real e personalize cada jornada com a identidade da sua marca.
        </p>
      </div>
      <div class="relative space-y-5 rounded-3xl border border-white/15 bg-white/10 p-6 text-sm text-white backdrop-blur">
        <div class="grid gap-4 sm:grid-cols-3">
          <div
            v-for="item in heroHighlights"
            :key="item.label"
            class="rounded-2xl border border-white/20 bg-white/5 p-4 shadow-sm shadow-black/15"
          >
            <component :is="item.icon" class="mb-3 h-5 w-5 text-white/80" />
            <p class="text-[11px] uppercase tracking-wide text-white/60">{{ item.label }}</p>
            <p class="text-2xl font-semibold">{{ item.value }}</p>
            <p class="text-[10px] text-emerald-100">{{ item.change }}</p>
          </div>
        </div>
        <div class="flex flex-wrap gap-4 text-white/85">
          <div
            v-for="badge in trustBadges"
            :key="badge.title"
            class="flex items-start gap-3 text-left"
          >
            <div class="rounded-full bg-white/15 p-2">
              <component :is="badge.icon" class="h-4 w-4" />
            </div>
            <div class="space-y-1">
              <p class="text-sm font-semibold text-white">{{ badge.title }}</p>
              <p class="text-[11px] text-white/70">{{ badge.description }}</p>
            </div>
          </div>
        </div>
      </div>
      <div class="relative flex items-center gap-4 rounded-2xl border border-white/20 bg-white/5 p-4 text-xs text-white/70">
        <Sparkles class="h-8 w-8 text-white" />
        <div>
          <p class="text-sm font-semibold text-white">Painel atualizado automaticamente</p>
          <p>Seus tokens e temas são carregados assim que você entra. Não perca o fluxo da sua operação.</p>
        </div>
      </div>
    </div>

    <div class="flex flex-col justify-center space-y-8 px-6 py-12 sm:px-10 lg:px-14">
      <div class="space-y-2 text-center lg:text-left">
        <p class="text-xs font-semibold uppercase tracking-[0.4em] text-muted-foreground">Acesso ao painel</p>
        <h2 class="text-3xl font-semibold text-foreground">Entrar no Fidelidade+</h2>
        <p class="text-sm text-muted-foreground">Informe suas credenciais para acessar o painel administrativo.</p>
      </div>

      <Card class="border border-border/80 bg-card/95 shadow-lg shadow-primary/5">
        <CardHeader class="space-y-1 text-center lg:text-left">
          <CardTitle class="text-2xl font-semibold text-foreground">Bem-vindo de volta</CardTitle>
          <CardDescription class="text-sm">Use as credenciais corporativas para acessar o painel Fidelidade+</CardDescription>
        </CardHeader>
        <CardContent>
          <form class="space-y-5" @submit.prevent="handleSubmit">
            <div class="space-y-2">
              <label class="text-sm font-medium text-muted-foreground">Email corporativo</label>
              <Input
                v-model="email"
                type="email"
                placeholder="nome@empresa.com"
                autocomplete="email"
                required
              />
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium text-muted-foreground">Senha</label>
              <div class="relative">
                <Input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="••••••••"
                  autocomplete="current-password"
                  required
                  class="pr-11"
                />
                <button
                  type="button"
                  class="absolute inset-y-0 right-3 flex items-center text-muted-foreground transition hover:text-foreground"
                  @click="showPassword = !showPassword"
                >
                  <Eye class="h-4 w-4" v-if="showPassword" />
                  <EyeOff class="h-4 w-4" v-else />
                </button>
              </div>
              <div class="flex items-center justify-between text-xs text-muted-foreground">
                <label class="inline-flex cursor-pointer items-center gap-2">
                  <input
                    v-model="keepSigned"
                    type="checkbox"
                    class="h-4 w-4 rounded border border-border/80 text-primary focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
                  />
                  Manter conectado
                </label>
                <span class="cursor-pointer font-medium text-primary hover:underline">Precisa de acesso?</span>
              </div>
            </div>

            <div
              v-if="authStore.error"
              class="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive"
            >
              {{ authStore.error }}
            </div>

            <Button type="submit" class="w-full gap-2" :disabled="authStore.loading">
              {{ authStore.loading ? 'Entrando...' : 'Entrar no painel' }}
              <ArrowRight class="h-4 w-4" />
            </Button>
          </form>

          <div class="mt-8 grid gap-4 rounded-2xl border border-dashed border-border/80 bg-muted/20 p-4 text-sm text-muted-foreground">
            <p class="font-medium text-foreground">Suporte prioritário</p>
            <p>Administradores podem solicitar reset de senha ou novos acessos diretamente com nosso time de onboarding.</p>
          </div>
        </CardContent>
        <CardFooter class="flex flex-col gap-2 text-center text-xs text-muted-foreground">
          <p>Ao entrar você concorda com os Termos de Uso e Política de Privacidade.</p>
          <p class="text-[11px] text-muted-foreground/80">© {{ currentYear }} Fidelidade+. Todos os direitos reservados.</p>
        </CardFooter>
      </Card>
    </div>
  </div>
</template>
