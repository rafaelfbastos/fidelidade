<script setup lang="ts">
import { computed, type Component } from 'vue'
import {
  ArrowUpRight,
  BarChart3,
  Bell,
  ChevronDown,
  CircleDollarSign,
  Gift,
  Sparkles,
  TrendingUp,
  Users,
} from 'lucide-vue-next'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'

interface StatCard {
  title: string
  value: string
  change: string
  icon: Component
}

interface WeeklyPoint {
  label: string
  value: number
}

interface Campaign {
  name: string
  description: string
  audience: string
  conversion: string
  status: string
}

interface Reward {
  name: string
  requirement: string
  redemption: string
  status: string
}

interface LoyaltyTier {
  name: string
  members: string
  progress: number
  target: string
}

type TransactionStatus = 'creditado' | 'pendente' | 'estornado'

interface Transaction {
  customer: string
  tier: string
  purchase: string
  points: string
  status: TransactionStatus
}

interface TopCustomer {
  name: string
  tier: string
  points: string
  growth: string
}

const statCards: StatCard[] = [
  {
    title: 'Clientes ativos',
    value: '24.582',
    change: '+8% vs. mês anterior',
    icon: Users,
  },
  {
    title: 'Pontos emitidos',
    value: '3,2M',
    change: '+112k nesta semana',
    icon: Sparkles,
  },
  {
    title: 'Trocas concluídas',
    value: '1.486',
    change: '-3% vs. última semana',
    icon: Gift,
  },
  {
    title: 'Ticket médio',
    value: 'R$ 268',
    change: '+12% após campanhas',
    icon: CircleDollarSign,
  },
]

const weeklyEngagement: WeeklyPoint[] = [
  { label: 'Seg', value: 180 },
  { label: 'Ter', value: 210 },
  { label: 'Qua', value: 240 },
  { label: 'Qui', value: 230 },
  { label: 'Sex', value: 260 },
  { label: 'Sab', value: 220 },
  { label: 'Dom', value: 195 },
]

const campaigns: Campaign[] = [
  {
    name: 'Cashback Weekend',
    description: 'Bônus de 5% em compras acima de R$ 300',
    audience: 'Segmento Ouro',
    conversion: '14% conversão',
    status: 'Ativa',
  },
  {
    name: 'Upgrade Expresso',
    description: 'Upgrade automático no tier após 3 pedidos',
    audience: 'Base completa',
    conversion: '1.240 clientes impactados',
    status: 'Em teste',
  },
]

const rewards: Reward[] = [
  {
    name: 'Delivery ilimitado',
    requirement: '15k pontos acumulados',
    redemption: '32 resgates na semana',
    status: 'Premium',
  },
  {
    name: 'Gift Card parceiros',
    requirement: '8k pontos',
    redemption: '58 conversões recentes',
    status: 'Alta demanda',
  },
]

const loyaltyTiers: LoyaltyTier[] = [
  { name: 'Essencial', members: '12.540 membros', progress: 72, target: 'Meta mensal: +3.5k cadastros' },
  { name: 'Ouro', members: '8.430 membros', progress: 64, target: 'Meta mensal: +1.2k upgrades' },
  { name: 'Diamante', members: '3.612 membros', progress: 41, target: 'Meta mensal: +650 upsells' },
]

const transactions: Transaction[] = [
  { customer: 'Larissa Santos', tier: 'Diamante', purchase: 'R$ 982,10', points: '+4.912 pts', status: 'creditado' },
  { customer: 'Diego Fernandes', tier: 'Ouro', purchase: 'R$ 458,40', points: '+1.386 pts', status: 'pendente' },
  { customer: 'Helena Costa', tier: 'Essencial', purchase: 'R$ 180,00', points: 'Troca realizada', status: 'creditado' },
  { customer: 'Ricardo Lima', tier: 'Ouro', purchase: 'R$ 264,80', points: '+864 pts', status: 'creditado' },
  { customer: 'Bianca Martins', tier: 'Diamante', purchase: 'Estornado', points: '-420 pts', status: 'estornado' },
]

const topCustomers: TopCustomer[] = [
  { name: 'Erika Souza', tier: 'Diamante', points: '64.580 pts', growth: '+420 pts' },
  { name: 'Marcos Alves', tier: 'Ouro', points: '48.230 pts', growth: '+310 pts' },
  { name: 'Camila Ribeiro', tier: 'Diamante', points: '39.100 pts', growth: '+610 pts' },
  { name: 'Rafael Porto', tier: 'Ouro', points: '33.480 pts', growth: '+190 pts' },
  { name: 'João Ricardo', tier: 'Essencial', points: '21.700 pts', growth: '+260 pts' },
]

const statusLabel: Record<TransactionStatus, string> = {
  creditado: 'Creditado',
  pendente: 'Pendente',
  estornado: 'Estornado',
}

const chartLinePoints = computed(() => {
  if (!weeklyEngagement.length) return ''
  const maxValue = Math.max(...weeklyEngagement.map((point) => point.value), 1)
  const step = weeklyEngagement.length > 1 ? 100 / (weeklyEngagement.length - 1) : 0
  return weeklyEngagement
    .map((point, index) => {
      const x = Number((index * step).toFixed(2))
      const normalized = (point.value / maxValue) * 70
      const y = Number((100 - normalized - 10).toFixed(2))
      return `${x},${y}`
    })
    .join(' ')
})

