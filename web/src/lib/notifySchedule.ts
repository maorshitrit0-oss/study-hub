// When he gets notifications (Israel time): Sun-Thu 08:00 and 20:00, Friday 08:00 only, Saturday 20:00 only.
const MORNING_DAYS = [0, 1, 2, 3, 4, 5]; // Sunday..Friday
const EVENING_DAYS = [0, 1, 2, 3, 4, 6]; // Sunday..Thursday, Saturday
const WINDOW_MIN = 20; // a call up to 20 minutes after the hour still counts

/** "daily" (morning digest), "evening" (recordings reminder) or null, for a moment in time. */
export function notifySlot(at: Date): "daily" | "evening" | null {
  const parts = Object.fromEntries(new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Jerusalem", weekday: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23",
  }).formatToParts(at).map((p) => [p.type, p.value]));
  const weekday = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(parts.weekday);
  const hour = Number(parts.hour), minute = Number(parts.minute);
  if (minute > WINDOW_MIN) return null;
  if (hour === 8 && MORNING_DAYS.includes(weekday)) return "daily";
  if (hour === 20 && EVENING_DAYS.includes(weekday)) return "evening";
  return null;
}
