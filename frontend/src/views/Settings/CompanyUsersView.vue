<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { Copy, KeyRound, Loader2, Mail, Phone, RefreshCcw, Shield, Trash2, UserPlus, X } from 'lucide-vue-next'

import api from '@/lib/http'
import { useAuthStore } from '@/stores/auth'
import type { CompanyMemberRecord, PaginatedResponse } from '@/types/company'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

const authStore = useAuthStore()

const members = ref<CompanyMemberRecord[]>([])
const loading = ref(false)
const submitting = ref(false)
const feedback = ref<{ type: 'success' | 'error'; message: string } | null>(null)
const lastResetInfo = ref<{ email: string; password: string } | null>(null)
const form = reactive({
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  role: 'attendant',
  password: '',
})

const currentCompanyUuid = computed(() => authStore.selectedCompany?.company.uuid ?? null)
const companyName = computed(() => authStore.selectedCompany?.company.trade_name ?? 'Empresa')
const roleOptions = [
  { value: 'owner', label: 'Proprietário' },
  { value: 'admin', label: 'Administrador' },
  { value: 'attendant', label: 'Atendente' },
]

const canManage = computed(() => ['owner', 'admin'].includes(authStore.selectedCompany?.role ?? ''))
const showModal = ref(false)
const modalPrimaryColor = computed(() => authStore.selectedCompany?.theme?.colors?.primary ?? '#111827')
const resetModal = reactive<{
  open: boolean
  password: string
  saving: boolean
  member: CompanyMemberRecord | null
}>({
  open: false,
  password: '',
  saving: false,
  member: null,
})

const createStrongPassword = (length = 12) => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz0123456789!@#$%&*'
  return Array.from({ length }, () => chars[Math.floor(Math.random() * chars.length)]).join('')
}

const copyToClipboard = async (value: string) => {
  if (!value) return false
  try {
    await navigator.clipboard.writeText(value)
    return true
  } catch {
    return false
  }
}

const resetForm = () => {
  form.email = ''
  form.first_name = ''
  form.last_name = ''
  form.phone = ''
  form.role = 'attendant'
  form.password = ''
}

const openModal = () => {
  if (!canManage.value) return
  resetForm()
  showModal.value = true
}

const closeModal = () => {
  if (submitting.value) return
  showModal.value = false
}

const handleGeneratePassword = () => {
  form.password = createStrongPassword()
}

const handleCopyPassword = async (password: string) => {
  const success = await copyToClipboard(password)
  if (!success) {
    feedback.value = {
      type: 'error',
      message: 'Não foi possível copiar a senha. Copie manualmente.',
    }
  }
}

const extractMembers = (
  payload: CompanyMemberRecord[] | PaginatedResponse<CompanyMemberRecord> | null | undefined,
) => {
  if (!payload) return []
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload.results)) return payload.results
  return []
}

const fetchMembers = async () => {
  if (!currentCompanyUuid.value) return
  loading.value = true
  lastResetInfo.value = null
  try {
    const { data } = await api.get<CompanyMemberRecord[] | PaginatedResponse<CompanyMemberRecord> | null>(
      `/companies/${currentCompanyUuid.value}/members/`,
    )
    const sanitized = extractMembers(data).filter(Boolean)
    members.value = sanitized
  } catch (error: any) {
    feedback.value = {
      type: 'error',
      message: error?.response?.data?.detail ?? 'Não foi possível carregar os usuários da empresa.',
    }
  } finally {
    loading.value = false
  }
}

const getErrorMessage = (err: any, fallback: string) => {
  const data = err?.response?.data
  if (!data) return fallback
  if (typeof data === 'string') return data
  if (typeof data.detail === 'string') return data.detail
  const firstValue = Object.values(data)[0]
  if (Array.isArray(firstValue)) return String(firstValue[0])
  if (typeof firstValue === 'string') return firstValue
  return fallback
}

const handleSubmit = async () => {
  if (!currentCompanyUuid.value || submitting.value || !canManage.value) return
  submitting.value = true
  feedback.value = null
  try {
    const payload = {
      email: form.email.trim(),
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      phone: form.phone.trim(),
      role: form.role,
      password: form.password.trim(),
    }
    const { data } = await api.post<CompanyMemberRecord>(
      `/companies/${currentCompanyUuid.value}/members/`,
      payload,
    )
    const existingIndex = members.value.findIndex((member) => member.uuid === data.uuid)
    if (existingIndex >= 0) {
      members.value.splice(existingIndex, 1, data)
    } else {
      members.value = [data, ...members.value]
    }
    resetForm()
    closeModal()
    feedback.value = { type: 'success', message: 'Usuário associado com sucesso.' }
  } catch (error: any) {
    feedback.value = {
      type: 'error',
      message: getErrorMessage(error, 'Não foi possível adicionar o usuário.'),
    }
  } finally {
    submitting.value = false
  }
}

