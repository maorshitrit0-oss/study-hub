import Link from "next/link";
import { addFact, deleteFact } from "@/app/(app)/actions";

export type Fact = { id: string; category: string; text: string; lesson_id: string | null };

const LABEL: Record<string, string> = {
  reservist: "🎖️ מילואים",
  exam: "📝 המבחן",
  exam_hint: "⭐ מה יהיה במבחן",
  grading: "📊 ציון ומשקלים",
  assignments: "📮 מטלות והגשות",
  attendance: "🙋 נוכחות",
  materials: "📚 חומרים וסביבת עבודה",
  industry: "💼 מהתעשייה ולראיונות עבודה",
  other: "ℹ️ כללי",
};

/** Admin info the lecturers said in class, grouped; reservist rules first for reservists. */
export default function CourseFacts({ courseId, facts, reservist, lessonNames }: {
  courseId: string;
  facts: Fact[];
  reservist: boolean;
  lessonNames: Map<string, string>;
}) {
  const order = reservist
    ? ["reservist", "exam", "exam_hint", "grading", "assignments", "attendance", "materials", "industry", "other"]
    : ["exam", "exam_hint", "grading", "assignments", "reservist", "attendance", "materials", "industry", "other"];
  const groups = order
    .map((cat) => [cat, facts.filter((f) => (LABEL[f.category] ? f.category : "other") === cat)] as const)
    .filter(([, list]) => list.length);

  return (
    <section className="card">
      <h2 className="font-semibold mb-1">מידע על הקורס</h2>
      <p className="text-xs text-muted mb-3">
        {groups.length ? "נאסף אוטומטית מהסילבוס ומההרצאות, ומה שהוספת בעצמך." : "יתמלא מהסילבוס ומההרצאות. אפשר גם להוסיף בעצמך למטה."}
      </p>
      <div className="space-y-4">
        {groups.map(([cat, list]) => (
          <div key={cat} className={cat === "reservist" && reservist ? "rounded-xl bg-warn-soft p-3 -mx-1" : ""}>
            <h3 className="text-sm font-semibold mb-1.5">{LABEL[cat]}</h3>
            <ul className="space-y-1.5 text-sm">
              {list.map((f) => (
                <li key={f.id} className="flex gap-2">
                  <span className="text-muted">•</span>
                  <span className="flex-1">
                    {f.text}
                    {f.lesson_id && lessonNames.get(f.lesson_id) && (
                      <Link href={`/lessons/${f.lesson_id}`} className="text-xs text-accent"> ({lessonNames.get(f.lesson_id)})</Link>
                    )}
                  </span>
                  <form action={deleteFact.bind(null, f.id, courseId)}>
                    <button className="text-muted text-xs px-1" aria-label="מחיקה">✕</button>
                  </form>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <details className="mt-4">
        <summary className="text-sm text-accent cursor-pointer">+ הוספת מידע (למשל: נוכחות חובה)</summary>
        <form action={addFact.bind(null, courseId)} className="mt-2 space-y-2">
          <select name="category" className="input" defaultValue="attendance">
            {Object.entries(LABEL).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
          <input name="text" className="input" required placeholder="למשל: חובת נוכחות בהרצאות" />
          <button className="btn w-full">הוספה</button>
        </form>
      </details>
    </section>
  );
}
