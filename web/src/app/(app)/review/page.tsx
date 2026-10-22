import Link from "next/link";
import { requireUser } from "@/lib/supabase/server";
import Quiz from "@/components/Quiz";
import { dueReviews } from "@/lib/review";

const SESSION = 15;

/** Daily spaced review: questions answered before come back after 1, 3, 7, 14, 30, 60 days (sooner after a mistake). */
export default async function Review({ searchParams }: PageProps<"/review">) {
  const courseId = (await searchParams).course as string | undefined;
  const { sb } = await requireUser();
  const [{ total, questions }, { data: courses }] = await Promise.all([
    dueReviews(sb, courseId),
    sb.from("courses").select("id, name").eq("archived", false).order("name"),
  ]);
  const set = questions.slice(0, SESSION);
  const names = new Map((courses ?? []).map((c) => [c.id, c.name]));
  const perCourse = new Map<string, number>();
  for (const q of questions) perCourse.set(q.course_id, (perCourse.get(q.course_id) ?? 0) + 1);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">🔁 חזרה יומית</h1>
      <p className="text-sm text-muted">
        שאלות שכבר ענית עליהן חוזרות במרווחים שגדלים: אחרי יום, 3 ימים, שבוע, שבועיים, חודש וחודשיים. טעות מחזירה את השאלה למחרת.
      </p>
      {perCourse.size > 1 && (
        <div className="flex flex-wrap gap-2">
          <Link href="/review" className={`chip ${!courseId ? "border-accent" : ""}`}>הכל ({total})</Link>
          {[...perCourse].map(([id, n]) => <Link key={id} href={`/review?course=${id}`} className="chip">{names.get(id)} ({n})</Link>)}
        </div>
      )}
      <div className="card">
        {set.length ? (
          <>
            <p className="text-sm text-muted mb-3">{total > SESSION ? `${SESSION} מתוך ${total} שאלות שהגיע זמנן` : `${total} שאלות שהגיע זמנן`}</p>
            <Quiz key={set.map((q) => q.id).join()} questions={set} title="חזרה" />
          </>
        ) : (
          <p className="text-muted">אין היום שאלות לחזרה 🎉 הן יופיעו כאן אחרי שתענה על שאלונים בפרקים.</p>
        )}
      </div>
    </div>
  );
}
