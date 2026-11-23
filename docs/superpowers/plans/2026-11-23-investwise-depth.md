# InvestWise Depth Plan

> Decision document. Do not implement until Daniel chooses a path.
> For agentic workers later: REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` only after explicit approval of one path below.

**Goal:** Turn the live InvestWise desk from a shallow shell into a Kenya-first research product that is honest, useful day to day, and still free to run.

**Architecture:** Keep the Next.js app in `web` on Vercel hobby. Deepen models and Kenya data first. Add a free Cloudflare edge layer (D1 or KV plus Worker cron) only when the browser alone cannot hold state or fire alerts. Never claim LSTM, OAuth, or a paid database unless those are actually shipped.

**Tech Stack (allowed):** Next.js 15, TypeScript, SVG charts, Yahoo chart API, World Bank, Google News RSS, AFX or another free Nairobi source, Cloudflare Workers, Cloudflare D1 or KV (free tier), optional free FRED or CBK HTML scrape. No Supabase Pro. No GitHub Actions. No paid market data.

**Live today:** https://investwise-predictor.vercel.app  
**PR:** https://github.com/MadScie254/InvestWise-Predictor/pull/3

---

## Global Constraints

- Free stack only: Vercel hobby, Cloudflare free, browser storage, keyless public APIs.
- No GitHub Actions (account billing lock; owner will not pay).
- No emojis and no em dashes in product copy, README, or PR text.
- Honest labels: if a board is captured, say so. If a model is a coin toss, say so.
- Nairobi share forecasts need real daily history. Do not invent prices.
- Research only. No order routing. No advice framing.

---

## Why it feels shallow

The current desk is a coherent UI over thin evidence.

| Area | What exists | Why it feels thin |
| --- | --- | --- |
| Markets | 9 Yahoo series + World Bank + delayed NSE board | No company pages, no volumes vs price, no sector view, NSE often stale |
| Forecast | Holt, boosted stumps, random forest on closes | No features beyond price, no regimes, no walk-forward report page, NSE names blocked |
| Briefing | Google RSS + word-count tone | Not article understanding, no link to holdings or CBK calendar |
| Ventures | 14 hard-coded ideas + score | Heuristic match, not market-backed, not editable, no sources |
| Alerts | localStorage, check while page open | Useless when the tab is closed |
| Account | PBKDF2 in browser | No sync across devices, no shared desk |
| Chart | One SVG line | No volume, no markers, no compare, no export |
| Depth of Kenya | Copy and a few macros | Missing CBK rate path, T-bill, inflation prints as a timeline, remittances, power, rain |

Depth here means: better evidence, better memory, better daily ritual. Not more marketing claims.

---

## Three paths (choose one)

### Path A: Browser depth only (recommended first cut)

Stay 100% on Vercel + browser. Make the desk feel serious without any new paid or free-database product.

- Richer instruments and compare charts
- Walk-forward forecast reports with feature notes
- CBK / KNBS / World Bank timelines on a Macro page
- Better briefing (entity tags, saved stories)
- Ventures with sources and editable capital math
- Export CSV / PNG of charts and forecasts

**Pros:** Zero new infra. Fits the current deploy. Can ship in small PRs.  
**Cons:** Alerts still die when the tab closes. No multi-device desk.

### Path B: Free edge memory (recommended full product)

Path A plus Cloudflare free tier as the only server memory:

- D1 or KV for desks, pins, alerts, saved forecasts (optional sync by email code or magic link later)
- Worker cron to evaluate alerts a few times per day and email via Resend free or Cloudflare Email Routing
- Cached Nairobi board snapshots written by the Worker when AFX answers

**Pros:** Alerts and sync become real without Supabase. Still free if kept inside quotas.  
**Cons:** More moving parts. Email delivery needs a free provider setup. Auth must stay simple and honest.

### Path C: Real ML lab (not recommended under current budget)

Train LSTM / XGBoost offline, host a Python worker, buy data, OAuth.

**Pros:** Matches the original README fantasy.  
**Cons:** Cost, ops, and honesty risk. Reject unless budget and data access change.

**Recommendation:** Approve **Path A** now. Approve **Path B** as a second decision after A feels deep. Skip C.

---

## Target product (if Path A + B both ship)

A Kenya research desk you open before allocating money.

1. **Morning brief:** shilling move, Brent, NASI or last board, inflation print, three headlines tagged to your pins.
2. **Instrument desk:** one name at a time with history, peers, macro overlays, and a written forecast card with walk-forward stats.
3. **Nairobi board that does not lie:** live when possible, dated snapshot when not, sector filters, pin-driven focus.
4. **Macro wall:** CBK policy rate path, inflation, GDP, USD/KES, Brent on one scrollable timeline.
5. **Ventures workbook:** capital and county in, three ideas out, each with assumptions you can edit and a link to the macro drivers.
6. **Alerts that wake up:** Worker cron checks thresholds; browser is the backup, not the only path.
7. **Desk memory:** optional Cloudflare-backed save so a phone and a laptop can share pins and kept forecasts.

Success test: a user who already knows Kenya finance still finds a reason to open it twice a week. If they would rather open Yahoo and a spreadsheet, the desk is still shallow.

---

## File map (what would change)

### Already central

- `web/lib/data.ts` - upstream fetch, cache, board fallback
- `web/lib/forecast.ts` - models and backtest
- `web/lib/ventures.ts` - scoring
- `web/lib/nse.ts` - board parse + snapshot
- `web/lib/local-desk.ts` - browser memory
- `web/components/Chart.tsx` - SVG chart
- `web/app/*/page.tsx` - routes
- `cloudflare/market-proxy/` - allowlisted fetch

### New under Path A

- `web/lib/features.ts` - returns, volatility, momentum features for models
- `web/lib/walkforward.ts` - rolling evaluation report
- `web/lib/macro-kenya.ts` - CBK / World Bank timeline builders
- `web/lib/briefing.ts` - entity tags against pins and instruments
- `web/app/macro/page.tsx` - Macro wall
- `web/app/name/[symbol]/page.tsx` - single instrument desk
- `web/components/CompareChart.tsx` - multi-series
- `web/data/` - more captured boards, CBK rate history JSON if scrape is awkward

### New under Path B

- `cloudflare/desk-api/` - Worker with D1 or KV
- `cloudflare/desk-api/schema.sql` - desks, pins, alerts, forecasts
- `cloudflare/desk-api/cron.js` - alert evaluation
- `web/lib/remote-desk.ts` - sync client with local fallback
- Env on Vercel: `DESK_API_URL` (public Worker origin only)

---

## Phase plan

Phases are independent enough to stop after any one. Each phase should leave the site deployable.

### Phase 0: Honest product surface (small, do first)

**Outcome:** The site stops reading like a demo of claims it does not keep.

- Rewrite home and Forecast copy so the models are named for what they are.
- Add a Methods page that shows the three models, the 80-day rule, and the NSE limit.
- Show data freshness on every panel (asOf, stale flag, source).
- Add a “What this is not” footer block once, not on every page.

**Done when:** A skeptical reader cannot accuse the UI of LSTM or live NSE when those are absent.

### Phase 1: Markets depth (Path A)

**Outcome:** Markets feels like a desk, not a ticker list.

1. Instrument page `/name/[symbol]` with history chart, change table (1d, 5d, 20d, 60d), and blurb.
2. Compare mode: overlay USD/KES vs Brent, or S&P vs EZA.
3. Nairobi board: sector or name search that stays sticky, volume leaders, gainers and losers from the same snapshot, pin strip at top.
4. Attempt a second free board source (if AFX stays dead). Candidates: scrape-friendly public pages only; keep snapshot fallback.
5. Capture a weekly board JSON in-repo when live fetch fails, with session date in the UI.

**Done when:** A user can study one FX name and the Nairobi board without leaving Markets feeling empty.

### Phase 2: Forecast depth (Path A)

**Outcome:** Forecasts feel inspectable, not magical.

1. Feature set on closes: log return, 5/20 day momentum, realized vol, distance from 20-day mean.
2. Keep Holt as the simple baseline. Upgrade boost and forest to use those features.
3. Walk-forward panel: for the last N windows, show direction hit, MAPE, and max drawdown of errors.
4. Regime note: calm vs noisy based on recent vol percentile. Soften claims in noisy regimes.
5. Peer table already exists; add “why this model won today” in one sentence from the walk-forward numbers.
6. Still refuse NSE tickers until a free daily history exists. If one is found, add it as a first-class series.

**Done when:** Running a forecast produces a short report a finance student would respect, even when the call is weak.

### Phase 3: Macro wall (Path A)

**Outcome:** Kenya context is a page, not four cells.

1. New `/macro` route.
2. World Bank series as charts, not only a table.
3. Add a CBK policy rate history file (curated JSON is fine if scrape is brittle).
4. Overlay shilling and Brent on the same page.
5. Ventures and Forecast can deep-link into Macro drivers.

**Done when:** Inflation, growth, policy rate, and USD/KES can be read in one sitting.

### Phase 4: Briefing that knows your desk (Path A)

**Outcome:** News is filtered by what you care about.

1. Tag headlines for shilling, oil, NSE, CBK, named pins (SCOM, EQTY, and so on).
2. Split the page into “On your pins” and “Wider Kenya”.
3. Keep tone as word-count, but label it “headline tone” always.
4. Save up to 20 stories in localStorage.
5. Optional: pull one CBK or KNBS press RSS if stable and keyless.

**Done when:** A user with SCOM pinned sees Safaricom-related headlines first.

### Phase 5: Ventures workbook (Path A)

**Outcome:** Ventures stops feeling like a random quiz.

1. Show the score breakdown (capital fit, risk, county, inflation, shilling, Brent).
2. Allow editing assumptions (rent, daily sales, margin) with a simple contribution margin sketch.
3. Attach 1 to 3 source links per idea (public articles or Kenya agency pages).
4. Save scored runs on the desk.
5. Add a clear disclaimer that this is matching, not licensing or credit advice.

**Done when:** A founder can argue with the score and leave with a note they wrote themselves.

### Phase 6: Chart and export craft (Path A)

**Outcome:** The visual desk matches the ambition of the brand.

1. Multi-series compare chart.
2. Markers for forecast join, hover that shows date and value (already partial).
3. Export CSV of series and forecast path.
4. Print-friendly Methods + Forecast report.
5. Keep the Ledger look. No card grids. No purple AI aesthetic.

**Done when:** Someone can paste a chart or CSV into a WhatsApp or email without screenshot pain.

### Phase 7: Free edge memory and alerts (Path B only)

**Outcome:** The desk works when the laptop is closed.

1. Cloudflare Worker `desk-api` with D1 tables: `desks`, `pins`, `alerts`, `forecasts`.
2. Device linking via a one-time code shown on Account (no OAuth required in v1).
3. Cron every few hours: evaluate alerts against Yahoo or board snapshot; send email if configured.
4. Browser remains the offline cache. Remote sync is optional and labeled.
5. Keep secrets out of the client. Public Worker URL only.

**Done when:** An alert can fire without the Alerts page being open, on the free Cloudflare quota.

### Phase 8: Optional later (only if Path A+B succeed)

- Multi-language (Swahili UI strings).
- Risk score for a tiny manual portfolio of pins.
- Blockchain or broker links: only with a real partner, never as decoration.
- True LSTM: only with offline training artifacts and a clear “experimental” badge.

---

## Implementation task outline (after approval)

This is the shape of the engineering work. Detailed TDD steps belong in a follow-on plan once a path is chosen.

### If Path A is approved

1. Phase 0 copy and Methods page.
2. Phase 1 instrument page + compare + board tools.
3. Phase 2 features + walk-forward.
4. Phase 3 Macro wall.
5. Phase 4 briefing tags.
6. Phase 5 ventures workbook.
7. Phase 6 chart export.

Ship order is the phase order. Stop after any phase.

### If Path B is approved after A

1. D1 schema + Worker CRUD for desk objects.
2. Account one-time code link flow.
3. Cron alert evaluator + email.
4. Board snapshot writer on Worker when AFX answers.
5. Point Vercel `DESK_API_URL` at the Worker.

### Testing standard for every phase

- Unit tests next to `web/lib/*` for pure logic.
- Manual browser pass on desktop and 390px width.
- Deploy preview on Vercel from the feature branch.
- No GitHub Actions.

---

## Effort shape (technical, not calendar)

| Phase | Invasiveness | Main risk |
| --- | --- | --- |
| 0 | Copy and one route | Low |
| 1 | New route, data helpers | Finding a live NSE source |
| 2 | Core model rewrite | Overfitting fancy features on thin series |
| 3 | New route + curated JSON | CBK scrape brittleness |
| 4 | Briefing rewrite | RSS noise |
| 5 | Ventures UX + math | Looking like advice |
| 6 | Chart component growth | Visual clutter |
| 7 | New Worker + schema | Free-tier limits, email setup |

Path A alone is a series of contained PRs on `web`. Path B is a second subsystem with its own deploy.

---

## Explicit non-goals (unless budget changes)

- Supabase, Mongo, Postgres on a paid host
- Google / LinkedIn OAuth
- Claiming trained LSTM or XGBoost without shipping training code and artifacts
- Broker execution
- GitHub Actions
- Fabricated NSE daily history

---

## Decision checklist for Daniel

Pick one:

1. **Path A only** - deepen the current free desk in the browser.
2. **Path A then B** - deepen first, then add Cloudflare memory and real alerts.
3. **Path B first** - not recommended; alerts without depth still feel shallow.
4. **Do nothing** - keep the live site as the research sketch it is.
5. **Custom mix** - name the phases you want (for example 0, 1, 2, 3 only).

Also answer, when ready:

- Is email-based alert delivery acceptable on a free provider?
- Is a curated CBK rate JSON (hand maintained) acceptable, or must it be scraped live?
- Should Ventures stay founder-oriented, or tilt more toward investor screening?

---

## Self-review

- Shallow diagnosis covered: markets, forecast, news, ventures, alerts, account, Kenya depth.
- Free-stack constraint preserved across all phases.
- Paths A/B/C are mutually clear; C rejected under budget.
- Phases can stop independently.
- No implementation started in this document’s companion work.
