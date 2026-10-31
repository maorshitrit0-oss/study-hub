import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import Exercises from "@/components/Exercises";
import { exercisesByWeek } from "@/lib/exercises";
import { studyWeek, todayWeek, weekDays } from "@/lib/week";

const ddmm = (d: string) => `${d.slice(8, 10)}/${d.slice(5, 7)}`;

/** What to solve: the exercises of one study week (from its lessons + homework/exams on its topics), or all files. */
export default async function CourseExercises({ params, searchParams }: PageProps<"/courses/[id]/exercises">) {
  const { id } = await params;
  const sp = await searchParams;
  const { sb } = await requireUser();
  const { data: course } = await sb.from("courses").select("id, name").eq("id", id).maybeSingle();
  if (!course) notFound();
  const { forWeek, fileExercises, fileReadyWeek } = await exercisesByWeek(sb, id);
  const files = sp.files === "1";
  const w = Math.max(1, Number(sp.w) || studyWeek());
  const { fromLessons, fromFiles } = forWeek(id, w);
  const allFiles = fileExercises(id);
  const { start, end } = weekDays(w);
  const weeks = Array.from({ length: todayWeek() }, (_, k) => k + 1);

  return (
    <div className="space-y-4">
      <Link href={`/courses/${id}`} className="text-sm text-accent">→ {course.name}</Link>
      <h1 className="text-2xl font-bold">✍️ תרגילים</h1>
      <div className="flex gap-2 flex-wrap">
        {weeks.map((x) => (
          <Link key={x} href={`/courses/${id}/exercises?w=${x}`}
            className={`px-3 py-1.5 rounded-xl text-sm ${!files && x === w ? "bg-accent text-white" : "bg-accent-soft text-accent"}`}>
            שבוע {x}{x === studyWeek() ? " (שלי)" : ""}
          </Link>
        ))}
        <Link href={`/courses/${id}/exercises?files=1`}
          className={`px-3 py-1.5 rounded-xl text-sm ${files ? "bg-accent text-white" : "bg-accent-soft text-accent"}`}>
          📂 מכל הקבצים ({allFiles.length})
        </Link>
      </div>

      {files ? (
        <section className="card">
          <h2 className="font-semibold mb-1">שיעורי בית, מבחנים קודמים ודפי תרגילים</h2>
          <p className="text-xs text-muted mb-3">כל תרגיל מקובץ של הקורס, עם פתרון (רשמי אם היה בקובץ). ⭐ = סגנון מבחן.</p>
          {[...new Set(allFiles.map((x) => x.material_id))].map((mid) => {
            const items = allFiles.filter((x) => x.material_id === mid);
            const ready = mid ? fileReadyWeek(id, mid) : null;
            return (
              <div key={mid ?? "none"} className="mt-4">
                <h3 className="font-semibold">📄 {items[0].label ?? "קובץ"}</h3>
                <p className="text-xs text-muted mb-2">
                  {ready ? `אפשר לפתור את כולו אחרי שבוע ${ready}` : "חלק מהחומר שלו עוד לא נלמד - כל תרגיל יעבור לשבוע שלו כשיילמד"}
                  {" · "}{items.filter((x) => x.done_at).length}/{items.length} נפתרו
                </p>
                <Exercises items={items} />
              </div>
            );
          })}
        </section>
      ) : (
        <>
          <section className="card">
            <h2 className="font-semibold mb-1">מהשיעורים של שבוע {w} ({ddmm(start)}-{ddmm(end)})</h2>
            <p className="text-xs text-muted mb-3">לפתור על דף, ורק אחר כך לפתוח את הפתרון.</p>
            {fromLessons.length ? <Exercises items={fromLessons} />
              : <p className="text-sm text-muted">אין עדיין תרגילים מהשבוע הזה. הם נוספים כשמעלים את ההקלטות של ההרצאה והתרגול.</p>}
          </section>
          {fromFiles.length > 0 && (
            <section className="card">
              <h2 className="font-semibold mb-1">מקבצים: שיעורי בית ומבחנים שאפשר לפתור אחרי השבוע הזה</h2>
              <Exercises items={fromFiles} />
            </section>
          )}
        </>
      )}
      <p className="text-xs text-muted">
        כל קובץ שמעלים לקורס נקרא לבד: התרגילים שבו נכנסים לשבוע שאחריו אפשר לפתור אותם, הדגשים למבחן נרשמים במידע על
        הקורס, והנוסחאות נכנסות לדף הנוסחאות.
      </p>
    </div>
  );
}
