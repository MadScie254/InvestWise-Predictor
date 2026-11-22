export type Risk = "steady" | "balanced" | "assertive"
export type Interest = "food" | "trade" | "energy" | "health" | "building" | "hospitality" | "logistics"

export type VentureInput = {
  capital: number
  risk: Risk
  county: string
  interest: Interest
  inflation: number | null
  shillingChangePct: number | null
  brent: number | null
}

type Idea = {
  id: string
  name: string
  summary: string
  capitalMin: number
  capitalMax: number
  risk: Risk
  interests: Interest[]
  counties: string[] | "any"
  inflationTilt: number
  fxTilt: number
  fuelTilt: number
}

const IDEAS: Idea[] = [
  {
    id: "dairy",
    name: "Milk collection and cooling",
    summary: "A small cooler and a pickup route for farmers who currently sell warm milk at the farm gate.",
    capitalMin: 400000,
    capitalMax: 2000000,
    risk: "balanced",
    interests: ["food", "logistics"],
    counties: ["Nakuru", "Nyeri", "Kiambu", "Eldoret", "Kakamega", "Meru"],
    inflationTilt: 0.4,
    fxTilt: -0.1,
    fuelTilt: -0.3,
  },
  {
    id: "agrovet",
    name: "Agrovet and farm inputs",
    summary: "Seed, feed, and veterinary supplies for a farming county, with advice attached to the sale.",
    capitalMin: 250000,
    capitalMax: 1200000,
    risk: "steady",
    interests: ["food", "trade"],
    counties: "any",
    inflationTilt: 0.5,
    fxTilt: -0.25,
    fuelTilt: -0.1,
  },
  {
    id: "pharmacy",
    name: "Neighborhood pharmacy",
    summary: "A licensed dispenser for a dense estate, focused on repeat prescriptions and basic tests.",
    capitalMin: 800000,
    capitalMax: 3000000,
    risk: "steady",
    interests: ["health"],
    counties: ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Kiambu", "Eldoret"],
    inflationTilt: 0.45,
    fxTilt: -0.35,
    fuelTilt: 0,
  },
  {
    id: "agency",
    name: "Cash agency and stationery",
    summary: "A counter for cash-in, cash-out, printing, and airtime. Small float, daily turnover.",
    capitalMin: 80000,
    capitalMax: 350000,
    risk: "steady",
    interests: ["trade"],
    counties: "any",
    inflationTilt: 0.2,
    fxTilt: 0,
    fuelTilt: 0,
  },
  {
    id: "solar",
    name: "Solar home installation",
    summary: "Panels, batteries, and a service contract for homes and shops that lose the grid.",
    capitalMin: 500000,
    capitalMax: 2500000,
    risk: "assertive",
    interests: ["energy"],
    counties: "any",
    inflationTilt: 0.1,
    fxTilt: -0.6,
    fuelTilt: 0.35,
  },
  {
    id: "spares",
    name: "Motorcycle spare parts",
    summary: "Fast-moving parts for boda riders, close to a stage, with a mechanic on a stool outside.",
    capitalMin: 200000,
    capitalMax: 900000,
    risk: "balanced",
    interests: ["trade", "logistics"],
    counties: ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Kiambu"],
    inflationTilt: 0.15,
    fxTilt: -0.3,
    fuelTilt: -0.15,
  },
  {
    id: "lunch",
    name: "School and site lunches",
    summary: "A fixed menu for a school or a building site, cooked nearby and delivered before noon.",
    capitalMin: 150000,
    capitalMax: 700000,
    risk: "balanced",
    interests: ["food"],
    counties: "any",
    inflationTilt: -0.15,
    fxTilt: 0,
    fuelTilt: -0.2,
  },
  {
    id: "cold",
    name: "Horticulture cold room",
    summary: "Shared cold storage for growers who miss the export truck because the produce warms up.",
    capitalMin: 2000000,
    capitalMax: 8000000,
    risk: "assertive",
    interests: ["food", "logistics"],
    counties: ["Nakuru", "Nyeri", "Meru", "Kiambu", "Nairobi"],
    inflationTilt: 0.1,
    fxTilt: 0.55,
    fuelTilt: -0.25,
  },
  {
    id: "hardware",
    name: "Hardware and materials",
    summary: "Cement, iron sheets, and paint for a growing town, with delivery to the site.",
    capitalMin: 1500000,
    capitalMax: 6000000,
    risk: "balanced",
    interests: ["building", "trade"],
    counties: ["Nairobi", "Kiambu", "Machakos", "Nakuru", "Mombasa", "Eldoret"],
    inflationTilt: -0.1,
    fxTilt: -0.25,
    fuelTilt: -0.3,
  },
  {
    id: "layers",
    name: "Layer poultry",
    summary: "A few hundred layers, sold as eggs to shops and estates. Feed price is the whole business.",
    capitalMin: 300000,
    capitalMax: 1500000,
    risk: "balanced",
    interests: ["food"],
    counties: ["Kiambu", "Nakuru", "Machakos", "Kakamega", "Nyeri"],
    inflationTilt: 0.2,
    fxTilt: -0.2,
    fuelTilt: -0.15,
  },
  {
    id: "water",
    name: "Water kiosk",
    summary: "Treated water sold by the jerrycan where the municipal line is unreliable.",
    capitalMin: 180000,
    capitalMax: 800000,
    risk: "steady",
    interests: ["health", "trade"],
    counties: ["Nairobi", "Mombasa", "Machakos", "Kajiado", "Kilifi", "Kisumu"],
    inflationTilt: 0.35,
    fxTilt: 0,
    fuelTilt: -0.1,
  },
  {
    id: "coast",
    name: "Small guesthouse desk",
    summary: "A few rooms or a booking desk for coast and rift visitors, paid partly in hard currency.",
    capitalMin: 400000,
    capitalMax: 2500000,
    risk: "assertive",
    interests: ["hospitality"],
    counties: ["Mombasa", "Kilifi", "Kwale", "Nakuru", "Kisumu"],
    inflationTilt: -0.05,
    fxTilt: 0.65,
    fuelTilt: -0.2,
  },
  {
    id: "uniforms",
    name: "Uniforms and alterations",
    summary: "School uniforms and repairs, with a contract from one or two schools if you can get it.",
    capitalMin: 80000,
    capitalMax: 400000,
    risk: "steady",
    interests: ["trade"],
    counties: "any",
    inflationTilt: 0.1,
    fxTilt: -0.1,
    fuelTilt: 0,
  },
  {
    id: "grain",
    name: "Grain aggregation",
    summary: "Buy maize or beans at harvest, store them dry, and sell into the lean months.",
    capitalMin: 1000000,
    capitalMax: 5000000,
    risk: "assertive",
    interests: ["food", "trade"],
    counties: ["Eldoret", "Nakuru", "Kakamega", "Kitale", "Meru"],
    inflationTilt: 0.35,
    fxTilt: 0.1,
    fuelTilt: -0.25,
  },
]

