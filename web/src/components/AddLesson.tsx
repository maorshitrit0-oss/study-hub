"use client";

import { useActionState, useRef, useState } from "react";
import { addLesson, type AddLessonState } from "@/app/(app)/actions";
import { supabaseBrowser } from "@/lib/supabase/client";

const KINDS = [["lecture", "הרצאה"], ["practice", "תרגול"], ["lab", "ניסוי במעבדה"], ["web", "קישור לאתר"]] as const;

export default function AddLesson({ courseId, userId, nextByKind, isLab }: {
  courseId: string;
  userId: string;
  nextByKind: Record<string, number>; // lectures and practices are numbered separately
  isLab: boolean;
}) {
  const [state, action, pending] = useActionState<AddLessonState, FormData>(addLesson.bind(null, courseId), {});
  const [kind, setKind] = useState<string>(isLab ? "lab" : "lecture");
  const [uploading, setUploading] = useState("");
  const [sourcePath, setSourcePath] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);

  async function upload(file: File | undefined) {
    if (!file) return;
    setUploading(`מעלה ${file.name}...`);
    const path = `${userId}/sources/${courseId}/${Date.now()}_${file.name.replace(/[^\w.\-]+/g, "_")}`;
    const { error } = await supabaseBrowser().storage.from("study").upload(path, file, { contentType: file.type });
    setUploading(error ? `שגיאה: ${error.message}` : `✓ ${file.name}`);
    setSourcePath(error ? "" : path);
  }

  const placeholder = kind === "web" ? "https://..." : kind === "lab"
    ? "קישור לחוברת הניסוי / דוח מכין בדרייב (או העלאת קובץ למטה)"
    : "קישור להקלטת זום או לקובץ בדרייב";

  return (
    <form action={action} className="space-y-3">
      <div className="flex gap-2 flex-wrap">
        {KINDS.map(([v, l]) => (
          <label key={v} className={`chip cursor-pointer py-1.5 px-3 ${kind === v ? "!bg-accent !text-white" : ""}`}>
            <input type="radio" name="kind" value={v} checked={kind === v} onChange={() => setKind(v)} className="hidden" />
            {l}
          </label>
        ))}
      </div>
      <input className="input" name="url" dir="ltr" inputMode="url" required={!sourcePath} placeholder={placeholder} />
      {kind === "lab" && (
        <div className="space-y-1">
          <input type="hidden" name="source_path" value={sourcePath} />
          <button type="button" className="btn-ghost w-full" onClick={() => fileInput.current?.click()}>
            📄 העלאת חוברת הניסוי / הדוח המכין (PDF)
          </button>
          <input ref={fileInput} type="file" accept=".pdf,image/*" className="hidden" onChange={(e) => upload(e.target.files?.[0])} />
          {uploading && <p className="text-sm text-muted">{uploading}</p>}
        </div>
      )}
      <div className="flex gap-3">
        {kind !== "web" && (
          <input key={kind} className="input w-24" name="number" type="number" min={1} defaultValue={nextByKind[kind] ?? 1} aria-label="מספר" />
        )}
        <input className="input flex-1" name="title" placeholder={kind === "lab" ? "שם הניסוי (לא חובה)" : "כותרת (לא חובה)"} />
      </div>
      <details className="text-sm">
        <summary className="text-muted cursor-pointer">מי כותב את הפרק?</summary>
        <label className="flex gap-2 mt-2"><input type="radio" name="author" value="gemini" defaultChecked /> אוטומטי (Gemini) - מוכן לבד</label>
        <label className="flex gap-2 mt-1"><input type="radio" name="author" value="claude" /> Claude - רק מכין את החומר, ואני אבקש מ-Claude Code לכתוב</label>
      </details>
      {state.error && <p className="text-bad text-sm">{state.error}</p>}
      {state.ok && <p className="text-good text-sm">נוסף! העיבוד רץ ברקע ותקבל התראה כשהוא מוכן.</p>}
      <button className="btn w-full" disabled={pending || uploading.startsWith("מעלה")}>{pending ? "שולח..." : "הוספה ועיבוד"}</button>
    </form>
  );
}
