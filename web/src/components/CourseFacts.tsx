import Link from "next/link";

export type Fact = { id: string; category: string; text: string; lesson_id: string | null };

const LABEL: Record<string, string> = {
  reservist: "🎖️ מילואים",
  exam: "📝 המבחן",
  exam_hint: "⭐ מה יהיה במבחן",
  grading: "📊 ציון ומשקלים",
  assignments: "📮 מטלות והגשות",
  attendance: "🙋 נוכחות",
  materials: "📚 חומרים וסביבת עבודה",
  other: "ℹ️ כללי",
};

/** Admin info the lecturers said in class, grouped; reservist rules first for reservists. */
export default function CourseFacts({ facts, reservist, lessonNames }: {
  facts: Fact[];
  reservist: boolean;
  lessonNames: Map<string, string>;
}) {
  const order = reservist
    ? ["reservist", "exam", "exam_hint", "grading", "assignments", "attendance", "materials", "other"]
    : ["exam", "exam_hint", "grading", "assignments", "reservist", "attendance", "materials", "other"];
  const groups = order
    .map((cat) => [cat, facts.filter((f) => (LABEL[f.category] ? f.category : "other") === cat)] as const)
    .filter(([, list]) => list.length);
  if (!groups.length) return null;

  return (
    <section className="card">
      <h2 className="font-semibold mb-1">מה המרצה אמר על הקורס</h2>
      <p className="text-xs text-muted mb-3">נאסף אוטומטית מההרצאות. כדאי לבדוק מול הסילבוס.</p>
      <div className="space-y-4">
        {groups.map(([cat, list]) => (
          <div key={cat} className={cat === "reservist" && reservist ? "rounded-xl bg-warn-soft p-3 -mx-1" : ""}>
            <h3 className="text-sm font-semibold mb-1.5">{LABEL[cat]}</h3>
            <ul className="space-y-1.5 text-sm">
              {list.map((f) => (
                <li key={f.id} className="flex gap-2">
                  <span className="text-muted">•</span>
                  <span>
                    {f.text}
                    {f.lesson_id && lessonNames.get(f.lesson_id) && (
                      <Link href={`/lessons/${f.lesson_id}`} className="text-xs text-accent"> ({lessonNames.get(f.lesson_id)})</Link>
                    )}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}
