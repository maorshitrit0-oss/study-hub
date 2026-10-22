const TZ = "Asia/Jerusalem";

export function fmtDue(iso: string) {
  return new Intl.DateTimeFormat("he-IL", {
    weekday: "short", day: "numeric", month: "numeric", hour: "2-digit", minute: "2-digit", timeZone: TZ,
  }).format(new Date(iso));
}

export function daysLeft(iso: string) {
  const d = (new Date(iso).getTime() - Date.now()) / 864e5;
  if (d < 0) return "עבר";
  if (d < 1) return "היום";
  if (d < 2) return "מחר";
  return `עוד ${Math.floor(d)} ימים`;
}

export function urgency(iso: string) {
  const d = (new Date(iso).getTime() - Date.now()) / 864e5;
  return d < 2 ? "bad" : d < 7 ? "warn" : "muted";
}

/** ISO timestamp `days` from now (request-time helper for server components). */
export const isoFromNow = (days: number) => new Date(Date.now() + days * 864e5).toISOString();
export const isPast = (iso: string) => new Date(iso).getTime() < Date.now();

/** "2026-11-03T14:00" typed in Israel (summer or winter time) -> UTC ISO string. */
export function israelLocalToIso(local: string) {
  const value = local.length <= 10 ? `${local}T23:59` : local;
  const guess = new Date(`${value}:00Z`);
  const offset = new Intl.DateTimeFormat("en-US", { timeZone: TZ, timeZoneName: "longOffset" })
    .formatToParts(guess).find((p) => p.type === "timeZoneName")?.value.replace("GMT", "") || "+02:00";
  return new Date(`${value}:00${offset}`).toISOString();
}

/** UTC ISO -> value for <input type="datetime-local"> in Israel time. */
export function isoToIsraelLocal(iso: string) {
  const p = Object.fromEntries(
    new Intl.DateTimeFormat("en-CA", {
      timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23",
    }).formatToParts(new Date(iso)).map((x) => [x.type, x.value]),
  );
  return `${p.year}-${p.month}-${p.day}T${p.hour}:${p.minute}`;
}
