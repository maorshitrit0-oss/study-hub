"""Daily check of the free-plan limits; warns before one runs out and says what to do.

  python usage.py     (run by notify.yml every morning; writes usage_snapshot and pushes alerts)
"""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

import notify

GB = 1024 ** 3
LIMITS = {"storage": 1 * GB, "db": 500 * 1024 ** 2, "actions_min": 2000}
WARN, CRIT = 0.75, 0.9

ADVICE = {
    "storage": ("אחסון הקבצים ב-Supabase",
                "להעביר קבצי PDF גדולים (מצגות, ספרים) ל-Google Drive: למחוק אותם מהאפליקציה ולהוסיף שוב כקישור דרייב. "
                "חומר ההרצאות לא נמחק. אם זה לא מספיק - לפתוח שיחה עם Claude Code להעברת אחסון לדרייב."),
    "db": ("מסד הנתונים ב-Supabase",
           "לפתוח שיחה עם Claude Code להעברת סמסטרים ישנים לארכיון (בלי למחוק)."),
    "actions_min": ("דקות העיבוד ב-GitHub החודש",
                    "להפוך את המאגר ב-GitHub לציבורי (Settings ← General ← Change visibility): הקוד לא מכיל מידע אישי "
                    "וכל הנתונים ב-Supabase, ואז הדקות ללא הגבלה. עד סוף החודש - להעלות רק את ההקלטות החשובות."),
    "gemini": ("המכסה היומית של Gemini",
               "המכסה מתאפסת כל יום בסביבות 10:00 בבוקר (שעון ישראל). אחרי זה ללחוץ 'לנסות שוב' בהרצאות שנכשלו."),
}


def actions_minutes():
    """Minutes used by this repo's workflow runs since the start of the month (GitHub API)."""
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if not repo or not token:
        return None
    start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_ms, page = 0, 1
    while True:
        url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=100&page={page}&created=>={start:%Y-%m-%d}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
        runs = json.load(urllib.request.urlopen(req)).get("workflow_runs", [])
        for r in runs:
            if r.get("run_started_at") and r.get("updated_at"):
                a = datetime.fromisoformat(r["run_started_at"].replace("Z", "+00:00"))
                b = datetime.fromisoformat(r["updated_at"].replace("Z", "+00:00"))
                total_ms += max(0, (b - a).total_seconds() * 1000 + 59_000)  # billed per started minute
        if len(runs) < 100:
            break
        page += 1
    return round(total_ms / 60000)


def main():
    sb = notify.db()
    stats = sb.rpc("usage_stats").execute().data or {}
    used = {"storage": stats.get("storage_bytes", 0), "db": stats.get("db_bytes", 0)}
    try:
        used["actions_min"] = actions_minutes()
    except Exception as e:  # noqa: BLE001
        print(f"actions usage unavailable: {e}")
    since = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    quota_errors = (sb.table("lessons").select("id", count="exact").eq("status", "error").gte("updated_at", since)
                    .or_("error.ilike.%429%,error.ilike.%RESOURCE_EXHAUSTED%,error.ilike.%quota%").execute().count or 0)

    alerts = []
    for key, limit in LIMITS.items():
        if used.get(key) is None:
            continue
        share = used[key] / limit
        if share >= WARN:
            title, fix = ADVICE[key]
            alerts.append({"key": key, "level": "critical" if share >= CRIT else "warning",
                           "text": f"{title}: {round(share * 100)}% מהמכסה החינמית", "fix": fix})
    if quota_errors:
        title, fix = ADVICE["gemini"]
        alerts.append({"key": "gemini", "level": "warning", "text": f"{title} נגמרה ({quota_errors} הרצאות נכשלו)", "fix": fix})

    data = {"used": used, "limits": LIMITS, "alerts": alerts, "checked_at": datetime.now(timezone.utc).isoformat()}
    sb.table("usage_snapshot").upsert({"id": 1, "data": data, "updated_at": data["checked_at"]}).execute()
    print(json.dumps(data, ensure_ascii=False))

    if alerts:
        users = {r["user_id"] for r in sb.table("push_subscriptions").select("user_id").execute().data}
        body = "\n".join(f"{'🔴' if a['level'] == 'critical' else '🟡'} {a['text']}" for a in alerts)
        for uid in users:
            notify.send(sb, uid, "⚠️ מתקרבים למגבלה של שירות חינמי", body + "\nלחץ לפרטים והמלצה", "/settings#usage")


if __name__ == "__main__":
    main()
