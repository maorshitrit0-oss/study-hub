"use client";
import { useState } from "react";

/** One tap copies a long text (his request 16/11/2026: "copy all the assignment solutions at once"). */
export default function CopyText({ text, label }: { text: string; label: string }) {
  const [done, setDone] = useState(false);
  return (
    <button type="button" className="btn w-full"
      onClick={async () => {
        await navigator.clipboard.writeText(text);
        setDone(true);
        setTimeout(() => setDone(false), 2500);
      }}>
      {done ? "✓ הועתק" : label}
    </button>
  );
}
