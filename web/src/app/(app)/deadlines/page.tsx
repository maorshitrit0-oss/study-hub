import { requireUser } from "@/lib/supabase/server";
import DeadlineRow from "@/components/DeadlineRow";
import { addDeadline } from "../actions";
import type { Course, Deadline } from "@/lib/types";

export default async function Deadlines({ searchParams }: PageProps<"/deadlines">) {
  const preset = (await searchParams).course as string | undefined;
  const { sb } = await requireUser();
  const [{ data: courses }, { data: deadlines }] = await Promise.all([
    sb.from("courses").select("id, name").eq("archived", false).order("name"),
    sb.from("deadlines").select("*").order("due_at"),
  ]);
  const names = new Map((courses as Course[] | null)?.map((c) => [c.id, c.name]));
  const all = (deadlines ?? []) as Deadline[];
  const open = all.filter((d) => !d.done);
  const closed = all.filter((d) => d.done).reverse().slice(0, 20);

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold">משימות ומבחנים</h1>

      <section className="card">
        {open.length ? (
          <ul className="divide-y divide-line">
            {open.map((d) => <DeadlineRow key={d.id} d={d} courseName={d.course_id ? names.get(d.course_id) : undefined} />)}
          </ul>
        ) : <p className="text-muted text-sm">אין משימות פתוחות 🎉</p>}
      </section>

      <section className="card">
        <h2 className="font-semibold mb-3">הוספה</h2>
        <form action={addDeadline} className="space-y-3">
          <input className="input" name="title" required placeholder="מטלה 3 / מבחן מועד א / דוח מכין ניסוי 2" />
          <div className="grid grid-cols-2 gap-3">
            <select className="input" name="kind" defaultValue="assignment">
              <option value="assignment">מטלה</option>
              <option value="exam">מבחן</option>
              <option value="quiz">בוחן</option>
              <option value="lab_report">דוח מעבדה</option>
              <option value="other">אחר</option>
            </select>
            <select className="input" name="course_id" defaultValue={preset ?? ""}>
              <option value="">ללא קורס</option>
              {(courses ?? []).map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <input className="input" name="due_at" type="datetime-local" required />
          <button className="btn w-full">הוספה</button>
        </form>
      </section>

      {closed.length > 0 && (
        <details className="card">
          <summary className="cursor-pointer font-medium">בוצעו</summary>
          <ul className="divide-y divide-line mt-2">
            {closed.map((d) => <DeadlineRow key={d.id} d={d} courseName={d.course_id ? names.get(d.course_id) : undefined} />)}
          </ul>
        </details>
      )}
    </div>
  );
}
