import Link from "next/link";
import BackLink from "@/components/BackLink";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import Exercises, { type Exercise } from "@/components/Exercises";
import Fold from "@/components/Fold";
import { exercisesByWeek } from "@/lib/exercises";

/** What to solve: the exercises of one study week (from its lessons + homework/exams on its topics), or all files. */
export default async function CourseExercises({ params, searchParams }: PageProps<"/courses/[id]/exercises">) {
  const { id } = await params;
  const sp = await searchParams;
  const { sb, userId } = await requireUser();
  const { data: course } = await sb.from("courses").select("id, name").eq("id", id).maybeSingle();
  if (!course) notFound();
  const { forWeek, fileExercises, fileReadyWeek, byId, weekOf, weeksOf, all } = await exercisesByWeek(sb, id, userId);
  const files = sp.files === "1";
  // Week N = lecture N + practice N (his way, 11/11/2026). Opens on the first week that still has unsolved exercises.
  const last = weeksOf(id);
  const open = Array.from({ length: last }, (_, k) => k + 1)
    .find((n) => all.some((x) => x.course_id === id && weekOf(x) === n && !x.done_at));
  const w = Math.max(1, Number(sp.w) || open || last);
  const { fromLessons, fromFiles } = forWeek(id, w);
  const allFiles = fileExercises(id);
  const weeks = Array.from({ length: last }, (_, k) => k + 1);
  // The week's core: 3-5 exercises picked by what the exams ask (his request, 08/11/2026); the rest is an optional bank.
  type Core = { weeks: Record<string, { id: string; why: string; where?: string }[]>; exam_note?: string };
  const core: Core | null = await sb.storage.from("study").download(`${userId}/materials/${id}/exercise_core.json`)
    .then(async ({ data }) => (data ? JSON.parse(await data.text()) as Core : null)).catch(() => null);
  // The core was picked per calendar week; each pick now shows in the week of its own lesson (week N = lecture N),
  // and a pick with no lesson (e.g. his own exam) stays in the week it was given.
  const picks = Object.entries(core?.weeks ?? {}).flatMap(([k, list]) => list.map((p) => ({ ...p, k: Number(k) })))
    .filter((p) => { const x = byId.get(p.id); const pw = x ? weekOf(x) : undefined; return (pw ?? p.k) === w; })
    .filter((p, i, a) => a.findIndex((q) => q.id === p.id) === i);
  // with the file / lesson it came from and the exact page (a hand-set "where" in the core file wins)
  const coreItems = picks.map((p) => {
    const x = byId.get(p.id);
    return x ? { ...x, why: p.why, where: p.where || x.where } as Exercise : null;
  }).filter((x): x is Exercise => !!x);
  const coreIds = new Set(coreItems.map((x) => x.id));
  const bankLessons = fromLessons.filter((x) => !coreIds.has(x.id));
  const bankFiles = fromFiles.filter((x) => !coreIds.has(x.id));

  return (
    <div className="space-y-4">
      <BackLink href={`/courses/${id}`}>→ {course.name}</BackLink>
      <h1 className="text-2xl font-bold">✍️ תרגילים</h1>
      <div className="flex gap-2 flex-wrap">
        {weeks.map((x) => (
          <Link key={x} href={`/courses/${id}/exercises?w=${x}`}
            className={`px-3 py-1.5 rounded-xl text-sm ${!files && x === w ? "bg-accent text-white" : "bg-accent-soft text-accent"}`}>
            שבוע {x}{x === open ? " (כאן אני)" : ""}
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
        coreItems.length > 0 ? (
          <>
            <section className="card">
              <h2 className="font-semibold mb-1">⭐ הליבה של שבוע {w} ({coreItems.length} תרגילים)</h2>
              <p className="text-xs text-muted mb-3">
                מה שכדאי לתרגל השבוע, לפי מה ששואלים במבחנים. לקרוא את הפתרון המלא, ואחר כך לנסות לבד.
                {core?.exam_note ? ` ${core.exam_note}` : ""}
              </p>
              <Exercises items={coreItems} />
            </section>
            {bankLessons.length + bankFiles.length > 0 && (
              <Fold id={`bank-${id}-${w}`} title="📚 בנק תרגילים נוסף (רשות)" hint={`${bankLessons.length + bankFiles.length}`}>
                <Exercises items={[...bankLessons, ...bankFiles]} />
              </Fold>
            )}
          </>
        ) : <>
          <section className="card">
            <h2 className="font-semibold mb-1">שבוע {w}: מהרצאה {w} ומתרגול {w}</h2>
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
