"use client";

import { useActionState, useState } from "react";
import { addLesson, type AddLessonState } from "@/app/(app)/actions";

export default function AddLesson({ courseId, nextNumber }: { courseId: string; nextNumber: number }) {
  const [state, action, pending] = useActionState<AddLessonState, FormData>(addLesson.bind(null, courseId), {});
  const [kind, setKind] = useState("lecture");
  return (
    <form action={action} className="space-y-3">
      <div className="flex gap-2 flex-wrap">
        {[["lecture", "הרצאה"], ["practice", "תרגול"], ["lab", "מעבדה"], ["web", "קישור לאתר"]].map(([v, l]) => (
          <label key={v} className={`chip cursor-pointer py-1.5 px-3 ${kind === v ? "!bg-accent !text-white" : ""}`}>
            <input type="radio" name="kind" value={v} checked={kind === v} onChange={() => setKind(v)} className="hidden" />
            {l}
          </label>
        ))}
      </div>
      <input className="input" name="url" dir="ltr" required inputMode="url"
        placeholder={kind === "web" ? "https://..." : "https://ariel-ac-il.zoom.us/rec/share/..."} />
      <div className="flex gap-3">
        {kind !== "web" && (
          <input className="input w-24" name="number" type="number" min={1} defaultValue={nextNumber} aria-label="מספר" />
        )}
        <input className="input flex-1" name="title" placeholder={kind === "web" ? "נושא (לא חובה)" : "כותרת (לא חובה)"} />
      </div>
      <details className="text-sm">
        <summary className="text-muted cursor-pointer">מי כותב את הפרק?</summary>
        <label className="flex gap-2 mt-2"><input type="radio" name="author" value="gemini" defaultChecked /> אוטומטי (Gemini) - מוכן לבד</label>
        <label className="flex gap-2 mt-1"><input type="radio" name="author" value="claude" /> Claude - רק מתמלל, ואני אבקש מ-Claude Code לכתוב</label>
      </details>
      {state.error && <p className="text-bad text-sm">{state.error}</p>}
      {state.ok && <p className="text-good text-sm">נוסף! העיבוד רץ ברקע (הרצאה של שעה וחצי: כ-40 דקות).</p>}
      <button className="btn w-full" disabled={pending}>{pending ? "שולח..." : "הוספה ועיבוד"}</button>
    </form>
  );
}
