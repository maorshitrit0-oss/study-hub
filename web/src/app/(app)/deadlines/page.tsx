import Link from "next/link";
import { requireUser } from "@/lib/supabase/server";
import { attachOrphanTasks, syncPrepTasks } from "@/lib/prep";
import { syncWeekTasks } from "@/lib/week";
import DeadlineRow from "@/components/DeadlineRow";
import DeadlineForm from "@/components/DeadlineForm";
import { addDeadline } from "../actions";
import type { Course, Deadline } from "@/lib/types";

export default async function Deadlines({ searchParams }: PageProps<"/deadlines">) {
  const preset = (await searchParams).course as string | undefined;
  const { sb } = await requireUser();
  await Promise.all([syncPrepTasks(sb).catch(() => {}), attachOrphanTasks(sb).catch(() => {}), syncWeekTasks(sb).catch(() => {})]);
  const [{ data: courses }, { data: deadlines }] = await Promise.all([
    sb.from("courses").select("id, name").eq("archived", false).order("name"),
    sb.from("deadlines").select("*").neq("kind", "exam").order("due_at"),
  ]);
  const names = new Map((courses as Course[] | null)?.map((c) => [c.id, c.name]));
  const all = (deadlines ?? []) as Deadline[];
  const open = all.filter((d) => !d.done);
  const closed = all.filter((d) => d.done).reverse().slice(0, 20);

  return (
    <div className="space-y-5">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">משימות</h1>
        <Link href="/exams" className="btn-ghost text-sm">לוח מבחנים</Link>
      </div>
      <p className="text-sm text-muted -mt-3">לחיצה על משימה פותחת עריכה. העיגול מסמן שבוצעה.</p>

      <section className="card">
        {open.length ? (
          <ul className="divide-y divide-line">
            {open.map((d) => <DeadlineRow key={d.id} d={d} courseName={d.course_id ? names.get(d.course_id) : undefined} />)}
          </ul>
        ) : <p className="text-muted text-sm">אין משימות פתוחות 🎉</p>}
      </section>

      <section className="card">
        <h2 className="font-semibold mb-3">הוספה</h2>
        <DeadlineForm action={addDeadline} courses={courses ?? []} presetCourse={preset} submit="הוספה" />
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
