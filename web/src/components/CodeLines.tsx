"use client";

import { useEffect, useRef, useState } from "react";
import { fixArabic } from "@/lib/math";
import { codeHash } from "@/lib/codeHash";

type Line = { code: string; he: string };


/**
 * Under every code block (04/11/2026, he is not strong in code): "מה כל שורה עושה" - each line and what it does in
 * Hebrew. Loaded when the block scrolls into view: written ahead of time by worker/codelines.py, or once by Gemini, kept
 * in storage for all his devices and in this browser. When Gemini is out (quota / busy) the fold stays closed with a
 * quiet note and a retry button - never a red error over the chapter (06/11/2026).
 */
export default function CodeLines({ code, lang }: { code: string; lang: string }) {
  const key = `codelines:${codeHash(code)}`;
  const box = useRef<HTMLDetailsElement>(null);
  const [lines, setLines] = useState<Line[] | null>(null);
  const [error, setError] = useState("");
  const [later, setLater] = useState(false);
  const [loading, setLoading] = useState(false);
  const [tries, setTries] = useState(0);

  useEffect(() => {
    const el = box.current;
    if (!el) return;
    let started = false;
    const load = async () => {
      if (started) return;
      started = true;
      try {
        // Before 06/11 the key hashed the block with its trailing newline - those are still his.
        const saved = localStorage.getItem(key) ?? localStorage.getItem(`codelines:${codeHash(code, true)}`);
        if (saved) { setLines(JSON.parse(saved)); return; }
      } catch { /* private mode */ }
      setLoading(true);
      try {
        const res = await fetch("/api/explain-code", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ code, lang }) });
        const out = await res.json();
        if (!res.ok) { setLater(Boolean(out.later)); throw new Error(out.error || "שגיאה"); }
        setError("");
        setLines(out.lines);
        try { localStorage.setItem(key, JSON.stringify(out.lines)); } catch { /* full */ }
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e));
        started = false;
      } finally {
        setLoading(false);
      }
    };
    if (tries) { load(); return; }
    const io = new IntersectionObserver((es) => { if (es.some((e) => e.isIntersecting)) { io.disconnect(); load(); } }, { rootMargin: "300px" });
    io.observe(el);
    return () => io.disconnect();
  }, [code, lang, key, tries]);

  return (
    <details ref={box} open={!error} className="codelines">
      <summary className="cursor-pointer text-sm text-accent">
        📖 מה כל שורה עושה{error && <span className="text-xs text-muted"> · {later ? "יגיע מאוחר יותר" : "לא נטען"}</span>}
      </summary>
      {loading && <p className="text-xs text-muted py-1">מתרגם את הקוד לעברית, שורה-שורה...</p>}
      {error && (
        <p className="text-xs text-muted py-1">
          {later
            ? "Gemini לא זמין כרגע (המכסה החינמית מתאפסת בסביבות 10:00). ההסבר ייכתב לבד בבוקר; עד אז - ההסבר בטקסט של הפרק."
            : error}{" "}
          <button type="button" className="text-accent underline" onClick={() => { setError(""); setTries((t) => t + 1); }}>לנסות שוב</button>
        </p>
      )}
      {lines && (
        // Each code line whole on its own row (scrolls sideways, never wraps), its Hebrew under it.
        <ol>
          {lines.map((l, i) => (
            <li key={i}>
              <pre className="cl-code">{l.code}</pre>
              <div className="cl-he">{fixArabic(l.he)}</div>
            </li>
          ))}
        </ol>
      )}
    </details>
  );
}
