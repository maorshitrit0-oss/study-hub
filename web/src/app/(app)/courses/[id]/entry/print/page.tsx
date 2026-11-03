import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import { fetchAll } from "@/lib/fetchAll";
import { Rich } from "@/components/Chapter";
import PrintButton from "@/components/PrintButton";

type Row = { id: string; question: string; options: string[]; correct: number; explanation: string | null; experiment: number; source: string };

/** Every entry-quiz question students reported, by experiment, with answers - to print / save as PDF and pass on. */
export default async function EntryPrint({ params }: PageProps<"/courses/[id]/entry/print">) {
  const { id } = await params;
  const { sb } = await requireUser();
  const { data: course } = await sb.from("courses").select("name").eq("id", id).maybeSingle();
  if (!course) notFound();
  const rows = await fetchAll<Row>(() => sb.from("questions").select("id, question, options, correct, explanation, experiment, source")
    .eq("course_id", id).eq("source", "entry_reported").order("experiment").order("created_at").order("id")).catch(() => [] as Row[]);
  const experiments = [...new Set(rows.map((r) => r.experiment))].sort((a, b) => a - b);

  return (
    <article className="space-y-5 print:text-black">
      <div className="print:hidden"><PrintButton /></div>
      <header>
        <h1 className="text-2xl font-bold">{course.name} - שאלות מבוחני הכניסה</h1>
        <p className="text-sm text-muted">שאלות שסטודנטים נשאלו בפועל, לפי ניסוי, עם התשובה וההסבר. {rows.length} שאלות.</p>
      </header>
      {experiments.map((n) => (
        <section key={n} className="card break-inside-avoid-page">
          <h2 className="text-lg font-bold mb-2">ניסוי {n}</h2>
          <ol className="space-y-4 list-decimal ps-5">
            {rows.filter((r) => r.experiment === n).map((r) => (
              <li key={r.id} className="break-inside-avoid">
                <Rich text={r.question} />
                <ul className="mt-1 space-y-0.5 text-sm">
                  {r.options.map((o, k) => (
                    <li key={k} className={k === r.correct ? "font-semibold text-good" : ""}>{k === r.correct ? "✅" : "◻"} <Rich text={o} /></li>
                  ))}
                </ul>
                {r.explanation && <div className="text-sm text-muted mt-1"><Rich text={r.explanation} /></div>}
              </li>
            ))}
          </ol>
        </section>
      ))}
      {!rows.length && <p className="card text-muted">עוד אין שאלות שדווחו.</p>}
    </article>
  );
}
