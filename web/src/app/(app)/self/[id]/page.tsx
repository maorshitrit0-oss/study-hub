import Link from "next/link";
import TrackTabs from "@/components/TrackTabs";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import SkillRow from "@/components/SkillRow";
import Fold from "@/components/Fold";
import { addSkill } from "@/app/(app)/actions";
import { FREEZES, weekDates, type Skill } from "@/lib/skills";
import { ensureSyllabus, parseModules } from "@/lib/vlsiSyllabus";
import DeadlineRow from "@/components/DeadlineRow";
import type { Deadline } from "@/lib/types";

const WEEK_TARGET = 3; // three 20-minute sessions a week (his plan)

export default async function Track({ params }: PageProps<"/self/[id]">) {
  const { id } = await params;
  const { sb } = await requireUser();
  const { weekStart, today } = weekDates();
  const [{ data: course }, { data: skills }, { data: msgs }, { data: deadlines }, { data: tracks }] = await Promise.all([
    sb.from("courses").select("id, name, notes, syllabus_topics").eq("id", id).maybeSingle(),
    sb.from("skills").select("*").eq("course_id", id).order("ord"),
    sb.from("chat_messages").select("created_at").eq("course_id", id).eq("role", "user").gte("created_at", weekStart),
    sb.from("deadlines").select("*").eq("course_id", id).eq("done", false).order("due_at"),
    sb.from("courses").select("id, name").eq("kind", "self").eq("archived", false).order("created_at"),
  ]);
  if (!course) notFound();
  let list = (skills ?? []) as Skill[];
  let modulesRaw = course.syllabus_topics;
  // His VLSI track gets the syllabus once (existing topics keep their level).
  if (/VLSI/i.test(course.name) && await ensureSyllabus(sb, id, list, modulesRaw).catch(() => false)) {
    const [{ data: s2 }, { data: c2 }] = await Promise.all([
      sb.from("skills").select("*").eq("course_id", id).order("ord"),
      sb.from("courses").select("syllabus_topics").eq("id", id).single(),
    ]);
    list = (s2 ?? []) as Skill[];
    modulesRaw = c2?.syllabus_topics;
  }
  const modules = parseModules(modulesRaw);
  const topics = list.filter((s) => s.kind === "topic");
  const groups = modules.length
    ? modules.map((m, i) => ({ ...m, items: topics.filter((t) => t.ord >= m.from && (i + 1 >= modules.length || t.ord < modules[i + 1].from)) }))
    : [{ from: 1, title: "", goal: "", items: topics }];
  const sessions = new Set((msgs ?? []).map((m) => m.created_at.slice(0, 10))).size;
  const freeze = FREEZES.find((f) => today >= f.from && today <= f.to);

  return (
    <div className="space-y-5">
      <Link href="/self" className="text-sm text-accent">→ לימוד עצמי</Link>
      <TrackTabs tracks={tracks ?? []} current={id} />
      <h1 className="text-2xl font-bold">{course.name}</h1>
      {freeze && <p className="card text-sm text-warn">⏸️ {freeze.text}</p>}

      <div className="grid grid-cols-2 gap-3">
        <Link href={`/self/${id}/chat`} className="card text-center font-medium">🎓 למפגש עם המורה</Link>
        <div className="card text-center">
          <div className="text-xl font-bold">{sessions} / {WEEK_TARGET}</div>
          <div className="text-xs text-muted">ימי לימוד השבוע</div>
        </div>
      </div>

      <Fold id="self-map" title="מפת הלימוד" hint={`סגורים ${topics.filter((t) => t.level >= 3).length}/${topics.length}`}>
        <p className="text-xs text-muted mb-2">נושא נחשב סגור רק אחרי שתי שאלות חדשות שפתרת והסברת בעצמך. המורה מעדכן את הרמה אחרי כל מפגש, ואפשר גם לשנות ידנית.</p>
        {groups.map((g) => {
          const done = g.items.filter((t) => t.level >= 3).length;
          return (
            <details key={g.title || "all"} open={!g.title || (done < g.items.length && g.items.some((t) => t.level > 0))} className="mt-2">
              {g.title && (
                <summary className="cursor-pointer font-medium">
                  {g.title} <span className="text-xs text-muted">({done}/{g.items.length})</span>
                  <span className="block text-xs text-muted font-normal">{g.goal}</span>
                </summary>
              )}
              <ul className="divide-y divide-line">{g.items.map((s) => <SkillRow key={s.id} s={s} />)}</ul>
            </details>
          );
        })}
      </Fold>

      <Fold id="self-project" title="הפרויקט" hint={`${list.filter((s) => s.kind === "project").length} שלבים`}>
        <ul className="divide-y divide-line">{list.filter((s) => s.kind === "project").map((s) => <SkillRow key={s.id} s={s} />)}</ul>
        {(deadlines ?? []).length > 0 && <ul className="mt-2">{((deadlines ?? []) as Deadline[]).map((d) => <DeadlineRow key={d.id} d={d} />)}</ul>}
      </Fold>

      <Fold id="self-add" title="➕ הוספת נושא או שלב">
      <form action={addSkill.bind(null, id)} className="space-y-2">
        <div className="flex gap-2">
          <input className="input flex-1" name="title" required placeholder="למשל: מכונת מצבים (FSM)" />
          <select className="input w-28" name="kind" defaultValue="topic">
            <option value="topic">נושא</option>
            <option value="project">פרויקט</option>
          </select>
        </div>
        <button className="btn w-full">הוספה</button>
      </form>
      </Fold>

      {course.notes && (
        <Fold id="self-rules" title="ההקשר והכללים שהמורה עובד לפיהם">
          <p className="text-sm whitespace-pre-line">{course.notes}</p>
          <Link href={`/courses/${id}/edit`} className="text-sm text-accent mt-2 inline-block">עריכה</Link>
        </Fold>
      )}
    </div>
  );
}
