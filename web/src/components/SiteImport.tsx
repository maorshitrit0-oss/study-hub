"use client";

import { useState } from "react";
import { importSite } from "@/app/(app)/actions";

/** "Import the course site": one link instead of uploading the lecturer's files one by one. */
export default function SiteImport({ courseId, imported }: { courseId: string; imported: boolean }) {
  const [url, setUrl] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  async function go() {
    setBusy(true);
    setMsg(await importSite(courseId, url));
    setBusy(false);
  }

  return (
    <details className="mt-3 border-t border-line pt-3" >
      <summary className="cursor-pointer text-sm font-medium">
        🌐 {imported ? "אתר הקורס מיובא - מתעדכן כל בוקר" : "ייבוא אתר הקורס של המרצה (Notion)"}
      </summary>
      <p className="text-sm text-muted mt-2">
        מדביקים את הקישור לאתר, והמערכת מעתיקה לכאן את כל הקבצים שבו, וכותבת פרק קריאה ושאלון לכל שבוע,
        לדף שאלות החזרה ולכל מבחן קודם. מה שהמרצה מוסיף לאתר נכנס אוטומטית כל בוקר.
      </p>
      <div className="flex gap-2 mt-2">
        <input className="input flex-1" dir="ltr" placeholder="https://....notion.site/..." value={url}
          onChange={(e) => setUrl(e.target.value)} />
        <button className="btn" disabled={busy || !url.trim()} onClick={go}>{busy ? "..." : "ייבוא"}</button>
      </div>
      {msg && <p className="text-sm mt-2">{msg}</p>}
    </details>
  );
}
