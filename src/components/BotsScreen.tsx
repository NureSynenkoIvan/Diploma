import { useEffect, useMemo, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import type { StrategySummary, TradingBot } from '../services/api'
import { createOrUpdateBot, deleteBot, fetchBots, fetchStrategies } from '../services/api'

type BotFormState = {
  id?: number
  name: string
  strategyId: string
  symbols: string[]
  amount: string
  currency: string
  wallet: string
}

const DEFAULT_FORM: BotFormState = {
  name: '',
  strategyId: '',
  symbols: [''],
  amount: '',
  currency: 'USDT',
  wallet: '',
}

export function BotsScreen() {
  const { token } = useAuth()
  const [bots, setBots] = useState<TradingBot[]>([])
  const [strategies, setStrategies] = useState<StrategySummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [formState, setFormState] = useState<BotFormState>(DEFAULT_FORM)
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    if (!token) {
      return
    }

    let isMounted = true
    Promise.all([fetchBots(token), fetchStrategies(token)])
      .then(([botsData, strategiesData]) => {
        if (isMounted) {
          setBots(botsData)
          setStrategies(strategiesData)
          setFormState((current) => ({
            ...current,
            strategyId: current.strategyId || String(strategiesData[0]?.id ?? ''),
          }))
        }
      })
      .catch((error) => {
        if (isMounted) {
          const message = error instanceof Error ? error.message : 'Failed to load data'
          setErrorMessage(message)
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
  }, [token])

  const filteredBots = useMemo(
    () =>
      bots.filter(
        (bot) =>
          bot.name.toLowerCase().includes(search.toLowerCase()) ||
          bot.strategyName.toLowerCase().includes(search.toLowerCase()) ||
          bot.symbols.some((symbol) => symbol.toLowerCase().includes(search.toLowerCase())),
      ),
    [bots, search],
  )

  const handleAdd = () => {
    setFormState({ ...DEFAULT_FORM, strategyId: String(strategies[0]?.id ?? '') })
    setIsDialogOpen(true)
  }

  const handleEdit = (bot: TradingBot) => {
    setFormState({
      id: bot.id,
      name: bot.name,
      strategyId: String(bot.strategyId),
      symbols: bot.symbols.length > 0 ? bot.symbols : [''],
      amount: '',
      currency: 'USDT',
      wallet: '',
    })
    setIsDialogOpen(true)
  }

  const handleDelete = (id: number) => {
    if (!token) {
      return
    }

    setBots((previous) => previous.filter((bot) => bot.id !== id))
    void deleteBot(token, id).catch(() => {
      void fetchBots(token).then((data) => setBots(data))
    })
  }

  const handleFormSubmit = () => {
    if (!token) {
      return
    }

    const sanitizedSymbols = formState.symbols.map((symbol) => symbol.trim()).filter(Boolean)
    if (!formState.strategyId) {
      return
    }

    void createOrUpdateBot(token, {
      id: formState.id,
      name: formState.name.trim(),
      strategyId: Number(formState.strategyId),
      symbols: sanitizedSymbols,
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

  const activeStrategyMeta = strategies.find((strategy) => String(strategy.id) === formState.strategyId)
  const requiresMultipleSymbols = (activeStrategyMeta?.symbols_required ?? 1) > 1

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
                      Loading bots from API...
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
                    <td>{bot.strategyName}</td>
                    <td>{bot.symbols.join(', ')}</td>
                    <td>{new Date(bot.startedAt).toLocaleDateString()}</td>
                    <td className="muted">N/A</td>
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
                {errorMessage ? <p className="field-help field-help--error">{errorMessage}</p> : null}
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
                    value={formState.strategyId}
                    onChange={(event) => {
                      const nextStrategyId = event.target.value
                      const nextMeta = strategies.find((strategy) => String(strategy.id) === nextStrategyId)
                      const requiredSymbols = nextMeta?.symbols_required ?? 1
                      setFormState({
                        ...formState,
                        strategyId: nextStrategyId,
                        symbols: Array.from({ length: Math.max(1, requiredSymbols) }, () => ''),
                      })
                    }}
                  >
                    {strategies.map((strategy) => (
                      <option key={strategy.id} value={String(strategy.id)}>
                        {strategy.name}
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
                disabled={!formState.name.trim() || !formState.symbols[0]?.trim() || !formState.strategyId}
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

