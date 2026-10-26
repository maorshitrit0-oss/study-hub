import Link from "next/link";
import { requireUser } from "@/lib/supabase/server";
import { classMeetings, type Missing } from "@/lib/recordings";
import { isSiteLesson, paceAlerts, studyWeek, semesterWeek, STUDY_LAG, todayWeek, weekDays } from "@/lib/week";
import { lessonName } from "@/lib/types";

const KIND: Record<string, string> = { lecture: "הרצאה", practice: "תרגול" };
const ddmm = (d: string) => `${d.slice(8, 10)}/${d.slice(5, 7)}`;
const DAY = ["א׳", "ב׳", "ג׳", "ד׳", "ה׳", "ו׳", "ש׳"];

function Row({ m }: { m: Missing }) {
  const when = `${KIND[m.slot.kind] ?? m.slot.title} · יום ${DAY[m.slot.weekday]} ${ddmm(m.date)}`;
  if (m.noRecording) return <li className="py-2 flex justify-between text-sm"><span>{when}</span><span className="text-muted">אין הקלטה</span></li>;
  if (!m.lesson) {
    return (
      <li className="py-2 flex justify-between text-sm">
        <span>{when}</span>
        <Link href={`/courses/${m.slot.course_id}`} className="text-bad">📹 לא הועלה ←</Link>
      </li>
    );
  }
  const l = m.lesson;
  const state = l.status !== "ready" ? "⏳ בעיבוד" : l.read_at ? "✅ נקרא" : "📖 לקרוא";
  return (
    <li className="py-2 flex justify-between text-sm">
      <span>{when}</span>
      <Link href={`/lessons/${l.id}`} className={l.read_at ? "text-muted" : "text-accent"}>{state} · {lessonName(l)} ←</Link>
    </li>
  );
}

/** His week: he learns one week behind the semester; what that week had per course, and what is left from before. */
export default async function Week({ searchParams }: PageProps<"/week">) {
  const { sb } = await requireUser();
  const sp = await searchParams;
  const current = studyWeek();
  const w = Math.max(1, Number(sp.w) || current);
  const { start, end } = weekDays(w);
  const [{ held }, { data: courses }, { data: site }, pace] = await Promise.all([
    classMeetings(sb),
    sb.from("courses").select("id, name, kind").eq("archived", false).order("name"),
    sb.from("lessons").select("id, course_id, kind, number, title, source_url, status, read_at").eq("kind", "web").eq("number", w),
    paceAlerts(sb).catch(() => []),
  ]);
  const name = new Map((courses ?? []).map((c) => [c.id, c.name as string]));
  const thisWeek = held.filter((m) => m.date >= start && m.date <= end);
  const behind = held.filter((m) => m.date < start && !m.noRecording && (!m.lesson || !m.lesson.read_at));
  const lastYear = (site ?? []).filter((l) => isSiteLesson(l) && l.status === "ready");
  const byCourse = (ms: Missing[]) => [...new Set(ms.map((m) => m.slot.course_id!))]
    .map((id) => [id, ms.filter((m) => m.slot.course_id === id)] as const)
    .sort((a, b) => (name.get(a[0]) ?? "").localeCompare(name.get(b[0]) ?? ""));

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <Link href={`/week?w=${w - 1}`} className={`text-accent ${w <= 1 ? "invisible" : ""}`}>→ שבוע {w - 1}</Link>
        <div className="text-center">
          <h1 className="text-2xl font-bold">שבוע לימוד {w}</h1>
          <p className="text-sm text-muted">{ddmm(start)}-{ddmm(end)} · בסמסטר עכשיו שבוע {todayWeek()}{w === current ? " (אתה שבוע אחורה, בכוונה)" : ""}</p>
        </div>
        <Link href={`/week?w=${w + 1}`} className={`text-accent ${w >= todayWeek() ? "invisible" : ""}`}>שבוע {w + 1} ←</Link>
      </div>

      {pace.length > 0 && (
        <section className="card border-warn">
          <h2 className="font-semibold mb-2">⚡ להגביר קצב - יש הגשה על חומר שעוד לא הגעת אליו</h2>
          <ul className="space-y-1 text-sm">
            {pace.map((p) => (
              <li key={p.title + p.due_at}>
                <b>{name.get(p.course_id)}</b>: {p.title} - הגשה {new Date(p.due_at).toLocaleDateString("he-IL", { timeZone: "Asia/Jerusalem" })}.
                כדאי להגיע עד שבוע {p.need} (אתה בשבוע {current}).
              </li>
            ))}
          </ul>
        </section>
      )}

      {thisWeek.length === 0 && lastYear.length === 0 ? (
        <p className="card text-muted">לא היו שיעורים בשבוע הזה לפי מערכת השעות.</p>
      ) : byCourse(thisWeek).map(([id, ms]) => (
        <section key={id} className="card">
          <Link href={`/courses/${id}`} className="font-semibold">{name.get(id)}</Link>
          <ul className="divide-y divide-line mt-1">{ms.map((m) => <Row key={m.slot.id + m.date} m={m} />)}</ul>
          {lastYear.filter((l) => l.course_id === id).map((l) => (
            <Link key={l.id} href={`/lessons/${l.id}`} className="block text-sm text-muted mt-2">📼 החומר של שבוע {w} משנה שעברה ←</Link>
          ))}
        </section>
      ))}

      {lastYear.filter((l) => !thisWeek.some((m) => m.slot.course_id === l.course_id)).map((l) => (
        <Link key={l.id} href={`/lessons/${l.id}`} className="card block">
          <span className="font-semibold">{name.get(l.course_id)}</span>
          <span className="block text-sm text-muted">📼 החומר של שבוע {w} משנה שעברה (אתר המרצה) ←</span>
        </Link>
      ))}

      {behind.length > 0 && (
        <section className="card">
          <h2 className="font-semibold mb-1">להשלים משבועות קודמים</h2>
          {byCourse(behind).map(([id, ms]) => (
            <div key={id} className="mt-2">
              <p className="text-sm font-medium">{name.get(id)}</p>
              <ul className="divide-y divide-line">{ms.map((m) => <Row key={m.slot.id + m.date} m={m} />)}</ul>
            </div>
          ))}
        </section>
      )}

      <p className="text-xs text-muted">
        שבוע הלימוד = שבוע הסמסטר פחות {STUDY_LAG}. ההגשות והמבחנים נשארים בתאריכים האמיתיים (במסך המשימות).
        שבוע {semesterWeek(start)} בסמסטר התחיל ב-{ddmm(start)}.
      </p>
    </div>
  );
}
