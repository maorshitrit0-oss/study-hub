"""Push notifications to the user's phone (Web Push, sent from GitHub Actions).

  python notify.py setup            create the VAPID signing keys if they don't exist yet
  python notify.py daily            morning digest: deadlines today/tomorrow, exams this week, unread chapters
  python notify.py evening          after classes: which of today's lectures/practices still need their recording
  python notify.py test <user_id>   send a test notification

Also imported by hub.py to announce a finished lesson. Never raises: a failed
notification must not fail the job that sent it.
"""
import base64
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from supabase import create_client

TZ = ZoneInfo("Asia/Jerusalem")
CONTACT = "mailto:study-hub@users.noreply.github.com"


def db():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def ensure_keys(sb):
    rows = sb.table("push_config").select("public_key, private_key").eq("id", 1).execute().data
    if rows:
        return rows[0]
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    key = ec.generate_private_key(ec.SECP256R1())
    b64 = lambda raw: base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
    row = {
        "id": 1,
        "private_key": b64(key.private_numbers().private_value.to_bytes(32, "big")),
        "public_key": b64(key.public_key().public_bytes(serialization.Encoding.X962,
                                                        serialization.PublicFormat.UncompressedPoint)),
    }
    sb.table("push_config").insert(row).execute()
    print("created VAPID keys")
    return row


def send(sb, user_id, title, body, url="/"):
    """Send to every device the user enabled; drop subscriptions the browser revoked."""
    try:
        from pywebpush import WebPushException, webpush

        keys = ensure_keys(sb)
        subs = sb.table("push_subscriptions").select("*").eq("user_id", user_id).execute().data
        payload = json.dumps({"title": title, "body": body, "url": url}, ensure_ascii=False)
        for s in subs:
            try:
                webpush({"endpoint": s["endpoint"], "keys": {"p256dh": s["p256dh"], "auth": s["auth"]}},
                        payload, vapid_private_key=keys["private_key"], vapid_claims={"sub": CONTACT}, ttl=12 * 3600)
            except WebPushException as e:
                if e.response is not None and e.response.status_code in (404, 410):
                    sb.table("push_subscriptions").delete().eq("id", s["id"]).execute()
                else:
                    print(f"push failed: {e}")
        return len(subs)
    except Exception as e:  # noqa: BLE001 - notifications are best-effort
        print(f"notify error: {e}")
        return 0


def local(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(TZ)


KIND = {"assignment": "מטלה", "exam": "מבחן", "quiz": "בוחן", "lab_report": "דוח", "other": ""}


def daily():
    sb = db()
    ensure_keys(sb)
    users = {r["user_id"] for r in sb.table("push_subscriptions").select("user_id").execute().data}
    now = datetime.now(TZ)
    today, tomorrow = now.date(), now.date() + timedelta(days=1)
    horizon = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

    for uid in users:
        courses = {c["id"]: c["name"] for c in sb.table("courses").select("id, name").eq("user_id", uid).execute().data}
        deadlines = (sb.table("deadlines").select("title, kind, due_at, course_id").eq("user_id", uid)
                     .eq("done", False).gte("due_at", datetime.now(timezone.utc).isoformat())
                     .lte("due_at", horizon).order("due_at").execute().data)
        unread = (sb.table("lessons").select("id", count="exact").eq("user_id", uid)
                  .eq("status", "ready").is_("read_at", "null").execute().count or 0)

        lines = []
        for d in deadlines:
            when = local(d["due_at"])
            name = f"{KIND.get(d['kind'], '')} {d['title']}".strip()
            course = f" ({courses[d['course_id']]})" if d.get("course_id") in courses else ""
            if when.date() == today:
                lines.append(f"⏰ היום {when:%H:%M}: {name}{course}")
            elif when.date() == tomorrow:
                lines.append(f"📌 מחר: {name}{course}")
            elif d["kind"] in ("exam", "quiz"):
                lines.append(f"📚 {when:%d/%m}: {name}{course}")
        if unread:
            lines.append(f"📖 {unread} פרקים מחכים לקריאה")
        if not lines:
            continue
        title = "בוקר טוב! מה על הפרק היום" if any("היום" in l or "מחר" in l for l in lines) else "בוקר טוב"
        n = send(sb, uid, title, "\n".join(lines[:6]), "/")
        print(f"{uid}: {len(lines)} items -> {n} devices")


SLOT_KIND = {"lecture": "הרצאה", "practice": "תרגול"}


def evening():
    """Remind to upload today's recordings that weren't added or marked yet."""
    sb = db()
    users = {r["user_id"] for r in sb.table("push_subscriptions").select("user_id").execute().data}
    now = datetime.now(TZ)
    today = now.date().isoformat()
    weekday = (now.weekday() + 1) % 7  # Python Monday=0 -> Sunday=0
    start_of_day = datetime.combine(now.date(), datetime.min.time(), TZ).astimezone(timezone.utc).isoformat()
    for uid in users:
        slots = (sb.table("schedule_slots").select("id, course_id, kind, title, end_time").eq("user_id", uid)
                 .eq("weekday", weekday).in_("kind", ["lecture", "practice"]).execute().data)
        if not slots:
            continue
        marked = {m["slot_id"] for m in sb.table("recording_marks").select("slot_id").eq("user_id", uid)
                  .eq("class_date", today).execute().data}
        added = {(l["course_id"], l["kind"]) for l in sb.table("lessons").select("course_id, kind").eq("user_id", uid)
                 .gte("created_at", start_of_day).execute().data}
        courses = {c["id"]: c["name"] for c in sb.table("courses").select("id, name").eq("user_id", uid).execute().data}
        todo = [f"{SLOT_KIND[s['kind']]} · {courses.get(s['course_id'], s['title'])}" for s in slots
                if s["id"] not in marked and (s["course_id"], s["kind"]) not in added and s["end_time"][:5] <= now.strftime("%H:%M")]
        if todo:
            n = send(sb, uid, "📹 להעלות הקלטות מהיום", "\n".join(todo) + "\nכשההקלטה עולה לזום - מדביקים את הקישור באפליקציה.", "/")
            print(f"{uid}: {len(todo)} recordings -> {n} devices")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "daily"
    if cmd == "setup":
        ensure_keys(db())
    elif cmd == "evening":
        evening()
    elif cmd == "test":
        print("devices:", send(db(), sys.argv[2], "Study Hub 🎉", "ההתראות עובדות! מעכשיו תקבל כאן תזכורות על משימות ופרקים חדשים.", "/"))
    else:
        daily()
