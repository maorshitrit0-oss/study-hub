import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import Chapter from "@/components/Chapter";
import DocActions from "@/components/DocActions";
import { DOCS, readDoc, type DocKind } from "@/lib/courseDocs";

// Building the document is one long Gemini call over every lesson of the course.
export const maxDuration = 300;

export default async function CourseDoc({ params }: PageProps<"/courses/[id]/doc/[kind]">) {
  const { id, kind } = await params;
  if (!(kind in DOCS)) notFound();
  const { sb, userId } = await requireUser();
  const { data: course } = await sb.from("courses").select("name").eq("id", id).maybeSingle();
  if (!course) notFound();
  const md = await readDoc(sb, userId, id, kind as DocKind);

  return (
    <div className="space-y-4">
      <div className="print:hidden space-y-2">
        <Link href={`/courses/${id}`} className="text-sm text-accent">→ {course.name}</Link>
        <h1 className="text-2xl font-bold">{DOCS[kind as DocKind].title}</h1>
        <DocActions courseId={id} kind={kind as DocKind} exists={!!md} />
      </div>
      {md ? (
        <article className={`card ${kind === "formulas" ? "formula-sheet" : ""}`}>
          <Chapter md={md} slideUrls={{}} />
        </article>
      ) : (
        <p className="card text-muted">עוד לא נבנה. לחץ על לבנות - זה לוקח דקה-שתיים.</p>
      )}
    </div>
  );
}
