import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from '@/components/ui/toaster'
import { QueryProvider } from '@/components/query-provider'
import { AuthProvider } from '@/components/auth-provider'
import { Navigation } from '@/components/navigation'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'InvestWise Predictor',
  description: 'AI-powered investment predictions and financial insights',
  keywords: ['investment', 'AI', 'predictions', 'finance', 'machine learning'],
  authors: [{ name: 'InvestWise Team' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AuthProvider>
            <QueryProvider>
              <div className="relative flex min-h-screen flex-col">
                <Navigation />
                <main className="flex-1">{children}</main>
              </div>
              <Toaster />
            </QueryProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}