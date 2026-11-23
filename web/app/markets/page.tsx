"use client"

import { useEffect, useMemo, useState } from "react"
import { Chart } from "@/components/Chart"
import { INSTRUMENTS } from "@/lib/instruments"
import { formatCompact, formatDay, formatNumber, formatPercent, formatQuote, toneClass } from "@/lib/format"
import { loadPins, savePins } from "@/lib/local-desk"
import type { Board, BoardRow, MacroSeries, Series } from "@/lib/types"

export default function MarketsPage() {
  const [symbol, setSymbol] = useState(INSTRUMENTS[0].symbol)
  const [series, setSeries] = useState<Series | null>(null)
  const [seriesError, setSeriesError] = useState("")
  const [board, setBoard] = useState<Board | null>(null)
  const [macro, setMacro] = useState<MacroSeries[] | null>(null)
  const [query, setQuery] = useState("")
  const [picked, setPicked] = useState<BoardRow | null>(null)
  const [pins, setPins] = useState<string[]>([])

  useEffect(() => {
    setPins(loadPins())
    fetch("/api/board").then((response) => response.json()).then(setBoard).catch(() => setBoard(null))
    fetch("/api/macro").then((response) => response.json()).then((data) => {
      if (Array.isArray(data)) setMacro(data)
    }).catch(() => setMacro(null))
  }, [])

  useEffect(() => {
    let cancel = false
    setSeriesError("")
    fetch(`/api/series?symbol=${encodeURIComponent(symbol)}&tail=520`)
      .then(async (response) => {
        const data = await response.json()
        if (!response.ok) throw new Error(data.error || "The series did not load.")
        return data as Series
      })
      .then((data) => { if (!cancel) setSeries(data) })
      .catch((error: Error) => { if (!cancel) setSeriesError(error.message) })
    return () => { cancel = true }
  }, [symbol])

  const rows = useMemo(() => {
    const list = board?.rows || []
    const needle = query.trim().toLowerCase()
    return list
      .filter((row) => !needle || row.ticker.toLowerCase().includes(needle) || row.name.toLowerCase().includes(needle))
      .slice()
      .sort((a, b) => (b.volume || 0) - (a.volume || 0))
  }, [board, query])

  const pinnedRows = (board?.rows || []).filter((row) => pins.includes(row.ticker))

  function togglePin(ticker: string) {
    const next = pins.includes(ticker) ? pins.filter((item) => item !== ticker) : [...pins, ticker].slice(0, 8)
    setPins(next)
    savePins(next)
  }

  return (
    <section>
      <div className="section-head">
        <h1>Markets</h1>
        <p>
          Rates and commodities are daily closes. The Nairobi board is a delayed public list. When the live page does not answer, the last captured session stays on the desk and is marked as such.
        </p>
      </div>

      <div className="desk">
        <div className="rail">
          {INSTRUMENTS.map((item) => (
            <button key={item.symbol} type="button" aria-pressed={item.symbol === symbol} onClick={() => setSymbol(item.symbol)}>
              {item.short}
              <small>{item.venue}</small>
            </button>
          ))}
        </div>
        <div>
          {seriesError ? <p className="error">{seriesError}</p> : null}
          {series ? (
            <>
              <p className="pair">{series.name}</p>
              <p className="quote-num">{formatQuote(series.last, series.currency)}</p>
              <p className={`delta ${toneClass(series.change)}`}>
                {formatPercent(series.changePct)} from the prior close, {formatDay(series.asOf)}
              </p>
              <p className="caption">{series.blurb}</p>
              <Chart history={series.points} currency={series.currency} />
            </>
          ) : (
            <p className="note">Fetching prices.</p>
          )}
        </div>
      </div>

      {macro ? (
        <div style={{ marginTop: 36 }}>
          <h2>Kenya, from the World Bank</h2>
          <table>
            <thead>
              <tr><th>Indicator</th><th>Year</th><th className="right">Latest</th><th className="right">Prior</th></tr>
            </thead>
            <tbody>
              {macro.map((item) => {
                const latest = item.points.at(-1)
                const prior = item.points.at(-2)
                return (
                  <tr key={item.id}>
                    <td>{item.name}</td>
                    <td>{latest?.year || ""}</td>
                    <td className="right">{latest ? `${formatNumber(latest.value)}${item.unit === "%" ? "%" : ""}` : ""}</td>
                    <td className="right">{prior ? `${formatNumber(prior.value)}${item.unit === "%" ? "%" : ""}` : ""}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
          <p className="caption">Annual figures. GDP per person is in US dollars.</p>
        </div>
      ) : null}

      <div className="board-tools">
        <h2 style={{ margin: 0 }}>Nairobi board</h2>
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Find a company" aria-label="Find a company" />
      </div>
      {board?.stale ? (
        <p className="banner">Live board did not answer. Showing the captured session of {board.sessionLabel}.</p>
      ) : board ? (
        <p className="caption">Session of {board.sessionLabel}. Source: {board.source}.</p>
      ) : (
        <p className="note">Fetching the board.</p>
      )}
      {board?.nasi != null ? (
        <p>
          NASI {formatNumber(board.nasi)} <span className={toneClass(board.nasiChange || 0)}>{formatNumber(board.nasiChange || 0)}</span>
          {board.ytdPct != null ? `, year to date ${formatPercent(board.ytdPct)}` : ""}
          {board.marketCapTrillionKes != null ? `, market cap KES ${formatNumber(board.marketCapTrillionKes)} trillion` : ""}
        </p>
      ) : null}

      {pinnedRows.length ? (
        <p className="caption">
          Pinned: {pinnedRows.map((row) => `${row.ticker} ${formatNumber(row.price)}`).join(", ")}
        </p>
      ) : null}

      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Name</th>
            <th className="right">Volume</th>
            <th className="right">Price</th>
            <th className="right">Change</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.ticker} className={picked?.ticker === row.ticker ? "picked" : undefined}>
              <td>
                <button className="linkish" type="button" onClick={() => setPicked(row)}>{row.ticker}</button>
              </td>
              <td>{row.name}</td>
              <td className="right">{row.volume != null ? formatCompact(row.volume) : ""}</td>
              <td className="right">{formatNumber(row.price)}</td>
              <td className={`right ${toneClass(row.change || 0)}`}>{row.change == null ? "" : formatNumber(row.change)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {picked ? (
        <div className="banner">
          <strong>{picked.name}</strong> last printed at KES {formatNumber(picked.price)}.
          {" "}A path forecast needs a longer daily history than this public board provides, so this name stays a quote.
          <div className="actions" style={{ marginTop: 12 }}>
            <button className="button quiet" type="button" onClick={() => togglePin(picked.ticker)}>
              {pins.includes(picked.ticker) ? "Remove pin" : "Pin to this browser"}
            </button>
          </div>
        </div>
      ) : null}
    </section>
  )
}