const RISK_RANK: Record<Risk, number> = { steady: 0, balanced: 1, assertive: 2 }

export function money(value: number) {
  return new Intl.NumberFormat("en-KE", { style: "currency", currency: "KES", maximumFractionDigits: 0 }).format(value)
}

export function scoreVentures(input: VentureInput) {
  const ranked = IDEAS.map((idea) => {
    const reasons: string[] = []
    let score = 40

    if (input.capital < idea.capitalMin) {
      score -= 35
      reasons.push(`Your capital sits below the ${money(idea.capitalMin)} this usually takes to open.`)
    } else if (input.capital > idea.capitalMax * 2.5) {
      score -= 8
      reasons.push("Your capital is larger than this idea needs, so it may be a side desk rather than the main one.")
    } else {
      score += 18
      reasons.push(`It fits a float between ${money(idea.capitalMin)} and ${money(idea.capitalMax)}.`)
    }

    const gap = Math.abs(RISK_RANK[input.risk] - RISK_RANK[idea.risk])
    if (gap === 0) {
      score += 14
      reasons.push("The risk sits at the level you asked for.")
    } else if (gap === 1) {
      score += 4
    } else {
      score -= 12
      reasons.push("It is a sharper risk than the setting you chose.")
    }

    if (idea.interests.includes(input.interest)) {
      score += 16
      reasons.push("It matches the kind of work you said you want.")
    }

    if (idea.counties !== "any" && !idea.counties.includes(input.county)) {
      score -= 8
    } else if (idea.counties !== "any") {
      score += 8
      reasons.push(`${input.county} is one of the counties where this trade already has customers.`)
    }

    if (input.inflation != null && input.inflation >= 6) {
      score += idea.inflationTilt * 12
      if (idea.inflationTilt > 0.3) reasons.push("High inflation tends to keep demand on essentials like this.")
    }
    if (input.shillingChangePct != null && input.shillingChangePct > 1.5) {
      score += idea.fxTilt * 14
      if (idea.fxTilt > 0.4) reasons.push("A weaker shilling helps this more than it hurts, because part of the income is tied to hard currency or exports.")
      if (idea.fxTilt < -0.4) reasons.push("A weaker shilling raises the cost of the imported parts this depends on.")
    }
    if (input.brent != null && input.brent > 90) {
      score += idea.fuelTilt * 10
      if (idea.fuelTilt < -0.2) reasons.push("Expensive oil raises the transport cost inside this idea.")
    }

    return {
      id: idea.id,
      name: idea.name,
      summary: idea.summary,
      capitalMin: idea.capitalMin,
      capitalMax: idea.capitalMax,
      score: Math.round(Math.max(0, Math.min(100, score))),
      reasons: reasons.slice(0, 3),
    }
  })

  return ranked.sort((a, b) => b.score - a.score).slice(0, 3)
}
