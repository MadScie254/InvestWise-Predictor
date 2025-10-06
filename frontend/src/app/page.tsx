import { Hero } from '@/components/hero'
import { Features } from '@/components/features'
import { PredictionDemo } from '@/components/prediction-demo'
import { Stats } from '@/components/stats'

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Hero />
      <Features />
      <PredictionDemo />
      <Stats />
    </div>
  )
}