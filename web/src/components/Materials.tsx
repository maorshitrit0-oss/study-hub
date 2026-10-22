"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { supabaseBrowser } from "@/lib/supabase/client";
import { addMaterial, deleteMaterial } from "@/app/(app)/actions";

type Material = { id: string; title: string; kind: string; storage_path: string };
const KINDS: Record<string, string> = {
  syllabus: "סילבוס", slides: "מצגת", past_exam: "מבחן עבר", solution: "פתרון", lab_guide: "חוברת מעבדה", other: "אחר",
};

export default function Materials({ courseId, userId, items }: { courseId: string; userId: string; items: Material[] }) {
  const [kind, setKind] = useState("slides");
  const [busy, setBusy] = useState("");
  const router = useRouter();

  async function upload(files: FileList | null) {
    if (!files?.length) return;
    const sb = supabaseBrowser();
    for (const file of Array.from(files)) {
      setBusy(`מעלה ${file.name}...`);
      const safe = file.name.replace(/[^\w.\-]+/g, "_");
      const path = `${userId}/materials/${courseId}/${Date.now()}_${safe}`;
      const { error } = await sb.storage.from("study").upload(path, file, { contentType: file.type });
      if (error) { setBusy(`שגיאה: ${error.message}`); return; }
      await addMaterial(courseId, { title: file.name, kind, path, mime: file.type, size: file.size });
    }
    setBusy("");
    router.refresh();
  }

  async function open(path: string) {
    const { data } = await supabaseBrowser().storage.from("study").createSignedUrl(path, 3600);
    if (data) window.open(data.signedUrl, "_blank");
  }

  return (
    <div className="space-y-3">
      {items.length > 0 && (
        <ul className="divide-y divide-line">
          {items.map((m) => (
            <li key={m.id} className="flex items-center gap-2 py-2">
              <span className="chip">{KINDS[m.kind] ?? m.kind}</span>
              <button className="flex-1 text-start truncate" onClick={() => open(m.storage_path)}>{m.title}</button>
              <button className="text-muted text-sm" onClick={async () => { await deleteMaterial(m.id, courseId); router.refresh(); }}>מחיקה</button>
            </li>
          ))}
        </ul>
      )}
      <div className="flex gap-2">
        <select className="input w-36" value={kind} onChange={(e) => setKind(e.target.value)}>
          {Object.entries(KINDS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
        <label className="btn-ghost flex-1 cursor-pointer">
          העלאת קבצים
          <input type="file" multiple className="hidden" accept=".pdf,.docx,.pptx,.txt,.md,image/*"
            onChange={(e) => upload(e.target.files)} />
        </label>
      </div>
      {busy && <p className="text-sm text-muted">{busy}</p>}
      <p className="text-xs text-muted">ה-AI בצ&apos;אט של הקורס קורא את קבצי ה-PDF והתמונות (מבחני עבר, מצגות, סילבוס).</p>
    </div>
  );
}
