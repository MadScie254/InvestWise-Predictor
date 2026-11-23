export type DeskUser = {
  id: string
  name: string
  email: string
  salt: string
  passwordHash: string
}

export type AlertRule = {
  id: string
  symbol: string
  label: string
  direction: "above" | "below"
  price: number
  currency: string
}

export type SavedForecast = {
  id: string
  symbol: string
  label: string
  model: string
  horizon: number
  changePct: number
  savedAt: string
}

function read<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback
  try {
    const raw = window.localStorage.getItem(key)
    return raw ? (JSON.parse(raw) as T) : fallback
  } catch {
    return fallback
  }
}

function write(key: string, value: unknown) {
  window.localStorage.setItem(key, JSON.stringify(value))
}

export function loadUsers() {
  return read<DeskUser[]>("iw-users", [])
}

export function loadSession() {
  return read<string | null>("iw-session", null)
}

export function currentUser() {
  const id = loadSession()
  if (!id) return null
  return loadUsers().find((user) => user.id === id) || null
}

export function saveSession(id: string | null) {
  if (!id) window.localStorage.removeItem("iw-session")
  else window.localStorage.setItem("iw-session", JSON.stringify(id))
}

export async function hashPassword(password: string, saltHex: string) {
  const salt = Uint8Array.from(saltHex.match(/.{2}/g)!.map((byte) => Number.parseInt(byte, 16)))
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveBits"])
  const bits = await crypto.subtle.deriveBits({ name: "PBKDF2", salt, iterations: 120000, hash: "SHA-256" }, key, 256)
  return [...new Uint8Array(bits)].map((byte) => byte.toString(16).padStart(2, "0")).join("")
}

export function freshSalt() {
  const bytes = crypto.getRandomValues(new Uint8Array(16))
  return [...bytes].map((byte) => byte.toString(16).padStart(2, "0")).join("")
}

export async function registerUser(name: string, email: string, password: string) {
  const users = loadUsers()
  const normalized = email.trim().toLowerCase()
  if (users.some((user) => user.email === normalized)) throw new Error("That email already has a desk on this browser.")
  const salt = freshSalt()
  const user: DeskUser = {
    id: crypto.randomUUID(),
    name: name.trim(),
    email: normalized,
    salt,
    passwordHash: await hashPassword(password, salt),
  }
  write("iw-users", [...users, user])
  saveSession(user.id)
  return user
}

export async function loginUser(email: string, password: string) {
  const normalized = email.trim().toLowerCase()
  const user = loadUsers().find((item) => item.email === normalized)
  if (!user || !user.passwordHash) throw new Error("No desk on this browser uses that email.")
  const hash = await hashPassword(password, user.salt)
  if (hash !== user.passwordHash) throw new Error("The password does not match.")
  saveSession(user.id)
  return user
}

export function openGuest(name: string) {
  const user: DeskUser = {
    id: crypto.randomUUID(),
    name: name.trim() || "Guest",
    email: "",
    salt: "",
    passwordHash: "",
  }
  write("iw-users", [...loadUsers(), user])
  saveSession(user.id)
  return user
}

export function signOut() {
  saveSession(null)
}

export function loadAlerts() {
  return read<AlertRule[]>("iw-alerts", [])
}

export function saveAlerts(alerts: AlertRule[]) {
  write("iw-alerts", alerts)
}

export function loadSaved() {
  return read<SavedForecast[]>("iw-forecasts", [])
}

export function loadPins() {
  return read<string[]>("iw-pins", ["SCOM", "EQTY", "KCB", "EABL"])
}

export function savePins(pins: string[]) {
  write("iw-pins", pins)
}

export function saveForecast(entry: SavedForecast) {
  const next = [entry, ...loadSaved()].slice(0, 12)
  write("iw-forecasts", next)
  return next
}
