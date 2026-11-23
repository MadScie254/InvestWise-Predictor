const numberFormat = new Intl.NumberFormat("en-KE", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const compactFormat = new Intl.NumberFormat("en-KE", {
  notation: "compact",
  maximumFractionDigits: 2,
})

export function formatNumber(value: number, digits = 2) {
  return new Intl.NumberFormat("en-KE", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value)
}

export function formatQuote(value: number, currency: string) {
  const body = numberFormat.format(value)
  if (currency === "KES") return `KES ${body}`
  if (currency === "USD") return `USD ${body}`
  if (currency === "USc") return `${body} cents`
  return body
}

export function formatCompact(value: number) {
  return compactFormat.format(value)
}

export function formatPercent(value: number) {
  const sign = value > 0 ? "+" : ""
  return `${sign}${numberFormat.format(value)}%`
}

export function formatSigned(value: number, digits = 2) {
  const sign = value > 0 ? "+" : ""
  return `${sign}${formatNumber(value, digits)}`
}

export function toneClass(value: number) {
  if (value > 0.0000001) return "up"
  if (value < -0.0000001) return "down"
  return "flat"
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

export function formatDay(iso: string) {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso)
  if (!match) return iso
  const month = MONTHS[Number(match[2]) - 1] || match[2]
  return `${Number(match[3])} ${month} ${match[1]}`
}
