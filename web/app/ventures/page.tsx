"use client"

import { useEffect, useState } from "react"
import { formatNumber } from "@/lib/format"
import { scoreVentures, type Interest, type Risk } from "@/lib/ventures"
import type { MacroSeries, Series } from "@/lib/types"

const COUNTIES = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Kiambu", "Nyeri", "Machakos", "Kakamega", "Kilifi", "Meru", "Kwale", "Kajiado", "Kitale"]
const INTERESTS: Array<{ id: Interest; label: string }> = [
  { id: "food", label: "Food" },
  { id: "trade", label: "Trade" },
  { id: "energy", label: "Energy" },
  { id: "health", label: "Health" },
  { id: "building", label: "Building" },
  { id: "hospitality", label: "Hospitality" },
  { id: "logistics", label: "Logistics" },
]

export default function VenturesPage() {
  const [capital, setCapital] = useState(500000)
  const [risk, setRisk] = useState<Risk>("balanced")
  const [county, setCounty] = useState("Nairobi")
  const [interest, setInterest] = useState<Interest>("food")
  const [inflation, setInflation] = useState<number | null>(null)
  const [shilling, setShilling] = useState<number | null>(null)
  const [brent, setBrent] = useState<number | null>(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    fetch("/api/macro").then((response) => response.json()).then((data: MacroSeries[]) => {
      if (!Array.isArray(data)) return
      const latest = data.find((item) => item.id === "FP.CPI.TOTL.ZG")?.points.at(-1)
      if (latest) setInflation(latest.value)
    }).catch(() => undefined)
    fetch("/api/series?symbol=USDKES%3DX&tail=40").then((response) => response.json()).then((data: Series) => {
      if (!data.points || data.points.length < 22) return
      const last = data.points.at(-1)!.close
      const then = data.points.at(-21)!.close
      setShilling(((last - then) / then) * 100)
    }).catch(() => undefined)
    fetch("/api/series?symbol=BZ%3DF&tail=5").then((response) => response.json()).then((data: Series) => {
      if (data.last) setBrent(data.last)
    }).catch(() => undefined)
  }, [])

  const ideas = ready
    ? scoreVentures({ capital, risk, county, interest, inflation, shillingChangePct: shilling, brent })
    : []

  return (
    <section>
      <div className="section-head">
        <h1>Ventures</h1>
        <p>
          A short list of Kenyan trades, scored against the capital and county you enter
          {inflation != null ? `, with inflation last printed at ${formatNumber(inflation)}%` : ""}.
          This is a match, not a licence, a loan, or a business plan.
        </p>
      </div>
      <form
        className="form"
        onSubmit={(event) => {
          event.preventDefault()
          setReady(true)
        }}
      >
        <label className="field">
          <span>Capital, KES</span>
          <input type="number" min={10000} step={10000} value={capital} onChange={(event) => setCapital(Number(event.target.value))} />
        </label>
        <label className="field">
          <span>County</span>
          <select value={county} onChange={(event) => setCounty(event.target.value)}>
            {COUNTIES.map((item) => <option key={item}>{item}</option>)}
          </select>
        </label>
        <label className="field">
          <span>Interest</span>
          <select value={interest} onChange={(event) => setInterest(event.target.value as Interest)}>
            {INTERESTS.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}
          </select>
        </label>
        <fieldset className="field" style={{ border: 0, margin: 0, padding: 0 }}>
          <span>Risk</span>
          <div className="choices">
            {(["steady", "balanced", "assertive"] as Risk[]).map((item) => (
              <label key={item}>
                <input type="radio" name="risk" checked={risk === item} onChange={() => setRisk(item)} />
                {item}
              </label>
            ))}
          </div>
        </fieldset>
        <button className="button" type="submit">Score ideas</button>
      </form>
      {ideas.map((idea, index) => (
        <article className="idea" key={idea.id}>
          <p className="score">{index + 1}. Score {idea.score}</p>
          <h3>{idea.name}</h3>
          <p>{idea.summary}</p>
          <ul>
            {idea.reasons.map((reason) => <li key={reason}>{reason}</li>)}
          </ul>
        </article>
      ))}
    </section>
  )
}
