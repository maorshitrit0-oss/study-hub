import { requireUser } from "@/lib/supabase/server";
import SlotCard from "@/components/SlotCard";
import WeekGrid from "@/components/WeekGrid";
import Fold from "@/components/Fold";
import SlotForm from "@/components/SlotForm";
import { addSlot } from "../actions";
import { israelNow } from "@/lib/format";
import { DAYS, EXAM_LABEL, type Course, type Slot } from "@/lib/types";
import { courseSummaries } from "@/lib/facts";

export default async function Schedule() {
  const { sb } = await requireUser();
  const [{ data: slots }, { data: courses }] = await Promise.all([
    sb.from("schedule_slots").select("*").order("weekday").order("start_time"),
    sb.from("courses").select("id, name, user_id, kind, exam_type, grade_weights").eq("archived", false).order("name"),
  ]);
  const summaries = await courseSummaries(sb, (courses ?? []) as { id: string; user_id: string }[]);
  const names = new Map((courses ?? []).map((c) => [c.id, c.name]));
  const now = israelNow();
  const all = (slots ?? []) as Slot[];
  // Start the week from today so the next classes are on top.
  const order = Array.from({ length: 7 }, (_, k) => (now.weekday + k) % 7).filter((d) => all.some((s) => s.weekday === d));

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold">מערכת שעות</h1>
      {all.length > 0 && <WeekGrid slots={all} names={names} today={now.weekday} nowTime={now.time} />}
      <Fold id="schedule-list" title="רשימה מלאה ועריכה" hint={`${all.length} שיעורים`}>
      <div className="space-y-5">
      {order.length ? (
        order.map((d) => (
          <section key={d}>
            <h2 className={`text-sm mb-2 ${d === now.weekday ? "text-accent font-semibold" : "text-muted"}`}>
              יום {DAYS[d]}{d === now.weekday ? " · היום" : ""}
            </h2>
            <div className="space-y-2">
              {all.filter((s) => s.weekday === d).map((s) => (
                <SlotCard key={s.id} s={s} courseName={s.course_id ? names.get(s.course_id) : undefined}
                  now={d === now.weekday && s.start_time.slice(0, 5) <= now.time && now.time < s.end_time.slice(0, 5)} />
              ))}
            </div>
          </section>
        ))
      ) : (
        <p className="text-muted">עוד אין שיעורים במערכת.</p>
      )}
      </div>
      </Fold>
      {/* Under each course: grade components, exam format, formula sheet (only when allowed) - 04/11/2026. */}
      <Fold id="schedule-courses" title="📋 הקורסים: ציון ומבחן" hint={`${(courses ?? []).filter((c) => c.kind !== "self").length}`}>
        <ul className="divide-y divide-line">
          {(courses ?? []).filter((c) => c.kind !== "self").map((c) => {
            const sm = summaries.get(c.id) ?? {};
            const weights = (c.grade_weights as Course["grade_weights"] | null) ?? [];
            const grade = sm.grade || (weights.length ? weights.map((w) => `${w.weight}% ${w.name}`).join(", ") : "");
            const exam = sm.exam || (c.exam_type ? EXAM_LABEL[c.exam_type as keyof typeof EXAM_LABEL] : "");
            return (
              <li key={c.id} className="py-2.5 text-sm space-y-0.5">
                <p className="font-semibold">{c.name}</p>
                {grade && <p>📊 <span className="text-muted">ציון:</span> {grade}</p>}
                {exam && <p>📝 <span className="text-muted">בחינה:</span> {exam}</p>}
                {sm.formula_sheet && <p>📄 <span className="text-muted">דף נוסחאות:</span> {sm.formula_sheet}</p>}
                {!grade && !exam && <p className="text-xs text-muted">עוד לא נאמר בשיעורים או בסילבוס.</p>}
              </li>
            );
          })}
        </ul>
      </Fold>
      <details className="card">
        <summary className="cursor-pointer font-semibold">+ הוספת שיעור</summary>
        <div className="mt-3"><SlotForm action={addSlot} courses={courses ?? []} submit="הוספה" /></div>
      </details>
    </div>
  );
}
