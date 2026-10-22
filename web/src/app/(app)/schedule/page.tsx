import { requireUser } from "@/lib/supabase/server";
import SlotCard from "@/components/SlotCard";
import SlotForm from "@/components/SlotForm";
import { addSlot } from "../actions";
import { israelNow } from "@/lib/format";
import { DAYS, type Slot } from "@/lib/types";

export default async function Schedule() {
  const { sb } = await requireUser();
  const [{ data: slots }, { data: courses }] = await Promise.all([
    sb.from("schedule_slots").select("*").order("weekday").order("start_time"),
    sb.from("courses").select("id, name").eq("archived", false).order("name"),
  ]);
  const names = new Map((courses ?? []).map((c) => [c.id, c.name]));
  const now = israelNow();
  const all = (slots ?? []) as Slot[];
  // Start the week from today so the next classes are on top.
  const order = Array.from({ length: 7 }, (_, k) => (now.weekday + k) % 7).filter((d) => all.some((s) => s.weekday === d));

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold">מערכת שעות</h1>
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
      <details className="card">
        <summary className="cursor-pointer font-semibold">+ הוספת שיעור</summary>
        <div className="mt-3"><SlotForm action={addSlot} courses={courses ?? []} submit="הוספה" /></div>
      </details>
    </div>
  );
}
