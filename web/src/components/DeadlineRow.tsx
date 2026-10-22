import Link from "next/link";
import { toggleDeadline } from "@/app/(app)/actions";
import { DEADLINE_LABEL, type Deadline } from "@/lib/types";
import { daysLeft, fmtDue, urgency } from "@/lib/format";

const tone = { bad: "text-bad bg-bad-soft", warn: "text-warn bg-warn-soft", muted: "text-muted bg-bg" };

export default function DeadlineRow({ d, courseName }: { d: Deadline; courseName?: string }) {
  return (
    <li className="flex items-center gap-3 py-2.5">
      <form action={toggleDeadline.bind(null, d.id, !d.done)}>
        <button
          aria-label={d.done ? "סמן כלא בוצע" : "סמן כבוצע"}
          className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${d.done ? "bg-good border-good text-white" : "border-line"}`}
        >
          {d.done && "✓"}
        </button>
      </form>
      <Link href={`/deadlines/${d.id}`} className="flex-1 min-w-0">
        <div className={`font-medium truncate ${d.done ? "line-through text-muted" : ""}`}>{d.title}</div>
        <div className="text-xs text-muted">
          {DEADLINE_LABEL[d.kind]}
          {courseName ? ` · ${courseName}` : ""} · {d.check_due ? "אין עדיין מועד הגשה" : fmtDue(d.due_at)}
        </div>
        {d.check_due && d.notes && <div className="text-xs text-warn">{d.notes}</div>}
      </Link>
      {!d.done && d.check_due && <span className="text-xs rounded-full px-2 py-0.5 text-warn bg-warn-soft">🔎 לבדוק</span>}
      {!d.done && !d.check_due && <span className={`text-xs rounded-full px-2 py-0.5 ${tone[urgency(d.due_at)]}`}>{daysLeft(d.due_at)}</span>}
    </li>
  );
}
