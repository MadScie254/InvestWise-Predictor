import { getNews } from "@/lib/data"

export const dynamic = "force-dynamic"

export const metadata = { title: "Briefing" }

function when(value: string) {
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  return new Intl.DateTimeFormat("en-KE", {
    timeZone: "Africa/Nairobi",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(parsed)
}

export default async function BriefingPage() {
  const stories = await getNews().catch(() => [])
  return (
    <section>
      <div className="section-head">
        <h1>Briefing</h1>
        <p>
          Headlines from a public Kenya news search. Tone is a word count on the title, not a reading of the full article. Times are East Africa time.
        </p>
      </div>
      {stories.length ? (
        <ul className="stories">
          {stories.map((story) => (
            <li key={story.url}>
              <h3><a href={story.url} rel="noreferrer">{story.title}</a></h3>
              <p className="meta">{story.source}, {when(story.published)}, {story.tone}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p className="note">The briefing did not load. Try again in a minute.</p>
      )}
      </section>
  )
}
