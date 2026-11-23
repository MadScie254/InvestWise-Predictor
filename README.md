# InvestWise Predictor

## Table of Contents

1. [Introduction](#introduction)
2. [Project Overview](#project-overview)
3. [Key Features](#key-features)
4. [Technology Stack](#technology-stack)
5. [Installation Guide](#installation-guide)
6. [Usage Instructions](#usage-instructions)
7. [API Integration](#api-integration)
8. [Database Schema](#database-schema)
9. [Security Considerations](#security-considerations)
10. [Performance Optimization](#performance-optimization)
11. [Contributing](#contributing)
12. [License](#license)
13. [Future Plans](#future-plans)
14. [Acknowledgments](#acknowledgments)
15. [Contact Information](#contact-information)
16. [Appendix](#appendix)

---

## Introduction

InvestWise Predictor is a research desk for people allocating capital in Kenya. It reads public prices, prints a short statistical forecast, and scores a few small-business ideas against the capital and county you enter. It does not place trades, and it does not need a paid database.

The application that runs is in `web`. Older notes in this repository describe drafts that were never wired to a live site.

---

## Project Overview

### What is InvestWise Predictor?

A desk for reading the shilling, the Nairobi board, and a forecast before committing money. It is a sketch, not a broker.

- **Prices**: Daily closes for the shilling, the euro, the pound, Brent, gold, coffee, wheat, the S&P 500, and a Johannesburg ETF used only as a regional stand-in.
- **Nairobi board**: A delayed public list. If the live page does not answer, the last captured session stays on the desk and is marked as such.
- **Forecasts**: Sequence smoothing, boosted stumps, and a small random forest, each with a recent direction hit and a typical miss.
- **Ventures**: Fourteen Kenyan trades scored against capital, county, risk, inflation, the shilling, and Brent.
- **Account**: A name and a password hash that stay in this browser.

---

## Key Features

### 1. Market page

Daily closes, World Bank figures for Kenya, and the Nairobi board. Pin a name and it stays on this browser.

### 2. Forecast

Three models on series that publish a long daily history:

- **Sequence smoothing**: Holt's method, for a level and a capped drift. This is the practical time-series reading.
- **Boosted stumps**: short rules that correct one another, then fade.
- **Random forest**: a stand of short trees voting on the next return.

Forecasts run on rates, commodities, and two global equity series that publish long daily history. Nairobi quotes stay on the board until a free source publishes a long enough daily file.

### 3. Charts

One SVG chart. History is ink, the forecast is copper, and the band is the recent miss widened with the horizon.

### 4. Briefing

Headlines from a public Kenya news search. Tone is a word count on the title, not a reading of the article. Times are East Africa time.

### 5. Alerts

Set a price and the open Alerts page checks it about once a minute. There is no background watcher, because that would need a paid job.

### 6. Light and dark

The theme is stored in this browser and applied before the page paints.

---

## Technology Stack

This version is built to run on free tiers. There is no Supabase project and no paid database.

### Application

- **Framework**: Next.js, in the `web` directory
- **Charts**: drawn as SVG in the app, so there is no chart vendor to license
- **Accounts, pins, alerts, saved forecasts**: stored in the browser
- **Forecasts**: sequence smoothing (Holt), boosted stumps, and a small random forest, fit on the prices the page just loaded

### Data, all keyless

- **Rates and commodities**: Yahoo Finance chart endpoint (dollar, euro, pound, Brent, gold, coffee, wheat, S&P 500, and a Johannesburg ETF used only as a regional stand-in)
- **Nairobi board**: the public AFX board. If that page does not answer, the desk shows the last captured session and says so
- **Kenya macro**: World Bank API (GDP growth, inflation, unemployment, GDP per person)
- **Briefing**: Google News RSS, with a word-count tone on the headline

### Hosting

- **App**: Vercel hobby plan, root directory `web`
- **Edge fetch**: a Cloudflare Worker in `cloudflare/market-proxy` caches the four allowlisted sources and is used only when a direct fetch fails. Set `MARKET_PROXY_URL` to the worker origin if you deploy it.

---

## Installation Guide

To set up and run the InvestWise Predictor locally, follow the steps below:

### Prerequisites

- Node.js 20 or newer
- npm
- Git

No database is required.

### Step 1: Clone the Repository

```bash
git clone https://github.com/MadScie254/InvestWise-Predictor.git
cd InvestWise-Predictor
```

### Step 2: Install and start

```bash
cd web
npm install
npm test
npm run dev
```

Open `http://localhost:3000`. Tests run on your machine. This repository does not use GitHub Actions.

### Optional: Cloudflare proxy

```bash
cd cloudflare/market-proxy
npx wrangler deploy
```

Then set `MARKET_PROXY_URL` on the Vercel project to the worker origin, including `https` and without a trailing path. The worker only forwards four public hosts.

---

## Usage Instructions

Once the application is running, you can explore its features as follows:

### 1. Home

The home page prints the shilling, a thirty-session sketch, and four facts: NASI, GDP growth, inflation, and Brent.

### 2. Account

Create a desk with an email and password, or continue as a guest. The password is hashed in the browser and never leaves the machine. Signing in on another computer will not find the account.

### 3. Markets

Open Markets to move across a series, read the World Bank table, search the Nairobi board, and pin a name.

### 4. Forecast

Open Forecast, choose a series with a long public history, pick a model and a horizon, and run it. The page shows the path, a widening band, and how often the same model got the recent direction right. Nairobi share quotes are not forecast here, because the free board does not publish enough daily history.

### 5. Account, alerts, ventures

Kept forecasts appear on Account. Alerts fire only while that page is open. Ventures scores three ideas from the capital and county you type.

---

## API Integration

The app exposes its own routes. They cache briefly at the edge.

- `GET /api/series?symbol=USDKES=X`
- `GET /api/board`
- `GET /api/macro`
- `GET /api/news`
- `GET /api/forecast?symbol=BZ=F&model=holt&horizon=20`

`model` is `holt`, `boost`, or `forest`.

---

## What is stored

Nothing is stored on a server. In this browser, local storage holds:

| Key | Contents |
| --- | --- |
| `iw-users` | Name, email, salt, and a PBKDF2 password hash |
| `iw-session` | The id of the open desk |
| `iw-alerts` | Price alerts |
| `iw-pins` | Pinned Nairobi tickers |
| `iw-forecasts` | Forecasts you chose to keep |
| `iw-theme` | Light or dark |

---

## Security Considerations

Security is paramount for any financial application. InvestWise Predictor implements the following measures to safeguard user data:

1. Passwords are hashed with PBKDF2 in the browser and are not sent to a server.
2. The Cloudflare proxy allowlists four public hosts and refuses every other address.
3. Page text is rendered as text. News links open the publisher, they are not injected as HTML.
4. Forecast routes only accept the series and models the desk knows.

---

## Performance Optimization

Series, the board, macro figures, and headlines are cached in memory for a few minutes, and the API routes send a short shared cache header. The forecast is computed when you ask for it.

---

## Contributing

We welcome contributions from the community! To contribute to InvestWise Predictor, please follow these guidelines:

1. Fork the repository and create a new branch for your feature or bug fix.
2. Ensure your changes adhere to the coding standards outlined in the [Code of Conduct](CODE_OF_CONDUCT.md).
3. Submit a pull request with a clear description of your changes.

For more details, refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file.

---

## License

InvestWise Predictor is open-source software licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---

## Future Plans

We are continuously improving InvestWise Predictor to meet the evolving needs of our users. Some upcoming features include:

- Enhanced ML models for improved accuracy.
- Multi-language support for global accessibility.
- Advanced risk assessment tools.
- Integration with blockchain-based platforms.

Stay tuned for updates!

---

## Acknowledgments

Public series come from Yahoo Finance chart data, the World Bank API, Google News, and the AFX Nairobi board.

---

## Contact Information

Daniel Wanjala Machimbo
[dmwanjala254@gmail.com](mailto:dmwanjala254@gmail.com)
[LinkedIn](https://www.linkedin.com/in/daniel-wanjala-91)
[GitHub](https://github.com/MadScie254)

---

## Appendix

Older write-ups in this repository (`README_COMPLETE.md`, `IMPLEMENTATION_COMPLETE.md`, `TESTING_GUIDE.md`) describe a draft stack. The running application is `web`.

## Troubleshooting

1. **The Nairobi board says it is a captured session.** The public board page did not answer. Rates, commodities, and the World Bank figures are separate and can still be live.
2. **A forecast is refused.** The series needs at least 80 daily closes. Nairobi quotes from the free board are too short, so they stay on Markets.
3. **The app does not start.** Run `npm install` inside `web`, with Node 20 or newer.

## Use cases

1. **Individual investors.** Read the shilling, Brent, and the Nairobi board before deciding an entry.
2. **Founders.** Score a venture against capital, county, and the latest inflation print.
3. **Analysts.** Compare three models on the same series and read the recent miss rate before quoting a path.

## Contact

Daniel Wanjala Machimbo
[dmwanjala254@gmail.com](mailto:dmwanjala254@gmail.com)
[LinkedIn](https://www.linkedin.com/in/daniel-wanjala-91)
[GitHub](https://github.com/MadScie254)
