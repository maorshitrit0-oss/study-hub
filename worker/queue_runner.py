"""The line of lessons waiting for Gemini, worked one at a time (05/11/2026: he opened ~20 lessons at once, they all
ran together, the free daily quota ran out and 90% failed). Runs every half hour from site.yml ("check").

Order: lessons waiting in line (the app queues them when two are already being written) -> lessons that failed only
on the daily quota (after it resets, ~10:00 Israel) -> overloads (after 25 min) -> filling in, so that every lecture
and practice has BOTH a condensed summary and a full chapter. Stops for the day when the quota is used up.
Nothing is deleted: a quiz he already answered is kept (hub.save_chapter), and a failed fill leaves the lesson as it was.

  python queue_runner.py         one pass (time budget)
"""
import json
import os
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import author
import hub

BUCKET = "study"
STATE = "system/queue_state.json"   # {"quota_until": iso, "claude": {day: count}}
BUDGET_SEC = 100 * 60
WAITING = "⏳ בתור"


def is_quota(e):
    return author._is(e, "RESOURCE_EXHAUSTED", "429", "quota", "המכסה")


def next_reset():
    """10:30 Israel time today, or tomorrow if that has passed - the free quota resets around 10:00."""
    now = datetime.now(ZoneInfo("Asia/Jerusalem"))
    reset = now.replace(hour=10, minute=30, second=0, microsecond=0)
    return (reset if now < reset else reset + timedelta(days=1)).astimezone(timezone.utc)


def quota_blocked(sb):
    try:
        until = json.loads(sb.storage.from_(BUCKET).download(STATE).decode()).get("quota_until")
        return bool(until) and datetime.now(timezone.utc) < datetime.fromisoformat(until)
    except Exception:  # noqa: BLE001 - no state yet
        return False


def block_quota(sb):
    st = state(sb)
    st["quota_until"] = next_reset().isoformat()
    save_state(sb, st)
    print(f"::notice title=Queue::daily Gemini quota used up - waiting until {next_reset().isoformat()}", flush=True)


CLAUDE_PER_DAY = 4   # chapters a day Claude may write instead of Gemini (his Pro usage is shared with his chats)


def state(sb):
    try:
        return json.loads(sb.storage.from_(BUCKET).download(STATE).decode())
    except Exception:  # noqa: BLE001
        return {}


def save_state(sb, st):
    sb.storage.from_(BUCKET).upload(STATE, json.dumps(st).encode(), {"content-type": "application/json", "upsert": "true"})


def to_claude(sb, r):
    """When Gemini can't (overloaded / quota): his Claude Pro writes the chapter (claude-chapter.yml), a few a day.
    The recording is transcribed first if needed (no Gemini in that). Returns True if handed over."""
    if os.environ.get("HAS_CLAUDE") != "true":
        return False
    st = state(sb)
    today = datetime.now(ZoneInfo("Asia/Jerusalem")).date().isoformat()
    used = st.get("claude", {}).get(today, 0)
    if used >= CLAUDE_PER_DAY:
        return False
    row = sb.table("lessons").select("transcript").eq("id", r["id"]).single().execute().data
    if not (row.get("transcript") or "").strip():
        hub.cmd_process(r["id"], do_author=False)
    import course_site
    res = course_site.dispatch(r["id"], workflow="claude-chapter.yml")
    if res != "started":
        print(f"::warning title=Queue::Claude not started for {r['id']}: {res}", flush=True)
        return False
    sb.table("lessons").update({"status": "processing", "error": None,
                                "progress": "Gemini לא זמין - Claude כותב את הפרק"}).eq("id", r["id"]).execute()
    st.setdefault("claude", {})[today] = used + 1
    save_state(sb, st)
    print(f"::notice title=Queue::{r['id']} -> Claude ({used + 1}/{CLAUDE_PER_DAY} today)", flush=True)
    return True


