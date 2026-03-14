import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import type { BacktestResult, StrategySummary } from '../services/api'
import { fetchStrategies, runBacktest } from '../services/api'

export function BacktestScreen() {
  const { token } = useAuth()
  const [strategies, setStrategies] = useState<StrategySummary[]>([])
  const [strategyId, setStrategyId] = useState('')
  const [amount, setAmount] = useState('1000')
  const [currency, setCurrency] = useState('USDT')
  const [datasetName, setDatasetName] = useState<string | null>(null)
  const [stats, setStats] = useState<BacktestResult | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    if (!token) {
      return
    }

    let isMounted = true
    void fetchStrategies(token)
      .then((data) => {
        if (!isMounted) {
          return
        }
        setStrategies(data)
        setStrategyId(String(data[0]?.id ?? ''))
      })
      .catch((error) => {
        if (!isMounted) {
          return
        }
        const message = error instanceof Error ? error.message : 'Failed to load strategies'
        setErrorMessage(message)
      })

    return () => {
      isMounted = false
    }
  }, [token])

  return (
    <section aria-labelledby="backtest-heading" className="page">
      <h1 id="backtest-heading" className="page-title">
        Backtest
      </h1>

      <div className="backtest-layout">
        <aside className="card backtest-sidebar">
          <h2 className="section-title">Configuration</h2>

          <form
            className="form"
            onSubmit={(event) => {
              event.preventDefault()
              if (!token) {
                return
              }

              const selectedStrategy = strategies.find((current) => String(current.id) === strategyId)
              if (!selectedStrategy) {
                setErrorMessage('Choose a strategy first')
                return
              }

              const parsedAmount = Number(amount) || 0
              setIsRunning(true)
              setErrorMessage('')
              void runBacktest(token, {
                strategyId: selectedStrategy.id,
                strategyName: selectedStrategy.name,
                amount: parsedAmount,
                currency,
                datasetName: datasetName || `manual-${new Date().toISOString()}`,
              })
                .then((result) => {
                  setStats(result)
                })
                .catch((error) => {
                  const message = error instanceof Error ? error.message : 'Backtest failed'
                  setErrorMessage(message)
                })
                .finally(() => {
                  setIsRunning(false)
                })
            }}
          >
            <label className="field">
              <span className="field-label">Strategy</span>
              <select value={strategyId} onChange={(event) => setStrategyId(event.target.value)}>
                {strategies.map((currentStrategy) => (
                  <option key={currentStrategy.id} value={String(currentStrategy.id)}>
                    {currentStrategy.name}
                  </option>
                ))}
              </select>
            </label>

            <div className="field field--inline">
              <div className="field field--flex">
                <span className="field-label">Amount of money</span>
                <input
                  type="number"
                  min={0}
                  step="0.0001"
                  value={amount}
                  onChange={(event) => setAmount(event.target.value)}
                />
              </div>
              <label className="field field--small">
                <span className="field-label sr-only">Currency</span>
                <select value={currency} onChange={(event) => setCurrency(event.target.value)}>
                  <option value="USDT">USDT</option>
                  <option value="USD">USD</option>
                  <option value="BTC">BTC</option>
                </select>
              </label>
            </div>

            <label className="field">
              <span className="field-label">Dataset</span>
              <input
                type="file"
                accept=".csv,.json"
                onChange={(event) => {
                  const file = event.target.files?.[0]
                  setDatasetName(file?.name ?? null)
                }}
              />
              <p className="field-help">
                {datasetName ? `Selected: ${datasetName}` : 'Choose a CSV or JSON file.'}
              </p>
            </label>

            <button type="submit" className="primary-button" disabled={isRunning}>
              {isRunning ? 'Running...' : 'Run backtest'}
            </button>
            {errorMessage ? <p className="field-help field-help--error">{errorMessage}</p> : null}
          </form>
        </aside>

        <div className="backtest-main">
          <div className="card backtest-chart-card">
            <h2 className="section-title">Equity curve</h2>
            <div className="chart-placeholder" aria-label="Backtest equity chart">
              <div className="chart-line" />
            </div>
          </div>

          <div className="backtest-bottom">
            <div className="card backtest-summary-card">
              <h2 className="section-title">Summary</h2>
              <dl className="stats-grid">
                <div>
                  <dt>Overall profit</dt>
                  <dd>
                    {stats ? `${stats.overallProfitPercent.toFixed(1)}%` : '—'}
                  </dd>
                </div>
                <div>
                  <dt>Mean profit by month</dt>
                  <dd>
                    {stats ? `${stats.meanMonthlyProfitPercent.toFixed(2)}%` : '—'}
                  </dd>
                </div>
                <div>
                  <dt>Max drawdown</dt>
                  <dd>
                    {stats ? `${stats.maxDrawdownPercent.toFixed(1)}%` : '—'}
                  </dd>
                </div>
                <div>
                  <dt>Win rate</dt>
                  <dd>{stats ? `${stats.winRatePercent.toFixed(0)}%` : '—'}</dd>
                </div>
              </dl>
            </div>

            <aside className="card backtest-notes-card">
              <h2 className="section-title">Additional info</h2>
              <p className="muted">
                This screen is now connected to the backend API. The submitted run is persisted as a
                backtest record and the summary is read from stored results.
              </p>
            </aside>
          </div>
        </div>
      </div>
    </section>
  )
}

