"use client";

import { useState } from "react";

const SIM = "https://www.falstad.com/circuit/circuitjs.html";

/**
 * The virtual lab: Falstad CircuitJS (free, in the browser) - components, power supplies, function generator,
 * scope and meters. Loaded only when opened (it is heavy). Builds start from an empty board.
 */
export default function VirtualLab() {
  const [open, setOpen] = useState(false);
  const empty = `${SIM}?cct=${encodeURIComponent("$ 1 0.000005 10.20027730826997 50 5 50 5e-11\n")}&whiteBackground=false`;
  return (
    <div className="mt-2">
      {!open ? (
        <button type="button" className="btn-ghost w-full" onClick={() => setOpen(true)}>🔧 לבנות במעבדה הווירטואלית</button>
      ) : (
        <div className="space-y-1">
          <iframe src={empty} title="מעבדה וירטואלית" className="w-full h-[70vh] rounded-xl border border-line bg-white" />
          <p className="text-xs text-muted">
            רכיבים: מקש ימני / לחיצה ארוכה על הלוח ← Draw (נגדים, קבלים, Op-Amp, מקורות AC/DC, אדמה). סקופ: לחיצה ארוכה על
            רכיב ← View in Scope. <a href={empty} target="_blank" rel="noreferrer" className="text-accent">פתיחה במסך מלא ↗</a>
          </p>
        </div>
      )}
    </div>
  );
}
