import { NextResponse } from "next/server"
import { getForecast, getSeries, isModel } from "@/lib/data"

export const dynamic = "force-dynamic"

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const symbol = searchParams.get("symbol") || "USDKES=X"
  const model = searchParams.get("model") || "holt"
  const horizon = Number(searchParams.get("horizon") || "20")
  if (!isModel(model)) return NextResponse.json({ error: "Choose a model on the desk." }, { status: 400 })
  if (!Number.isFinite(horizon) || horizon < 5 || horizon > 40) {
    return NextResponse.json({ error: "Choose a horizon between 5 and 40 sessions." }, { status: 400 })
  }
  try {
    const [series, views] = await Promise.all([getSeries(symbol), getForecast(symbol, horizon)])
    const focus = views.find((view) => view.model === model) || views[0]
    const peers = views
      .filter((view) => view.model !== focus.model)
      .map((view) => ({
        model: view.model,
        label: view.label,
        changePct: view.changePct,
        projected: view.projected,
        backtest: view.backtest,
        reading: view.reading,
      }))
    return NextResponse.json(
      {
        symbol: series.symbol,
        name: series.name,
        currency: series.currency,
        asOf: series.asOf,
        focus,
        peers,
      },
      { headers: { "cache-control": "public, s-maxage=300, stale-while-revalidate=900" } },
    )
  } catch (error) {
    const message = error instanceof Error ? error.message : "The forecast did not run."
    return NextResponse.json({ error: message }, { status: 400 })
  }
}
