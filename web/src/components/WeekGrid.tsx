import Link from "next/link";
import { DAYS, type Slot } from "@/lib/types";

const HOUR_PX = 34;
const KIND: Record<string, string> = { lecture: "", practice: "תרגול", lab: "מעבדה", other: "" };
const TONE: Record<string, string> = { lecture: "bg-accent/25 border-accent", practice: "bg-good/20 border-good", lab: "bg-warn/25 border-warn", other: "bg-bg border-line" };

/** A short name that fits a narrow column on the phone. */
function short(name: string) {
  const rules: [RegExp, string][] = [[/גלים/, "גלים"], [/תקשורת/, "תקשורת"], [/ספרתי|digital/i, "ספרתיים"], [/java/i, "Java"],
    [/מיקרו/, "מיקרו"], [/לינאר|ליניאר/, "לינאריים"], [/מעבדה\s*(\d+)/, "מעבדה $1"]];
  for (const [re, label] of rules) {
    const m = name.match(re);
    if (m) return label.replace("$1", m[1] ?? "");
  }
  return name.split(/\s+/).slice(0, 2).join(" ");
}

const minutes = (t: string) => Number(t.slice(0, 2)) * 60 + Number(t.slice(3, 5));

/** The week as a table: days across (Sunday on the right), hours down - readable on a phone. */
export default function WeekGrid({ slots, names, today, nowTime }: {
  slots: Slot[]; names: Map<string, string>; today: number; nowTime: string;
}) {
  const days = [0, 1, 2, 3, 4, 5, 6].filter((d) => d <= 4 || slots.some((s) => s.weekday === d));
  const first = Math.min(8 * 60, ...slots.map((s) => minutes(s.start_time)));
  const last = Math.max(17 * 60, ...slots.map((s) => minutes(s.end_time)));
  const from = Math.floor(first / 60), to = Math.ceil(last / 60);
  const hours = Array.from({ length: to - from }, (_, k) => from + k);
  const top = (t: string) => ((minutes(t) - from * 60) / 60) * HOUR_PX;

  return (
    <div className="card p-2">
      <div className="grid" style={{ gridTemplateColumns: `2rem repeat(${days.length}, minmax(0, 1fr))` }}>
        <div />
        {days.map((d) => (
          <div key={d} className={`text-center text-xs pb-1 ${d === today ? "text-accent font-bold" : "text-muted"}`}>{DAYS[d]}</div>
        ))}
        <div className="relative" style={{ height: hours.length * HOUR_PX }}>
          {hours.map((h) => (
            <div key={h} className="absolute text-[10px] text-muted" style={{ top: (h - from) * HOUR_PX - 6 }}>{h}</div>
          ))}
        </div>
        {days.map((d) => (
          <div key={d} className={`relative border-s border-line ${d === today ? "bg-accent-soft" : ""}`} style={{ height: hours.length * HOUR_PX }}>
            {hours.map((h) => <div key={h} className="absolute inset-x-0 border-t border-line/50" style={{ top: (h - from) * HOUR_PX }} />)}
            {d === today && minutes(nowTime) >= from * 60 && minutes(nowTime) <= to * 60 && (
              <div className="absolute inset-x-0 border-t-2 border-bad z-10" style={{ top: top(nowTime) }} />
            )}
            {slots.filter((s) => s.weekday === d).map((s) => {
              const name = s.course_id ? names.get(s.course_id) ?? s.title : s.title;
              return (
                <Link key={s.id} href={s.course_id ? `/courses/${s.course_id}` : "#"}
                  className={`absolute inset-x-0.5 rounded-md border px-0.5 overflow-hidden leading-tight ${TONE[s.kind] ?? TONE.other}`}
                  style={{ top: top(s.start_time) + 1, height: Math.max(18, top(s.end_time) - top(s.start_time) - 2) }}>
                  <span className="block text-[10px] font-semibold truncate">{short(name)}</span>
                  {KIND[s.kind] && <span className="block text-[9px] truncate">{KIND[s.kind]}</span>}
                  <span className="block text-[9px] text-muted truncate">{s.start_time.slice(0, 5)}</span>
                </Link>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}
