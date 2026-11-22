import { NextResponse } from "next/server"
import { getNews } from "@/lib/data"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const news = await getNews()
    return NextResponse.json(news, {
      headers: { "cache-control": "public, s-maxage=900, stale-while-revalidate=1800" },
    })
  } catch (error) {
    const message = error instanceof Error ? error.message : "The briefing did not load."
    return NextResponse.json({ error: message }, { status: 502 })
  }
}