const chartPointList = computed(() => (chartLinePoints.value ? chartLinePoints.value.split(' ') : []))

const chartAreaPoints = computed(() => {
  if (!chartLinePoints.value) return ''
  return `0,100 ${chartLinePoints.value} 100,100`
})

const getTrendColor = (change: string) =>
  change.startsWith('-') ? 'text-destructive' : 'text-emerald-600 dark:text-emerald-400'

const getStatusVariant = (status: TransactionStatus) => {
  if (status === 'creditado') return 'secondary'
  if (status === 'pendente') return 'outline'
  return 'destructive'
}

const getCampaignVariant = (status: string) => {
  if (status === 'Ativa') return 'secondary'
  if (status === 'Em teste') return 'outline'
  return 'default'
}

const getInitials = (name: string) =>
  name
    .split(' ')
    .map((part) => part[0])
    .filter(Boolean)
    .join('')
    .slice(0, 2)
    .toUpperCase()
</script>

<template>
  <main class="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-10 lg:px-6">
    <section class="flex flex-wrap items-center justify-between gap-4 rounded-3xl border border-white/60 bg-white p-6 shadow-md">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.3em] text-muted-foreground">Programa fidelidade+</p>
        <h1 class="mt-2 text-3xl font-semibold tracking-tight">Painel de desempenho</h1>
        <p class="text-sm text-muted-foreground">
          Acompanhe clientes, campanhas e recompensas conectadas à sua API proprietária.
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <Input type="search" placeholder="Buscar clientes ou campanhas" class="w-full min-w-[220px] max-w-xs" />
        <Button variant="outline" size="icon">
          <Bell class="h-4 w-4" />
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger>
            <Button variant="secondary" class="gap-2">
              <Avatar class="h-6 w-6">
                <AvatarFallback>FS</AvatarFallback>
              </Avatar>
              Equipe Fidelidade
              <ChevronDown class="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent class="w-56" align="end">
            <DropdownMenuLabel>Conta</DropdownMenuLabel>
            <DropdownMenuItem>Perfil</DropdownMenuItem>
            <DropdownMenuItem>Integrações</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Preferências</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        <Button class="gap-2">
          <Sparkles class="h-4 w-4" />
          Nova campanha
        </Button>
      </div>
    </section>

    <section class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card
        v-for="card in statCards"
        :key="card.title"
        class="rounded-3xl border border-white/60 bg-white shadow-md transition hover:-translate-y-0.5 hover:shadow-lg"
      >
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">{{ card.title }}</CardTitle>
          <div class="rounded-full bg-primary/10 p-2 text-primary">
            <component :is="card.icon" class="h-4 w-4" />
          </div>
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-semibold">{{ card.value }}</div>
          <p :class="cn('text-xs font-medium', getTrendColor(card.change))">{{ card.change }}</p>
        </CardContent>
      </Card>
    </section>

    <section class="grid gap-4 lg:grid-cols-3">
      <Card class="lg:col-span-2 rounded-3xl border border-white/60 bg-white shadow-md">
        <CardHeader class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle>Engajamento semanal</CardTitle>
            <CardDescription>Taxa média de 68% dos clientes ativos utilizando algum benefício.</CardDescription>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <Badge variant="outline" class="gap-1 text-xs">
              <BarChart3 class="h-3.5 w-3.5" />
              Atualizado há 2h
            </Badge>
            <Button variant="ghost" size="sm" class="gap-1 text-muted-foreground">
              Relatórios
              <ArrowUpRight class="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent class="space-y-6">
          <div class="h-48 w-full rounded-2xl bg-muted/40 p-4">
            <svg viewBox="0 0 100 100" class="h-full w-full" preserveAspectRatio="none">
              <defs>
                <linearGradient id="chartStroke" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stop-color="currentColor" stop-opacity="0.9" />
                  <stop offset="100%" stop-color="currentColor" stop-opacity="0.3" />
                </linearGradient>
              </defs>
              <polygon
                v-if="chartAreaPoints"
                :points="chartAreaPoints"
                fill="url(#chartStroke)"
                fill-opacity="0.2"
              />
              <polyline
                v-if="chartLinePoints"
                :points="chartLinePoints"
                fill="none"
                stroke="url(#chartStroke)"
                stroke-width="2.5"
                stroke-linecap="round"
              />
              <circle
                v-for="(point, index) in chartPointList"
                :key="`point-${index}`"
                :cx="point.split(',')[0]"
                :cy="point.split(',')[1]"
                r="1.6"
                class="fill-primary"
                stroke="white"
                stroke-width="0.5"
              />
            </svg>
          </div>
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div v-for="day in weeklyEngagement" :key="day.label">
              <p class="text-sm text-muted-foreground">{{ day.label }}</p>
              <p class="text-lg font-semibold">{{ day.value }} interações</p>
            </div>
          </div>

          <Tabs default-value="campanhas" class="space-y-4">
            <TabsList class="grid w-full grid-cols-2 rounded-full bg-muted/70">
              <TabsTrigger value="campanhas">Campanhas</TabsTrigger>
              <TabsTrigger value="recompensas">Recompensas</TabsTrigger>
            </TabsList>
            <TabsContent value="campanhas" class="space-y-3">
              <div
                v-for="campaign in campaigns"
                :key="campaign.name"
                class="rounded-2xl border border-border/60 bg-background/80 p-4 shadow-sm"
              >
                <div class="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p class="font-medium">{{ campaign.name }}</p>
                    <p class="text-sm text-muted-foreground">{{ campaign.description }}</p>
                  </div>
                  <Badge :variant="getCampaignVariant(campaign.status)">{{ campaign.status }}</Badge>
                </div>
                <div class="mt-3 flex flex-wrap gap-3 text-xs text-muted-foreground">
                  <span>{{ campaign.audience }}</span>
                  <span class="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
                    <TrendingUp class="h-3 w-3" />
                    {{ campaign.conversion }}
                  </span>
                </div>
              </div>
            </TabsContent>
            <TabsContent value="recompensas" class="space-y-3">
              <div
                v-for="reward in rewards"
                :key="reward.name"
                class="rounded-2xl border border-border/60 bg-background/80 p-4 shadow-sm"
              >
                <div class="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p class="font-medium">{{ reward.name }}</p>
                    <p class="text-sm text-muted-foreground">{{ reward.requirement }}</p>
                  </div>
                  <Badge variant="outline">{{ reward.status }}</Badge>
                </div>
                <p class="mt-3 text-xs text-muted-foreground">{{ reward.redemption }}</p>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <Card class="rounded-3xl border border-white/60 bg-white shadow-md">
        <CardHeader>
          <CardTitle>Metas por nível</CardTitle>
          <CardDescription>Distribuição dos clientes ativos por categoria.</CardDescription>
        </CardHeader>
        <CardContent class="space-y-5">
          <div v-for="tier in loyaltyTiers" :key="tier.name" class="space-y-2">
            <div class="flex items-center justify-between text-sm">
              <p class="font-medium">{{ tier.name }}</p>
              <span class="text-muted-foreground">{{ tier.members }}</span>
            </div>
            <Progress :model-value="tier.progress" />
            <p class="text-xs text-muted-foreground">{{ tier.target }}</p>
          </div>
        </CardContent>
        <CardFooter class="flex items-center gap-3">
          <Badge variant="secondary" class="gap-1">
            <Sparkles class="h-3.5 w-3.5" />
            Automação ativa
          </Badge>
          <p class="text-sm text-muted-foreground">Clientes elegíveis recebem upgrade automático.</p>
        </CardFooter>
      </Card>
    </section>

    <section class="grid gap-4 lg:grid-cols-3">
      <Card class="lg:col-span-2 rounded-3xl border border-white/60 bg-white shadow-md">
        <CardHeader class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle>Transações recentes</CardTitle>
            <CardDescription>Principais eventos sincronizados com a API nas últimas 24 horas.</CardDescription>
          </div>
          <div class="flex items-center gap-2">
            <Button variant="outline" size="sm">Exportar</Button>
            <Button size="sm" class="gap-1">
              Sincronizar
              <ArrowUpRight class="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent class="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Cliente</TableHead>
                <TableHead>Nível</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Pontos</TableHead>
                <TableHead class="text-right">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="transaction in transactions" :key="transaction.customer">
                <TableCell class="font-medium">{{ transaction.customer }}</TableCell>
                <TableCell>{{ transaction.tier }}</TableCell>
                <TableCell>{{ transaction.purchase }}</TableCell>
                <TableCell>{{ transaction.points }}</TableCell>
                <TableCell class="text-right">
                  <Badge :variant="getStatusVariant(transaction.status)" class="capitalize">
                    {{ statusLabel[transaction.status] }}
                  </Badge>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
        <CardFooter>
          <Button variant="ghost" class="gap-1 text-muted-foreground">
            Ver todas
            <ChevronDown class="h-4 w-4" />
          </Button>
        </CardFooter>
      </Card>

      <Card class="rounded-3xl border border-white/60 bg-white shadow-md">
        <CardHeader>
          <CardTitle>Clientes destaque</CardTitle>
          <CardDescription>Membros com maior propensão à recompra.</CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea class="h-[360px] pr-3">
            <div class="space-y-4">
              <div v-for="(customer, index) in topCustomers" :key="customer.name" class="space-y-3">
                <div class="flex items-center gap-3">
                  <Avatar class="h-10 w-10">
                    <AvatarFallback>{{ getInitials(customer.name) }}</AvatarFallback>
                  </Avatar>
                  <div>
                    <p class="font-medium">{{ customer.name }}</p>
                    <p class="text-xs text-muted-foreground">{{ customer.tier }} • {{ customer.points }}</p>
                  </div>
                  <Badge variant="outline" class="ml-auto text-xs">{{ customer.growth }}</Badge>
                </div>
                <Separator v-if="index !== topCustomers.length - 1" />
              </div>
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </section>
  </main>
</template>
