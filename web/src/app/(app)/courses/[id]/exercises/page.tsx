import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import Exercises from "@/components/Exercises";
import ReadExerciseFiles from "@/components/ReadExerciseFiles";
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
  const { forWeek, fileExercises } = await exercisesByWeek(sb, id);
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
          <Exercises items={allFiles} />
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
              <h2 className="font-semibold mb-1">מבחנים ושיעורי בית על הנושאים של השבוע</h2>
              <Exercises items={fromFiles} />
            </section>
          )}
        </>
      )}
      <ReadExerciseFiles courseId={id} />
    </div>
  );
}
