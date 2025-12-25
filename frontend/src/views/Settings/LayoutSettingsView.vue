<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import { useThemeStore, type ThemeFormValues } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'

const themeStore = useThemeStore()
const authStore = useAuthStore()

type ColorKey =
  | 'primaryColor'
  | 'secondaryColor'
  | 'accentColor'
  | 'successColor'
  | 'warningColor'
  | 'errorColor'
  | 'textPrimary'
  | 'textSecondary'
  | 'backgroundPrimary'
  | 'backgroundSecondary'
  | 'backgroundCard'

interface ColorField {
  key: ColorKey
  label: string
  helper?: string
}

const paletteFields: ColorField[] = [
  { key: 'primaryColor', label: 'Primária', helper: 'Botões e CTAs' },
  { key: 'secondaryColor', label: 'Secundária', helper: 'Links e destaques' },
  { key: 'accentColor', label: 'Acento', helper: 'Elementos decorativos' },
]

const statusFields: ColorField[] = [
  { key: 'successColor', label: 'Sucesso' },
  { key: 'warningColor', label: 'Aviso' },
  { key: 'errorColor', label: 'Erro' },
]

const textFields: ColorField[] = [
  { key: 'textPrimary', label: 'Texto primário', helper: 'Títulos' },
  { key: 'textSecondary', label: 'Texto secundário', helper: 'Descrições' },
]

const backgroundFields: ColorField[] = [
  { key: 'backgroundPrimary', label: 'Fundo principal' },
  { key: 'backgroundSecondary', label: 'Fundo secundário' },
  { key: 'backgroundCard', label: 'Cartões' },
]

const form = reactive<ThemeFormValues>({ ...themeStore.formDefaults })

const formDefaults = computed(() => themeStore.formDefaults)

watch(
  formDefaults,
  (defaults) => {
    Object.assign(form, defaults)
  },
  { immediate: true, deep: true },
)

const fetchedCompanyUuid = ref<string | null>(null)

watch(
  () => authStore.selectedCompany?.company.uuid,
  (uuid) => {
    if (!uuid || fetchedCompanyUuid.value === uuid) return
    fetchedCompanyUuid.value = uuid
    themeStore.fetchCompanyTheme(uuid).catch(() => null)
  },
  { immediate: true },
)

const isLoading = computed(() => themeStore.loadingTheme)
const isSaving = computed(() => themeStore.savingTheme)
const isResetting = computed(() => themeStore.resettingTheme)
const hasPendingAction = computed(() => isSaving.value || isResetting.value)
const errorMessage = computed(() => themeStore.error)

const handleApply = async () => {
  try {
    await themeStore.updateTheme({ ...form })
  } catch (error) {
    console.error(error)
  }
}

const handleReset = async () => {
  try {
    await themeStore.resetThemeToCompanyDefaults()
  } catch (error) {
    console.error(error)
  }
}
</script>

<template>
  <div class="space-y-6">
    <p v-if="errorMessage" class="rounded-lg border border-destructive/40 bg-destructive/5 p-3 text-sm text-destructive">
      {{ errorMessage }}
    </p>
    <Card>
      <CardHeader>
        <CardTitle>Identidade visual</CardTitle>
        <CardDescription>Defina a logo utilizada no cabeçalho e na sidebar.</CardDescription>
      </CardHeader>
      <CardContent class="grid items-center gap-6 md:grid-cols-[1fr_auto]">
        <div class="space-y-2">
          <label class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Logo (URL)</label>
          <Input v-model="form.logoUrl" type="url" placeholder="https://cdn.exemplo.com/logo.png" />
          <p class="text-[11px] text-muted-foreground">PNG com fundo transparente é recomendado.</p>
        </div>
        <div class="flex h-24 w-full max-w-[180px] items-center justify-center rounded-2xl border bg-muted/30 p-4">
          <img v-if="form.logoUrl" :src="form.logoUrl" alt="Prévia da logo" class="h-full object-contain" />
          <span v-else class="text-xs text-muted-foreground">Prévia indisponível</span>
        </div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Paleta de cores</CardTitle>
        <CardDescription>Atualize as cores principais e estados aplicados no painel.</CardDescription>
      </CardHeader>
      <CardContent class="space-y-6">
        <div class="grid gap-4 md:grid-cols-3">
          <div v-for="field in paletteFields" :key="field.key" class="space-y-2 rounded-2xl border bg-muted/20 p-4">
            <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{{ field.label }}</p>
            <div class="flex items-center gap-3">
              <input
                v-model="form[field.key]"
                type="color"
                class="h-10 w-14 cursor-pointer rounded-lg border border-border/70 bg-background"
              />
              <Input v-model="form[field.key]" placeholder="#000000" class="font-mono text-sm uppercase" />
            </div>
            <p v-if="field.helper" class="text-[11px] text-muted-foreground">{{ field.helper }}</p>
          </div>
        </div>
        <Separator />
        <div class="grid gap-4 md:grid-cols-3">
          <div v-for="field in statusFields" :key="field.key" class="space-y-2 rounded-2xl border bg-muted/20 p-4">
            <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{{ field.label }}</p>
            <div class="flex items-center gap-3">
              <input
                v-model="form[field.key]"
                type="color"
                class="h-10 w-14 cursor-pointer rounded-lg border border-border/70 bg-background"
              />
              <Input v-model="form[field.key]" placeholder="#000000" class="font-mono text-sm uppercase" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Textos e fundos</CardTitle>
        <CardDescription>Controle de contraste para manter o painel sempre legível.</CardDescription>
      </CardHeader>
      <CardContent class="grid gap-6 lg:grid-cols-2">
        <div class="space-y-4 rounded-2xl border bg-muted/20 p-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Textos</p>
          <div v-for="field in textFields" :key="field.key" class="space-y-2">
            <label class="text-sm font-medium">{{ field.label }}</label>
            <div class="flex items-center gap-3">
              <input
                v-model="form[field.key]"
                type="color"
                class="h-10 w-14 cursor-pointer rounded-lg border border-border/70 bg-background"
              />
              <Input v-model="form[field.key]" placeholder="#000000" class="font-mono text-sm uppercase" />
            </div>
            <p v-if="field.helper" class="text-[11px] text-muted-foreground">{{ field.helper }}</p>
          </div>
        </div>
        <div class="space-y-4 rounded-2xl border bg-muted/20 p-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Fundos</p>
          <div v-for="field in backgroundFields" :key="field.key" class="space-y-2">
            <label class="text-sm font-medium">{{ field.label }}</label>
            <div class="flex items-center gap-3">
              <input
                v-model="form[field.key]"
                type="color"
                class="h-10 w-14 cursor-pointer rounded-lg border border-border/70 bg-background"
              />
              <Input v-model="form[field.key]" placeholder="#000000" class="font-mono text-sm uppercase" />
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter class="flex flex-wrap gap-3">
        <Button
          class="min-w-[160px]"
          :disabled="hasPendingAction || isLoading"
          @click="handleApply"
        >
          {{ isSaving ? 'Salvando...' : 'Aplicar alterações' }}
        </Button>
        <Button
          variant="outline"
          class="min-w-[160px]"
          :disabled="hasPendingAction || isLoading"
          @click="handleReset"
        >
          {{ isResetting ? 'Restaurando...' : 'Restaurar padrão' }}
        </Button>
      </CardFooter>
    </Card>
  </div>
</template>
