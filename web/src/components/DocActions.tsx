"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { rebuildDoc } from "@/app/(app)/actions";
import type { DocKind } from "@/lib/courseDocs";

export default function DocActions({ courseId, kind, exists }: { courseId: string; kind: DocKind; exists: boolean }) {
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const router = useRouter();
  return (
    <div className="flex gap-2 items-center flex-wrap">
      <button className="btn" disabled={busy} onClick={async () => {
        setBusy(true); setMsg("בונה מכל השיעורים (דקה-שתיים)...");
        const res = await rebuildDoc(courseId, kind);
        setMsg(res); setBusy(false); router.refresh();
      }}>{busy ? "..." : exists ? "🔄 לעדכן מכל השיעורים" : "לבנות"}</button>
      {exists && <button className="btn-ghost" onClick={() => window.print()}>🖨️ הדפסה</button>}
      {msg && <span className="text-sm">{msg}</span>}
    </div>
  );
}
