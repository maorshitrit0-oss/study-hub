import { notifySlot } from "@/lib/notifySchedule";

export const dynamic = "force-dynamic";

/**
 * Called by Supabase pg_cron at 05/06/17/18 UTC (covers summer and winter time). Starts the notification
 * workflow only when it is one of his notification times in Israel, and at most once per slot - so the
 * endpoint can be public without a secret: calling it can't send anything extra.
 */
export async function GET() {
  const slot = notifySlot(new Date());
  if (!slot) return Response.json({ sent: false, reason: "not a notification time" });
  const repo = process.env.GITHUB_REPO, token = process.env.GITHUB_TOKEN;
  if (!repo || !token) return Response.json({ sent: false, reason: "GITHUB_REPO / GITHUB_TOKEN missing" }, { status: 500 });
  const gh = (path: string, init?: RequestInit) => fetch(`https://api.github.com/repos/${repo}/actions/workflows/notify.yml${path}`, {
    ...init,
    headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" },
  });
  // Already started in the last 45 minutes (an earlier call of this slot)? Then do nothing.
  const since = new Date(Date.now() - 45 * 60_000).toISOString();
  const runs = await gh(`/runs?event=workflow_dispatch&created=${encodeURIComponent(">=" + since)}&per_page=5`);
  if (runs.ok && ((await runs.json()) as { total_count: number }).total_count > 0) {
    return Response.json({ sent: false, reason: "already sent for this slot" });
  }
  const res = await gh("/dispatches", { method: "POST", body: JSON.stringify({ ref: "main", inputs: { mode: slot } }) });
  // Mornings also continue rewriting old chapters into his structure (stops on quota, resumes the next day).
  if (slot === "daily") {
    await fetch(`https://api.github.com/repos/${repo}/actions/workflows/enrich.yml/dispatches`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" },
      body: JSON.stringify({ ref: "main", inputs: { lesson_id: "" } }),
    }).catch(() => null);
  }
  return Response.json({ sent: res.ok, slot, status: res.status }, { status: res.ok ? 200 : 502 });
}
