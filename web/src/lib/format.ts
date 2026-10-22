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
