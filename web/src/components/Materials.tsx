"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { supabaseBrowser } from "@/lib/supabase/client";
import { guessKind, mimeOf, readZip } from "@/lib/zip";
import { addDriveMaterial, addMaterial, deleteMaterial, readSyllabus, setMaterialKind } from "@/app/(app)/actions";

type Material = { id: string; title: string; kind: string; storage_path: string };
const KINDS: Record<string, string> = {
  syllabus: "סילבוס", slides: "מצגת", past_exam: "מבחנים ובחנים קודמים", solution: "פתרון", lab_guide: "חוברת מעבדה", prev_report: "דוח קודם (של שותפים)", other: "אחר",
};
const MAX_UPLOAD = 50 * 1024 * 1024; // Supabase free plan limit per file

export default function Materials({ courseId, userId, items, isLab = false }: {
  courseId: string; userId: string; items: Material[]; isLab?: boolean;
}) {
  const [kind, setKind] = useState("slides");
  const [busy, setBusy] = useState("");
  const [drive, setDrive] = useState({ url: "", title: "" });
  const router = useRouter();

  async function upload(picked: FileList | File[] | null) {
    if (!picked?.length) return;
    const sb = supabaseBrowser();
    // ZIPs are unpacked here on the device; each file inside is stored on its own.
    const files: { file: File; kind: string }[] = [];
    const tooBig: string[] = [];
    for (const f of Array.from(picked)) {
      if (!/\.zip$/i.test(f.name)) { files.push({ file: f, kind }); continue; }
      setBusy(`פותח את ${f.name}...`);
      try {
        for (const e of await readZip(f)) {
          const file = new File([e.data as BlobPart], e.name, { type: mimeOf(e.name) });
          files.push({ file, kind: guessKind(e.name, isLab) });
        }
      } catch {
        setBusy(`לא הצלחתי לפתוח את ${f.name} - ודא שזה קובץ ZIP תקין`);
        return;
      }
    }
    let done = 0;
    for (const { file, kind } of files) {
      if (files.length > 1) setBusy(`מעלה ${++done} מתוך ${files.length}: ${file.name}`);
      if (file.size > MAX_UPLOAD) {
        tooBig.push(`${file.name} (${Math.round(file.size / 1048576)}MB)`);
        continue;
      }
      if (files.length === 1) setBusy(`מעלה ${file.name}... (סילבוס נקרא אוטומטית, זה לוקח כחצי דקה)`);
      const safe = file.name.replace(/[^\w.\-]+/g, "_");
      const path = `${userId}/materials/${courseId}/${Date.now()}_${safe}`;
      const { error } = await sb.storage.from("study").upload(path, file, { contentType: file.type });
      if (error) { setBusy(`שגיאה ב-${file.name}: ${error.message}`); return; }
      const note = await addMaterial(courseId, { title: file.name, kind, path, mime: file.type || mimeOf(file.name), size: file.size });
      if (note && files.length === 1) { setBusy(note); router.refresh(); return; }
    }
    setBusy(tooBig.length
      ? `הועלו ${files.length - tooBig.length} קבצים. גדולים מ-50MB ולא הועלו - הוסף אותם מקישור דרייב: ${tooBig.join(", ")}`
      : files.length > 1 ? `✓ הועלו ${files.length} קבצים. הסוג נקבע לפי השם - אפשר לשנות בלחיצה על התגית.` : "");
    router.refresh();
  }

  /** A ZIP uploaded before ZIPs were unpacked: download it, unpack it like a fresh upload, then remove it. */
  async function extractStored(m: Material) {
    setBusy(`מוריד את ${m.title}...`);
    const { data } = await supabaseBrowser().storage.from("study").createSignedUrl(m.storage_path, 3600);
    if (!data) { setBusy("לא הצלחתי להוריד את הקובץ"); return; }
    const blob = await (await fetch(data.signedUrl)).blob();
    await upload([new File([blob], m.title, { type: "application/zip" })]);
    await deleteMaterial(m.id, courseId);
    router.refresh();
  }

  async function addFromDrive() {
    if (!drive.url.trim()) return;
    setBusy("מוסיף מהדרייב...");
    setBusy(await addDriveMaterial(courseId, drive.url.trim(), kind, drive.title));
    setDrive({ url: "", title: "" });
    router.refresh();
  }

  async function open(path: string) {
    if (path.startsWith("drive:")) return window.open(`https://drive.google.com/file/d/${path.slice(6)}/view`, "_blank");
    const { data } = await supabaseBrowser().storage.from("study").createSignedUrl(path, 3600);
    if (data) window.open(data.signedUrl, "_blank");
  }

  return (
    <div className="space-y-3">
      {items.length > 0 && (
        <ul className="divide-y divide-line">
          {items.map((m) => (
            <li key={m.id} className="flex items-center gap-2 py-2">
              <select value={m.kind} aria-label="סוג הקובץ" className="chip appearance-none cursor-pointer border-0 shrink-0"
                onChange={async (e) => {
                  setBusy(e.target.value === "syllabus" ? `קורא את ${m.title} כסילבוס... (כחצי דקה)` : "");
                  const note = await setMaterialKind(m.id, e.target.value);
                  setBusy(note ?? "");
                  router.refresh();
                }}>
                {Object.entries(KINDS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
              <button className="flex-1 text-start truncate" onClick={() => open(m.storage_path)}>
                {m.storage_path.startsWith("drive:") && "☁️ "}{m.title}
              </button>
              {/\.zip$/i.test(m.title) && !m.storage_path.startsWith("drive:") && (
                <button className="text-accent text-sm shrink-0" onClick={() => extractStored(m)}>חלץ</button>
              )}
              {m.kind === "syllabus" && (
                <button className="text-accent text-sm shrink-0"
                  onClick={async () => { setBusy(`קורא את ${m.title}... (כחצי דקה)`); setBusy(await readSyllabus(m.id)); router.refresh(); }}>
                  קרא מחדש
                </button>
              )}
              <button className="text-muted text-sm shrink-0" onClick={async () => { await deleteMaterial(m.id, courseId); router.refresh(); }}>מחיקה</button>
            </li>
          ))}
        </ul>
      )}
      <div className="flex gap-2">
        <select className="input w-40" value={kind} onChange={(e) => setKind(e.target.value)} aria-label="סוג הקובץ להעלאה">
          {Object.entries(KINDS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
        <label className="btn-ghost flex-1 cursor-pointer">
          העלאת קבצים / ZIP
          <input type="file" multiple className="hidden" accept=".pdf,.docx,.pptx,.txt,.md,.zip,image/*"
            onChange={(e) => upload(e.target.files)} />
        </label>
      </div>
      <details className="text-sm">
        <summary className="text-accent cursor-pointer">קובץ גדול (מעל 50MB)? הוספה מקישור Google Drive</summary>
        <div className="mt-2 space-y-2">
          <input className="input" dir="ltr" inputMode="url" placeholder="https://drive.google.com/file/d/..."
            value={drive.url} onChange={(e) => setDrive({ ...drive, url: e.target.value })} />
          <input className="input" placeholder="שם הקובץ (למשל: בחני כניסה)" value={drive.title}
            onChange={(e) => setDrive({ ...drive, title: e.target.value })} />
          <button className="btn w-full" onClick={addFromDrive}>הוספה מהדרייב</button>
          <p className="text-xs text-muted">בדרייב: לחיצה על הקובץ ← שיתוף ← &quot;כל מי שיש לו את הקישור&quot; ← העתקת קישור. הסוג נלקח מהבחירה למעלה.</p>
        </div>
      </details>
      {busy && <p className="text-sm text-muted">{busy}</p>}
      <p className="text-xs text-muted">לשינוי סוג של קובץ - לוחצים על התגית שלו. סילבוס נקרא אוטומטית (PDF או Word) ומבנה המבחן, המשקלים וההקלות עוברים ל&quot;מידע על הקורס&quot;. ה-AI בצ&apos;אט קורא את כל הקבצים.</p>
    </div>
  );
}
