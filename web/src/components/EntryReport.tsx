"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { supabaseBrowser } from "@/lib/supabase/client";
import { addEntryReport, readEntryFiles, retryEntryReport } from "@/app/(app)/actions";

/** "What were you asked?" - paste what classmates said (or a screenshot of the group chat). */
export default function EntryReport({ courseId, userId, experiment, experiments }: {
  courseId: string; userId: string; experiment: number; experiments: number[];
}) {
  const [n, setN] = useState(experiment);
  const [text, setText] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const router = useRouter();

  async function send() {
    setBusy(true);
    setMsg("מעלה...");
    const paths: string[] = [];
    for (const [i, f] of files.entries()) {
      const path = `${userId}/entry/${courseId}/${Date.now()}_${i}.${(f.name.split(".").pop() || "jpg").toLowerCase()}`;
      const { error } = await supabaseBrowser().storage.from("study").upload(path, f, { contentType: f.type || "image/jpeg" });
      if (error) { setMsg(`העלאת הצילום נכשלה: ${error.message}`); setBusy(false); return; }
      paths.push(path);
    }
    setMsg("כותב את השאלות והפתרונות (עד דקה)...");
    const res = await addEntryReport(courseId, n, text, paths);
    setMsg(res);
    if (res.startsWith("✓")) { setText(""); setFiles([]); router.refresh(); }
    setBusy(false);
  }

  return (
    <div className="space-y-2">
      <label className="flex items-center gap-2 text-sm">
        ניסוי
        <select className="input w-24" value={n} onChange={(e) => setN(Number(e.target.value))}>
          {[...new Set([...experiments, experiment, ...Array.from({ length: 10 }, (_, i) => i + 1)])].sort((a, b) => a - b)
            .map((x) => <option key={x} value={x}>{x}</option>)}
        </select>
      </label>
      <textarea className="input w-full min-h-28" value={text} onChange={(e) => setText(e.target.value)}
        placeholder={"מה שאלו אותם? אפשר להדביק מהוואטסאפ כמו שזה, גם בלי תשובות.\nלמשל: שאלו מה תדר הקטעון של המסנן בסימולציה, ומה קורה ליציאה כשמגדילים את R2"} />
      <div className="flex gap-2 items-center flex-wrap">
        <label className="btn-ghost cursor-pointer">
          📷 צילומי מסך ({files.length})
          <input type="file" accept="image/*" multiple className="hidden" onChange={(e) => setFiles(Array.from(e.target.files ?? []))} />
        </label>
        <button className="btn" disabled={busy || (!text.trim() && !files.length)} onClick={send}>{busy ? "..." : "שליחה"}</button>
      </div>
      {msg && <p className="text-sm">{msg}</p>}
    </div>
  );
}

export function ReadEntryFiles({ courseId }: { courseId: string }) {
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const router = useRouter();
  return (
    <div>
      <button className="btn-ghost" disabled={busy} onClick={async () => {
        setBusy(true); setMsg("קורא את הקבצים (דקה-שתיים)...");
        setMsg(await readEntryFiles(courseId)); setBusy(false); router.refresh();
      }}>📂 לקרוא בחני כניסה מהקבצים של הקורס</button>
      {msg && <p className="text-sm mt-1">{msg}</p>}
    </div>
  );
}

export function RetryReport({ id, courseId }: { id: string; courseId: string }) {
  const [msg, setMsg] = useState("");
  const router = useRouter();
  return (
    <>
      <button className="text-accent text-sm" onClick={async () => { setMsg("..."); setMsg(await retryEntryReport(id, courseId)); router.refresh(); }}>לנסות שוב</button>
      {msg && <span className="text-sm"> {msg}</span>}
    </>
  );
}
