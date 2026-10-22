import Link from "next/link";
import { requireUser } from "@/lib/supabase/server";
import { KIND_LABEL, type Course } from "@/lib/types";

export default async function Courses() {
  const { sb } = await requireUser();
  const { data } = await sb.from("courses").select("*").order("year", { ascending: false }).order("semester").order("name");
  const courses = (data ?? []) as Course[];
  const active = courses.filter((c) => !c.archived);
  const archived = courses.filter((c) => c.archived);

  // Group active courses by "year / semester" so the whole degree stays organized.
  const groups = new Map<string, Course[]>();
  for (const c of active) {
    const key = c.kind === "self" ? "לימוד עצמי" : c.year ? `שנה ${c.year}${c.semester ? ` · סמסטר ${c.semester}` : ""}` : "כללי";
    groups.set(key, [...(groups.get(key) ?? []), c]);
  }

  return (
    <div className="space-y-5">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">קורסים</h1>
        <div className="flex gap-2">
          <Link href="/grades" className="btn-ghost">📜 ציונים</Link>
          <Link href="/courses/new" className="btn">+ קורס</Link>
        </div>
      </div>
      {[...groups].map(([label, list]) => (
        <section key={label}>
          <h2 className="text-sm text-muted mb-2">{label}</h2>
          <ul className="card divide-y divide-line py-0">
            {list.map((c) => (
              <li key={c.id}>
                <Link href={`/courses/${c.id}`} className="flex justify-between py-3">
                  <span className="font-medium">{c.name}</span>
                  <span className="chip">{KIND_LABEL[c.kind]}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ))}
      {archived.length > 0 && (
        <details className="card">
          <summary className="cursor-pointer font-medium">ארכיון ({archived.length})</summary>
          <ul className="divide-y divide-line mt-2">
            {archived.map((c) => (
              <li key={c.id}>
                <Link href={`/courses/${c.id}`} className="flex justify-between py-2.5 text-muted">
                  <span>{c.name}</span>
                  <span className="text-xs">{c.year ? `שנה ${c.year} · ${c.semester ?? ""}` : ""}</span>
                </Link>
              </li>
            ))}
          </ul>
        </details>
      )}
      {!courses.length && <p className="text-muted">עוד אין קורסים.</p>}
    </div>
  );
}
