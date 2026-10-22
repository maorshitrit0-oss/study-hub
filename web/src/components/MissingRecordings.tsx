import Link from "next/link";
import { markRecording } from "@/app/(app)/actions";
import { SLOT_LABEL } from "@/lib/types";
import type { Missing } from "@/lib/recordings";

const fmt = (date: string) =>
  new Intl.DateTimeFormat("he-IL", { weekday: "long", day: "numeric", month: "numeric", timeZone: "UTC" }).format(new Date(`${date}T12:00:00Z`));

/** Classes that ended without an uploaded recording, with quick "uploaded" / "no recording" marks. */
export default function MissingRecordings({ items, courseName }: { items: Missing[]; courseName: Map<string, string> }) {
  if (!items.length) return null;
  return (
    <section className="card">
      <h2 className="font-semibold">📹 הקלטות להעלות</h2>
      <p className="text-xs text-muted mb-2">כשמוסיפים את ההקלטה בדף הקורס, השורה נעלמת לבד.</p>
      <ul className="divide-y divide-line">
        {items.map(({ slot, date }) => (
          <li key={`${slot.id}${date}`} className="py-2.5 space-y-2">
            <Link href={`/courses/${slot.course_id}#add`} className="block">
              <span className="font-medium">{SLOT_LABEL[slot.kind]} · {courseName.get(slot.course_id!) ?? slot.title}</span>
              <span className="text-xs text-muted"> · {fmt(date)}</span>
            </Link>
            <div className="flex gap-2">
              <Link href={`/courses/${slot.course_id}#add`} className="btn text-sm py-1.5 flex-1">להעלאה</Link>
              <form action={markRecording.bind(null, slot.id, date, "uploaded")} className="flex-1">
                <button className="btn-ghost text-sm py-1.5 w-full">העליתי ✓</button>
              </form>
              <form action={markRecording.bind(null, slot.id, date, "none")} className="flex-1">
                <button className="btn-ghost text-sm py-1.5 w-full !text-muted">אין הקלטה</button>
              </form>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
