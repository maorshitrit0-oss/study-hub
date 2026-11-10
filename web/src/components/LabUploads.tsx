"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { supabaseBrowser } from "@/lib/supabase/client";
import { addLecturerText, addLesson, addMaterial } from "@/app/(app)/actions";
import { mimeOf } from "@/lib/zip";

/**
 * Lab 2: the summary report of each experiment (his and his partner's - he hands in experiment N-1's report on the day
 * of experiment N), and WhatsApp recordings of the lecturer about the exam. Both feed the practical-exam questions.
 */
export default function LabUploads({ courseId, userId, reports }: { courseId: string; userId: string; reports: string[] }) {
  const [n, setN] = useState(1);
  const [who, setWho] = useState("שלי");
  const [msg, setMsg] = useState<React.ReactNode>("");
  const [busy, setBusy] = useState(false);
  const [said, setSaid] = useState("");
  const router = useRouter();
  const safe = (name: string) => name.replace(/[^\w.\-]+/g, "_");

  async function report(file: File | undefined) {
    if (!file) return;
    setBusy(true);
    setMsg(`מעלה ${file.name}...`);
    const ext = file.name.split(".").pop() || "docx";
    const path = `${userId}/materials/${courseId}/${Date.now()}_${safe(file.name)}`;
    const { error } = await supabaseBrowser().storage.from("study").upload(path, file, { contentType: file.type || mimeOf(file.name) });
    if (error) { setMsg(`שגיאה: ${error.message}`); setBusy(false); return; }
    await addMaterial(courseId, { title: `דוח מסכם ניסוי ${n} - ${who}.${ext}`, kind: "other", path, mime: file.type || mimeOf(file.name), size: file.size });
    setMsg(<>✓ דוח ניסוי {n} ({who}) הועלה. ועכשיו: <Link href={`/courses/${courseId}/entry?n=${n}`} className="text-accent underline">מה שאלו בבוחן הכניסה של ניסוי {n}?</Link></>);
    setBusy(false);
    router.refresh();
  }

  async function recording(file: File | undefined) {
    if (!file) return;
    setBusy(true);
    setMsg(`מעלה את ההקלטה...`);
    const path = `${userId}/sources/${courseId}/${Date.now()}_${safe(file.name)}`;
    const { error } = await supabaseBrowser().storage.from("study").upload(path, file, { contentType: file.type || "audio/ogg" });
    if (error) { setMsg(`שגיאה: ${error.message}`); setBusy(false); return; }
    const f = new FormData();
    f.set("kind", "other");
    f.set("source_path", path);
    f.set("title", `🎙️ המרצה על המבחן (${new Date().toLocaleDateString("he-IL", { timeZone: "Asia/Jerusalem" })})`);
    const res = await addLesson(courseId, {}, f);
    setMsg(res.error ? `שגיאה: ${res.error}` : "✓ ההקלטה מתומללת. כל דגש על המבחן ייכנס למבחן המעשי.");
    setBusy(false);
    router.refresh();
  }

  const have = (k: number) => reports.filter((t) => new RegExp(`ניסוי ${k}\\b`).test(t));
  const maxN = Math.max(6, ...reports.map((t) => Number(t.match(/ניסוי (\d+)/)?.[1] ?? 0)));

  return (
    <section className="card space-y-3">
      <h2 className="font-semibold">📝 דוחות מסכמים</h2>
      <p className="text-xs text-muted">ביום של ניסוי N מעלים את הדוח המסכם של ניסוי N-1 (שלך ושל השותפה). הם נכנסים לשאלות המבחן המעשי.</p>
      <div className="flex flex-wrap gap-1.5">
        {Array.from({ length: maxN }, (_, k) => k + 1).map((k) => (
          <span key={k} className={`chip ${have(k).length ? "" : "opacity-50"}`}>ניסוי {k}: {have(k).length ? `✓ ${have(k).length}` : "—"}</span>
        ))}
      </div>
      <div className="flex gap-2 flex-wrap items-center">
        <select className="input w-28" value={n} onChange={(e) => setN(Number(e.target.value))} aria-label="מספר ניסוי">
          {Array.from({ length: 12 }, (_, k) => k + 1).map((k) => <option key={k} value={k}>ניסוי {k}</option>)}
        </select>
        <select className="input w-32" value={who} onChange={(e) => setWho(e.target.value)} aria-label="של מי">
          <option>שלי</option>
          <option>של השותפה</option>
        </select>
        <label className={`btn-ghost cursor-pointer ${busy ? "opacity-50" : ""}`}>
          📎 העלאת הדוח
          <input type="file" className="hidden" accept=".docx,.pdf" disabled={busy}
            onChange={(e) => { report(e.target.files?.[0]); e.target.value = ""; }} />
        </label>
      </div>
      <div className="border-t border-line pt-3">
        <h3 className="font-semibold text-sm">🎙️ הקלטה של המרצה על המבחן</h3>
        <p className="text-xs text-muted mb-2">הקלטה מוואטסאפ (או כל קובץ קול / וידאו): היא מתומללת, וכל דגש על המבחן נכנס למבחן המעשי.</p>
        <label className={`btn-ghost cursor-pointer ${busy ? "opacity-50" : ""}`}>
          🎙️ העלאת הקלטה
          <input type="file" className="hidden" accept="audio/*,video/*,.opus,.ogg,.m4a,.mp3,.aac,.amr" disabled={busy}
            onChange={(e) => { recording(e.target.files?.[0]); e.target.value = ""; }} />
        </label>
      </div>
      <div className="border-t border-line pt-3">
        <h3 className="font-semibold text-sm">✍️ או לכתוב מה המרצה אמרה</h3>
        <p className="text-xs text-muted mb-2">בלי הקלטה – לכתוב (או להדביק) מה היא אמרה על המבחן; זה מעובד כמו הקלטה.</p>
        <textarea className="input min-h-28" value={said} onChange={(e) => setSaid(e.target.value)} disabled={busy}
          placeholder="למשל: במבחן המעשי יהיה ניסוי 3, צריך לדעת למדוד זמן עלייה בסקופ..." />
        <button className="btn mt-2" disabled={busy || said.trim().length < 20} onClick={async () => {
          setBusy(true); setMsg("שומר...");
          const r = await addLecturerText(courseId, said);
          setMsg(r); setBusy(false);
          if (r.startsWith("✓")) { setSaid(""); router.refresh(); }
        }}>💾 שמירה</button>
      </div>
      {msg && <p className="text-sm">{msg}</p>}
    </section>
  );
}
