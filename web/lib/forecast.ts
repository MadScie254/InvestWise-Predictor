import type { ForecastView, ModelId, Point } from "./types"

const LABELS: Record<ModelId, string> = {
  holt: "Sequence smoothing",
  boost: "Boosted stumps",
  forest: "Random forest",
}

export function hashSeed(text: string) {
  let hash = 2166136261
  for (let i = 0; i < text.length; i += 1) {
    hash ^= text.charCodeAt(i)
    hash = Math.imul(hash, 16777619)
  }
  return hash >>> 0
}

function mean(values: number[]) {
  let sum = 0
  for (const value of values) sum += value
  return values.length ? sum / values.length : 0
}

function stdev(values: number[]) {
  if (values.length < 2) return 0
  const center = mean(values)
  let sum = 0
  for (const value of values) {
    const delta = value - center
    sum += delta * delta
  }
  return Math.sqrt(sum / (values.length - 1))
}

function sse(values: number[]) {
  const center = mean(values)
  let sum = 0
  for (const value of values) {
    const delta = value - center
    sum += delta * delta
  }
  return sum
}

function mulberry32(seed: number) {
  let state = seed >>> 0
  return () => {
    state = (state + 0x6d2b79f5) | 0
    let t = Math.imul(state ^ (state >>> 15), 1 | state)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function dailyMoves(values: number[]) {
  const moves: number[] = []
  for (let i = 1; i < values.length; i += 1) moves.push(Math.abs(values[i] - values[i - 1]))
  return moves
}

function quantile(sorted: number[], q: number) {
  if (!sorted.length) return 0
  const index = Math.min(sorted.length - 1, Math.max(0, Math.floor(q * (sorted.length - 1))))
  return sorted[index]
}

type HoltFit = { level: number; trend: number; sigma: number }

export function fitHolt(values: number[], alpha = 0.42, beta = 0.16): HoltFit {
  let level = values[0]
  let trend = values.length > 1 ? values[1] - values[0] : 0
  const errors: number[] = []
  for (let i = 1; i < values.length; i += 1) {
    const forecast = level + trend
    errors.push(values[i] - forecast)
    const nextLevel = alpha * values[i] + (1 - alpha) * forecast
    trend = beta * (nextLevel - level) + (1 - beta) * trend
    level = nextLevel
  }
  const moves = dailyMoves(values).sort((a, b) => a - b)
  const cap = quantile(moves, 0.9) || 0
  if (trend > cap) trend = cap
  if (trend < -cap) trend = -cap
  return { level, trend, sigma: stdev(errors) }
}

function rsi(values: number[], end: number, period = 14) {
  let gains = 0
  let losses = 0
  for (let i = end - period + 1; i <= end; i += 1) {
    const delta = values[i] - values[i - 1]
    if (delta >= 0) gains += delta
    else losses -= delta
  }
  if (losses === 0) return 100
  const rs = gains / losses
  return 100 - 100 / (1 + rs)
}

function featuresAt(values: number[], end: number) {
  const last = values[end]
  const ret = (back: number) => last / values[end - back] - 1
  let sma10 = 0
  let sma20 = 0
  for (let i = 0; i < 10; i += 1) sma10 += values[end - i]
  for (let i = 0; i < 20; i += 1) sma20 += values[end - i]
  sma10 /= 10
  sma20 /= 20
  const window: number[] = []
  for (let i = end - 14; i <= end; i += 1) window.push(values[i] / values[i - 1] - 1)
  return [ret(1), ret(5), ret(20), last / sma20 - 1, last / sma10 - 1, stdev(window), rsi(values, end) / 100]
}

type Sample = { x: number[]; y: number }

function samplesFrom(values: number[]) {
  const samples: Sample[] = []
  for (let end = 30; end < values.length - 1; end += 1) {
    samples.push({ x: featuresAt(values, end), y: values[end + 1] / values[end] - 1 })
  }
  return samples
}

type Leaf = { leaf: true; value: number }
type Branch = { leaf: false; feature: number; threshold: number; left: Node; right: Node }
type Node = Leaf | Branch

function buildTree(samples: Sample[], depth: number, rng: () => number, maxDepth: number): Node {
  const fallback = (): Leaf => ({ leaf: true, value: mean(samples.map((sample) => sample.y)) })
  if (depth >= maxDepth || samples.length < 14) return fallback()

  const featureCount = samples[0].x.length
  const order = [...Array(featureCount).keys()]
  for (let i = order.length - 1; i > 0; i -= 1) {
    const j = Math.floor(rng() * (i + 1))
    const swap = order[i]
    order[i] = order[j]
    order[j] = swap
  }
  const chosen = order.slice(0, 3)
  let bestScore = Infinity
  let best: { feature: number; threshold: number; left: Sample[]; right: Sample[] } | null = null

  for (const feature of chosen) {
    const column = samples.map((sample) => sample.x[feature]).sort((a, b) => a - b)
    const cuts = [0.25, 0.4, 0.5, 0.6, 0.75].map((q) => quantile(column, q))
    const seen = new Set<number>()
    for (const threshold of cuts) {
      const key = Math.round(threshold * 1e6)
      if (seen.has(key)) continue
      seen.add(key)
      const left: Sample[] = []
      const right: Sample[] = []
      for (const sample of samples) {
        if (sample.x[feature] <= threshold) left.push(sample)
        else right.push(sample)
      }
      if (left.length < 6 || right.length < 6) continue
      const score = sse(left.map((sample) => sample.y)) + sse(right.map((sample) => sample.y))
      if (score < bestScore) {
        bestScore = score
        best = { feature, threshold, left, right }
      }
    }
  }

  if (!best) return fallback()
  return {
    leaf: false,
    feature: best.feature,
    threshold: best.threshold,
    left: buildTree(best.left, depth + 1, rng, maxDepth),
    right: buildTree(best.right, depth + 1, rng, maxDepth),
  }
}

function readTree(node: Node, input: number[]): number {
  let current = node
  while (!current.leaf) {
    current = input[current.feature] <= current.threshold ? current.left : current.right
  }
  return current.value
}

function bootstrap(samples: Sample[], rng: () => number) {
  const drawn: Sample[] = []
  for (let i = 0; i < samples.length; i += 1) {
    drawn.push(samples[Math.floor(rng() * samples.length)])
  }
  return drawn
}

function forestReturn(values: number[], seed: number) {
  const samples = samplesFrom(values)
  const rng = mulberry32(seed)
  const trees: Node[] = []
  for (let i = 0; i < 18; i += 1) {
    trees.push(buildTree(bootstrap(samples, rng), 0, rng, 3))
  }
  const input = featuresAt(values, values.length - 1)
  const votes = trees.map((tree) => readTree(tree, input))
  return { estimate: mean(votes), sigma: Math.max(stdev(votes), stdev(samples.map((sample) => sample.y)) * 0.35) }
}

type Stump = { feature: number; threshold: number; left: number; right: number }

function bestStump(samples: Sample[], residual: number[]): Stump | null {
  const featureCount = samples[0].x.length
  let bestScore = Infinity
  let best: Stump | null = null
  for (let feature = 0; feature < featureCount; feature += 1) {
    const column = samples.map((sample) => sample.x[feature]).sort((a, b) => a - b)
    const cuts = [0.3, 0.45, 0.55, 0.7].map((q) => quantile(column, q))
    const seen = new Set<number>()
    for (const threshold of cuts) {
      const key = Math.round(threshold * 1e6)
      if (seen.has(key)) continue
      seen.add(key)
      const left: number[] = []
      const right: number[] = []
      for (let i = 0; i < samples.length; i += 1) {
        if (samples[i].x[feature] <= threshold) left.push(residual[i])
        else right.push(residual[i])
      }
      if (left.length < 8 || right.length < 8) continue
      const score = sse(left) + sse(right)
      if (score < bestScore) {
        bestScore = score
        best = { feature, threshold, left: mean(left), right: mean(right) }
      }
    }
  }
  return best
}

function boostReturn(values: number[]) {
  const samples = samplesFrom(values)
  const rate = 0.18
  const prediction = new Array(samples.length).fill(0)
  let residual = samples.map((sample) => sample.y)
  const stumps: Stump[] = []
  for (let round = 0; round < 24; round += 1) {
    const stump = bestStump(samples, residual)
    if (!stump) break
    stumps.push(stump)
    for (let i = 0; i < samples.length; i += 1) {
      const step = samples[i].x[stump.feature] <= stump.threshold ? stump.left : stump.right
      prediction[i] += rate * step
      residual[i] = samples[i].y - prediction[i]
    }
  }
  const input = featuresAt(values, values.length - 1)
  let estimate = 0
  for (const stump of stumps) {
    estimate += rate * (input[stump.feature] <= stump.threshold ? stump.left : stump.right)
  }
  const misses = samples.map((sample, index) => sample.y - prediction[index])
  return { estimate, sigma: Math.max(stdev(misses), stdev(samples.map((sample) => sample.y)) * 0.35) }
}

function fadedPath(last: number, dailyReturn: number, sigma: number, horizon: number) {
  const path: number[] = []
  const low: number[] = []
  const high: number[] = []
  let factor = 1
  for (let step = 1; step <= horizon; step += 1) {
    const faded = dailyReturn * Math.exp(-(step - 1) / 12)
    factor *= 1 + faded
    const price = Math.max(0.0001, last * factor)
    const width = price * sigma * Math.sqrt(step) * 1.2
    path.push(price)
    low.push(Math.max(0.0001, price - width))
    high.push(price + width)
  }
  return { path, low, high }
}

function futureDates(lastDate: string, horizon: number) {
  const dates: string[] = []
  const cursor = new Date(`${lastDate}T00:00:00Z`)
  let made = 0
  while (made < horizon) {
    cursor.setUTCDate(cursor.getUTCDate() + 1)
    const day = cursor.getUTCDay()
    if (day === 0 || day === 6) continue
    dates.push(cursor.toISOString().slice(0, 10))
    made += 1
  }
  return dates
}

function oneStep(values: number[], model: ModelId, seed: number) {
  if (model === "holt") {
    const fit = fitHolt(values)
    return fit.level + fit.trend
  }
  const estimate = model === "forest" ? forestReturn(values, seed).estimate : boostReturn(values).estimate
  return values[values.length - 1] * (1 + estimate)
}

function backtest(values: number[], model: ModelId, seed: number) {
  const steps = model === "holt" ? 24 : 10
  const start = Math.max(60, values.length - steps - 1)
  let absPct = 0
  let hits = 0
  let count = 0
  for (let index = start; index < values.length - 1; index += 1) {
    const history = values.slice(0, index + 1)
    if (history.length < 50) continue
    const predicted = oneStep(history, model, seed + index)
    const actual = values[index + 1]
    const last = values[index]
    absPct += Math.abs(predicted - actual) / Math.abs(actual)
    const predictedDir = Math.sign(predicted - last)
    const actualDir = Math.sign(actual - last)
    if (predictedDir === actualDir || (predictedDir === 0 && actualDir === 0)) hits += 1
    count += 1
  }
  return {
    samples: count,
    mape: count ? absPct / count : 0,
    directionHit: count ? hits / count : 0,
  }
}

function readingFor(hit: number) {
  if (hit >= 0.62) {
    return "On the recent stretch, the direction call landed more often than not. The size of the move can still be wrong."
  }
  if (hit >= 0.52) {
    return "Recent direction calls were only a little better than a coin toss. Use the path as a sketch."
  }
  return "Recent direction calls were no better than a coin toss. The band matters more than the line."
}

export function project(values: number[], dates: string[], model: ModelId, horizon: number, seed: number): ForecastView {
  if (values.length < 80 || values.length !== dates.length) {
    throw new Error("This series is too short for a forecast.")
  }
  if (horizon < 5 || horizon > 40) throw new Error("Choose a horizon between 5 and 40 sessions.")

  const sample = model === "holt" ? values : values.slice(-380)
  const last = values[values.length - 1]
  const lastDate = dates[dates.length - 1]
  const ahead = futureDates(lastDate, horizon)
  let path: number[]
  let low: number[]
  let high: number[]

  if (model === "holt") {
    const fit = fitHolt(sample)
    path = []
    low = []
    high = []
    for (let step = 1; step <= horizon; step += 1) {
      const price = Math.max(0.0001, fit.level + step * fit.trend)
      const width = fit.sigma * Math.sqrt(step)
      path.push(price)
      low.push(Math.max(0.0001, price - width))
      high.push(price + width)
    }
  } else {
    const fitted = model === "forest" ? forestReturn(sample, seed) : boostReturn(sample)
    const faded = fadedPath(last, fitted.estimate, fitted.sigma, horizon)
    path = faded.path
    low = faded.low
    high = faded.high
  }

  const historyStart = Math.max(0, values.length - 160)
  const history: Point[] = []
  for (let i = historyStart; i < values.length; i += 1) history.push({ date: dates[i], close: values[i] })

  const toPoints = (series: number[]): Point[] => ahead.map((date, index) => ({ date, close: series[index] }))
  const projected = path[path.length - 1]
  const changePct = ((projected - last) / last) * 100
  const tested = backtest(sample, model, seed)

  return {
    model,
    label: LABELS[model],
    horizon,
    last,
    projected,
    changePct,
    path: toPoints(path),
    low: toPoints(low),
    high: toPoints(high),
    history,
    backtest: tested,
    reading: readingFor(tested.directionHit),
    note:
      model === "holt"
        ? "Sequence smoothing carries the latest level and a capped drift. The band is the recent one-step miss, widened with the horizon."
        : "This model estimates the next session's return, then lets that impulse fade. The band widens because later sessions are less sure.",
  }
}

export function projectAll(values: number[], dates: string[], horizon: number, seed: number) {
  return (["holt", "boost", "forest"] as ModelId[]).map((model) => project(values, dates, model, horizon, seed))
}
