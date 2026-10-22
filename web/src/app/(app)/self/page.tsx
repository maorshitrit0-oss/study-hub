import Link from "next/link";
import { requireUser } from "@/lib/supabase/server";
import { FREEZES, LEVELS, weekDates, type Skill } from "@/lib/skills";

/** Self-study tracks (outside the university): roadmap, project and a private tutor each. */
export default async function SelfStudy() {
  const { sb } = await requireUser();
  const [{ data: courses }, { data: skills, error }] = await Promise.all([
    sb.from("courses").select("id, name").eq("kind", "self").eq("archived", false).order("created_at"),
    sb.from("skills").select("*").order("ord"),
  ]);
  const { today } = weekDates();
  const freeze = FREEZES.find((f) => today >= f.from && today <= f.to);

  return (
    <div className="space-y-5">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">לימוד עצמי</h1>
        <Link href="/courses/new?kind=self" className="btn-ghost text-sm">+ מסלול</Link>
      </div>
      <p className="text-sm text-muted">לימוד שלך, בלי האוניברסיטה: מפת נושאים, פרויקט, ומורה פרטי שמלמד לפי הכללים שלך.</p>
      {error && <p className="card text-sm text-warn">צריך להריץ את קוד ה-SQL של הלימוד העצמי ב-Supabase.</p>}
      {freeze && <p className="card text-sm text-warn">⏸️ {freeze.text}</p>}
      {(courses ?? []).map((c) => {
        const mine = ((skills ?? []) as Skill[]).filter((s) => s.course_id === c.id);
        const topics = mine.filter((s) => s.kind === "topic");
        const next = topics.find((s) => s.level < 3);
        const nextProject = mine.filter((s) => s.kind === "project").find((s) => s.level < 4);
        return (
          <Link key={c.id} href={`/self/${c.id}`} className="card block space-y-2">
            <h2 className="font-semibold">{c.name}</h2>
            {topics.length > 0 && (
              <>
                <div className="h-1.5 rounded-full bg-bg overflow-hidden">
                  <div className="h-full bg-good" style={{ width: `${(100 * topics.filter((s) => s.level >= 3).length) / topics.length}%` }} />
                </div>
                <p className="text-xs text-muted">{topics.filter((s) => s.level >= 3).length} מתוך {topics.length} נושאים ברמת &quot;פותר ומסביר לבד&quot; ומעלה</p>
              </>
            )}
            {next && <p className="text-sm">▶️ הנושא הבא: {next.title} <span className="text-muted">({LEVELS[next.level]})</span></p>}
            {nextProject && <p className="text-sm">🛠️ בפרויקט: {nextProject.title}</p>}
          </Link>
        );
      })}
      {!courses?.length && !error && <p className="card text-sm text-muted">עוד אין מסלולים. לחץ &quot;+ מסלול&quot;.</p>}
    </div>
  );
}
