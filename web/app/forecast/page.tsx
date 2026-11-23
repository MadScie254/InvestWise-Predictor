"use client"

import { useState } from "react"
import { Chart } from "@/components/Chart"
import { INSTRUMENTS } from "@/lib/instruments"
import { formatDay, formatNumber, formatPercent, formatQuote, toneClass } from "@/lib/format"
import { saveForecast } from "@/lib/local-desk"
import type { ForecastView, ModelId } from "@/lib/types"

type Payload = {
  symbol: string
  name: string
  currency: string
  asOf: string
  focus: ForecastView
  peers: Array<Pick<ForecastView, "model" | "label" | "changePct" | "projected" | "backtest" | "reading">>
}

const MODELS: Array<{ id: ModelId; label: string }> = [
  { id: "holt", label: "Sequence smoothing" },
  { id: "boost", label: "Boosted stumps" },
  { id: "forest", label: "Random forest" },
]

export default function ForecastPage() {
  const [symbol, setSymbol] = useState(INSTRUMENTS[0].symbol)
  const [model, setModel] = useState<ModelId>("holt")
  const [horizon, setHorizon] = useState(20)
  const [result, setResult] = useState<Payload | null>(null)
  const [error, setError] = useState("")
  const [pending, setPending] = useState(false)
  const [kept, setKept] = useState(false)

  async function run(event: React.FormEvent) {
    event.preventDefault()
    setPending(true)
    setError("")
    setKept(false)
    try {
      const response = await fetch(`/api/forecast?symbol=${encodeURIComponent(symbol)}&model=${model}&horizon=${horizon}`)
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || "The forecast did not run.")
      setResult(data)
    } catch (cause) {
      setResult(null)
      setError(cause instanceof Error ? cause.message : "The forecast did not run.")
    } finally {
      setPending(false)
    }
  }

  function keep() {
    if (!result) return
    saveForecast({
      id: crypto.randomUUID(),
      symbol: result.symbol,
      label: result.name,
      model: result.focus.label,
      horizon: result.focus.horizon,
      changePct: result.focus.changePct,
      savedAt: new Date().toISOString(),
    })
    setKept(true)
  }

  const rows = result ? [result.focus, ...result.peers] : []

  return (
    <section>
      <div className="section-head">
        <h1>Forecast</h1>
        <p>
          Pick a series with a long public history. Nairobi share quotes are on the markets page. They are not forecast here, because the free board does not publish enough daily history to train a model honestly.
        </p>
      </div>
      <form className="form" onSubmit={run}>
        <label className="field">
          <span>Series</span>
          <select value={symbol} onChange={(event) => setSymbol(event.target.value)}>
            {INSTRUMENTS.map((item) => (
              <option key={item.symbol} value={item.symbol}>{item.name}</option>
            ))}
          </select>
        </label>
        <fieldset className="field" style={{ border: 0, padding: 0, margin: 0 }}>
          <span>Model</span>
          <div className="choices">
            {MODELS.map((item) => (
              <label key={item.id}>
                <input type="radio" name="model" checked={model === item.id} onChange={() => setModel(item.id)} />
                {item.label}
              </label>
            ))}
          </div>
        </fieldset>
        <fieldset className="field" style={{ border: 0, padding: 0, margin: 0 }}>
          <span>Sessions ahead</span>
          <div className="choices">
            {[10, 20, 40].map((value) => (
              <label key={value}>
                <input type="radio" name="horizon" checked={horizon === value} onChange={() => setHorizon(value)} />
                {value}
              </label>
            ))}
          </div>
        </fieldset>
        <button className="button" type="submit" disabled={pending}>{pending ? "Running" : "Run forecast"}</button>
      </form>
      {error ? <p className="error">{error}</p> : null}
      {result ? (
        <div>
          <p className="pair">{result.name}, {result.focus.label}</p>
          <p className="quote-num">{formatQuote(result.focus.projected, result.currency)}</p>
          <p className={`delta ${toneClass(result.focus.changePct)}`}>
            {formatPercent(result.focus.changePct)} from {formatQuote(result.focus.last, result.currency)} on {formatDay(result.asOf)}
          </p>
          <Chart
            history={result.focus.history}
            forecast={result.focus.path}
            low={result.focus.low}
            high={result.focus.high}
            currency={result.currency}
          />
          <p className="caption">{result.focus.note} {result.focus.reading}</p>
          <p className="caption">
            On the last {result.focus.backtest.samples} one-step checks, direction landed {formatNumber(result.focus.backtest.directionHit * 100, 0)}% of the time. Typical miss was {formatNumber(result.focus.backtest.mape * 100)}% of the price.
          </p>
          <div className="actions">
            <button className="button quiet" type="button" onClick={keep}>{kept ? "Kept on this browser" : "Keep this forecast"}</button>
          </div>
          <table>
            <thead>
              <tr>
                <th>Model</th>
                <th className="right">Projected</th>
                <th className="right">Change</th>
                <th className="right">Direction hit</th>
                <th className="right">Typical miss</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.model}>
                  <td>{row.label}</td>
                  <td className="right">{formatQuote(row.projected, result.currency)}</td>
                  <td className={`right ${toneClass(row.changePct)}`}>{formatPercent(row.changePct)}</td>
                  <td className="right">{formatNumber(row.backtest.directionHit * 100, 0)}%</td>
                  <td className="right">{formatNumber(row.backtest.mape * 100)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  )
}
