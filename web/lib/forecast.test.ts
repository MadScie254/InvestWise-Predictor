import assert from "node:assert/strict"
import test from "node:test"
import { fitHolt, project } from "./forecast.ts"

function line(length: number, step = 1, start = 1) {
  return Array.from({ length }, (_, index) => start + index * step)
}

function dates(length: number) {
  const out: string[] = []
  const cursor = new Date("2024-01-02T00:00:00Z")
  while (out.length < length) {
    const day = cursor.getUTCDay()
    if (day !== 0 && day !== 6) out.push(cursor.toISOString().slice(0, 10))
    cursor.setUTCDate(cursor.getUTCDate() + 1)
  }
  return out
}

test("sequence smoothing follows a straight line", () => {
  const values = line(120)
  const fit = fitHolt(values)
  assert.ok(Math.abs(fit.trend - 1) < 0.05)
  const view = project(values, dates(120), "holt", 5, 7)
  assert.equal(view.path.length, 5)
  assert.ok(Math.abs(view.path[4].close - 125) < 1.5)
})

test("a flat series stays near its level", () => {
  const values = Array.from({ length: 100 }, () => 50)
  const view = project(values, dates(100), "holt", 10, 3)
  assert.ok(Math.abs(view.projected - 50) < 0.5)
})

test("tree models return a finite path", () => {
  const values = line(160, 0.4, 20).map((value, index) => value + Math.sin(index / 4))
  for (const model of ["boost", "forest"] as const) {
    const view = project(values, dates(160), model, 8, 11)
    assert.equal(view.path.length, 8)
    assert.ok(view.path.every((point) => Number.isFinite(point.close) && point.close > 0))
    assert.ok(view.backtest.samples > 0)
    assert.ok(view.high[7].close >= view.low[7].close)
  }
})

test("short history is refused", () => {
  assert.throws(() => project(line(20), dates(20), "holt", 5, 1))
})
