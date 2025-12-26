<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref, watch } from 'vue'

import { useThemeStore, type ThemeFormValues } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { UploadCloud, Trash2 } from 'lucide-vue-next'

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

const existingLogo = computed(
  () => themeStore.selectedTheme?.logos?.light ?? authStore.selectedCompany?.company.logo ?? '',
)

const fileInputRef = ref<HTMLInputElement | null>(null)
const filePreviewUrl = ref<string | null>(null)

const resetFilePreview = () => {
  if (filePreviewUrl.value) {
    URL.revokeObjectURL(filePreviewUrl.value)
    filePreviewUrl.value = null
  }
}

watch(
  () => form.logoFile,
  (file) => {
    resetFilePreview()
    if (file) {
      filePreviewUrl.value = URL.createObjectURL(file)
    }
  },
)

onBeforeUnmount(() => {
  resetFilePreview()
})

const logoPreview = computed(() => {
  if (filePreviewUrl.value) return filePreviewUrl.value
  if (form.logoMode === 'url' && form.logoUrl) return form.logoUrl
  return form.logoUrl || existingLogo.value || ''
})

const triggerLogoUpload = () => {
  fileInputRef.value?.click()
}

const handleLogoFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files || !files.length) return
  const file = files.item(0)
  if (!file) return
  form.logoMode = 'upload'
  form.logoFile = file
}

const clearLogoFile = () => {
  form.logoFile = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

const handleLogoModeChange = (value: string | number) => {
  const parsedValue = value === 'url' ? 'url' : 'upload'
  form.logoMode = parsedValue
  if (parsedValue === 'url') {
    clearLogoFile()
  }
}

const formatBytes = (bytes: number) => {
  if (!bytes) return '0 KB'
  const kbValue = bytes / 1024
  if (kbValue >= 1024) {
    return `${(kbValue / 1024).toFixed(1)} MB`
  }
  return `${Math.max(1, Math.round(kbValue))} KB`
}

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
        <CardDescription>Envie uma nova arte ou informe a URL pública utilizada no painel.</CardDescription>
      </CardHeader>
      <CardContent class="space-y-6">
        <Tabs
          v-model:model-value="form.logoMode"
          class="space-y-4"
          @update:model-value="handleLogoModeChange"
        >
          <TabsList class="grid w-full grid-cols-2 rounded-full bg-muted/60 p-1">
            <TabsTrigger
              value="upload"
              class="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
            >
              Fazer upload
            </TabsTrigger>
            <TabsTrigger
              value="url"
              class="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
            >
              Usar URL
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload">
            <div class="grid items-start gap-6 md:grid-cols-[minmax(0,1fr)_220px]">
              <div class="space-y-4">
                <div
                  class="rounded-3xl border-2 border-dashed bg-muted/10 p-6 text-center shadow-sm transition hover:bg-muted/20"
                  :style="{ borderColor: form.primaryColor }"
                >
                  <UploadCloud class="mx-auto h-10 w-10 text-muted-foreground" />
                  <p class="mt-3 text-sm font-medium">PNG ou SVG com transparência</p>
                  <p class="text-xs text-muted-foreground">Sugestão: fundo transparente • até 2&nbsp;MB</p>
                  <Button class="mt-4" type="button" @click="triggerLogoUpload">Selecionar arquivo</Button>
                  <input
                    ref="fileInputRef"
                    type="file"
                    accept="image/png,image/jpeg,image/svg+xml"
                    class="sr-only"
                    @change="handleLogoFileChange"
                  />
                </div>
                <div
                  v-if="form.logoFile"
                  class="flex items-center justify-between rounded-2xl border bg-muted/40 px-4 py-2"
                >
                  <div class="min-w-0">
                    <p class="truncate text-sm font-medium">{{ form.logoFile.name }}</p>
                    <p class="text-xs text-muted-foreground">{{ formatBytes(form.logoFile.size) }}</p>
                  </div>
                  <Button variant="ghost" size="icon" class="h-8 w-8 text-muted-foreground" @click="clearLogoFile">
                    <Trash2 class="h-4 w-4" />
                  </Button>
                </div>
                <p class="text-[11px] text-muted-foreground">
                  A logo enviada substitui a atual após salvar. Para remover, limpe o campo e restaure o padrão.
                </p>
              </div>
              <div class="flex h-32 w-full items-center justify-center rounded-2xl border bg-muted/20 p-4">
                <img
                  v-if="logoPreview"
                  :src="logoPreview"
                  alt="Prévia da logo"
                  class="max-h-full object-contain"
                />
                <span v-else class="text-xs text-muted-foreground">Prévia indisponível</span>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="url">
            <div class="grid items-start gap-6 md:grid-cols-[minmax(0,1fr)_220px]">
              <div class="space-y-2">
                <label class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Logo (URL pública)
                </label>
                <Input v-model="form.logoUrl" type="url" placeholder="https://cdn.exemplo.com/logo.png" />
                <p class="text-[11px] text-muted-foreground">Utilize HTTPS e um PNG transparente hospedado no CDN.</p>
              </div>
              <div class="flex h-32 w-full items-center justify-center rounded-2xl border bg-muted/20 p-4">
                <img
                  v-if="logoPreview"
                  :src="logoPreview"
                  alt="Prévia da logo"
                  class="max-h-full object-contain"
                />
                <span v-else class="text-xs text-muted-foreground">Prévia indisponível</span>
              </div>
            </div>
          </TabsContent>
        </Tabs>
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
