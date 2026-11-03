// Timing diagrams that are computed, not drawn by the AI: the tutor gives the inputs (clock, D, reset) and the
// flip-flop output Q is simulated here, so a diagram can never show a wrong Q.
//
// ```wave
// {"cycles": 6, "signals": {"rst": "1100000000..", "D": "001111000011"}, "ff": {"type": "sync", "q": "Q"}}
// ```
// - Time is in half clock periods ("ticks"): tick 2k is the rising edge of cycle k, tick 2k+1 the falling edge.
//   A signal string has one char per tick ("0", "1", "x", or "." = same as before); shorter strings hold their last value.
// - ff.type: "none" (plain D flip-flop), "sync" (reset only at a rising edge), "async" (reset at once, any time).
//   ff.reset: name of the reset signal (default "rst"), ff.active: 1 (default) or 0 for active-low.
//   ff.hide: true draws Q as "?" - for "predict Q" questions.

export type Level = "0" | "1" | "x";
export type WaveSpec = {
  cycles: number;
  signals: Record<string, string>;
  ff?: { type: "none" | "sync" | "async"; q?: string; d?: string; reset?: string; active?: 0 | 1; init?: Level; hide?: boolean };
  // A mark sits on a tick; "edge": n puts it on rising edge n (1-based) - what the AI usually means (03/11/2026).
  marks?: { tick?: number; edge?: number; label: string }[];
};
export type Edge = { n: number; inputs: [string, Level][]; q?: Level };
export type Row = { name: string; levels: Level[]; clock?: boolean; hidden?: boolean };

function expand(s: string, ticks: number): Level[] {
  const out: Level[] = [];
  let last: Level = "x";
  for (let t = 0; t < ticks; t++) {
    const c = s[t] ?? ".";
    if (c === "0" || c === "1" || c === "x") last = c;
    out.push(last);
  }
  return out;
}

/**
 * Marks on whole ticks. Gemini put "עלייה 1..4" on ticks 1,3,5,7 - the falling edges: a mark that names a rising edge
 * (or is given as "edge") goes on the rising edge itself.
 */
function placeMarks(marks: WaveSpec["marks"], ticks: number) {
  return (marks ?? []).map((m) => {
    let tick = m.edge ? 2 * (m.edge - 1) : Math.round(m.tick ?? 0);
    if (!m.edge && tick % 2 === 1 && /עלי|↑|rising|posedge|edge/i.test(m.label)) tick -= 1;
    return { tick: Math.max(0, Math.min(ticks - 1, tick)), label: m.label };
  });
}

export function parseWave(src: string): { rows: Row[]; ticks: number; marks: { tick: number; label: string }[]; edges: Edge[] } {
  const spec = JSON.parse(src) as WaveSpec;
  const cycles = Math.max(1, Math.min(16, Math.round(spec.cycles || 6)));
  const ticks = cycles * 2;
  const clk: Level[] = Array.from({ length: ticks }, (_, t) => (t % 2 === 0 ? "1" : "0"));
  const rows: Row[] = [{ name: "clk", levels: clk, clock: true }];
  const sig = new Map<string, Level[]>();
  for (const [name, s] of Object.entries(spec.signals ?? {})) {
    if (/^clk$/i.test(name)) continue;
    const levels = expand(String(s), ticks);
    sig.set(name, levels);
    rows.push({ name, levels });
  }
  if (spec.ff) {
    const d = sig.get(spec.ff.d ?? "D") ?? expand("x", ticks);
    const rst = sig.get(spec.ff.reset ?? "rst");
    const active: Level = spec.ff.active === 0 ? "0" : "1";
    const q: Level[] = [];
    let cur: Level = spec.ff.init ?? "x";
    for (let t = 0; t < ticks; t++) {
      const inReset = rst?.[t] === active;
      if (spec.ff.type === "async" && inReset) cur = "0";
      else if (t % 2 === 0) {
        // Rising edge: the flip-flop takes D as it was just before the edge.
        const before = t === 0 ? d[0] : d[t - 1];
        cur = spec.ff.type === "sync" && (t === 0 ? rst?.[0] : rst?.[t - 1]) === active ? "0" : before;
      }
      q.push(cur);
    }
    rows.push({ name: spec.ff.q ?? "Q", levels: q, hidden: !!spec.ff.hide });
  }
  // What the flip-flop saw at each rising edge (inputs just before it) and what Q became - computed, never written.
  const edges: Edge[] = spec.ff ? Array.from({ length: cycles }, (_, k) => {
    const t = 2 * k;
    const inputs = [...sig].map(([name, lv]) => [name, t === 0 ? lv[0] : lv[t - 1]] as [string, Level]);
    const q = rows[rows.length - 1].levels[t];
    return { n: k + 1, inputs, q: spec.ff?.hide ? undefined : q };
  }) : [];
  return { rows, ticks, marks: placeMarks(spec.marks, ticks), edges };
}
