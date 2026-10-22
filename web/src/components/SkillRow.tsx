"use client";

import { setSkillLevel } from "@/app/(app)/actions";
import { LEVELS, LEVEL_TONE, PROJECT_LEVELS, type Skill } from "@/lib/skills";

export default function SkillRow({ s }: { s: Skill }) {
  const names = s.kind === "project" ? PROJECT_LEVELS : LEVELS;
  return (
    <li className="py-2.5 space-y-1">
      <div className="flex justify-between items-center gap-3">
        <span className="font-medium">{s.ord}. {s.title}</span>
        <select aria-label="רמה" value={s.level} onChange={(e) => setSkillLevel(s.id, Number(e.target.value))}
          className={`shrink-0 rounded-full px-2 py-0.5 text-xs border-0 ${LEVEL_TONE[s.level]}`} style={{ fontSize: 16 }}>
          {names.map((n, i) => <option key={i} value={i}>{n}</option>)}
        </select>
      </div>
      {s.notes && <p className="text-xs text-muted whitespace-pre-line">{s.notes}</p>}
    </li>
  );
}
