import BackLink from "@/components/BackLink";
import Chapter from "@/components/Chapter";
import CopyText from "@/components/CopyText";
import Fold from "@/components/Fold";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";

type Assignments = { title: string; updated: string; note?: string; items: { n: number; title: string; md: string }[] };

/**
 * 📝 The course's graded assignments with full checked solutions (his request 16/11/2026, communication systems: 10% of
 * the grade). Stored privately (worker/sealed.py -> hub assignments); each one can be copied, or all at once.
 */
export default async function AssignmentsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { sb, userId } = await requireUser();
  const { data: course } = await sb.from("courses").select("id, name").eq("id", id).maybeSingle();
  if (!course) notFound();
  const a: Assignments | null = await sb.storage.from("study").download(`${userId}/materials/${id}/assignments.json`)
    .then(async ({ data }) => (data ? JSON.parse(await data.text()) as Assignments : null)).catch(() => null);
  const all = (a?.items ?? []).map((x) => `# ${x.n}. ${x.title}\n\n${x.md}`).join("\n\n---\n\n");

  return (
    <div className="space-y-4">
      <BackLink href={`/courses/${id}`}>→ {course.name}</BackLink>
      <h1 className="text-2xl font-bold">📝 {a?.title ?? "מטלות"}</h1>
      {!a ? <p className="card text-muted">עוד אין מטלות לקורס הזה.</p> : (
        <>
          {a.note && <p className="card text-sm">{a.note} · עודכן {a.updated}</p>}
          <CopyText text={all} label={`📋 להעתיק את כל ${a.items.length} המטלות והפתרונות`} />
          {a.items.map((x) => (
            <Fold key={x.n} id={`asg-${id}-${x.n}`} title={`${x.n}. ${x.title}`} defaultOpen={false}>
              <div className="mb-3"><CopyText text={`# ${x.n}. ${x.title}\n\n${x.md}`} label="📋 להעתיק את המטלה הזאת" /></div>
              <Chapter md={x.md} slideUrls={{}} />
            </Fold>
          ))}
        </>
      )}
    </div>
  );
}
