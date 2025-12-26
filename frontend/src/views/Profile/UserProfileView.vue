<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { CalendarDays, KeyRound, Mail, Phone, ShieldCheck } from 'lucide-vue-next'

import { useAuthStore } from '@/stores/auth'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'

const authStore = useAuthStore()

const form = reactive({
  firstName: '',
  lastName: '',
  phone: '',
})
const passwordForm = reactive({
  current: '',
  newPassword: '',
  confirm: '',
})

const feedback = ref<{ type: 'success' | 'error'; message: string } | null>(null)
const isSaving = ref(false)
const passwordFeedback = ref<{ type: 'success' | 'error'; message: string } | null>(null)
const passwordErrors = ref<Record<string, string> | null>(null)
const isChangingPassword = ref(false)
const localPasswordErrors = ref<Record<string, string>>({})

const initials = computed(() => {
  const first = authStore.user?.first_name?.[0] ?? ''
  const last = authStore.user?.last_name?.[0] ?? ''
  const fallback = (first + last).trim()
  return fallback || (authStore.user?.email?.[0]?.toUpperCase() ?? 'US')
})

const companyCount = computed(() => authStore.user?.companies?.length ?? 0)
const selectedCompanyName = computed(() => authStore.selectedCompany?.company.trade_name ?? 'Sem empresa selecionada')
const memberSince = computed(() => {
  if (!authStore.user?.date_joined) return null
  const date = new Date(authStore.user.date_joined)
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(date)
})

watch(
  () => authStore.user,
  (user) => {
    form.firstName = user?.first_name ?? ''
    form.lastName = user?.last_name ?? ''
    form.phone = user?.phone ?? ''
  },
  { immediate: true },
)

const handleSubmit = async () => {
  if (!authStore.user) return
  isSaving.value = true
  feedback.value = null

  const payload = {
    first_name: form.firstName.trim(),
    last_name: form.lastName.trim(),
    phone: form.phone.trim(),
  }

  try {
    const result = await authStore.updateProfile(payload)
    if (!result.success) {
      throw new Error(result.message || 'Não foi possível atualizar o perfil.')
    }
    feedback.value = { type: 'success', message: 'Perfil atualizado com sucesso.' }
  } catch (error: any) {
    feedback.value = { type: 'error', message: error.message || 'Não foi possível atualizar o perfil.' }
  } finally {
    isSaving.value = false
  }
}

const normalizePasswordErrors = (errors: Record<string, any> | null) => {
  if (!errors) return null
  const normalized: Record<string, string> = {}
  Object.entries(errors).forEach(([key, value]) => {
    if (Array.isArray(value) && value.length) {
      normalized[key] = String(value[0])
    } else if (typeof value === 'string') {
      normalized[key] = value
    }
  })
  return normalized
}

const handlePasswordChange = async () => {
  if (!authStore.user) return
  const localErrors: Record<string, string> = {}
  if (passwordForm.newPassword.length < 8) {
    localErrors.new_password = 'A nova senha deve ter pelo menos 8 caracteres.'
  }
  if (!/[A-Za-z]/.test(passwordForm.newPassword) || !/\d/.test(passwordForm.newPassword)) {
    localErrors.new_password = localErrors.new_password
      ? localErrors.new_password + ' Inclua letras e números.'
      : 'Inclua letras e números na nova senha.'
  }
  if (passwordForm.newPassword !== passwordForm.confirm) {
    localErrors.new_password_confirm = 'As senhas não coincidem.'
  }
  localPasswordErrors.value = localErrors
  if (Object.keys(localErrors).length > 0) {
    passwordFeedback.value = {
      type: 'error',
      message: 'Corrija os erros antes de salvar.',
    }
    return
  }
  isChangingPassword.value = true
  passwordFeedback.value = null
  passwordErrors.value = null
  try {
    const result = await authStore.changePassword({
      current_password: passwordForm.current,
      new_password: passwordForm.newPassword,
      new_password_confirm: passwordForm.confirm,
    })
    if (!result.success) {
      passwordFeedback.value = { type: 'error', message: result.message || 'Não foi possível alterar a senha.' }
      passwordErrors.value = normalizePasswordErrors(result.errors ?? null)
      return
    }
    passwordFeedback.value = { type: 'success', message: 'Senha atualizada com sucesso.' }
    passwordErrors.value = null
    localPasswordErrors.value = {}
    passwordForm.current = ''
    passwordForm.newPassword = ''
    passwordForm.confirm = ''
  } catch (error: any) {
    passwordFeedback.value = { type: 'error', message: error.message || 'Não foi possível alterar a senha.' }
  } finally {
    isChangingPassword.value = false
  }
}
</script>

