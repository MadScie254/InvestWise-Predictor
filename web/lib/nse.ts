import { readFileSync } from "node:fs"
import path from "node:path"
import type { Board, BoardRow } from "./types"

function loadSnapshot() {
  const candidates = [
    path.join(process.cwd(), "data", "nse-board.json"),
    path.join(process.cwd(), "web", "data", "nse-board.json"),
  ]
  for (const candidate of candidates) {
    try {
      return JSON.parse(readFileSync(candidate, "utf8")) as Board
    } catch {
      continue
    }
  }
  throw new Error("The captured Nairobi board is missing.")
}

const MONTHS: Record<string, string> = {
  Jan: "01",
  Feb: "02",
  Mar: "03",
  Apr: "04",
  May: "05",
  Jun: "06",
  Jul: "07",
  Aug: "08",
  Sep: "09",
  Oct: "10",
  Nov: "11",
  Dec: "12",
}

function stripTags(value: string) {
  return value
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/\s+/g, " ")
    .trim()
}

function parseNumber(value: string) {
  const cleaned = value.replace(/,/g, "").replace(/\s/g, "").trim()
  if (!cleaned || cleaned === "-" || cleaned === "\u2014") return null
  const parsed = Number(cleaned)
  return Number.isFinite(parsed) ? parsed : null
}

export function parseSessionDate(html: string) {
  const text = stripTags(html)
  const match = text.match(/\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),\s+(\d{4})\b/)
  if (!match) return null
  const month = MONTHS[match[1]]
  const day = match[2].padStart(2, "0")
  return {
    asOf: `${match[3]}-${month}-${day}`,
    sessionLabel: `${Number(match[2])} ${match[1]} ${match[3]}`,
  }
}

export function parseBoardHtml(html: string): Board {
  const text = stripTags(html)
  const summary = text.match(
    /([0-9]{2,4}\.[0-9]{2})\s*\(([+-]?[0-9.]+)\)\s*([+-]?[0-9.]+)\s*\(([+-]?[0-9.]+)%\)\s*KES\s*([0-9.]+)\s*Tr/i,
  )
  const session = parseSessionDate(html)
  const rows: BoardRow[] = []
  const chunks = html.match(/<tr[\s\S]*?<\/tr>/gi) || []
  for (const chunk of chunks) {
    const tickerMatch = chunk.match(/\/nse\/([a-z0-9-]+)\.html/i)
    if (!tickerMatch) continue
    const ticker = tickerMatch[1].toUpperCase()
    const title = chunk.match(/title="([^"]+)"/i)
    const cells = [...chunk.matchAll(/<td[^>]*>([\s\S]*?)<\/td>/gi)].map((cell) => stripTags(cell[1]))
    if (cells.length < 3) continue
    const numbers = cells.map(parseNumber)
    const price = numbers[numbers.length - 2]
    const change = numbers[numbers.length - 1]
    const volume = numbers.length >= 3 ? numbers[numbers.length - 3] : null
    if (price == null) continue
    const name = title?.[1] || cells[1] || ticker
    if (rows.some((row) => row.ticker === ticker)) continue
    rows.push({
      ticker,
      name,
      volume: volume != null && volume > 100 ? volume : volume,
      price,
      change,
    })
  }
  if (!rows.length) throw new Error("The Nairobi board page had no quotes.")
  return {
    asOf: session?.asOf || "2026-11-20",
    sessionLabel: session?.sessionLabel || "20 Nov 2026",
    source: "AFX public Nairobi board",
    sourceUrl: "https://afx.kwayisi.org/nse/",
    nasi: summary ? Number(summary[1]) : null,
    nasiChange: summary ? Number(summary[2]) : null,
    ytdPoints: summary ? Number(summary[3]) : null,
    ytdPct: summary ? Number(summary[4]) : null,
    marketCapTrillionKes: summary ? Number(summary[5]) : null,
    stale: false,
    rows,
  }
}

export function capturedBoard(): Board {
  const snapshot = loadSnapshot()
  return { ...snapshot, stale: true }
}
