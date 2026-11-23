import { NextResponse } from "next/server"
import { getSeries } from "@/lib/data"

export const dynamic = "force-dynamic"

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const symbol = searchParams.get("symbol") || ""
  const tail = Number(searchParams.get("tail") || "420")
  try {
    const series = await getSeries(symbol)
    const count = Number.isFinite(tail) ? Math.min(Math.max(tail, 30), series.points.length) : 420
    return NextResponse.json(
      { ...series, points: series.points.slice(-count) },
      { headers: { "cache-control": "public, s-maxage=300, stale-while-revalidate=900" } },
    )
  } catch (error) {
    const message = error instanceof Error ? error.message : "The series did not load."
    return NextResponse.json({ error: message }, { status: 400 })
  }
}
