export type Point = {
  date: string
  close: number
}

export type Series = {
  symbol: string
  name: string
  short: string
  currency: string
  venue: string
  blurb: string
  last: number
  previous: number
  change: number
  changePct: number
  asOf: string
  points: Point[]
}

export type BoardRow = {
  ticker: string
  name: string
  volume: number | null
  price: number
  change: number | null
}

export type Board = {
  asOf: string
  sessionLabel: string
  source: string
  sourceUrl: string
  nasi: number | null
  nasiChange: number | null
  ytdPoints: number | null
  ytdPct: number | null
  marketCapTrillionKes: number | null
  stale: boolean
  rows: BoardRow[]
}

export type MacroPoint = {
  year: number
  value: number
}

export type MacroSeries = {
  id: string
  name: string
  unit: string
  points: MacroPoint[]
}

export type NewsItem = {
  title: string
  source: string
  url: string
  published: string
  tone: "constructive" | "mixed" | "strained"
  score: number
}

export type ModelId = "holt" | "boost" | "forest"

export type ForecastView = {
  model: ModelId
  label: string
  horizon: number
  last: number
  projected: number
  changePct: number
  path: Point[]
  low: Point[]
  high: Point[]
  history: Point[]
  backtest: {
    samples: number
    mape: number
    directionHit: number
  }
  reading: string
  note: string
}