<template>
  <div class="mx-auto flex max-w-5xl flex-col gap-6">
    <section class="rounded-3xl border border-border/70 bg-white p-6 shadow-sm">
      <div class="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div class="flex flex-1 items-center gap-4">
          <Avatar class="h-20 w-20 border-2 border-primary/20 text-xl">
            <AvatarImage v-if="authStore.user?.avatar" :src="authStore.user.avatar" alt="Avatar do usuário" />
            <AvatarFallback>{{ initials }}</AvatarFallback>
          </Avatar>
          <div>
            <p class="text-xs uppercase tracking-[0.3em] text-muted-foreground">Perfil do usuário</p>
            <h1 class="text-3xl font-semibold text-foreground">
              {{ authStore.user?.full_name || authStore.user?.email }}
            </h1>
            <p class="text-sm text-muted-foreground">
              {{ selectedCompanyName }}
            </p>
          </div>
        </div>
        <div class="grid gap-4 text-sm sm:grid-cols-2">
          <div class="rounded-2xl border border-border/60 bg-muted/30 p-4">
            <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Acesso</p>
            <div class="mt-2 flex items-center gap-2 text-sm text-foreground">
              <ShieldCheck class="h-4 w-4 text-primary" />
              {{ companyCount }} empresas vinculadas
            </div>
          </div>
          <div class="rounded-2xl border border-border/60 bg-muted/30 p-4">
            <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Desde</p>
            <div class="mt-2 flex items-center gap-2 text-sm text-foreground">
              <CalendarDays class="h-4 w-4 text-primary" />
              {{ memberSince ?? '—' }}
            </div>
          </div>
        </div>
      </div>
      <Separator class="my-6" />
      <div class="grid gap-4 text-sm md:grid-cols-3">
        <div class="rounded-2xl border border-border/60 bg-muted/20 p-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Email corporativo</p>
          <div class="mt-2 flex items-center gap-2 break-all font-medium">
            <Mail class="h-4 w-4 text-muted-foreground" />
            {{ authStore.user?.email }}
          </div>
        </div>
        <div class="rounded-2xl border border-border/60 bg-muted/20 p-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Telefone</p>
          <div class="mt-2 flex items-center gap-2 font-medium">
            <Phone class="h-4 w-4 text-muted-foreground" />
            {{ authStore.user?.phone || 'não informado' }}
          </div>
        </div>
        <div class="rounded-2xl border border-border/60 bg-muted/20 p-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Empresa atual</p>
          <div class="mt-2 font-medium">
            {{ selectedCompanyName }}
          </div>
        </div>
      </div>
    </section>

    <Card>
      <CardHeader>
        <CardTitle>Atualizar dados pessoais</CardTitle>
        <CardDescription>
          Ajuste como seu nome e telefone aparecem para outros administradores e atendentes.
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-5">
        <div
          v-if="feedback"
          :class="[
            'rounded-xl border px-4 py-3 text-sm',
            feedback.type === 'success'
              ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
              : 'border-destructive/40 bg-destructive/10 text-destructive',
          ]"
        >
          {{ feedback.message }}
        </div>
        <form class="space-y-5" @submit.prevent="handleSubmit">
          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <label class="text-sm font-medium text-muted-foreground">Nome</label>
              <Input v-model="form.firstName" placeholder="Seu nome" required />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium text-muted-foreground">Sobrenome</label>
              <Input v-model="form.lastName" placeholder="Seu sobrenome" />
            </div>
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <label class="text-sm font-medium text-muted-foreground">Telefone</label>
              <Input v-model="form.phone" placeholder="(11) 99999-9999" />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium text-muted-foreground">Email</label>
              <Input :value="authStore.user?.email" disabled />
            </div>
          </div>
          <div class="flex justify-end">
            <Button type="submit" :disabled="isSaving" class="min-w-[180px]">
              {{ isSaving ? 'Salvando...' : 'Salvar alterações' }}
            </Button>
          </div>
        </form>
      </CardContent>
      <CardFooter class="text-xs text-muted-foreground">
        Atualizações no nome e telefone são refletidas imediatamente no histórico de atividades e nos registros das
        empresas vinculadas.
      </CardFooter>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Atualizar senha</CardTitle>
        <CardDescription>Defina uma nova senha seguindo as regras de segurança aplicadas pelo servidor.</CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div
          v-if="passwordFeedback"
          :class="[
            'rounded-xl border px-4 py-3 text-sm',
            passwordFeedback.type === 'success'
              ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
              : 'border-destructive/40 bg-destructive/10 text-destructive',
          ]"
        >
          {{ passwordFeedback.message }}
        </div>
        <form class="space-y-4" @submit.prevent="handlePasswordChange">
          <div class="space-y-2">
            <label class="text-sm font-medium text-muted-foreground">Senha atual</label>
            <Input
              v-model="passwordForm.current"
              type="password"
              placeholder="Digite sua senha atual"
              autocomplete="current-password"
              required
            />
            <p v-if="passwordErrors?.current_password" class="text-xs text-destructive">
              {{ passwordErrors.current_password }}
            </p>
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <label class="text-sm font-medium text-muted-foreground">Nova senha</label>
              <Input
                v-model="passwordForm.newPassword"
                type="password"
                placeholder="Mínimo 8 caracteres"
                autocomplete="new-password"
                required
              />
              <p v-if="passwordErrors?.new_password || localPasswordErrors.new_password" class="text-xs text-destructive">
                {{ passwordErrors?.new_password ?? localPasswordErrors.new_password }}
              </p>
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium text-muted-foreground">Confirmar nova senha</label>
              <Input
                v-model="passwordForm.confirm"
                type="password"
                placeholder="Repita sua nova senha"
                autocomplete="new-password"
                required
              />
              <p
                v-if="passwordErrors?.new_password_confirm || localPasswordErrors.new_password_confirm"
                class="text-xs text-destructive"
              >
                {{ passwordErrors?.new_password_confirm ?? localPasswordErrors.new_password_confirm }}
              </p>
            </div>
          </div>
          <div class="flex items-center justify-between text-xs text-muted-foreground">
            <div class="flex items-center gap-2">
              <KeyRound class="h-4 w-4 text-primary" />
              <span>Use letras, números e caracteres especiais para mais segurança.</span>
            </div>
            <Button type="submit" :disabled="isChangingPassword" class="min-w-[180px]">
              {{ isChangingPassword ? 'Atualizando...' : 'Alterar senha' }}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  </div>
</template>
