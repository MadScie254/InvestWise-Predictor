import { NextResponse } from "next/server"
import { getMacro } from "@/lib/data"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const macro = await getMacro()
    return NextResponse.json(macro, {
      headers: { "cache-control": "public, s-maxage=86400, stale-while-revalidate=172800" },
    })
  } catch (error) {
    const message = error instanceof Error ? error.message : "Kenya indicators did not load."
    return NextResponse.json({ error: message }, { status: 502 })
  }
}
