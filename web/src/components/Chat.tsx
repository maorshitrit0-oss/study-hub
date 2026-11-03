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

const SELF_STARTERS = [
  "חידון: שאלה אמריקאית על כל נושא שלמדתי עד עכשיו, אחת בכל פעם",
  "יש לי 20 דקות - בוא נמשיך מהנושא הבא במפה",
  "יש לי 10 דקות - שאלה אחת על נקודה שטעיתי בה",
  "שעה מול המחשב - בוא נתקדם בפרויקט",
  "תבחן אותי: שאלת ראיון סטודנט על מה שכבר למדתי",
];

const STARTERS = [
  "תלמד אותי את ההרצאה האחרונה שלב אחרי שלב",
  "תן לי שאלון אמריקאי של 5 שאלות על כל החומר",
  "לפי מבחני העבר - איך ייראה המבחן ומה הכי חשוב ללמוד?",
  "מה הנושאים שהכי כדאי לחזור עליהם?",
  "איך מה שלמדנו משמש בתעשייה, ומה שואלים על זה בראיונות עבודה?",
  "תתרגם לי לעברית את המצגת / הקובץ באנגלית, עם המונחים באנגלית בסוגריים",
];

/** The tutor's last message ends with a 4-option question: offer one-tap answers (he still writes the reasoning). */
function hasChoices(m?: Msg) {
  return m?.role === "model" && (m.content.match(/^\s*(?:\*\*)?[1-4][.)]/gm)?.length ?? 0) >= 4;
}

export default function Chat({ courseId, userId, initial, isLab = false, isSelf = false, threadId = null, autoPrompt }: {
  courseId: string; userId: string; initial: Msg[]; isLab?: boolean; isSelf?: boolean; threadId?: string | null;
  autoPrompt?: string; // sent once when the chat opens empty (a VLSI program session)
}) {
  const [msgs, setMsgs] = useState<Msg[]>(initial);
  const [text, setText] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const [withFiles, setWithFiles] = useState(isLab); // lab work always needs the booklets and reports
  const end = useRef<HTMLDivElement>(null);
  const input = useRef<HTMLTextAreaElement>(null);

  const autoSent = useRef(false);
  useEffect(() => {
    if (!autoPrompt || autoSent.current || initial.length) return;
    autoSent.current = true;
    send(autoPrompt);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- once, on open
  }, []);

  // Braces matter: newer browsers return a Promise from scrollIntoView, and React would call it as the cleanup.
  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs]);

  // Images can be pasted (iPhone: long-press -> Paste, computer: Ctrl+V) as well as picked with 📷.
  function addImages(list: FileList | File[] | null | undefined) {
    const imgs = Array.from(list ?? []).filter((f) => f.type.startsWith("image/"));
    if (imgs.length) setFiles((old) => [...old, ...imgs].slice(0, 10));
    return imgs.length > 0;
  }

  async function send(raw: string) {
    // An image on its own is a question too.
    const message = raw.trim() || (files.length ? "מה יש בתמונה? תסביר אותה, ואם יש בה תרגיל - תפתור אותו שלב אחרי שלב." : "");
    if (!message.trim() || busy) return;
    setBusy(true);
    const sb = supabaseBrowser();
    const imagePaths: string[] = [];
    const previews: string[] = [];
    for (const f of files.slice(0, 10)) {
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
      body: JSON.stringify({ courseId, message, imagePaths, withFiles, threadId }),
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

  /** Independent check of answer k against the course material (and search); appended as a new message. */
  async function verify(k: number) {
    if (busy) return;
    const question = [...msgs.slice(0, k)].reverse().find((m) => m.role === "user")?.content ?? "";
    setBusy(true);
    setMsgs((m) => [...m, { role: "model", content: "" }]);
    const res = await fetch("/api/chat/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courseId, question, answer: msgs[k].content, threadId }),
    }).catch(() => null);
    const text = res ? await res.text() : "⚠️ אין חיבור - לנסות שוב.";
    setMsgs((m) => [...m.slice(0, -1), { role: "model", content: res?.ok ? text : `⚠️ ${text}` }]);
    setBusy(false);
  }

  return (
    <div className="flex flex-col gap-3">
      {msgs.length === 0 && (
        <div className="grid gap-2">
          {(isSelf ? SELF_STARTERS : isLab ? LAB_STARTERS : STARTERS).map((s) => <button key={s} className="card text-start text-sm" onClick={() => send(s)}>{s}</button>)}
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
            <>
              <Chapter md={m.content} slideUrls={{}} />
              {!busy && !/^(🔍|⚠️)/.test(m.content.trim()) && msgs[k + 1]?.content?.startsWith("🔍") !== true && (
                <button type="button" onClick={() => verify(k)} className="text-xs text-accent mt-1">🔍 לאמת את התשובה</button>
              )}
            </>
          ) : (
            <p className="text-muted animate-pulse">חושב...</p>
          )}
        </div>
      ))}
      {isSelf && !busy && hasChoices(msgs[msgs.length - 1]) && (
        <div className="flex gap-2 justify-center">
          {[1, 2, 3, 4].map((n) => (
            <button key={n} type="button" className="btn-ghost w-14 text-lg"
              onClick={() => { setText(`תשובה ${n}. הנימוק שלי: `); input.current?.focus(); }}>{n}</button>
          ))}
        </div>
      )}
      <div ref={end} />
      <form
        onSubmit={(e) => { e.preventDefault(); send(text); }}
        className="sticky bottom-20 card p-2 flex flex-col gap-2 shadow-lg"
      >
        <label className={`flex items-center gap-2 text-xs text-muted px-1 ${isSelf ? "hidden" : ""}`}>
          <input type="checkbox" checked={withFiles} onChange={(e) => setWithFiles(e.target.checked)} />
          עם קבצי הקורס (מבחני עבר, מצגות) - איטי יותר
        </label>
        {files.length > 0 && (
          <div className="flex gap-2 items-center overflow-x-auto">
            {files.map((f, i) => (
              <span key={i} className="relative shrink-0">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={URL.createObjectURL(f)} alt="" className="h-14 w-14 object-cover rounded-lg border border-line" />
                <button type="button" aria-label="הסרה" onClick={() => setFiles((old) => old.filter((_, k) => k !== i))}
                  className="absolute -top-1.5 -start-1.5 bg-bad text-white rounded-full w-5 h-5 text-xs leading-5">×</button>
              </span>
            ))}
          </div>
        )}
        <div className="flex gap-2 items-end">
          <label className="btn-ghost px-3 cursor-pointer" aria-label="צירוף תמונה">
            📷
            <input type="file" accept="image/*" multiple className="hidden"
              onChange={(e) => { addImages(e.target.files); e.target.value = ""; }} />
          </label>
          <textarea ref={input} className="input flex-1 min-h-11 max-h-40" rows={1} value={text} placeholder={isSelf ? "התשובה שלך + הנימוק..." : "שאל כל דבר, או הדבק תמונה..."}
            onChange={(e) => setText(e.target.value)}
            onPaste={(e) => { if (addImages(e.clipboardData?.files)) e.preventDefault(); }}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey && !("ontouchstart" in window)) { e.preventDefault(); send(text); } }} />
          <button className="btn px-4" disabled={busy || (!text.trim() && !files.length)}>שלח</button>
        </div>
      </form>
    </div>
  );
}
