import assert from "node:assert/strict"
import test from "node:test"
import { scoreVentures } from "./ventures.ts"

test("a small Nairobi trade desk prefers the cash agency", () => {
  const top = scoreVentures({
    capital: 150000,
    risk: "steady",
    county: "Nairobi",
    interest: "trade",
    inflation: 7,
    shillingChangePct: 0.2,
    brent: 80,
  })
  assert.equal(top.length, 3)
  assert.equal(top[0].id, "agency")
  assert.ok(top[0].score >= top[1].score)
})

test("a coast hospitality plan rises when the shilling weakens", () => {
  const weak = scoreVentures({
    capital: 1200000,
    risk: "assertive",
    county: "Mombasa",
    interest: "hospitality",
    inflation: 5,
    shillingChangePct: 4,
    brent: 88,
  })
  const firm = scoreVentures({
    capital: 1200000,
    risk: "assertive",
    county: "Mombasa",
    interest: "hospitality",
    inflation: 5,
    shillingChangePct: 0,
    brent: 88,
  })
  const weakCoast = weak.find((idea) => idea.id === "coast")
  const firmCoast = firm.find((idea) => idea.id === "coast")
  assert.ok(weakCoast && firmCoast)
  assert.ok(weakCoast.score > firmCoast.score)
})
