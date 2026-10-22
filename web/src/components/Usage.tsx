type Snapshot = {
  used: { storage?: number; db?: number; actions_min?: number | null };
  limits: { storage: number; db: number; actions_min: number };
  alerts: { key: string; level: "warning" | "critical"; text: string; fix: string }[];
  checked_at: string;
};

const ROWS = [
  { key: "storage", label: "קבצים (Supabase)", fmt: (b: number) => `${(b / 1048576).toFixed(0)}MB` },
  { key: "db", label: "נתונים (Supabase)", fmt: (b: number) => `${(b / 1048576).toFixed(0)}MB` },
  { key: "actions_min", label: "דקות עיבוד החודש (GitHub)", fmt: (m: number) => `${m}` },
] as const;

/** Free-plan usage bars with the recommended fix for anything close to its limit. */
export function UsagePanel({ snap }: { snap: Snapshot | null }) {
  if (!snap) return <p className="text-sm text-muted">הבדיקה הראשונה תרוץ מחר בבוקר.</p>;
  return (
    <div className="space-y-3">
      {ROWS.map((r) => {
        const used = snap.used[r.key];
        if (used == null) return null;
        const share = Math.min(1, used / snap.limits[r.key]);
        return (
          <div key={r.key}>
            <div className="flex justify-between text-sm">
              <span>{r.label}</span>
              <span className="text-muted">{r.fmt(used)} / {r.fmt(snap.limits[r.key])}</span>
            </div>
            <div className="mt-1 h-1.5 rounded-full bg-bg overflow-hidden">
              <div className={`h-full ${share >= 0.9 ? "bg-bad" : share >= 0.75 ? "bg-warn" : "bg-good"}`} style={{ width: `${share * 100}%` }} />
            </div>
          </div>
        );
      })}
      <UsageAlerts snap={snap} />
      <p className="text-xs text-muted">נבדק כל בוקר. התראה תגיע לטלפון כשמשהו מגיע ל-75%.</p>
    </div>
  );
}

export function UsageAlerts({ snap }: { snap: Snapshot | null }) {
  if (!snap?.alerts?.length) return null;
  return (
    <div className="space-y-2">
      {snap.alerts.map((a) => (
        <div key={a.key} className={`rounded-xl p-3 text-sm ${a.level === "critical" ? "bg-bad-soft" : "bg-warn-soft"}`}>
          <p className="font-semibold">{a.level === "critical" ? "🔴" : "🟡"} {a.text}</p>
          <p className="mt-1"><b>מה לעשות:</b> {a.fix}</p>
        </div>
      ))}
    </div>
  );
}

export type { Snapshot };
