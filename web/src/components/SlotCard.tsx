import Link from "next/link";
import { SLOT_LABEL, hhmm, type Slot } from "@/lib/types";

export default function SlotCard({ s, courseName, now }: { s: Slot; courseName?: string; now?: boolean }) {
  return (
    <Link href={`/schedule/${s.id}`}
      className={`flex gap-3 rounded-xl border p-3 ${now ? "border-accent bg-accent-soft" : "border-line bg-card"}`}>
      <div className="text-sm font-medium tabular-nums text-muted w-12 shrink-0 leading-5">
        {hhmm(s.start_time)}<br />{hhmm(s.end_time)}
      </div>
      <div className="min-w-0">
        <div className="font-medium">{courseName ?? s.title}{now && <span className="text-xs text-accent"> · עכשיו</span>}</div>
        <div className="text-xs text-muted">
          {SLOT_LABEL[s.kind]}
          {s.room ? ` · חדר ${s.room}` : ""}
          {s.instructor ? ` · ${s.instructor}` : ""}
        </div>
      </div>
    </Link>
  );
}
