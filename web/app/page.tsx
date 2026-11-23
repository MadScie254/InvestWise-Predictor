import Link from "next/link"
import { Chart } from "@/components/Chart"
import { getBoard, getMacro, getSeries } from "@/lib/data"
import { hashSeed, project } from "@/lib/forecast"
import { formatDay, formatNumber, formatPercent, toneClass } from "@/lib/format"

export const dynamic = "force-dynamic"

export default async function HomePage() {
  const [shilling, brent, board, macro] = await Promise.all([
    getSeries("USDKES=X").catch(() => null),
    getSeries("BZ=F").catch(() => null),
    getBoard().catch(() => null),
    getMacro().catch(() => null),
  ])

  const growth = macro?.find((item) => item.id === "NY.GDP.MKTP.KD.ZG")?.points.at(-1)
  const inflation = macro?.find((item) => item.id === "FP.CPI.TOTL.ZG")?.points.at(-1)
  let forecast = null
  if (shilling && shilling.points.length >= 80) {
    forecast = project(
      shilling.points.map((point) => point.close),
      shilling.points.map((point) => point.date),
      "holt",
      30,
      hashSeed(`home:${shilling.asOf}`),
    )
  }
  const history = forecast?.history || shilling?.points.slice(-180) || []

  return (
    <>
      <section className="hero">
        <div>
          <h1>Check the shilling, the Nairobi board, and a forecast before you commit money.</h1>
          <p className="lede">
            InvestWise is a research desk for people allocating capital in Kenya. It reads public prices and runs three small statistical models on this site. It does not place trades, and it does not need a paid database.
          </p>
          <div className="actions">
            <Link className="button" href="/markets">Open markets</Link>
            <Link className="button quiet" href="/forecast">Run a forecast</Link>
          </div>
          <dl className="facts">
            <div>
              <dt>NASI</dt>
              <dd>{board?.nasi != null ? formatNumber(board.nasi) : "Waiting"}</dd>
            </div>
            <div>
              <dt>GDP growth{growth ? `, ${growth.year}` : ""}</dt>
              <dd>{growth ? formatPercent(growth.value) : "Waiting"}</dd>
            </div>
            <div>
              <dt>Inflation{inflation ? `, ${inflation.year}` : ""}</dt>
              <dd>{inflation ? formatPercent(inflation.value) : "Waiting"}</dd>
            </div>
            <div>
              <dt>Brent</dt>
              <dd className={toneClass(brent?.change || 0)}>{brent ? formatNumber(brent.last) : "Waiting"}</dd>
            </div>
          </dl>
        </div>
        <div className="hero-chart">
          <p className="pair">Shilling per dollar</p>
          {shilling ? (
            <>
              <p className="num">{formatNumber(shilling.last)}</p>
              <p className={`delta ${toneClass(shilling.change)}`}>
                {formatPercent(shilling.changePct)} from the prior close, {formatDay(shilling.asOf)}
              </p>
              {history.length > 1 ? (
                <Chart
                  history={history}
                  forecast={forecast?.path}
                  low={forecast?.low}
                  high={forecast?.high}
                  currency="KES"
                />
              ) : null}
              <p className="caption">
                Daily closes. The copper line is a 30-session sequence forecast. It is a sketch of the drift, not a promise.
              </p>
            </>
          ) : (
            <p className="note">The dollar rate did not load. The markets page will try again.</p>
          )}
        </div>
      </section>

      <section className="methods">
        <div>
          <h2>Three readings of the next stretch</h2>
          <p>Each one is fit on the prices you can see. You can compare them before you trust any of them.</p>
        </div>
        <div>
          <article className="method">
            <h3>Sequence smoothing</h3>
            <p>Holt's method keeps a level and a drift, then caps that drift at a large recent daily move. It is the first look for a rate or a commodity.</p>
          </article>
          <article className="method">
            <h3>Boosted stumps</h3>
            <p>Short rules correct one another on recent returns. The impulse is allowed to fade, because a one-day signal should not be compounded forever.</p>
          </article>
          <article className="method">
            <h3>Random forest</h3>
            <p>A stand of short trees votes on the next return. The band is the disagreement among the trees, widened as the horizon gets longer.</p>
          </article>
        </div>
      </section>

      <section className="split">
        <div>
          <h2>If you are starting something, not only buying a share</h2>
          <p>
            The venture desk scores a short list of Kenyan trades against your capital, your county, and the macro picture from the World Bank. It is a match, not a business plan.
          </p>
        </div>
        <div className="actions">
          <Link className="button" href="/ventures">Score a venture</Link>
          <Link className="button quiet" href="/briefing">Read the briefing</Link>
        </div>
      </section>
    </>
  )
}
