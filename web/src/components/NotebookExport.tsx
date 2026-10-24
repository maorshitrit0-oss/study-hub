"use client";

import { useState } from "react";

/** Board snapshots are links only the app can open; NotebookLM gets the text. */
const clean = (md: string) => md.replace(/!\[[^\]]*\]\(slide:\d+\)\n?/g, "").trim();

/**
 * Sends a chapter (or a whole course) to NotebookLM, which turns it into a podcast in Hebrew ("Audio Overview"),
 * free with his Google account. Copy the text, or download it as a file, and add it there as a source.
 */
export default function NotebookExport({ title, text }: { title: string; text: string }) {
  const [msg, setMsg] = useState("");
  const body = `# ${title}\n\n${clean(text)}`;
  const file = `${title.replace(/[\\/:*?"<>|]+/g, " ").trim()}.md`;

  async function copy() {
    try {
      await navigator.clipboard.writeText(body);
      setMsg("✓ הועתק. עכשיו ב-NotebookLM: הוספת מקור ← טקסט שהועתק ← הדבקה.");
    } catch {
      setMsg("ההעתקה נחסמה - השתמש בהורדת הקובץ.");
    }
  }
  function download() {
    const url = URL.createObjectURL(new Blob([body], { type: "text/markdown;charset=utf-8" }));
    const a = Object.assign(document.createElement("a"), { href: url, download: file });
    a.click();
    URL.revokeObjectURL(url);
    setMsg("✓ הקובץ ירד. ב-NotebookLM: הוספת מקור ← העלאה ← לבחור את הקובץ.");
  }

  return (
    <details className="card">
      <summary className="cursor-pointer font-medium">🎧 פודקאסט בעברית (NotebookLM)</summary>
      <div className="space-y-3 mt-3 text-sm">
        <ol className="list-decimal ps-5 space-y-1 text-muted">
          <li>להעתיק את הטקסט (או להוריד כקובץ).</li>
          <li>לפתוח את NotebookLM ← מחברת חדשה ← להוסיף את הטקסט כמקור.</li>
          <li>בהגדרות (למעלה) ← שפת הפלט: עברית.</li>
          <li>Studio ← Audio Overview (סקירה קולית) ← יצירה. אחרי כמה דקות יש פודקאסט.</li>
        </ol>
        <div className="grid grid-cols-2 gap-2">
          <button type="button" className="btn" onClick={copy}>📋 העתקה</button>
          <button type="button" className="btn-ghost" onClick={download}>⬇️ הורדת קובץ</button>
        </div>
        <a href="https://notebooklm.google.com/" target="_blank" rel="noreferrer" className="btn-ghost w-full">פתיחת NotebookLM</a>
        {msg && <p className="text-good">{msg}</p>}
        <p className="text-xs text-muted">הפודקאסט נוצר מהפרק שכבר נבדק, אבל הדיבור עצמו נוצר אצל גוגל ולא נבדק. העברית שם לא מושלמת, לפעמים יש טעויות הגייה. מה שקובע הוא הפרק הכתוב.</p>
      </div>
    </details>
  );
}
