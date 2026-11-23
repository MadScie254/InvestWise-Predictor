import assert from "node:assert/strict"
import test from "node:test"
import { parseBoardHtml } from "./nse.ts"
import { scoreHeadline } from "./sentiment.ts"

const html = `
<html><body>
<p>Nov 20, 2026 at 12:58</p>
<table>
<tr><th>NASI Index</th><th>Year-to-Date</th><th>Market Cap.</th></tr>
<tr><td>237.86 (-1.82)</td><td>+51.28 (27.48%)</td><td>KES 4.06Tr</td></tr>
</table>
<table>
<tr><th>Ticker</th><th>Name</th><th>Volume</th><th>Price</th><th>Change</th></tr>
<tr>
  <td><a href="/nse/scom.html" title="Safaricom Plc">SCOM</a></td>
  <td><a href="/nse/scom.html" title="Safaricom Plc">Safaricom Plc</a></td>
  <td>5,739,197</td><td>34.20</td><td>-0.20</td>
</tr>
<tr>
  <td><a href="/nse/eqty.html" title="Equity Group Holdings Ltd">EQTY</a></td>
  <td>Equity Group Holdings Ltd</td>
  <td>1,547,447</td><td>97.50</td><td>-1.75</td>
</tr>
</table>
</body></html>
`

test("parses a Nairobi board page", () => {
  const board = parseBoardHtml(html)
  assert.equal(board.stale, false)
  assert.equal(board.asOf, "2026-11-20")
  assert.equal(board.nasi, 237.86)
  assert.equal(board.ytdPct, 27.48)
  assert.equal(board.rows.length, 2)
  assert.equal(board.rows[0].ticker, "SCOM")
  assert.equal(board.rows[0].price, 34.2)
  assert.equal(board.rows[0].volume, 5739197)
  assert.equal(board.rows[1].name, "Equity Group Holdings Ltd")
})

test("headline tone is counted from words", () => {
  assert.equal(scoreHeadline("Kenya records growth and a surplus").tone, "constructive")
  assert.equal(scoreHeadline("Bank warns of default and a debt crisis").tone, "strained")
  assert.equal(scoreHeadline("Market opens for the week").tone, "mixed")
})
