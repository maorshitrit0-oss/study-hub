import BackLink from "@/components/BackLink";
import { requireUser } from "@/lib/supabase/server";
import Quiz from "@/components/Quiz";
import { weeklyReview } from "@/lib/review";
import { lessonName, type Lesson } from "@/lib/types";

/**
 * 🔁 Weekly review (his request 17/11/2026, instead of the daily one): Saturday night, understanding questions only
 * (no formulas), from the lessons he marked read this week - nothing else.
 */
export default async function Review() {
  const { sb } = await requireUser();
  const [{ lessons, questions }, { data: courses }] = await Promise.all([
    weeklyReview(sb),
    sb.from("courses").select("id, name"),
  ]);
  const names = new Map((courses ?? []).map((c) => [c.id, c.name]));
  const byCourse = new Map<string, string[]>();
  for (const l of lessons) byCourse.set(l.course_id, [...(byCourse.get(l.course_id) ?? []), lessonName(l as Lesson)]);

  return (
    <div className="space-y-4">
      <BackLink href={"/"}>→ דף הבית</BackLink>
      <h1 className="text-2xl font-bold">🔁 חזרה שבועית</h1>
      <p className="text-sm text-muted">
        שאלות הבנה (בלי חישובים ונוסחאות) רק מהשיעורים שסימנת כנקראו בשבוע האחרון. כל מוצאי שבת מגיעה תזכורת.
      </p>
      {byCourse.size > 0 && (
        <section className="card text-sm space-y-1">
          <p className="font-semibold">מה למדת השבוע:</p>
          {[...byCourse].map(([id, ls]) => <p key={id}><b>{names.get(id)}:</b> {ls.join(", ")}</p>)}
        </section>
      )}
      <div className="card">
        {questions.length ? (
          <>
            <p className="text-sm text-muted mb-3">{questions.length} שאלות · קודם שאלות שטעית בהן או שעוד לא ענית עליהן</p>
            <Quiz key={questions.map((q) => q.id).join()} questions={questions} title="חזרה שבועית" />
          </>
        ) : (
          <p className="text-muted">עוד לא סימנת השבוע שיעור כנקרא – השאלות יופיעו כאן אחרי &quot;✓ סיימתי&quot; בשיעורים.</p>
        )}
      </div>
    </div>
  );
}
