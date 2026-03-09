export type TradingBot = {
  id: number
  name: string
  strategy: string
  symbol: string
  startedAt: string
  profitPercent: number
}

export type CreateOrUpdateBotInput = {
  id?: number
  name: string
  strategy: string
  symbol: string
}

export type BacktestRequest = {
  strategy: string
  amount: number
  currency: string
}

export type BacktestResult = {
  overallProfitPercent: number
  meanMonthlyProfitPercent: number
  maxDrawdownPercent: number
  winRatePercent: number
}

let botsStore: TradingBot[] = [
  {
    id: 1,
    name: 'Bot‑1 BTC',
    strategy: 'BLSH BTC',
    symbol: 'BTC',
    startedAt: '2026-06-01',
    profitPercent: 11,
  },
  {
    id: 2,
    name: 'Bot‑2 ETH',
    strategy: 'Grid URUS',
    symbol: 'ETH',
    startedAt: '2026-06-07',
    profitPercent: 20,
  },
]

function simulateLatency<T>(value: T, delay = 400): Promise<T> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(structuredClone(value)), delay)
  })
}

export async function fetchBots(): Promise<TradingBot[]> {
  return simulateLatency(botsStore)
}

export async function createOrUpdateBot(input: CreateOrUpdateBotInput): Promise<TradingBot> {
  if (input.id != null) {
    botsStore = botsStore.map((bot) =>
      bot.id === input.id
        ? {
            ...bot,
            name: input.name,
            strategy: input.strategy,
            symbol: input.symbol,
          }
        : bot,
    )
    const updated = botsStore.find((bot) => bot.id === input.id)
    return simulateLatency(updated as TradingBot)
  }

  const nextId = botsStore.reduce((maxId, bot) => Math.max(maxId, bot.id), 0) + 1
  const newBot: TradingBot = {
    id: nextId,
    name: input.name,
    strategy: input.strategy,
    symbol: input.symbol,
    startedAt: new Date().toISOString().slice(0, 10),
    profitPercent: 0,
  }

  botsStore = [...botsStore, newBot]
  return simulateLatency(newBot)
}

export async function deleteBot(id: number): Promise<void> {
  botsStore = botsStore.filter((bot) => bot.id !== id)
  return simulateLatency(undefined)
}

export async function runBacktest(request: BacktestRequest): Promise<BacktestResult> {
  const baseMultiplier = request.strategy.includes('Grid') ? 1.2 : 1
  const overallProfitPercent = 15 * baseMultiplier
  const meanMonthlyProfitPercent = 1.2 * baseMultiplier
  const maxDrawdownPercent = 4.5 / baseMultiplier
  const winRatePercent = 58 * baseMultiplier

  return simulateLatency({
    overallProfitPercent,
    meanMonthlyProfitPercent,
    maxDrawdownPercent,
    winRatePercent,
  })
}

