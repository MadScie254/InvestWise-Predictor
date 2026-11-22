"use client"

import { useEffect, useRef, useState } from "react"
import { INSTRUMENTS } from "@/lib/instruments"
import { formatQuote } from "@/lib/format"
import { loadAlerts, saveAlerts, type AlertRule } from "@/lib/local-desk"
import type { Board, Series } from "@/lib/types"

type Option = { symbol: string; label: string; currency: string }

export default function AlertsPage() {
  const [rules, setRules] = useState<AlertRule[]>([])
  const [options, setOptions] = useState<Option[]>(INSTRUMENTS.map((item) => ({ symbol: item.symbol, label: item.name, currency: item.currency })))
  const [symbol, setSymbol] = useState(INSTRUMENTS[0].symbol)
  const [direction, setDirection] = useState<"above" | "below">("above")
  const [price, setPrice] = useState(130)
  const [hits, setHits] = useState<string[]>([])
  const [note, setNote] = useState("Alerts are checked while this page is open. Nothing watches the market after you leave, because there is no paid server doing that job.")
  const notified = useRef(new Set<string>())

  useEffect(() => {
    setRules(loadAlerts())
    fetch("/api/board").then((response) => response.json()).then((board: Board) => {
      if (!board.rows) return
      const extra = board.rows.slice(0, 40).map((row) => ({ symbol: row.ticker, label: `${row.ticker}, ${row.name}`, currency: "KES" }))
      setOptions([...INSTRUMENTS.map((item) => ({ symbol: item.symbol, label: item.name, currency: item.currency })), ...extra])
    }).catch(() => undefined)
  }, [])

  useEffect(() => {
    let stop = false
    async function check() {
      const current = loadAlerts()
      if (!current.length) {
        setHits([])
        return
      }
      const board = await fetch("/api/board").then((response) => response.json()).catch(() => null) as Board | null
      const found: string[] = []
      for (const rule of current) {
        let last: number | null = board?.rows.find((row) => row.ticker === rule.symbol)?.price ?? null
        const needsSeries = last == null && (rule.symbol.includes("=") || rule.symbol.startsWith("^") || rule.symbol === "EZA")
        if (needsSeries) {
          const series = await fetch(`/api/series?symbol=${encodeURIComponent(rule.symbol)}&tail=30`).then((response) => response.json()).catch(() => null) as Series | null
          last = series?.last ?? null
        }
        if (last == null) continue
        const crossed = rule.direction === "above" ? last >= rule.price : last <= rule.price
        if (crossed) found.push(`${rule.label} is ${formatQuote(last, rule.currency)}, ${rule.direction} ${formatQuote(rule.price, rule.currency)}.`)
      }
      if (stop) return
      setHits(found)
      const fresh = found.filter((line) => !notified.current.has(line))
      fresh.forEach((line) => notified.current.add(line))
      if (fresh.length && typeof Notification !== "undefined" && Notification.permission === "granted") {
        fresh.forEach((line) => new Notification("InvestWise", { body: line }))
      }
    }
    check()
    const timer = window.setInterval(check, 60000)
    return () => {
      stop = true
      window.clearInterval(timer)
    }
  }, [rules])

  function add(event: React.FormEvent) {
    event.preventDefault()
    const option = options.find((item) => item.symbol === symbol)
    if (!option || !Number.isFinite(price)) return
    const next = [
      ...rules,
      { id: crypto.randomUUID(), symbol, label: option.label, direction, price, currency: option.currency },
    ].slice(0, 12)
    setRules(next)
    saveAlerts(next)
    if (typeof Notification !== "undefined" && Notification.permission === "default") {
      Notification.requestPermission().catch(() => undefined)
    }
    setNote("Saved on this browser.")
  }

  function remove(id: string) {
    const next = rules.filter((rule) => rule.id !== id)
    setRules(next)
    saveAlerts(next)
  }

  return (
    <section>
      <div className="section-head">
        <h1>Alerts</h1>
        <p>{note}</p>
      </div>
      <form className="form" onSubmit={add}>
        <label className="field">
          <span>Name</span>
          <select value={symbol} onChange={(event) => setSymbol(event.target.value)}>
            {options.map((item) => <option key={item.symbol} value={item.symbol}>{item.label}</option>)}
          </select>
        </label>
        <label className="field">
          <span>Crosses</span>
          <select value={direction} onChange={(event) => setDirection(event.target.value as "above" | "below")}>
            <option value="above">Above</option>
            <option value="below">Below</option>
          </select>
        </label>
        <label className="field">
          <span>Price</span>
          <input type="number" step="0.01" value={price} onChange={(event) => setPrice(Number(event.target.value))} />
        </label>
        <button className="button" type="submit">Set alert</button>
      </form>
      {hits.map((hit) => <p className="banner" key={hit}>{hit}</p>)}
      <div className="stack">
        {rules.map((rule) => (
          <div className="alert-row" key={rule.id}>
            <span>{rule.label} {rule.direction} {formatQuote(rule.price, rule.currency)}</span>
            <button className="button quiet" type="button" onClick={() => remove(rule.id)}>Remove</button>
          </div>
        ))}
        {!rules.length ? <p className="note">No alerts yet.</p> : null}
      </div>
    </section>
  )
}
