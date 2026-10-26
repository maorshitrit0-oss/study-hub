"use client";

import { useEffect, useState, type ReactNode } from "react";

/**
 * A collapsed card: one line with the title and a short summary; tap to open. Remembers open/closed per section
 * (same section in every course) on this device, and opens itself when the page is reached with its #id.
 */
export default function Fold({ id, title, hint, children, defaultOpen = false }: {
  id: string; title: ReactNode; hint?: ReactNode; children: ReactNode; defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  useEffect(() => {
    let saved: string | null = null;
    try { saved = localStorage.getItem(`fold:${id}`); } catch { /* private mode */ }
    // eslint-disable-next-line react-hooks/set-state-in-effect -- the saved choice exists only in the browser
    if (window.location.hash === `#${id}`) setOpen(true);
    else if (saved !== null) setOpen(saved === "1");
  }, [id]);

  return (
    <details id={id} open={open} className="card fold group scroll-mt-4"
      onToggle={(e) => {
        const now = (e.currentTarget as HTMLDetailsElement).open;
        setOpen(now);
        try { localStorage.setItem(`fold:${id}`, now ? "1" : "0"); } catch { /* private mode */ }
      }}>
      <summary className="flex items-center justify-between gap-3 cursor-pointer list-none select-none">
        <span className="font-semibold min-w-0">{title}</span>
        <span className="flex items-center gap-2 text-sm text-muted shrink-0">
          {hint}
          <span className="transition-transform group-open:rotate-180" aria-hidden>▾</span>
        </span>
      </summary>
      <div className="mt-3">{children}</div>
    </details>
  );
}
