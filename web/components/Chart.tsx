"use client"

import { useMemo, useState } from "react"
import type { Point } from "@/lib/types"
import { formatDay, formatQuote } from "@/lib/format"

type Props = {
  history: Point[]
  forecast?: Point[]
  low?: Point[]
  high?: Point[]
  currency: string
}

export function Chart({ history, forecast = [], low = [], high = [], currency }: Props) {
  const [hover, setHover] = useState<number | null>(null)
  const width = 1000
  const height = 380
  const pad = 12

  const geometry = useMemo(() => {
    const series = [...history, ...forecast]
    const extra = [...low, ...high]
    const values = [...series, ...extra].map((point) => point.close)
    const min = Math.min(...values)
    const max = Math.max(...values)
    const span = max - min || Math.abs(max) * 0.04 || 1
    const yMin = min - span * 0.08
    const yMax = max + span * 0.08
    const xFor = (index: number) => pad + (index / Math.max(series.length - 1, 1)) * (width - pad * 2)
    const yFor = (value: number) => pad + ((yMax - value) / (yMax - yMin)) * (height - pad * 2)
    const line = (points: Point[], offset: number) =>
      points
        .map((point, index) => `${index === 0 ? "M" : "L"}${xFor(index + offset).toFixed(2)} ${yFor(point.close).toFixed(2)}`)
        .join(" ")
    let band = ""
    if (forecast.length && low.length === forecast.length && high.length === forecast.length) {
      const start = history.length - 1
      const upper = forecast.map((point, index) => `${index === 0 ? "M" : "L"}${xFor(start + index + 1).toFixed(2)} ${yFor(high[index].close).toFixed(2)}`)
      const lower = [...forecast].reverse().map((point, index) => {
        const source = forecast.length - 1 - index
        return `L${xFor(start + source + 1).toFixed(2)} ${yFor(low[source].close).toFixed(2)}`
      })
      const join = `M${xFor(start).toFixed(2)} ${yFor(history[history.length - 1].close).toFixed(2)}`
      band = `${join} ${upper.join(" ").replace(/^M/, "L")} ${lower.join(" ")} Z`
    }
    const spine = line(history, 0)
    const area = history.length > 1
      ? `${spine} L${xFor(history.length - 1).toFixed(2)} ${(height - pad).toFixed(2)} L${xFor(0).toFixed(2)} ${(height - pad).toFixed(2)} Z`
      : ""
    return { line: spine, area, future: line(forecast, history.length), band, xFor, yFor, count: series.length, series }
  }, [history, forecast, low, high])

  function move(event: React.PointerEvent<SVGSVGElement>) {
    const rect = event.currentTarget.getBoundingClientRect()
    const ratio = (event.clientX - rect.left) / rect.width
    const index = Math.round(ratio * (geometry.count - 1))
    setHover(Math.max(0, Math.min(geometry.count - 1, index)))
  }

  const active = hover == null ? null : geometry.series[hover]
  const joinX = history.length > 1 ? geometry.xFor(history.length - 1) : null

  return (
    <div>
      <p className="readout">
        {active ? `${formatDay(active.date)}  ${formatQuote(active.close, currency)}` : "Move across the line to read a session."}
      </p>
      <div className="chart-frame">
      <svg
        className="chart"
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Price chart"
        onPointerMove={move}
        onPointerLeave={() => setHover(null)}
      >
        {geometry.band ? <path className="band" d={geometry.band} /> : null}
        {joinX != null && forecast.length ? <line className="join" x1={joinX} x2={joinX} y1={8} y2={height - 8} /> : null}
        {geometry.area ? <path className="area" d={geometry.area} /> : null}
        <path className="history draw" d={geometry.line} />
        {forecast.length ? <path className="future draw" d={geometry.future} /> : null}
        {active && hover != null ? (
          <line className="hover" x1={geometry.xFor(hover)} x2={geometry.xFor(hover)} y1={8} y2={height - 8} />
        ) : null}
      </svg>
      </div>
    </div>
  )
}
