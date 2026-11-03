/** A graph for a practical-exam question, computed from its parameters (worker/practical.py): a frequency response
 * (1st order low/high-pass, 2nd order band-pass/stop) on a log axis, or signals in time. */
export type GraphSpec = {
  kind: string; title?: string; fc?: number; f0?: number; q?: number; gain_db?: number; duration_ms?: number;
  signals?: { shape?: string; amp?: number; freq?: number; offset?: number; phase_deg?: number; label?: string }[];
};

const W = 320, H = 190, L = 44, B = 28, T = 10, R = 8;
const COLORS = ["#38bdf8", "#f5b94a", "#4ade80", "#f472b6"];
const fmtHz = (f: number) => (f >= 1e6 ? `${+(f / 1e6).toPrecision(3)}M` : f >= 1e3 ? `${+(f / 1e3).toPrecision(3)}k` : `${+f.toPrecision(3)}`);

function response(g: GraphSpec, f: number) {
  const k = 10 ** ((g.gain_db ?? 0) / 20);
  const fc = g.fc || g.f0 || 1000, f0 = g.f0 || g.fc || 1000, q = g.q || 1;
  const x = f / fc, y = f / f0;
  switch (g.kind) {
    case "highpass": return k * x / Math.sqrt(1 + x * x);
    case "bandpass": return k / Math.sqrt(1 + q * q * (y - 1 / y) ** 2);
    case "bandstop": return k * Math.abs(1 - y * y) / Math.sqrt((1 - y * y) ** 2 + (y / q) ** 2);
    default: return k / Math.sqrt(1 + x * x); // lowpass
  }
}

function wave(s: NonNullable<GraphSpec["signals"]>[number], t: number) {
  const ph = 2 * Math.PI * (s.freq ?? 1000) * t + ((s.phase_deg ?? 0) * Math.PI) / 180;
  const a = s.amp ?? 1, o = s.offset ?? 0;
  if (s.shape === "square") return o + a * Math.sign(Math.sin(ph));
  if (s.shape === "triangle") return o + (2 * a / Math.PI) * Math.asin(Math.sin(ph));
  return o + a * Math.sin(ph);
}

export default function LabGraph({ g }: { g: GraphSpec }) {
  const time = g.kind === "time";
  let paths: { d: string; label?: string }[] = [];
  let xTicks: { x: number; label: string }[] = [], yTicks: { y: number; label: string }[] = [];
  const px = (u: number) => L + u * (W - L - R), py = (v: number) => T + (1 - v) * (H - T - B);

  if (time) {
    const sig = g.signals?.length ? g.signals : [{ shape: "sine", amp: 1, freq: 1000 }];
    const dur = (g.duration_ms ?? 3000 / (Math.min(...sig.map((s) => s.freq ?? 1000)))) / 1000;
    const vals = sig.map((s) => Array.from({ length: 301 }, (_, i) => wave(s, (i / 300) * dur)));
    const max = Math.max(1e-9, ...vals.flat().map(Math.abs)) * 1.1;
    paths = vals.map((v, k) => ({ d: v.map((y, i) => `${i ? "L" : "M"}${px(i / 300).toFixed(1)},${py(0.5 + y / (2 * max)).toFixed(1)}`).join(""), label: sig[k].label }));
    xTicks = [0, 0.25, 0.5, 0.75, 1].map((u) => ({ x: px(u), label: `${+(u * dur * 1000).toPrecision(2)}ms` }));
    yTicks = [-1, 0, 1].map((u) => ({ y: py(0.5 + u * 0.5 / 1.1), label: `${+(u * max / 1.1).toPrecision(2)}V` }));
  } else {
    const center = g.fc || g.f0 || 1000;
    const lo = Math.log10(center) - 2, hi = Math.log10(center) + 2;
    const pts = Array.from({ length: 201 }, (_, i) => {
      const f = 10 ** (lo + ((hi - lo) * i) / 200);
      return 20 * Math.log10(Math.max(1e-6, response(g, f)));
    });
    const top = Math.ceil(Math.max(...pts) / 10) * 10 + 5, bottom = Math.max(top - 65, Math.floor(Math.min(...pts) / 10) * 10);
    const yv = (db: number) => (Math.min(top, Math.max(bottom, db)) - bottom) / (top - bottom);
    paths = [{ d: pts.map((db, i) => `${i ? "L" : "M"}${px(i / 200).toFixed(1)},${py(yv(db)).toFixed(1)}`).join("") }];
    xTicks = Array.from({ length: 5 }, (_, k) => ({ x: px(k / 4), label: `${fmtHz(10 ** (lo + k))}Hz` }));
    yTicks = Array.from({ length: Math.floor((top - bottom) / 20) + 1 }, (_, k) => top - 5 - k * 20)
      .filter((v) => v >= bottom).map((v) => ({ y: py(yv(v)), label: `${v}dB` }));
  }

  return (
    <figure className="my-2" dir="ltr">
      {g.title && <figcaption className="text-xs text-muted text-center mb-1" dir="auto">{g.title}</figcaption>}
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-md mx-auto rounded-lg bg-black/30 border border-line">
        {yTicks.map((t) => <g key={t.label}><line x1={L} x2={W - R} y1={t.y} y2={t.y} stroke="currentColor" opacity="0.12" />
          <text x={L - 4} y={t.y + 3} fontSize="8" textAnchor="end" fill="currentColor" opacity="0.7">{t.label}</text></g>)}
        {xTicks.map((t) => <g key={t.label}><line x1={t.x} x2={t.x} y1={T} y2={H - B} stroke="currentColor" opacity="0.12" />
          <text x={t.x} y={H - B + 11} fontSize="8" textAnchor="middle" fill="currentColor" opacity="0.7">{t.label}</text></g>)}
        {paths.map((p, k) => <path key={k} d={p.d} fill="none" stroke={COLORS[k % COLORS.length]} strokeWidth="1.6" />)}
        {time && paths.map((p, k) => p.label && <text key={`l${k}`} x={L + 4} y={T + 9 + k * 10} fontSize="8" fill={COLORS[k % COLORS.length]}>{p.label}</text>)}
      </svg>
    </figure>
  );
}
