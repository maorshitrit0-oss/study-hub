import { parseWave, type Level } from "@/lib/wave";

const TICK = 26, ROW = 34, LEAD = 13, HIGH = 6, LOW = 24;
// Signals start a little before the first edge, so the first rising clock edge is visible too.
const LABEL = 46 + LEAD;
const y = (l: Level) => (l === "1" ? HIGH : LOW);

/** SVG timing diagram from a ```wave block (Q is simulated in lib/wave.ts, never drawn by hand). */
export default function Wave({ src }: { src: string }) {
  let parsed;
  try {
    parsed = parseWave(src);
  } catch {
    return <pre dir="ltr" className="text-xs text-bad">גרף לא תקין:{"\n"}{src}</pre>;
  }
  const { rows, ticks, marks = [] } = parsed;
  const width = LABEL + ticks * TICK + 8;
  const height = rows.length * ROW + 22;
  return (
    <div dir="ltr" className="overflow-x-auto my-3 rounded-xl bg-[#030a16] border border-line p-2">
      <svg width={width} height={height} role="img" aria-label="timing diagram" style={{ fontFamily: "ui-monospace, monospace" }}>
        {/* rising edges: dashed guides and cycle numbers */}
        {Array.from({ length: ticks / 2 }, (_, k) => (
          <g key={k}>
            <line x1={LABEL + 2 * k * TICK} x2={LABEL + 2 * k * TICK} y1={0} y2={rows.length * ROW} stroke="#2b4466" strokeDasharray="3 3" />
            <text x={LABEL + 2 * k * TICK + 2} y={rows.length * ROW + 14} fill="#7f93b3" fontSize="11">↑{k + 1}</text>
          </g>
        ))}
        {marks.map((m, i) => (
          <line key={i} x1={LABEL + m.tick * TICK} x2={LABEL + m.tick * TICK} y1={0} y2={rows.length * ROW} stroke="#f5b84b" strokeWidth="1.5" />
        ))}
        {rows.map((r, i) => {
          const top = i * ROW;
          const color = r.clock ? "#7cc4ff" : r.hidden ? "#7f93b3" : r.name === rows[rows.length - 1].name && !r.clock && rows.length > 2 ? "#6ee7a8" : "#e6e9f2";
          const parts = [];
          const first = r.clock ? "0" : r.levels[0];
          if (!r.hidden && first !== "x") {
            parts.push(<line key="lead" x1={LABEL - LEAD} x2={LABEL} y1={top + y(first)} y2={top + y(first)} stroke={color} strokeWidth="2" />);
            if (r.clock) parts.push(<line key="lead-edge" x1={LABEL} x2={LABEL} y1={top + HIGH} y2={top + LOW} stroke={color} strokeWidth="2" />);
          }
          for (let t = 0; t < ticks; t++) {
            const x0 = LABEL + t * TICK, x1 = x0 + TICK, l = r.levels[t], prev = t ? r.levels[t - 1] : l;
            if (r.hidden) {
              parts.push(<text key={t} x={x0 + TICK / 2 - 3} y={top + 19} fill={color} fontSize="13">?</text>);
              continue;
            }
            if (l === "x") {
              parts.push(<rect key={t} x={x0} y={top + HIGH} width={TICK} height={LOW - HIGH} fill="url(#hatch)" stroke={color} strokeWidth="0.5" />);
              continue;
            }
            if (t && prev !== l && prev !== "x") parts.push(<line key={`e${t}`} x1={x0} x2={x0} y1={top + HIGH} y2={top + LOW} stroke={color} strokeWidth="2" />);
            parts.push(<line key={t} x1={x0} x2={x1} y1={top + y(l)} y2={top + y(l)} stroke={color} strokeWidth="2" />);
          }
          return (
            <g key={r.name}>
              <text x={4} y={top + 20} fill={color} fontSize="13" fontWeight="bold">{r.name}</text>
              {parts}
            </g>
          );
        })}
        <defs>
          <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="6" stroke="#7f93b3" strokeWidth="1" />
          </pattern>
        </defs>
      </svg>
      {marks.length > 0 && <p className="text-xs text-warn mt-1" dir="rtl">{marks.map((m) => m.label).join(" · ")}</p>}
    </div>
  );
}
