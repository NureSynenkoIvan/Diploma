import { useEffect, useMemo, useState } from 'react'
import type { TradingBot } from '../services/mockApi'
import { createOrUpdateBot, deleteBot, fetchBots } from '../services/mockApi'

type BotFormState = {
  id?: number
  name: string
  strategy: string
  symbols: string[]
  amount: string
  currency: string
  wallet: string
}

const STRATEGIES = [
  { id: 'blsh-btc', label: 'BLSH BTC', requiresMultipleSymbols: false },
  { id: 'grid-urus', label: 'Grid URUS', requiresMultipleSymbols: true },
  { id: 'pairs', label: 'Pairs Trading', requiresMultipleSymbols: true },
]

const DEFAULT_FORM: BotFormState = {
  name: '',
  strategy: STRATEGIES[0]?.id ?? '',
  symbols: [''],
  amount: '',
  currency: 'USDT',
  wallet: '',
}

export function BotsScreen() {
  const [bots, setBots] = useState<TradingBot[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [formState, setFormState] = useState<BotFormState>(DEFAULT_FORM)

  useEffect(() => {
    let isMounted = true
    fetchBots()
      .then((data) => {
        if (isMounted) {
          setBots(data)
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false)
        }
      })

    return () => {
      isMounted = false
    }
  }, [])

  const filteredBots = useMemo(
    () =>
      bots.filter(
        (bot) =>
          bot.name.toLowerCase().includes(search.toLowerCase()) ||
          bot.strategy.toLowerCase().includes(search.toLowerCase()) ||
          bot.symbol.toLowerCase().includes(search.toLowerCase()),
      ),
    [bots, search],
  )

  const handleAdd = () => {
    setFormState(DEFAULT_FORM)
    setIsDialogOpen(true)
  }

  const handleEdit = (bot: TradingBot) => {
    setFormState({
      id: bot.id,
      name: bot.name,
      strategy:
        STRATEGIES.find((strategy) => strategy.label === bot.strategy)?.id ?? STRATEGIES[0]?.id ?? '',
      symbols: [bot.symbol],
      amount: '',
      currency: 'USDT',
      wallet: '',
    })
    setIsDialogOpen(true)
  }

  const handleDelete = (id: number) => {
    setBots((previous) => previous.filter((bot) => bot.id !== id))
    void deleteBot(id)
  }

  const handleFormSubmit = () => {
    const primarySymbol = formState.symbols[0] ?? ''
    const strategyLabel =
      STRATEGIES.find((strategy) => strategy.id === formState.strategy)?.label ?? formState.strategy

    const payloadName = `${formState.name} ${primarySymbol}`.trim()

    void createOrUpdateBot({
      id: formState.id,
      name: payloadName,
      strategy: strategyLabel,
      symbol: primarySymbol,
    }).then((saved) => {
      setBots((previous) => {
        const exists = previous.some((bot) => bot.id === saved.id)
        return exists
          ? previous.map((bot) => (bot.id === saved.id ? saved : bot))
          : [...previous, saved]
      })
    })

    setIsDialogOpen(false)
  }

  const activeStrategyMeta = STRATEGIES.find((strategy) => strategy.id === formState.strategy)
  const requiresMultipleSymbols = activeStrategyMeta?.requiresMultipleSymbols ?? false

  return (
    <section aria-labelledby="bots-heading" className="page">
      <div className="page-header">
        <h1 id="bots-heading">Bots</h1>
        <div className="page-header-actions">
          <button type="button" className="primary-button" onClick={handleAdd}>
            Add
          </button>
          <input
            type="search"
            placeholder="Search bots..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="search-input"
            aria-label="Search bots"
          />
        </div>
      </div>

      <div className="card table-card">
        <div className="table-wrapper" role="region" aria-label="Trading bots">
          <table className="data-table">
            <thead>
              <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th scope="col">Strategy</th>
                <th scope="col">Symbol</th>
                <th scope="col">Started</th>
                <th scope="col">Profit</th>
                <th scope="col" />
              </tr>
            </thead>
            <tbody>
              {filteredBots.length === 0 ? (
                isLoading ? (
                  <tr>
                    <td colSpan={7} className="table-empty">
                      Loading bots from mock API…
                    </td>
                  </tr>
                ) : (
                <tr>
                  <td colSpan={7} className="table-empty">
                    No bots match your search.
                  </td>
                </tr>
                )
              ) : (
                filteredBots.map((bot, index) => (
                  <tr key={bot.id}>
                    <td>{index + 1}</td>
                    <td>{bot.name}</td>
                    <td>{bot.strategy}</td>
                    <td>{bot.symbol}</td>
                    <td>{new Date(bot.startedAt).toLocaleDateString()}</td>
                    <td className={bot.profitPercent >= 0 ? 'profit-positive' : 'profit-negative'}>
                      {bot.profitPercent.toFixed(1)}%
                    </td>
                    <td className="table-actions">
                      <button type="button" onClick={() => handleEdit(bot)} className="ghost-button">
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(bot.id)}
                        className="ghost-button ghost-button--danger"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {isDialogOpen && (
        <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="bot-form-title">
          <div className="modal">
            <div className="modal-header">
              <h2 id="bot-form-title">{formState.id ? 'Edit bot' : 'Create bot'}</h2>
              <button
                type="button"
                className="icon-button"
                aria-label="Close"
                onClick={() => setIsDialogOpen(false)}
              >
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="form-grid">
                <label className="field">
                  <span className="field-label">Name</span>
                  <input
                    type="text"
                    value={formState.name}
                    onChange={(event) => setFormState({ ...formState, name: event.target.value })}
                  />
                </label>

                <label className="field">
                  <span className="field-label">Strategy</span>
                  <select
                    value={formState.strategy}
                    onChange={(event) => {
                      const nextStrategy = event.target.value
                      const nextMeta = STRATEGIES.find((strategy) => strategy.id === nextStrategy)
                      const needsMultiple = nextMeta?.requiresMultipleSymbols ?? false
                      setFormState({
                        ...formState,
                        strategy: nextStrategy,
                        symbols: needsMultiple ? ['', ''] : [''],
                      })
                    }}
                  >
                    {STRATEGIES.map((strategy) => (
                      <option key={strategy.id} value={strategy.id}>
                        {strategy.label}
                      </option>
                    ))}
                  </select>
                  <p className="field-help">
                    {requiresMultipleSymbols
                      ? 'This strategy requires several symbols.'
                      : 'This strategy uses a single symbol.'}
                  </p>
                </label>

                <div className="field">
                  <span className="field-label">
                    Symbol{requiresMultipleSymbols ? 's' : ''}
                  </span>
                  {formState.symbols.map((symbol, index) => (
                    <input
                      key={index}
                      type="text"
                      value={symbol}
                      onChange={(event) => {
                        const nextSymbols = [...formState.symbols]
                        nextSymbols[index] = event.target.value.toUpperCase()
                        setFormState({ ...formState, symbols: nextSymbols })
                      }}
                      placeholder={index === 0 ? 'e.g. BTC' : 'Additional symbol'}
                    />
                  ))}
                  {requiresMultipleSymbols && (
                    <button
                      type="button"
                      className="ghost-button ghost-button--small"
                      onClick={() =>
                        setFormState({
                          ...formState,
                          symbols: [...formState.symbols, ''],
                        })
                      }
                    >
                      Add symbol
                    </button>
                  )}
                </div>

                <div className="field field--inline">
                  <div className="field field--flex">
                    <span className="field-label">Money</span>
                    <input
                      type="number"
                      min={0}
                      step="0.0001"
                      value={formState.amount}
                      onChange={(event) =>
                        setFormState({
                          ...formState,
                          amount: event.target.value,
                        })
                      }
                    />
                  </div>
                  <label className="field field--small">
                    <span className="field-label sr-only">Currency</span>
                    <select
                      value={formState.currency}
                      onChange={(event) =>
                        setFormState({
                          ...formState,
                          currency: event.target.value,
                        })
                      }
                    >
                      <option value="USDT">USDT</option>
                      <option value="USD">USD</option>
                      <option value="BTC">BTC</option>
                    </select>
                  </label>
                </div>

                <label className="field field--full">
                  <span className="field-label">Crypto wallet (TBD)</span>
                  <input
                    type="text"
                    placeholder="Will be wired to a real wallet later"
                    value={formState.wallet}
                    onChange={(event) =>
                      setFormState({
                        ...formState,
                        wallet: event.target.value,
                      })
                    }
                  />
                </label>
              </div>
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="ghost-button"
                onClick={() => setIsDialogOpen(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="primary-button"
                onClick={handleFormSubmit}
                disabled={!formState.name.trim() || !formState.symbols[0]?.trim()}
              >
                Save bot
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}

