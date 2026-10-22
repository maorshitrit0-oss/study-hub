"use client";

import { useEffect, useRef, useState } from "react";
import Chapter from "./Chapter";
import { supabaseBrowser } from "@/lib/supabase/client";

type Msg = { role: "user" | "model"; content: string; images?: string[] };

const LAB_STARTERS = [
  "בוא נלמד את הניסוי הבא לפי הדוח המכין",
  "תעזור לי לפתור את שאלות הדוח המכין, שאלה אחרי שאלה",
  "תכין אותי ללוח: אני מסביר את הניסוי ואתה שואל כמו המדריך",
  "בוחן כניסה על הניסוי - שאלה אחת בכל פעם",
  "השווה את הדוח המסכם הקודם (של שיראל / יהונתן) לניסוי הזה לפי החוברת העדכנית - מה בדיוק לשנות?",
];

const STARTERS = [
  "תלמד אותי את ההרצאה האחרונה שלב אחרי שלב",
  "תן לי שאלון אמריקאי של 5 שאלות על כל החומר",
  "לפי מבחני העבר - איך ייראה המבחן ומה הכי חשוב ללמוד?",
  "מה הנושאים שהכי כדאי לחזור עליהם?",
];

export default function Chat({ courseId, userId, initial, isLab = false }: {
  courseId: string; userId: string; initial: Msg[]; isLab?: boolean;
}) {
  const [msgs, setMsgs] = useState<Msg[]>(initial);
  const [text, setText] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const [withFiles, setWithFiles] = useState(isLab); // lab work always needs the booklets and reports
  const end = useRef<HTMLDivElement>(null);

  useEffect(() => end.current?.scrollIntoView({ behavior: "smooth" }), [msgs]);

  async function send(message: string) {
    if (!message.trim() || busy) return;
    setBusy(true);
    const sb = supabaseBrowser();
    const imagePaths: string[] = [];
    const previews: string[] = [];
    for (const f of files) {
      const path = `${userId}/chat/${courseId}/${Date.now()}_${f.name.replace(/[^\w.\-]+/g, "_")}`;
      const { error } = await sb.storage.from("study").upload(path, f, { contentType: f.type });
      if (!error) { imagePaths.push(path); previews.push(URL.createObjectURL(f)); }
    }
    setFiles([]);
    setText("");
    setMsgs((m) => [...m, { role: "user", content: message, images: previews }, { role: "model", content: "" }]);

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courseId, message, imagePaths, withFiles }),
    });
    if (!res.ok || !res.body) {
      const err = await res.text();
      setMsgs((m) => [...m.slice(0, -1), { role: "model", content: `⚠️ ${err}` }]);
      setBusy(false);
      return;
    }
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    let acc = "";
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      acc += dec.decode(value, { stream: true });
      setMsgs((m) => [...m.slice(0, -1), { role: "model", content: acc }]);
    }
    setBusy(false);
  }

  return (
    <div className="flex flex-col gap-3">
      {msgs.length === 0 && (
        <div className="grid gap-2">
          {(isLab ? LAB_STARTERS : STARTERS).map((s) => <button key={s} className="card text-start text-sm" onClick={() => send(s)}>{s}</button>)}
        </div>
      )}
      {msgs.map((m, k) => (
        <div key={k} className={m.role === "user" ? "self-start max-w-[85%] rounded-2xl bg-accent text-white px-4 py-2.5" : "card"}>
          {m.images?.map((src) => (
            // eslint-disable-next-line @next/next/no-img-element
            <img key={src} src={src} alt="" className="rounded-lg mb-2 max-h-48" />
          ))}
          {m.role === "user" ? (
            <p className="whitespace-pre-line">{m.content}</p>
          ) : m.content ? (
            <Chapter md={m.content} slideUrls={{}} />
          ) : (
            <p className="text-muted animate-pulse">חושב...</p>
          )}
        </div>
      ))}
      <div ref={end} />
      <form
        onSubmit={(e) => { e.preventDefault(); send(text); }}
        className="sticky bottom-20 card p-2 flex flex-col gap-2 shadow-lg"
      >
        <label className="flex items-center gap-2 text-xs text-muted px-1">
          <input type="checkbox" checked={withFiles} onChange={(e) => setWithFiles(e.target.checked)} />
          עם קבצי הקורס (מבחני עבר, מצגות) - איטי יותר
        </label>
        {files.length > 0 && (
          <div className="flex gap-2 text-xs text-muted">
            📎 {files.map((f) => f.name).join(", ")}
            <button type="button" onClick={() => setFiles([])} className="text-bad">הסר</button>
          </div>
        )}
        <div className="flex gap-2 items-end">
          <label className="btn-ghost px-3 cursor-pointer" aria-label="צירוף תמונה">
            📷
            <input type="file" accept="image/*" multiple className="hidden"
              onChange={(e) => setFiles(Array.from(e.target.files ?? []))} />
          </label>
          <textarea className="input flex-1 min-h-11 max-h-40" rows={1} value={text} placeholder="שאל כל דבר על הקורס..."
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey && !("ontouchstart" in window)) { e.preventDefault(); send(text); } }} />
          <button className="btn px-4" disabled={busy || !text.trim()}>שלח</button>
        </div>
      </form>
    </div>
  );
}
