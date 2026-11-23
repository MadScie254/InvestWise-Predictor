"use client"

import { useEffect, useState } from "react"
import { formatDay, formatPercent } from "@/lib/format"
import {
  currentUser,
  loadSaved,
  loginUser,
  openGuest,
  registerUser,
  signOut,
  type DeskUser,
  type SavedForecast,
} from "@/lib/local-desk"

export default function AccountPage() {
  const [user, setUser] = useState<DeskUser | null>(null)
  const [saved, setSaved] = useState<SavedForecast[]>([])
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [message, setMessage] = useState("")
  const [mode, setMode] = useState<"register" | "login">("register")

  useEffect(() => {
    setUser(currentUser())
    setSaved(loadSaved())
  }, [])

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setMessage("")
    try {
      const next = mode === "register"
        ? await registerUser(name, email, password)
        : await loginUser(email, password)
      setUser(next)
      setPassword("")
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "That did not save.")
    }
  }

  function guest(event: React.FormEvent) {
    event.preventDefault()
    setUser(openGuest(name))
  }

  function leave() {
    signOut()
    setUser(null)
  }

  return (
    <section>
      <div className="section-head">
        <h1>Account</h1>
        <p>
          Your name, password hash, pins, alerts, and saved forecasts stay in this browser. A different computer will not see this desk. Nothing here is sent to a paid database.
        </p>
      </div>
      {user ? (
        <div>
          <p className="quote-num">{user.name}</p>
          <p className="note">{user.email || "Guest on this browser."}</p>
          <div className="actions">
            <button className="button quiet" type="button" onClick={leave}>Sign out</button>
          </div>
          <h2>Kept forecasts</h2>
          {saved.length ? saved.map((item) => (
            <div className="saved" key={item.id}>
              <span>{item.label}, {item.model}, {item.horizon} sessions</span>
              <span className={item.changePct >= 0 ? "up" : "down"}>{formatPercent(item.changePct)}, {formatDay(item.savedAt)}</span>
            </div>
          )) : <p className="note">Run a forecast and keep it if you want it here.</p>}
        </div>
      ) : (
        <div className="two">
          <form onSubmit={submit}>
            <h2>{mode === "register" ? "Create a desk" : "Open a desk"}</h2>
            {mode === "register" ? (
              <label className="field">
                <span>Name</span>
                <input value={name} onChange={(event) => setName(event.target.value)} required />
              </label>
            ) : null}
            <label className="field">
              <span>Email</span>
              <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
            </label>
            <label className="field">
              <span>Password</span>
              <input type="password" minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} required />
            </label>
            <div className="actions">
              <button className="button" type="submit">{mode === "register" ? "Create desk" : "Open desk"}</button>
              <button className="button quiet" type="button" onClick={() => setMode(mode === "register" ? "login" : "register")}>
                {mode === "register" ? "I already have one" : "I need a new one"}
              </button>
            </div>
            {message ? <p className="error">{message}</p> : null}
          </form>
          <form onSubmit={guest}>
            <h2>Use this browser only</h2>
            <p className="note">No password. The desk exists until you clear the site data.</p>
            <label className="field">
              <span>Name</span>
              <input value={name} onChange={(event) => setName(event.target.value)} required />
            </label>
            <button className="button quiet" type="submit">Continue</button>
          </form>
        </div>
      )}
    </section>
  )
}
