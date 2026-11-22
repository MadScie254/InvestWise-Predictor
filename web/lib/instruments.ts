export type Instrument = {
  symbol: string
  name: string
  short: string
  currency: string
  venue: string
  blurb: string
}

export const INSTRUMENTS: Instrument[] = [
  {
    symbol: "USDKES=X",
    name: "Shilling per dollar",
    short: "USD/KES",
    currency: "KES",
    venue: "FX",
    blurb: "How many shillings buy one US dollar.",
  },
  {
    symbol: "EURKES=X",
    name: "Shilling per euro",
    short: "EUR/KES",
    currency: "KES",
    venue: "FX",
    blurb: "How many shillings buy one euro.",
  },
  {
    symbol: "GBPKES=X",
    name: "Shilling per pound",
    short: "GBP/KES",
    currency: "KES",
    venue: "FX",
    blurb: "How many shillings buy one pound sterling.",
  },
  {
    symbol: "BZ=F",
    name: "Brent crude",
    short: "Brent",
    currency: "USD",
    venue: "ICE",
    blurb: "The oil benchmark that feeds into Kenyan fuel prices.",
  },
  {
    symbol: "GC=F",
    name: "Gold",
    short: "Gold",
    currency: "USD",
    venue: "COMEX",
    blurb: "Gold futures, in dollars per ounce.",
  },
  {
    symbol: "KC=F",
    name: "Coffee",
    short: "Coffee",
    currency: "USc",
    venue: "ICE",
    blurb: "Arabica futures in US cents per pound. A cousin of Kenya's export crop, not the Nairobi auction.",
  },
  {
    symbol: "ZW=F",
    name: "Wheat",
    short: "Wheat",
    currency: "USc",
    venue: "CBOT",
    blurb: "A global wheat future, in US cents per bushel. Kenya imports much of its wheat.",
  },
  {
    symbol: "^GSPC",
    name: "S&P 500",
    short: "S&P 500",
    currency: "PTS",
    venue: "New York",
    blurb: "A broad measure of large American companies.",
  },
  {
    symbol: "EZA",
    name: "South Africa ETF",
    short: "EZA",
    currency: "USD",
    venue: "NYSE",
    blurb: "A New York fund of Johannesburg shares. A regional stand-in, not the Nairobi board.",
  },
]

const bySymbol = new Map(INSTRUMENTS.map((item) => [item.symbol, item]))

export function findInstrument(symbol: string) {
  return bySymbol.get(symbol) || null
}
