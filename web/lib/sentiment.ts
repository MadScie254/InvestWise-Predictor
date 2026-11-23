const CONSTRUCTIVE = [
  "gain",
  "gains",
  "rise",
  "rises",
  "rising",
  "growth",
  "grew",
  "surplus",
  "record",
  "boost",
  "expand",
  "expansion",
  "upgrade",
  "profit",
  "profits",
  "recovery",
  "recover",
  "stable",
  "stability",
  "surge",
  "rally",
  "beat",
  "beats",
]

const STRAINED = [
  "fall",
  "falls",
  "drop",
  "drops",
  "loss",
  "losses",
  "debt",
  "crisis",
  "default",
  "layoff",
  "layoffs",
  "deficit",
  "slump",
  "fraud",
  "decline",
  "declines",
  "cut",
  "cuts",
  "warning",
  "warns",
  "shortage",
  "inflation",
  "lawsuit",
  "probe",
  "scandal",
]

export type Tone = "constructive" | "mixed" | "strained"

export function scoreHeadline(title: string) {
  const words = title.toLowerCase().match(/[a-z']+/g) || []
  let constructive = 0
  let strained = 0
  for (const word of words) {
    if (CONSTRUCTIVE.includes(word)) constructive += 1
    if (STRAINED.includes(word)) strained += 1
  }
  const score = words.length ? (constructive - strained) / words.length : 0
  const tone: Tone = score > 0.04 ? "constructive" : score < -0.04 ? "strained" : "mixed"
  return { score, tone }
}
