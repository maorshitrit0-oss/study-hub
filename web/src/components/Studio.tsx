"use client";

import { useState, useTransition } from "react";
import { createMedia, deleteMedia } from "@/app/(app)/actions";
import type { Media } from "@/lib/studio";
import AutoRefresh from "./AutoRefresh";
import Chapter from "./Chapter";

const KIND = { podcast: "🎙️ פודקאסט", video: "🎬 סרטון", examples: "🏠 דוגמאות מהחיים" } as const;
const mmss = (s: number | null) => (s ? `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}` : "");

/**
 * Podcast, video and everyday examples made inside the app from the (fact-checked) chapters.
 * On a lesson page it works on that lesson; on a course page he picks the lessons.
 */
export default function Studio({ courseId, lessons, items, canVideo = false }: {
  courseId: string;
  lessons: { id: string; label: string }[]; // one = lesson page; several = pick
  items: Media[] | null;
  canVideo?: boolean;
}) {
  const single = lessons.length === 1;
  const [picked, setPicked] = useState<Set<string>>(new Set(lessons.map((l) => l.id)));
  const [msg, setMsg] = useState("");
  const [pending, start] = useTransition();

  if (items === null) return <p className="card text-sm text-warn">כדי להפעיל את הסטודיו צריך להריץ את קוד ה-SQL שלו ב-Supabase (studio.sql).</p>;
  const busy = items.some((m) => m.status === "queued" || m.status === "processing");

  const make = (kind: keyof typeof KIND) => start(async () => {
    const ids = lessons.filter((l) => picked.has(l.id)).map((l) => l.id);
    const res = await createMedia(courseId, kind, ids, single ? undefined : `${ids.length} שיעורים`);
    setMsg(res.error ? `⚠️ ${res.error}` : "✓ התחיל. זה לוקח כמה דקות - תקבל התראה כשזה מוכן.");
  });

  return (
    <section className="card space-y-3">
      <h2 className="font-semibold">🎧 סטודיו</h2>
      {busy && <AutoRefresh seconds={15} />}
      {!single && (
        <div className="space-y-1 max-h-48 overflow-y-auto text-sm">
          <label className="flex gap-2 font-medium">
            <input type="checkbox" checked={picked.size === lessons.length}
              onChange={(e) => setPicked(new Set(e.target.checked ? lessons.map((l) => l.id) : []))} />
            כל השיעורים
          </label>
          {lessons.map((l) => (
            <label key={l.id} className="flex gap-2">
              <input type="checkbox" checked={picked.has(l.id)} onChange={(e) => setPicked((p) => {
                const n = new Set(p);
                if (e.target.checked) n.add(l.id); else n.delete(l.id);
                return n;
              })} />
              {l.label}
            </label>
          ))}
        </div>
      )}
      <div className="grid grid-cols-2 gap-2">
        <button className="btn" disabled={pending || !picked.size} onClick={() => make("podcast")}>🎙️ צור פודקאסט</button>
        {single && <button className="btn-ghost" disabled={pending || !canVideo} onClick={() => make("video")}
          title={canVideo ? "" : "אין צילומי לוח בשיעור הזה"}>🎬 צור סרטון</button>}
      </div>
      {single && !canVideo && <p className="text-xs text-muted">סרטון נבנה מצילומי הלוח של ההרצאה; בשיעור הזה אין כאלה.</p>}
      {msg && <p className="text-sm">{msg}</p>}

      {items.length > 0 && (
        <ul className="space-y-3">
          {items.map((m) => (
            <li key={m.id} className="rounded-xl bg-bg/60 p-3 space-y-2">
              <div className="flex justify-between gap-2 text-sm">
                <span className="font-medium">{KIND[m.kind]}{m.title ? ` · ${m.title}` : ""} <span className="text-muted">{mmss(m.duration_sec)}</span></span>
                <button className="text-muted" aria-label="מחיקה" onClick={() => confirm("למחוק?") && deleteMedia(m.id)}>×</button>
              </div>
              {(m.status === "queued" || m.status === "processing") && <p className="text-sm text-warn animate-pulse">{m.progress ?? "בתור..."}</p>}
              {m.status === "error" && <p className="text-sm text-bad">⚠️ {m.error}</p>}
              {m.status === "ready" && m.kind === "podcast" && m.url && <audio controls preload="none" src={m.url} className="w-full" />}
              {m.status === "ready" && m.kind === "video" && m.url && <video controls playsInline preload="metadata" src={m.url} className="w-full rounded-lg" />}
              {m.status === "ready" && m.kind === "examples" && m.script && <Chapter md={m.script} slideUrls={{}} />}
              {m.status === "ready" && m.kind !== "examples" && m.script && (
                <details className="text-sm"><summary className="cursor-pointer text-muted">התסריט</summary><Chapter md={m.script} slideUrls={{}} /></details>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
