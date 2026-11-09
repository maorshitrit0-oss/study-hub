import BackLink from "@/components/BackLink";
import Link from "next/link";
import { requireUser } from "@/lib/supabase/server";
import { attachOrphanTasks, syncPrepTasks } from "@/lib/prep";
import { syncExerciseTasks } from "@/lib/exercises";
import { syncLabTasks } from "@/lib/labTasks";
import { rollOverdueTasks } from "@/lib/rollTasks";
import { semesterWeek, syncWeekTasks, todayWeek, weekDays } from "@/lib/week";

const israelDay = (iso: string) => new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Jerusalem" }).format(new Date(iso));
import DeadlineRow from "@/components/DeadlineRow";
import DeadlineForm from "@/components/DeadlineForm";
import { addDeadline } from "../actions";
import type { Course, Deadline } from "@/lib/types";

export default async function Deadlines({ searchParams }: PageProps<"/deadlines">) {
  const preset = (await searchParams).course as string | undefined;
  const { sb } = await requireUser();
  await Promise.all([syncPrepTasks(sb).catch(() => {}), attachOrphanTasks(sb).catch(() => {}), syncWeekTasks(sb).catch(() => {}), syncExerciseTasks(sb).catch(() => {}), syncLabTasks(sb).catch(() => {})]);
  await rollOverdueTasks(sb).catch(() => {}); // after the syncs: a study task whose date passed moves to next week
  const [{ data: courses }, { data: deadlines }] = await Promise.all([
    sb.from("courses").select("id, name").eq("archived", false).order("name"),
    sb.from("deadlines").select("*").neq("kind", "exam").order("due_at"),
  ]);
  const names = new Map((courses as Course[] | null)?.map((c) => [c.id, c.name]));
  const all = (deadlines ?? []) as Deadline[];
  const open = all.filter((d) => !d.done);
  const closed = all.filter((d) => d.done).reverse().slice(0, 20);
  const thisWeek = todayWeek();
  const byWeek = new Map<number, Deadline[]>();
  for (const d of open) {
    const w = Math.max(thisWeek, semesterWeek(israelDay(d.due_at)));
    byWeek.set(w, [...(byWeek.get(w) ?? []), d]);
  }
  const weeks = [...byWeek.entries()].sort((a, b) => a[0] - b[0]);

  return (
    <div className="space-y-5">
      <BackLink href={"/"}>→ דף הבית</BackLink>
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">משימות</h1>
        <Link href="/exams" className="btn-ghost text-sm">לוח מבחנים</Link>
      </div>
      <p className="text-sm text-muted -mt-3">לחיצה על משימה פותחת עריכה. העיגול מסמן שבוצעה.</p>

      {/* By week (his request 09/11/2026: "too many tasks"): this week open, the following weeks folded. */}
      {open.length ? weeks.map(([w, list]) => (
        <details key={w} className="card" open={w <= thisWeek}>
          <summary className="cursor-pointer font-semibold flex justify-between">
            <span>{w <= thisWeek ? "📌 השבוע" : `שבוע ${w}`} <span className="text-sm text-muted font-normal">· {weekDays(Math.max(w, thisWeek)).start.slice(8, 10)}/{weekDays(Math.max(w, thisWeek)).start.slice(5, 7)}</span></span>
            <span className="text-sm text-muted">{list.length} משימות</span>
          </summary>
          <ul className="divide-y divide-line mt-2">
            {list.map((d) => <DeadlineRow key={d.id} d={d} courseName={d.course_id ? names.get(d.course_id) : undefined} />)}
          </ul>
        </details>
      )) : <section className="card"><p className="text-muted text-sm">אין משימות פתוחות 🎉</p></section>}

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
