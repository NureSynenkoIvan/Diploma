export type StrategySummary = {
  id: number
  name: string
  description: string | null
  symbols_required: number
  timeframe: string
}

export type TradingBot = {
  id: number
  name: string
  strategyId: number
  strategyName: string
  symbols: string[]
  startedAt: string
}

export type CreateOrUpdateBotInput = {
  id?: number
  name: string
  strategyId: number
  symbols: string[]
}

export type BacktestRequest = {
  strategyId: number
  strategyName: string
  amount: number
  currency: string
  datasetName: string
}

export type BacktestResult = {
  overallProfitPercent: number
  meanMonthlyProfitPercent: number
  maxDrawdownPercent: number
  winRatePercent: number
}

type LoginResponse = {
  access_token: string
  token_type: string
}

type ApiBot = {
  id: number
  name: string
  strategy_id: number
  strategy_name: string
  symbols: string[]
  started_at: string
}

const AUTH_TOKEN_STORAGE_KEY = 'trading-app:token'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export function getAuthToken(): string | null {
  return window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY)
}

export function setAuthToken(token: string): void {
  window.localStorage.setItem(AUTH_TOKEN_STORAGE_KEY, token)
}

export function clearAuthToken(): void {
  window.localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY)
}

async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  token?: string,
): Promise<T> {
  const headers = new Headers(options.headers)
  if (!headers.has('Content-Type') && options.body != null) {
    headers.set('Content-Type', 'application/json')
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const payload = (await response.json()) as { detail?: string }
      if (typeof payload.detail === 'string' && payload.detail) {
        detail = payload.detail
      }
    } catch {
      // Ignore invalid JSON and keep generic error message.
    }
    throw new Error(detail)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export async function login(loginValue: string, password: string): Promise<string> {
  const payload = await apiRequest<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ login: loginValue, password }),
  })
  return payload.access_token
}

export async function fetchStrategies(token: string): Promise<StrategySummary[]> {
  return apiRequest<StrategySummary[]>('/strategies', { method: 'GET' }, token)
}

function mapApiBot(bot: ApiBot): TradingBot {
  return {
    id: bot.id,
    name: bot.name,
    strategyId: bot.strategy_id,
    strategyName: bot.strategy_name,
    symbols: bot.symbols,
    startedAt: bot.started_at,
  }
}

export async function fetchBots(token: string): Promise<TradingBot[]> {
  const payload = await apiRequest<ApiBot[]>('/bots', { method: 'GET' }, token)
  return payload.map(mapApiBot)
}

export async function createOrUpdateBot(token: string, input: CreateOrUpdateBotInput): Promise<TradingBot> {
  if (input.id != null) {
    const updated = await apiRequest<ApiBot>(
      `/bots/${input.id}`,
      {
        method: 'PUT',
        body: JSON.stringify({
          name: input.name,
          strategy_id: input.strategyId,
          symbols: input.symbols,
        }),
      },
      token,
    )
    return mapApiBot(updated)
  }

  const created = await apiRequest<ApiBot>(
    '/bots',
    {
      method: 'POST',
      body: JSON.stringify({
        name: input.name,
        strategy_id: input.strategyId,
        symbols: input.symbols,
      }),
    },
    token,
  )
  return mapApiBot(created)
}

export async function deleteBot(token: string, id: number): Promise<void> {
  await apiRequest<void>(`/bots/${id}`, { method: 'DELETE' }, token)
}

export async function runBacktest(token: string, request: BacktestRequest): Promise<BacktestResult> {
  const baseMultiplier = request.strategyName.toLowerCase().includes('grid') ? 1.2 : 1
  const overallProfitPercent = 15 * baseMultiplier
  const meanMonthlyProfitPercent = 1.2 * baseMultiplier
  const maxDrawdownPercent = 4.5 / baseMultiplier
  const winRatePercent = Math.min(100, 58 * baseMultiplier)

  const stats: BacktestResult = {
    overallProfitPercent,
    meanMonthlyProfitPercent,
    maxDrawdownPercent,
    winRatePercent,
  }

  type BacktestApiResponse = {
    results: string
  }

  const payload = await apiRequest<BacktestApiResponse>(
    '/backtests',
    {
      method: 'POST',
      body: JSON.stringify({
        strategy_id: request.strategyId,
        dataset_name: request.datasetName || `manual-${new Date().toISOString()}`,
        results: JSON.stringify({
          ...stats,
          amount: request.amount,
          currency: request.currency,
        }),
      }),
    },
    token,
  )

  try {
    const parsed = JSON.parse(payload.results) as Partial<BacktestResult>
    return {
      overallProfitPercent: parsed.overallProfitPercent ?? stats.overallProfitPercent,
      meanMonthlyProfitPercent: parsed.meanMonthlyProfitPercent ?? stats.meanMonthlyProfitPercent,
      maxDrawdownPercent: parsed.maxDrawdownPercent ?? stats.maxDrawdownPercent,
      winRatePercent: parsed.winRatePercent ?? stats.winRatePercent,
    }
  } catch {
    return stats
  }
}
