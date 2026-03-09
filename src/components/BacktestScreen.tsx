import { useState } from 'react'
import type { BacktestResult } from '../services/mockApi'
import { runBacktest } from '../services/mockApi'

const BACKTEST_STRATEGIES = ['BLSH BTC', 'Grid URUS', 'Pairs Trading', 'Mean Reversion']

export function BacktestScreen() {
  const [strategy, setStrategy] = useState(BACKTEST_STRATEGIES[0] ?? '')
  const [amount, setAmount] = useState('1000')
  const [currency, setCurrency] = useState('USDT')
  const [datasetName, setDatasetName] = useState<string | null>(null)
  const [stats, setStats] = useState<BacktestResult | null>(null)
  const [isRunning, setIsRunning] = useState(false)

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
              const parsedAmount = Number(amount) || 0
              setIsRunning(true)
              void runBacktest({ strategy, amount: parsedAmount, currency }).then((result) => {
                setStats(result)
                setIsRunning(false)
              })
            }}
          >
            <label className="field">
              <span className="field-label">Strategy</span>
              <select value={strategy} onChange={(event) => setStrategy(event.target.value)}>
                {BACKTEST_STRATEGIES.map((currentStrategy) => (
                  <option key={currentStrategy} value={currentStrategy}>
                    {currentStrategy}
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
              {isRunning ? 'Running…' : 'Run backtest (mock)'}
            </button>
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
                This is a mocked backtest. Once the backend is connected, this area will display detailed
                statistics about trades, risk metrics, and strategy behaviour over time.
              </p>
            </aside>
          </div>
        </div>
      </div>
    </section>
  )
}