const handleRemove = async (member: CompanyMemberRecord) => {
  if (!currentCompanyUuid.value || !canManage.value) return
  const confirmed = window.confirm(`Remover ${member.user.full_name || member.user.email} desta empresa?`)
  if (!confirmed) return
  try {
    await api.delete(`/companies/${currentCompanyUuid.value}/members/${member.uuid}/`)
    members.value = members.value.filter((item) => item.uuid !== member.uuid)
  } catch (error: any) {
    feedback.value = {
      type: 'error',
      message: getErrorMessage(error, 'Não foi possível remover este usuário.'),
    }
  }
}

const openResetModal = (member: CompanyMemberRecord) => {
  if (!canManage.value) return
  resetModal.member = member
  resetModal.password = createStrongPassword()
  resetModal.open = true
}

const closeResetModal = () => {
  if (resetModal.saving) return
  resetModal.open = false
  resetModal.member = null
  resetModal.password = ''
}

const regenerateResetPassword = () => {
  resetModal.password = createStrongPassword()
}

const submitResetPassword = async () => {
  if (!currentCompanyUuid.value || !resetModal.member || !resetModal.password) return
  resetModal.saving = true
  try {
    const { data } = await api.post<{ password: string }>(
      `/companies/${currentCompanyUuid.value}/members/${resetModal.member.uuid}/reset-password/`,
      { password: resetModal.password },
    )
    const password = data?.password ?? resetModal.password
    lastResetInfo.value = { email: resetModal.member.user.email, password }
    feedback.value = {
      type: 'success',
      message: `Senha redefinida para ${resetModal.member.user.email}. Copie o valor abaixo.`,
    }
    await copyToClipboard(password)
    closeResetModal()
  } catch (error: any) {
    feedback.value = {
      type: 'error',
      message: getErrorMessage(error, 'Não foi possível redefinir a senha.'),
    }
  } finally {
    resetModal.saving = false
  }
}

watch(
  currentCompanyUuid,
  (uuid) => {
    if (uuid) fetchMembers()
  },
  { immediate: true },
)

</script>

