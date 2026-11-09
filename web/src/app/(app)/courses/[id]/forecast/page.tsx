import BackLink from "@/components/BackLink";
import Fold from "@/components/Fold";
import Exercises, { type Exercise } from "@/components/Exercises";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import { exercisesByWeek } from "@/lib/exercises";

type Section = {
  title: string; points?: number; chance: number; why: string; taught: boolean; tip?: string; exercise_ids?: string[];
};
type Forecast = { updated: string; format: string; basis: string; sections: Section[] };

const tone = (c: number) => (c >= 80 ? "bg-bad text-white" : c >= 50 ? "bg-warn text-black" : "bg-line text-muted");

/**
 * 🎯 The expected exam (his request 09/11/2026): what will most likely be asked, with the chance of each question and
 * its solved exercises, and how ready he is - written by Claude from the past exams and updated every week.
 */
export default async function ForecastPage({ params }: PageProps<"/courses/[id]/forecast">) {
  const { id } = await params;
  const { sb, userId } = await requireUser();
  const { data: course } = await sb.from("courses").select("id, name").eq("id", id).maybeSingle();
  if (!course) notFound();
  const fc: Forecast | null = await sb.storage.from("study").download(`${userId}/materials/${id}/exam_forecast.json`)
    .then(async ({ data }) => (data ? JSON.parse(await data.text()) as Forecast : null)).catch(() => null);
  const { byId } = await exercisesByWeek(sb, id, userId);
  const { data: pdf } = await sb.storage.from("study").createSignedUrl(`${userId}/materials/${id}/exam_forecast.pdf`, 3600);
  const sections = (fc?.sections ?? []).slice().sort((a, b) => b.chance - a.chance);
  // Readiness: of what is likely and already taught, how much he has solved (weighted by chance x points).
  let have = 0, all = 0;
  for (const s of sections.filter((x) => x.taught)) {
    const ex = (s.exercise_ids ?? []).map((x) => byId.get(x)).filter(Boolean) as Exercise[];
    const w = s.chance * (s.points ?? 10);
    all += w;
    have += ex.length ? w * ex.filter((e) => e.done_at).length / ex.length : 0;
  }
  const ready = all ? Math.round((100 * have) / all) : null;

  return (
    <div className="space-y-4">
      <BackLink href={`/courses/${id}`}>→ {course.name}</BackLink>
      <h1 className="text-2xl font-bold">🎯 המבחן הצפוי</h1>
      {!fc ? <p className="card text-muted">עוד לא נבנה מבחן צפוי לקורס הזה.</p> : (
        <>
          {pdf?.signedUrl && (
            <a href={pdf.signedUrl} target="_blank" rel="noreferrer" className="card block text-center font-semibold bg-accent-soft">
              📄 המבחן הצפוי כ-PDF להדפסה – שאלות, ואחריהן פתרונות מלאים
            </a>
          )}
          <section className="card space-y-2 text-sm">
            <p><b>המבנה:</b> {fc.format}</p>
            <p className="text-muted"><b>לפי:</b> {fc.basis} · עודכן {fc.updated}</p>
            {ready !== null && (
              <div>
                <div className="flex justify-between"><b>המוכנות שלי (במה שכבר נלמד)</b><span>{ready}%</span></div>
                <div className="h-2 rounded-full bg-bg overflow-hidden mt-1"><div className="h-full bg-good" style={{ width: `${ready}%` }} /></div>
                <p className="text-xs text-muted mt-1">= כמה מהתרגילים של השאלות הצפויות כבר סימנת &quot;פתרתי&quot;, לפי הסיכוי והניקוד של כל שאלה.</p>
              </div>
            )}
          </section>
          {sections.map((s, i) => {
            const ex = (s.exercise_ids ?? []).map((x) => byId.get(x)).filter(Boolean) as Exercise[];
            const solved = ex.filter((e) => e.done_at).length;
            return (
              <Fold key={i} id={`fc-${id}-${i}`} defaultOpen={false}
                title={<span className="flex items-center gap-2"><span className={`text-xs rounded-full px-2 py-0.5 ${tone(s.chance)}`}>{s.chance}%</span>{s.title}</span>}
                hint={!s.taught ? "עוד לא נלמד" : ex.length ? `פתרת ${solved}/${ex.length}` : undefined}>
                <div className="space-y-2 text-sm">
                  <p>{s.points ? <b>{s.points} נק׳ · </b> : null}<b>למה צפוי:</b> {s.why}</p>
                  {s.tip && <p className="rounded-xl bg-accent-soft p-2">💡 {s.tip}</p>}
                  {!s.taught && <p className="text-muted">⏳ הנושא עוד לא נלמד – התרגילים יתווספו כשיילמד.</p>}
                </div>
                {ex.length > 0 && <div className="mt-3"><Exercises items={ex} /></div>}
              </Fold>
            );
          })}
        </>
      )}
    </div>
  );
}
