import { projectAll, hashSeed } from "./forecast"
import { findInstrument } from "./instruments"
import { capturedBoard, parseBoardHtml } from "./nse"
import { scoreHeadline } from "./sentiment"
import type { Board, ForecastView, MacroSeries, ModelId, NewsItem, Series } from "./types"

const memory = new Map<string, { at: number; value: unknown }>()

function remember<T>(key: string, value: T) {
  memory.set(key, { at: Date.now(), value })
  return value
}

function recall<T>(key: string, ttlMs: number): T | null {
  const hit = memory.get(key)
  if (!hit) return null
  if (Date.now() - hit.at > ttlMs) return null
  return hit.value as T
}

function proxyBase() {
  return (process.env.MARKET_PROXY_URL || "").replace(/\/$/, "")
}

export async function fetchUpstream(url: string, options?: { timeoutMs?: number; proxy?: boolean }) {
  const headers = {
    "user-agent": "InvestWiseDesk/1.0",
    accept: "application/json, application/xml, text/html;q=0.9, */*;q=0.8",
  }
  const timeoutMs = options?.timeoutMs ?? 9000
  const allowProxy = options?.proxy !== false
  try {
    const response = await fetch(url, { headers, cache: "no-store", signal: AbortSignal.timeout(timeoutMs) })
    if (response.ok) return response
    if (response.status < 500) {
      const error = new Error(`status ${response.status}`) as Error & { retry?: boolean }
      error.retry = false
      throw error
    }
  } catch (error) {
    const proxy = proxyBase()
    if (!allowProxy || !proxy || (error && typeof error === "object" && "retry" in error && error.retry === false)) throw error
  }
  const proxy = proxyBase()
  if (!allowProxy || !proxy) throw new Error("The data source did not answer.")
  const response = await fetch(`${proxy}/fetch?url=${encodeURIComponent(url)}`, {
    cache: "no-store",
    signal: AbortSignal.timeout(9000),
  })
  if (!response.ok) throw new Error(`proxy status ${response.status}`)
  return response
}

export async function getSeries(symbol: string): Promise<Series> {
  const instrument = findInstrument(symbol)
  if (!instrument) throw new Error("That series is not on this desk.")
  const cached = recall<Series>(`series:${symbol}`, 5 * 60 * 1000)
  if (cached) return cached
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?interval=1d&range=5y`
  const payload = await (await fetchUpstream(url)).json()
  const result = payload?.chart?.result?.[0]
  const timestamps: number[] = result?.timestamp || []
  const closes: Array<number | null> = result?.indicators?.quote?.[0]?.close || []
  const points = []
  for (let index = 0; index < timestamps.length; index += 1) {
    const close = closes[index]
    if (close == null || !Number.isFinite(close)) continue
    points.push({ date: new Date(timestamps[index] * 1000).toISOString().slice(0, 10), close })
  }
  if (points.length < 2) throw new Error("The price history came back empty.")
  const last = points[points.length - 1]
  const previous = points[points.length - 2]
  const change = last.close - previous.close
  return remember(`series:${symbol}`, {
    ...instrument,
    last: last.close,
    previous: previous.close,
    change,
    changePct: (change / previous.close) * 100,
    asOf: last.date,
    points,
  })
}

export async function getBoard(): Promise<Board> {
  const cached = recall<Board>("board", 3 * 60 * 1000)
  if (cached) return cached
  try {
    const response = await fetchUpstream("https://afx.kwayisi.org/nse/", { timeoutMs: 4000, proxy: false })
    const board = parseBoardHtml(await response.text())
    return remember("board", board)
  } catch {
    return capturedBoard()
  }
}

const MACRO: Array<{ id: string; name: string; unit: string }> = [
  { id: "NY.GDP.MKTP.KD.ZG", name: "GDP growth", unit: "%" },
  { id: "FP.CPI.TOTL.ZG", name: "Inflation", unit: "%" },
  { id: "SL.UEM.TOTL.ZS", name: "Unemployment", unit: "%" },
  { id: "NY.GDP.PCAP.CD", name: "GDP per person", unit: "USD" },
]

export async function getMacro(): Promise<MacroSeries[]> {
  const cached = recall<MacroSeries[]>("macro", 12 * 60 * 60 * 1000)
  if (cached) return cached
  const series = await Promise.all(
    MACRO.map(async (item) => {
      const url = `https://api.worldbank.org/v2/country/KE/indicator/${item.id}?format=json&per_page=15`
      const payload = await (await fetchUpstream(url)).json()
      const rows = Array.isArray(payload?.[1]) ? payload[1] : []
      const points = rows
        .filter((row: { value: number | null; date: string }) => row.value != null)
        .map((row: { value: number; date: string }) => ({ year: Number(row.date), value: Number(row.value) }))
        .sort((a: { year: number }, b: { year: number }) => a.year - b.year)
      return { ...item, points }
    }),
  )
  return remember("macro", series)
}

function decodeXml(value: string) {
  return value
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .trim()
}

export async function getNews(): Promise<NewsItem[]> {
  const cached = recall<NewsItem[]>("news", 15 * 60 * 1000)
  if (cached) return cached
  const query = encodeURIComponent("Kenya economy OR Nairobi Securities Exchange OR Central Bank of Kenya")
  const url = `https://news.google.com/rss/search?q=${query}&hl=en-KE&gl=KE&ceid=KE:en`
  const xml = await (await fetchUpstream(url)).text()
  const items: NewsItem[] = []
  for (const block of xml.match(/<item>[\s\S]*?<\/item>/g) || []) {
    const title = decodeXml(block.match(/<title>([\s\S]*?)<\/title>/)?.[1] || "")
    const link = decodeXml(block.match(/<link>([\s\S]*?)<\/link>/)?.[1] || "")
    const published = decodeXml(block.match(/<pubDate>([\s\S]*?)<\/pubDate>/)?.[1] || "")
    if (!title || !link) continue
    const split = title.lastIndexOf(" - ")
    const headline = split > 0 ? title.slice(0, split) : title
    const source = split > 0 ? title.slice(split + 3) : "Google News"
    const tone = scoreHeadline(headline)
    items.push({ title: headline, source, url: link, published, tone: tone.tone, score: tone.score })
    if (items.length >= 14) break
  }
  return remember("news", items)
}

export async function getForecast(symbol: string, horizon: number): Promise<ForecastView[]> {
  const series = await getSeries(symbol)
  const values = series.points.map((point) => point.close)
  const dates = series.points.map((point) => point.date)
  const seed = hashSeed(`${symbol}:${dates[dates.length - 1]}:${horizon}`)
  return projectAll(values, dates, horizon, seed)
}

export function isModel(value: string): value is ModelId {
  return value === "holt" || value === "boost" || value === "forest"
}
