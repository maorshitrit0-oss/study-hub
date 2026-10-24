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
  marks?: { tick: number; label: string }[];
};
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

export function parseWave(src: string): { rows: Row[]; ticks: number; marks: WaveSpec["marks"] } {
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
  return { rows, ticks, marks: spec.marks };
}
