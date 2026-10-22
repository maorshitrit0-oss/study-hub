/** Minimal iCalendar (VEVENT) parser for the Moodle calendar export. */
export type IcsEvent = { uid: string; summary: string; start: Date; categories: string; description: string };

export function parseIcs(text: string): IcsEvent[] {
  // Unfold continuation lines (RFC 5545: CRLF followed by a space or tab).
  const lines = text.replace(/\r?\n[ \t]/g, "").split(/\r?\n/);
  const events: IcsEvent[] = [];
  let cur: Record<string, string> | null = null;
  for (const line of lines) {
    if (line === "BEGIN:VEVENT") cur = {};
    else if (line === "END:VEVENT" && cur) {
      const start = parseDate(cur.DTEND || cur.DTSTART);
      if (cur.UID && start) {
        events.push({
          uid: cur.UID,
          summary: unescape(cur.SUMMARY || ""),
          start,
          categories: unescape(cur.CATEGORIES || ""),
          description: unescape(cur.DESCRIPTION || ""),
        });
      }
      cur = null;
    } else if (cur) {
      const i = line.indexOf(":");
      if (i > 0) cur[line.slice(0, i).split(";")[0]] = line.slice(i + 1);
    }
  }
  return events;
}

function parseDate(v?: string) {
  if (!v) return null;
  const m = v.match(/^(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2})(\d{2})(Z)?)?/);
  if (!m) return null;
  const [, y, mo, d, h = "23", mi = "59", s = "00", z] = m;
  return z
    ? new Date(Date.UTC(+y, +mo - 1, +d, +h, +mi, +s))
    : new Date(`${y}-${mo}-${d}T${h}:${mi}:${s}+03:00`);
}

function unescape(s: string) {
  return s.replace(/\\n/gi, "\n").replace(/\\([,;\\])/g, "$1");
}
