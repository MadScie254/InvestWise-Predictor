"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useEffect, useState } from "react"

const LINKS = [
  ["/markets", "Markets"],
  ["/forecast", "Forecast"],
  ["/briefing", "Briefing"],
  ["/ventures", "Ventures"],
  ["/alerts", "Alerts"],
  ["/account", "Account"],
]

export function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname()
  const [theme, setTheme] = useState<"light" | "dark">("light")

  useEffect(() => {
    const stored = window.localStorage.getItem("iw-theme")
    const next = stored === "dark" || stored === "light"
      ? stored
      : window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light"
    document.documentElement.dataset.theme = next
    setTheme(next)
  }, [])

  function toggleTheme() {
    const next = theme === "dark" ? "light" : "dark"
    document.documentElement.dataset.theme = next
    window.localStorage.setItem("iw-theme", next)
    setTheme(next)
  }

  return (
    <div className="frame">
      <a className="skip" href="#content">Skip to content</a>
      <header className="top">
        <Link className="mark" href="/">InvestWise</Link>
        <nav>
          {LINKS.map(([href, label]) => (
            <Link key={href} href={href} aria-current={path === href ? "page" : undefined}>
              {label}
            </Link>
          ))}
        </nav>
        <button className="theme" type="button" onClick={toggleTheme}>
          {theme === "dark" ? "Light" : "Dark"}
        </button>
      </header>
      <div className="page" id="content">{children}</div>
      <footer className="foot">
        Research only. InvestWise does not take orders and does not hold client money. Prices can be delayed.
      </footer>
    </div>
  )
}
