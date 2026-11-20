"use client";

import { useRef, useState } from "react";
import { supabaseBrowser } from "@/lib/supabase/client";

const LIMIT = 48 * 1024 * 1024; // the storage takes up to 50 MB a file

type FF = {
  load: (o: { coreURL: string; wasmURL: string }) => Promise<boolean>;
  on: (e: "progress", cb: (p: { progress: number; time: number }) => void) => void;
  createDir: (p: string) => Promise<boolean>;
  mount: (t: string, o: { files: File[] }, p: string) => Promise<boolean>;
  exec: (args: string[]) => Promise<number>;
  readFile: (p: string) => Promise<Uint8Array | string>;
  deleteFile: (p: string) => Promise<boolean>;
  terminate: () => void;
};

/**
 * A lecture recording straight from his computer or phone (his request 20/11/2026: "upload the MP4 to the app, not via
 * Drive"). A file over 48 MB is shrunk IN THE BROWSER first (ffmpeg, served from this site): the speech (mono, 16 kHz -
 * all the transcription needs) + one frame every 2 s for the board snapshots (5 s if it is still too big). A 1.5 h
 * lecture becomes ~20-45 MB. Then it goes to storage and the worker processes it like any recording.
 */
export default function RecordingUpload({ userId, courseId, onDone }: {
  userId: string; courseId: string; onDone: (path: string) => void;
}) {
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  async function shrink(file: File, every: number, crf: number, ff: FF): Promise<Blob> {
    setMsg(`מכין את ההקלטה להעלאה (כוללת קול + תמונה כל ${every} שניות)... 0%`);
    const rc = await ff.exec(["-skip_frame:v", "nokey", "-i", `/in/${file.name}`, "-vf", `fps=1/${every},scale=1280:-2`,
      "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-crf", String(crf), "-g", "300",
      "-c:a", "aac", "-b:a", "24k", "-ac", "1", "-ar", "16000", "-movflags", "+faststart", "/out.mp4"]);
    if (rc !== 0) throw new Error("ההמרה נכשלה");
    const data = await ff.readFile("/out.mp4");
    await ff.deleteFile("/out.mp4");
    return new Blob([data as Uint8Array<ArrayBuffer>], { type: "video/mp4" });
  }

  async function pick(file: File | undefined) {
    if (!file) return;
    setBusy(true);
    try {
      let blob: Blob = file;
      if (file.size > LIMIT) {
        setMsg("טוען את כלי ההמרה (פעם ראשונה כ-30MB)...");
        const mod = await import(/* webpackIgnore: true */ /* turbopackIgnore: true */ "/ffmpeg/index.js" as string);
        const ff = new mod.FFmpeg() as FF;
        ff.on("progress", ({ progress }) => {
          if (progress > 0 && progress <= 1) setMsg((m) => m.replace(/\d+%$/, `${Math.round(progress * 100)}%`));
        });
        await ff.load({ coreURL: "/ffmpeg/ffmpeg-core.js", wasmURL: "/ffmpeg/ffmpeg-core.wasm" });
        await ff.createDir("/in");
        await ff.mount("WORKERFS", { files: [file] }, "/in");
        blob = await shrink(file, 2, 32, ff);
        if (blob.size > LIMIT) blob = await shrink(file, 5, 36, ff);
        ff.terminate();
        if (blob.size > LIMIT) throw new Error(`גם אחרי ההקטנה ${Math.round(blob.size / 1048576)}MB - אפשר לחלק את ההקלטה לשני חלקים`);
      }
      setMsg(`מעלה (${Math.round(blob.size / 1048576)}MB)...`);
      // the original name stays in the path: "x2" in it means a recording played faster (the worker slows it back)
      const stem = file.name.replace(/\.[^.]+$/, "").replace(/[^\w.\-]+/g, "_").slice(0, 60);
      const path = `${userId}/sources/${courseId}/${Date.now()}_${stem}.mp4`;
      const { error } = await supabaseBrowser().storage.from("study").upload(path, blob, { contentType: "video/mp4" });
      if (error) throw new Error(error.message);
      setMsg(`✓ ${file.name} הועלה – השיעור נוסף והעיבוד מתחיל לבד. אפשר לצאת מהדף.`);
      onDone(path);
    } catch (e) {
      setMsg(`⚠️ ${(e as Error).message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-1">
      <label className={`btn-ghost w-full text-center block ${busy ? "opacity-60 pointer-events-none" : "cursor-pointer"}`}>
        🎬 העלאת הקלטה מהמכשיר (MP4 / קובץ קול)
        <input type="file" accept="video/*,audio/*,.mp4,.m4a,.mp3" className="hidden" disabled={busy}
          onChange={(e) => pick(e.target.files?.[0])} />
      </label>
      {msg && <p className="text-sm text-muted">{msg}</p>}
      {busy && <p className="text-xs text-muted">להשאיר את הדף פתוח רק עד ש-✓ מופיע; אחרי זה הכל קורה לבד.</p>}
    </div>
  );
}

/** The same upload inside a form (a lesson whose Zoom link failed): fills a hidden "source_path" field. */
export function RecordingField({ userId, courseId }: { userId: string; courseId: string }) {
  const [path, setPath] = useState("");
  const ref = useRef<HTMLInputElement>(null);
  return (
    <>
      <input ref={ref} type="hidden" name="source_path" value={path} />
      <RecordingUpload userId={userId} courseId={courseId} onDone={(p) => {
        setPath(p);
        setTimeout(() => ref.current?.form?.requestSubmit(), 50); // saves by itself (his wish: only upload the file)
      }} />
    </>
  );
}
