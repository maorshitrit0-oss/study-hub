"use client";

import { useState, useTransition } from "react";
import { setCancelled } from "@/app/(app)/actions";

export type Meeting = { slotId: string; date: string; label: string; course: string; kind: string; time: string; cancelled: boolean };

/** The class meetings around today: mark one cancelled (make-up later) - the lecture moves to the next meeting. */
export default function MeetingsToggle({ items }: { items: Meeting[] }) {
  const [state, setState] = useState(() => new Map(items.map((m) => [`${m.slotId}|${m.date}`, m.cancelled])));
  const [pending, start] = useTransition();
  return (
    <ul className="divide-y divide-line">
      {items.map((m) => {
        const k = `${m.slotId}|${m.date}`;
        const off = state.get(k);
        return (
          <li key={k} className="flex items-center justify-between gap-2 py-2.5">
            <span className={`min-w-0 text-sm ${off ? "line-through text-muted" : ""}`}>
              <b>{m.label}</b> · {m.course} · {m.kind} · {m.time}
            </span>
            <button disabled={pending} className={`shrink-0 text-xs rounded-full px-3 py-1 border ${off ? "border-bad text-bad" : "border-line text-muted"}`}
              onClick={() => start(async () => {
                setState(new Map(state).set(k, !off));
                await setCancelled(m.slotId, m.date, !off);
              })}>
              {off ? "🚫 בוטל · לביטול" : "בוטל?"}
            </button>
          </li>
        );
      })}
    </ul>
  );
}
