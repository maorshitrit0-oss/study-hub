import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import SkillRow from "@/components/SkillRow";
import { addSkill } from "@/app/(app)/actions";
import { FREEZES, weekDates, type Skill } from "@/lib/skills";
import DeadlineRow from "@/components/DeadlineRow";
import type { Deadline } from "@/lib/types";

const WEEK_TARGET = 3; // three 20-minute sessions a week (his plan)

export default async function Track({ params }: PageProps<"/self/[id]">) {
  const { id } = await params;
  const { sb } = await requireUser();
  const { weekStart, today } = weekDates();
  const [{ data: course }, { data: skills }, { data: msgs }, { data: deadlines }] = await Promise.all([
    sb.from("courses").select("id, name, notes").eq("id", id).maybeSingle(),
    sb.from("skills").select("*").eq("course_id", id).order("ord"),
    sb.from("chat_messages").select("created_at").eq("course_id", id).eq("role", "user").gte("created_at", weekStart),
    sb.from("deadlines").select("*").eq("course_id", id).eq("done", false).order("due_at"),
  ]);
  if (!course) notFound();
  const list = (skills ?? []) as Skill[];
  const sessions = new Set((msgs ?? []).map((m) => m.created_at.slice(0, 10))).size;
  const freeze = FREEZES.find((f) => today >= f.from && today <= f.to);

  return (
    <div className="space-y-5">
      <Link href="/self" className="text-sm text-accent">→ לימוד עצמי</Link>
      <h1 className="text-2xl font-bold">{course.name}</h1>
      {freeze && <p className="card text-sm text-warn">⏸️ {freeze.text}</p>}

      <div className="grid grid-cols-2 gap-3">
        <Link href={`/self/${id}/chat`} className="card text-center font-medium">🎓 למפגש עם המורה</Link>
        <div className="card text-center">
          <div className="text-xl font-bold">{sessions} / {WEEK_TARGET}</div>
          <div className="text-xs text-muted">ימי לימוד השבוע</div>
        </div>
      </div>

      <section className="card">
        <h2 className="font-semibold mb-1">מפת הלימוד</h2>
        <p className="text-xs text-muted mb-2">נושא נחשב סגור רק אחרי שתי שאלות חדשות שפתרת והסברת בעצמך. המורה מעדכן את הרמה אחרי כל מפגש, ואפשר גם לשנות ידנית.</p>
        <ul className="divide-y divide-line">{list.filter((s) => s.kind === "topic").map((s) => <SkillRow key={s.id} s={s} />)}</ul>
      </section>

      <section className="card">
        <h2 className="font-semibold mb-2">הפרויקט</h2>
        <ul className="divide-y divide-line">{list.filter((s) => s.kind === "project").map((s) => <SkillRow key={s.id} s={s} />)}</ul>
        {(deadlines ?? []).length > 0 && <ul className="mt-2">{((deadlines ?? []) as Deadline[]).map((d) => <DeadlineRow key={d.id} d={d} />)}</ul>}
      </section>

      <form action={addSkill.bind(null, id)} className="card space-y-2">
        <h2 className="font-semibold">הוספת נושא או שלב</h2>
        <div className="flex gap-2">
          <input className="input flex-1" name="title" required placeholder="למשל: מכונת מצבים (FSM)" />
          <select className="input w-28" name="kind" defaultValue="topic">
            <option value="topic">נושא</option>
            <option value="project">פרויקט</option>
          </select>
        </div>
        <button className="btn w-full">הוספה</button>
      </form>

      {course.notes && (
        <details className="card">
          <summary className="cursor-pointer font-semibold">ההקשר והכללים שהמורה עובד לפיהם</summary>
          <p className="text-sm whitespace-pre-line mt-3">{course.notes}</p>
          <Link href={`/courses/${id}/edit`} className="text-sm text-accent mt-2 inline-block">עריכה</Link>
        </details>
      )}
    </div>
  );
}