def candidates(sb):
    now = datetime.now(timezone.utc)
    old = (now - timedelta(minutes=10)).isoformat()
    rows = (sb.table("lessons").select("id, kind, status, error, progress, updated_at, created_at, transcript, chapter_md, summary_md, course_id")
            .in_("status", ["queued", "error", "ready"]).order("created_at").execute().data)
    active = {c["id"] for c in sb.table("courses").select("id").eq("archived", False).execute().data}
    rows = [r for r in rows if r["course_id"] in active]
    site = __import__("course_site").SITE_NOTE
    waiting = [(r, "full" if "פרק מלא" in (r.get("progress") or "") else "auto") for r in rows
               if r["status"] == "queued" and r["updated_at"] < old]
    quota = [(r, "auto") for r in rows if r["status"] == "error" and "מכסה" in (r.get("error") or "")]
    busy = [(r, "auto") for r in rows if r["status"] == "error" and "עמוסים" in (r.get("error") or "")
            and r["updated_at"] < (now - timedelta(minutes=25)).isoformat()
            and r["created_at"] > (now - timedelta(days=2)).isoformat()]
    fill = []
    for r in rows:
        t = r.get("transcript") or ""
        if r["status"] != "ready" or r["kind"] not in ("lecture", "practice") or not t or t.startswith(site) \
                or t.startswith(author.VLSI_NOTE):
            continue
        if r.get("summary_md") and r.get("chapter_md") == r.get("summary_md"):
            fill.append((r, "full"))       # has only the summary -> write the full chapter
        elif r.get("chapter_md") and not r.get("summary_md"):
            fill.append((r, "summary"))    # has only the full chapter -> condensed summary from it (text only)
    # Summaries first among the fills: one cheap call each.
    fill.sort(key=lambda x: x[1] != "summary")
    return waiting + quota + busy + fill


def write_summary(sb, r):
    md = author.summary_from_chapter(r["chapter_md"])
    if len(md) > 200:
        sb.table("lessons").update({"summary_md": md}).eq("id", r["id"]).execute()


def write_full(r):
    """Full chapter for a lesson that has only the summary; on failure the lesson stays as it was (ready)."""
    os.environ["AUTHOR_MODE"], os.environ["QUIET"] = "full", "1"
    try:
        hub.cmd_process(r["id"])
    finally:
        os.environ["AUTHOR_MODE"] = "auto"
        os.environ.pop("QUIET", None)


def run():
    sb = hub.db()
    if quota_blocked(sb):
        # Gemini is out for today: lessons he is waiting for go to Claude (a few a day); fill-ins wait for the reset.
        for r, mode in candidates(sb):
            if r["status"] != "ready" and mode != "summary":
                if not to_claude(sb, r):
                    break
        print("::notice title=Queue::Gemini quota used up earlier today - fill-ins wait for the reset", flush=True)
        return
    start, done = time.time(), []
    for r, mode in candidates(sb):
        if time.time() - start > BUDGET_SEC:
            break
        filling = r["status"] == "ready"
        try:
            if mode == "summary":
                write_summary(sb, r)
            elif filling:
                write_full(r)
            else:
                os.environ["AUTHOR_MODE"] = mode
                try:
                    hub.cmd_process(r["id"])
                finally:
                    os.environ["AUTHOR_MODE"] = "auto"
            done.append(f"{r['kind']} {r['id'][:8]} {mode}")
        except Exception as e:  # noqa: BLE001
            if filling:  # a fill that failed: the lesson keeps what it had
                sb.table("lessons").update({"status": "ready", "error": None, "progress": None}).eq("id", r["id"]).execute()
            gemini_down = is_quota(e) or author._is(e, "UNAVAILABLE", "503", "overloaded", "high demand", "עמוסים")
            if gemini_down and not filling:
                to_claude(sb, r)
            if is_quota(e):
                block_quota(sb)
                break
            if gemini_down:  # overloaded now: don't spend the run retrying the next lessons - again in half an hour
                break
    print(f"::notice title=Queue::{len(done)} done: {'; '.join(done)[:3000] or '-'}", flush=True)


if __name__ == "__main__":
    run()
