import type { Metadata } from "next"
import { Figtree, Newsreader } from "next/font/google"
import { Shell } from "@/components/Shell"
import "./globals.css"

const sans = Figtree({ subsets: ["latin"], variable: "--font-sans", display: "swap" })
const display = Newsreader({
  subsets: ["latin"],
  style: ["normal", "italic"],
  variable: "--font-display",
  display: "swap",
})

export const metadata: Metadata = {
  title: { default: "InvestWise", template: "%s, InvestWise" },
  description: "A research desk for Kenyan investors. Public prices, the Nairobi board, and forecasts you can inspect.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sans.variable} ${display.variable}`} suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `try{var t=localStorage.getItem("iw-theme");if(t==="dark"||(!t&&matchMedia("(prefers-color-scheme: dark)").matches))document.documentElement.dataset.theme="dark"}catch(e){}`,
          }}
        />
      </head>
      <body>
        <Shell>{children}</Shell>
      </body>
    </html>
  )
}