<template>
  <div class="space-y-6">
    <section class="rounded-3xl border border-border/70 bg-white p-6 shadow-sm">
      <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="text-xs uppercase tracking-[0.3em] text-muted-foreground">Gestão de usuários</p>
          <h1 class="text-3xl font-semibold text-foreground">Equipe de {{ companyName }}</h1>
          <p class="text-sm text-muted-foreground">
            Proprietários e administradores podem convidar usuários pelo email corporativo.
          </p>
        </div>
        <div class="flex flex-wrap gap-3">
          <Button v-if="canManage" class="gap-2" @click="openModal">
            <UserPlus class="h-4 w-4" />
            Cadastrar usuário
          </Button>
          <Button variant="outline" class="gap-2" :disabled="loading" @click="fetchMembers">
            <RefreshCcw class="h-4 w-4" :class="{ 'animate-spin': loading }" />
            Atualizar lista
          </Button>
        </div>
      </div>
      <div
        v-if="!canManage"
        class="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800"
      >
        Você precisa ser proprietário ou administrador da empresa selecionada para gerenciar usuários.
      </div>
    </section>

    <div v-if="feedback" :class="[
      'rounded-xl border px-4 py-3 text-sm',
      feedback.type === 'success'
        ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
        : 'border-destructive/40 bg-destructive/10 text-destructive',
    ]">
      {{ feedback.message }}
    </div>

    <div
      v-if="lastResetInfo"
      class="rounded-2xl border border-primary/30 bg-primary/5 p-4 text-sm text-foreground"
    >
      <p>
        Nova senha para <span class="font-semibold">{{ lastResetInfo.email }}</span>:
      </p>
      <div class="mt-2 flex flex-wrap items-center gap-3">
        <code class="rounded-xl bg-white px-3 py-1 text-base font-semibold text-primary">
          {{ lastResetInfo.password }}
        </code>
        <Button variant="outline" size="sm" class="gap-2" @click="handleCopyPassword(lastResetInfo.password)">
          <Copy class="h-3.5 w-3.5" />
          Copiar
        </Button>
      </div>
      <p class="mt-1 text-xs text-muted-foreground">
        Compartilhe a senha com o usuário em um canal seguro e peça para alterá-la no primeiro acesso.
      </p>
    </div>

    <div>
      <Card>
        <CardHeader>
          <CardTitle>Usuários vinculados</CardTitle>
          <CardDescription>Lista de usuários com acesso ao painel desta empresa.</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div v-if="loading" class="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 class="h-4 w-4 animate-spin" />
            Carregando colaboradores...
          </div>
          <div v-else-if="members.length === 0" class="rounded-2xl border border-dashed border-border/70 p-6 text-center">
            <p class="text-sm text-muted-foreground">Nenhum usuário foi associado a esta empresa.</p>
          </div>
          <div v-else class="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Colaborador</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead class="hidden sm:table-cell">Telefone</TableHead>
                  <TableHead>Papel</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="member in members" :key="member.uuid">
                  <TableCell>
                    <div class="flex flex-col">
                      <span class="font-semibold">{{ member.user.full_name || member.user.email }}</span>
                      <span class="text-xs text-muted-foreground">
                        Desde {{ new Date(member.created_at).toLocaleDateString('pt-BR') }}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell class="text-sm">
                    <div class="flex items-center gap-2">
                      <Mail class="h-4 w-4 text-muted-foreground" />
                      <span class="break-all">{{ member.user.email }}</span>
                    </div>
                  </TableCell>
                  <TableCell class="hidden text-sm text-muted-foreground sm:table-cell">
                    <div class="flex items-center gap-2">
                      <Phone class="h-4 w-4" />
                      {{ member.user.phone || '—' }}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" class="capitalize">
                      {{ member.role_display }}
                    </Badge>
                  </TableCell>
                  <TableCell class="text-right">
                    <div v-if="canManage" class="flex justify-end gap-1">
                      <Button
                        size="icon"
                        variant="ghost"
                        class="text-muted-foreground hover:text-primary"
                        @click="openResetModal(member)"
                      >
                        <KeyRound class="h-4 w-4" />
                      </Button>
                      <Button
                        size="icon"
                        variant="ghost"
                        class="text-muted-foreground hover:text-destructive"
                        @click="handleRemove(member)"
                      >
                        <Trash2 class="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

    </div>

    <Teleport to="body">
      <transition name="fade">
        <div
          v-if="showModal"
          class="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur"
          @click.self="closeModal"
        >
          <div class="w-[80vw] max-w-4xl overflow-hidden rounded-t-3xl rounded-b-none border border-border/80 bg-white shadow-2xl">
            <div class="relative flex flex-col">
              <div
                class="flex items-start justify-between rounded-t-3xl bg-gradient-to-r from-primary to-primary/80 px-6 py-5 text-white"
                :style="{ background: `linear-gradient(110deg, ${modalPrimaryColor}, ${modalPrimaryColor}cc)` }"
              >
                <div>
                  <p class="text-xs uppercase tracking-[0.3em] text-white/70">Cadastro interno</p>
                  <h2 class="text-2xl font-semibold leading-tight">Adicionar colaborador</h2>
                  <p class="text-sm text-white/80">
                    Informe os dados básicos e o papel que o usuário deverá exercer.
                  </p>
                </div>
                <Button variant="ghost" size="icon" class="text-white/80 hover:text-white" @click="closeModal">
                  <X class="h-5 w-5" />
                </Button>
              </div>
              <div class="px-6 py-6">
                <form class="space-y-4" @submit.prevent="handleSubmit">
                  <div class="space-y-2">
                    <label class="text-sm font-medium text-muted-foreground">Email corporativo</label>
                    <Input v-model="form.email" type="email" placeholder="nome@empresa.com" required />
                  </div>
                  <div class="grid gap-3 md:grid-cols-2">
                    <div class="space-y-2">
                      <label class="text-sm font-medium text-muted-foreground">Nome</label>
                      <Input v-model="form.first_name" placeholder="Nome" />
                    </div>
                    <div class="space-y-2">
                      <label class="text-sm font-medium text-muted-foreground">Sobrenome</label>
                      <Input v-model="form.last_name" placeholder="Sobrenome" />
                    </div>
                  </div>
                  <div class="space-y-2">
                    <label class="text-sm font-medium text-muted-foreground">Telefone</label>
                    <Input v-model="form.phone" placeholder="(11) 99999-9999" />
                  </div>
                  <div class="space-y-2">
                    <label class="text-sm font-medium text-muted-foreground">Senha inicial</label>
                    <div class="flex flex-col gap-2 md:flex-row">
                      <Input v-model="form.password" type="text" placeholder="Defina uma senha temporária" class="flex-1" />
                      <div class="flex gap-2">
                        <Button type="button" variant="outline" class="gap-2" @click="handleGeneratePassword">
                          <RefreshCcw class="h-4 w-4" />
                          Gerar
                        </Button>
                        <Button
                          type="button"
                          variant="outline"
                          class="gap-2"
                          :disabled="!form.password"
                          @click="handleCopyPassword(form.password)"
                        >
                          <Copy class="h-4 w-4" />
                          Copiar
                        </Button>
                      </div>
                    </div>
                    <p class="text-xs text-muted-foreground">
                      Opcional. Gere e copie uma senha para enviar ao usuário. Se deixar vazio, defina depois pelo botão de reset.
                    </p>
                  </div>
                  <div class="space-y-2">
                    <label class="text-sm font-medium text-muted-foreground">Papel na empresa</label>
                    <div class="relative">
                      <select
                        v-model="form.role"
                        class="w-full rounded-xl border border-border/70 bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                      >
                        <option v-for="option in roleOptions" :key="option.value" :value="option.value">
                          {{ option.label }}
                        </option>
                      </select>
                      <Shield class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    </div>
                    <p class="text-xs text-muted-foreground">
                      Proprietários possuem controle total; administradores gerenciam cadastros; atendentes operam apenas o caixa.
                    </p>
                  </div>
                  <div class="flex flex-wrap justify-end gap-3 pt-2">
                    <Button type="button" variant="outline" @click="closeModal">Cancelar</Button>
                    <Button type="submit" class="gap-2" :disabled="submitting || !canManage">
                      <UserPlus class="h-4 w-4" />
                      {{ submitting ? 'Salvando...' : 'Cadastrar' }}
                    </Button>
                  </div>
                </form>
                <p class="mt-4 text-xs text-muted-foreground">
                  Compartilhe a senha inicial por um canal seguro e incentive a troca no primeiro acesso.
                </p>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
    <Teleport to="body">
      <transition name="fade">
        <div
          v-if="resetModal.open"
          class="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur"
          @click.self="closeResetModal"
        >
          <div class="w-[90vw] max-w-md overflow-hidden rounded-3xl border border-border/80 bg-white shadow-2xl">
            <div
              class="flex items-center justify-between rounded-t-3xl px-5 py-4 text-white"
              :style="{ background: `linear-gradient(120deg, ${modalPrimaryColor}, ${modalPrimaryColor}cc)` }"
            >
              <div>
                <p class="text-xs uppercase tracking-[0.3em] text-white/70">Redefinir senha</p>
                <h3 class="text-xl font-semibold leading-tight">
                  {{ resetModal.member?.user.full_name || resetModal.member?.user.email }}
                </h3>
              </div>
              <Button variant="ghost" size="icon" class="text-white/80 hover:text-white" @click="closeResetModal">
                <X class="h-5 w-5" />
              </Button>
            </div>
            <div class="space-y-5 px-6 py-5">
              <p class="text-sm text-muted-foreground">
                Gere uma nova senha temporária para enviar ao usuário. Ela substituirá imediatamente a senha anterior.
              </p>
              <div class="space-y-2">
                <label class="text-sm font-medium text-muted-foreground">Nova senha</label>
                <div class="flex flex-col gap-2 sm:flex-row">
                  <Input v-model="resetModal.password" type="text" class="flex-1" />
                  <div class="flex gap-2">
                    <Button type="button" variant="outline" class="gap-2" @click="regenerateResetPassword">
                      <RefreshCcw class="h-4 w-4" />
                      Gerar
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      class="gap-2"
                      :disabled="!resetModal.password"
                      @click="handleCopyPassword(resetModal.password)"
                    >
                      <Copy class="h-4 w-4" />
                      Copiar
                    </Button>
                  </div>
                </div>
                <p class="text-xs text-muted-foreground">
                  Compartilhe a senha por um canal seguro e peça uma troca no primeiro login.
                </p>
              </div>
              <div class="flex justify-end gap-3">
                <Button type="button" variant="outline" @click="closeResetModal">Cancelar</Button>
                <Button type="button" class="gap-2" :disabled="resetModal.saving" @click="submitResetPassword">
                  <KeyRound class="h-4 w-4" />
                  {{ resetModal.saving ? 'Salvando...' : 'Redefinir' }}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>
