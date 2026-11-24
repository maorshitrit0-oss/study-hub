"""The line of lessons waiting for Gemini, worked one at a time (05/11/2026: he opened ~20 lessons at once, they all
ran together, the free daily quota ran out and 90% failed). Runs every half hour from site.yml ("check").

Order: lessons waiting in line (the app queues them when two are already being written) -> lessons that failed only
on the daily quota (after it resets, ~10:00 Israel) -> overloads (after 25 min) -> filling in, so that every lecture
and practice has BOTH a condensed summary and a full chapter. Stops for the day when the quota is used up.
Nothing is deleted: a quiz he already answered is kept (hub.save_chapter), and a failed fill leaves the lesson as it was.

  python queue_runner.py         one pass (time budget)
"""
import json
import re
import os
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import author
import course_site
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


# The Claude fallback is OFF while his CLAUDE_CODE_OAUTH_TOKEN fails (401 since 06/11/2026: every claude-chapter run
# failed and left its lesson "processing" for days). Turn back on after he renews the token (claude setup-token).
CLAUDE_ON = False
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
    if not CLAUDE_ON or os.environ.get("HAS_CLAUDE") != "true":
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
    rows = (sb.table("lessons").select("id, kind, status, error, progress, updated_at, created_at, transcript, chapter_md, summary_md, course_id, source_url")
            .in_("status", ["queued", "error", "ready"]).order("created_at").execute().data)
    active = {c["id"] for c in sb.table("courses").select("id").eq("archived", False).execute().data}
    rows = [r for r in rows if r["course_id"] in active]
    site = __import__("course_site").SITE_NOTE
    waiting = [(r, "full" if "פרק מלא" in (r.get("progress") or "") else "auto") for r in rows
               if r["status"] == "queued" and r["updated_at"] < old]
    quota = [(r, "auto") for r in rows if r["status"] == "error" and "מכסה" in (r.get("error") or "")]
    # a recording Zoom would not let the server download (16/11/2026): tried again once a day with the newest yt-dlp,
    # so it processes by itself the day the tool is fixed
    zoom = [(r, "auto") for r in rows if r["status"] == "error" and ("[zoom]" in (r.get("error") or "") or "זום" in (r.get("error") or "")
            or ("confirm you" in (r.get("error") or "").lower() or "יוטיוב חוסם" in (r.get("error") or "")) and "zoom.us" in (r.get("source_url") or ""))
            and r["updated_at"] < (now - timedelta(hours=24)).isoformat()]
    busy = [(r, "auto") for r in rows if r["status"] == "error" and ("עמוסים" in (r.get("error") or "") or "INTERNAL" in (r.get("error") or ""))
            and r["updated_at"] < (now - timedelta(minutes=10)).isoformat()
            and r["created_at"] > (now - timedelta(days=2)).isoformat()]
    # A lesson that already failed 3 times today waits for tomorrow (no hammering one lesson all day).
    st = state(sb)
    today = datetime.now(ZoneInfo("Asia/Jerusalem")).date().isoformat()
    tries = st.get("tries", {}).get(today, {})
    busy = [x for x in busy if tries.get(x[0]["id"], 0) < 3]
    fill = []
    for r in rows:
        t = r.get("transcript") or ""
        if r["status"] != "ready" or not t or t.startswith(site) or t.startswith(author.VLSI_NOTE):
            continue
        if r["kind"] not in ("lecture", "practice"):  # a study session / Claude's practice: only the cheap summary
            if r.get("chapter_md") and not r.get("summary_md"):
                fill.append((r, "summary"))
            continue
        if r.get("summary_md") and r.get("chapter_md") == r.get("summary_md") and not t.startswith("<!-- written by Claude"):
            fill.append((r, "full"))       # has only the summary -> write the full chapter
        elif r.get("chapter_md") and not r.get("summary_md"):
            fill.append((r, "summary"))    # has only the full chapter -> condensed summary from it (text only)
    # Summaries first among the fills: one cheap call each.
    fill.sort(key=lambda x: x[1] != "summary")
    # His courses first; self-study sessions (written ahead of time) after them - they are not due yet.
    later = lambda x: (x[0].get("transcript") or "").startswith(author.VLSI_NOTE)  # noqa: E731
    return sorted(waiting + quota + busy + zoom[:1], key=later) + fill


ENGINE_SINCE = "2026-11-08T17:20"


def retry_studio(sb):
    """Podcasts / videos that stopped on the daily quota go again once Gemini is back (a few per run)."""
    import course_site
    try:
        rows = (sb.table("lesson_media").select("id, kind, error, course_id, lesson_ids, created_at").eq("status", "error").order("created_at").execute().data)
        ready = sb.table("lesson_media").select("kind, lesson_ids, created_at").eq("status", "ready").execute().data
        names = {c["id"]: c["name"] or "" for c in sb.table("courses").select("id, name").execute().data}
    except Exception:  # noqa: BLE001
        return
    # Only items that stopped on the quota (requested by him or for him); a video waits for the natural Gemini voice.
    rows = [r for r in rows if names.get(r["course_id"]) and r["kind"] == "video"]  # podcasts dropped 22/11/2026
    try:  # one course at a time when he set a focus (23/11/2026)
        import coverage
        f = coverage.load(sb).get("focus")
        if f:
            rows = [r for r in rows if f in names.get(r["course_id"], "")]
    except Exception:  # noqa: BLE001
        pass
    # not when the same lessons already have a ready one of that kind from the current engine (made after it failed, or
    # after ENGINE_SINCE: the subtitled, synced video he approved 08/11/2026) - a duplicate would waste the voice quota
    redo = [r for r in rows if "נוסחאות שנחתכו" in (r.get("error") or "")]  # studio-redo: made again on purpose
    rows = [r for r in rows if r in redo or not any(x["kind"] == r["kind"] and sorted(x.get("lesson_ids") or []) == sorted(r.get("lesson_ids") or [])
                                       and (x["created_at"] > r["created_at"] or x["created_at"] >= ENGINE_SINCE) for x in ready)]
    # a podcast / video left "queued" / "processing" for hours (its run died - Java lectures 1-2 waited from 14/11) goes again
    try:
        stale_at = (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
        stale = [dict(r, error="עמוסים (נתקע)") for r in sb.table("lesson_media").select("id, kind, error, course_id, lesson_ids, created_at")
                 .in_("status", ["queued", "processing"]).lt("created_at", stale_at).order("created_at").execute().data]
    except Exception:  # noqa: BLE001
        stale = []
    # what is missing comes before what is only made again (a lecture with no video > a nicer video of an old one)
    try:  # tomorrow's course first (his request 23/11/2026: everything for the next study day, then the rest)
        import coverage
        day = {cid: coverage.study_day(sb, cid) for cid in {r["course_id"] for r in stale + rows}}
    except Exception:  # noqa: BLE001
        day = {}
    rows = sorted(stale + rows, key=lambda r: (r in redo, day.get(r["course_id"], 99), r["created_at"]))
    try:
        import coverage
        f = coverage.load(sb).get("focus")
        if f:
            rows = [r for r in rows if f in names.get(r["course_id"], "")]
    except Exception:  # noqa: BLE001
        pass
    picks = [r for r in rows if any(w in (r.get("error") or "") for w in ("מכסה", "עמוסים"))]
    # 20/11/2026: he uploads a whole batch of lectures today - the video remakes wait until tomorrow morning, so all of
    # Gemini's quota goes to his lessons
    if datetime.now(timezone.utc) < datetime(2026, 11, 21, 9, 0, tzinfo=timezone.utc):
        picks = [r for r in picks if r not in redo]
    picks = [r for r in picks if r not in redo][:2] or picks[:1]  # remakes: one at a time, after what is missing
    for m in picks:
        sb.table("lesson_media").update({"status": "queued", "error": None}).eq("id", m["id"]).execute()
        print(f"::notice title=Studio again::{m['kind']} {m['id'][:8]}: {course_site.dispatch_inputs('media.yml', {'media_id': m['id']})}", flush=True)


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


def unstick(sb):
    """A lesson left "processing" for hours (its run died: a cancelled / failed Claude run, a killed job) goes back to the
    queue - the queue picks only queued / error / ready, so such a lesson waited forever (his report 09/11/2026)."""
    old = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
    rows = sb.table("lessons").select("id, title").eq("status", "processing").lt("updated_at", old).execute().data
    for r in rows:
        sb.table("lessons").update({"status": "queued", "error": None, "progress": "חזר לתור (העיבוד הקודם נתקע)"}).eq("id", r["id"]).execute()
        print(f"::notice title=Queue::unstuck {r['id'][:8]} {(r.get('title') or '')[:50]}", flush=True)
    # Failures that are not about the lesson itself: the dead Claude fallback, a Gemini timeout on a long YouTube
    # recording. The queue retried only quota / overload errors, so these waited forever too. Again at most twice a day.
    day_ago = (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat()
    for r in sb.table("lessons").select("id, title, error").eq("status", "error").lt("updated_at", day_ago).execute().data:
        if any(w in (r.get("error") or "") for w in ("Claude לא סיים", "DEADLINE_EXCEEDED", "504")):
            sb.table("lessons").update({"status": "queued", "error": None, "progress": "חזר לתור (נכשל קודם)"}).eq("id", r["id"]).execute()
            print(f"::notice title=Queue::retry {r['id'][:8]} {(r.get('title') or '')[:50]}", flush=True)


REC_EXT = (".mp4", ".mov", ".m4v", ".webm", ".mkv", ".m4a", ".mp3", ".wav", ".ogg", ".opus", ".aac")


def adopt_uploads(sb):
    """A recording he uploaded in the app with no lesson yet (his wish 20/11/2026: "I only upload the file - that's it"):
    becomes the next lecture of its course (a practice when the name says so) and is processed. Files younger than 10
    minutes are left to the page, which adds the lesson itself."""
    now = datetime.now(timezone.utc)
    for c in sb.table("courses").select("id, user_id, name").eq("archived", False).execute().data:
        folder = f"{c['user_id']}/sources/{c['id']}"
        try:
            files = sb.storage.from_(hub.BUCKET).list(folder, {"limit": 100})
        except Exception:  # noqa: BLE001
            continue
        les = sb.table("lessons").select("kind, number, source_path").eq("course_id", c["id"]).execute().data
        used = {l.get("source_path") for l in les}
        # 24/11/2026 (his "I did not upload lecture 7"): a file is adopted ONCE ever - a lesson he deleted must not come
        # back - and never when the same recording (same size) is already a lesson.
        st = state(sb)
        seen = set(st.get("adopted") or [])
        sizes = {int((f.get("metadata") or {}).get("size") or 0) for f in files or []
                 if f"{folder}/{f.get('name')}" in used}
        for f in files or []:
            name, path = f.get("name") or "", f"{folder}/{f.get('name')}"
            if not name.lower().endswith(REC_EXT) or path in used or path in seen:
                continue
            if int((f.get("metadata") or {}).get("size") or 0) in sizes:  # a second copy of a recording that is a lesson
                continue
            made = f.get("created_at") or ""
            try:
                age = now - datetime.fromisoformat(made.replace("Z", "+00:00"))
                # only a fresh upload the page did not turn into a lesson (10 min - 6 h old); an older file is never
                # adopted (24/11/2026: a deleted duplicate's file came back as "lecture 6" / "lecture 7" twice)
                if age < timedelta(minutes=10) or age > timedelta(hours=6):
                    continue
            except ValueError:
                continue
            kind = "practice" if re.search(r"תרגול|tirgul|practice|tutorial", name, re.I) else "lecture"
            number = max([l["number"] or 0 for l in les if l["kind"] == kind] or [0]) + 1
            row = sb.table("lessons").insert({"user_id": c["user_id"], "course_id": c["id"], "kind": kind, "number": number,
                                              "source_path": path, "status": "queued", "progress": "הקלטה הועלתה - בתור"}).execute().data[0]
            les.append({"kind": kind, "number": number, "source_path": path})
            st = state(sb)
            st["adopted"] = sorted(set(st.get("adopted") or []) | {path})
            save_state(sb, st)
            print(f"::notice title=Upload adopted::{c['name']} {kind} {number} <- {name}: "
                  f"{course_site.dispatch_inputs('process.yml', {'lesson_id': row['id']})}", flush=True)


def run():
    sb = hub.db()
    unstick(sb)
    try:
        adopt_uploads(sb)
    except Exception as e:  # noqa: BLE001
        print(f"::warning title=Uploads::{str(e)[:200]}", flush=True)
    if quota_blocked(sb) and not author.has_backups():
        # Gemini is out for today: lessons he is waiting for go to Claude (a few a day); fill-ins wait for the reset.
        for r, mode in candidates(sb):
            if r["status"] != "ready" and mode != "summary":
                if not to_claude(sb, r):
                    break
        print("::notice title=Queue::Gemini quota used up earlier today - fill-ins wait for the reset", flush=True)
        return "quota"
    # his priority is by days (23/11/2026): repairs of the course he studies next come before new uploads of others
    try:
        import coverage
        while coverage.pending_for_next_day(sb):
            pass
    except Exception as e:  # noqa: BLE001
        print(f"::warning title=Repairs::{author.friendly_error(e)[:300]}", flush=True)
        if is_quota(e):
            block_quota(sb)
            return "quota"
        if author._is(e, "UNAVAILABLE", "503", "overloaded", "high demand", "עמוסים", "INTERNAL"):
            return "busy"
    # a lecture he is waiting for comes before any video (his remark 20/11/2026: "it happened twice" - the video
    # remakes used up Gemini's daily quota and his new lecture failed on it): no studio work while a lesson waits
    waiting_lesson = any(r["status"] != "ready" for r, _ in candidates(sb))
    if waiting_lesson:
        print("::notice title=Studio::a lesson is waiting - videos wait for it", flush=True)
    else:
        retry_studio(sb)
    try:  # weeks still missing their exercise set (weekset.py)
        import weekset
        weekset.fill_missing(sb)
    except Exception as e:  # noqa: BLE001
        print(f"::warning title=Week sets::{str(e)[:200]}", flush=True)
    start, done, why = time.time(), [], "empty"
    for r, mode in candidates(sb):
        if time.time() - start > BUDGET_SEC:
            why = "budget"
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
            gemini_down = is_quota(e) or author._is(e, "UNAVAILABLE", "503", "overloaded", "high demand", "עמוסים", "INTERNAL")
            if not filling:
                st = state(sb)
                day = datetime.now(ZoneInfo("Asia/Jerusalem")).date().isoformat()
                st["tries"] = {day: {**st.get("tries", {}).get(day, {}), r["id"]: st.get("tries", {}).get(day, {}).get(r["id"], 0) + 1}}
                save_state(sb, st)
            if gemini_down and not filling:
                to_claude(sb, r)
            if is_quota(e):
                block_quota(sb)
                why = "quota"
                break
            if gemini_down:  # overloaded now: don't spend the run retrying the next lessons - wait and try again
                why = "busy"
                break
    # full coverage / completions (coverage.py, 22/11/2026): only when no lesson of his is waiting, one at a time
    if why == "empty" and not waiting_lesson:
        try:
            import coverage
            coverage.thursday_alert(sb)
            while time.time() - start < BUDGET_SEC and coverage.step(sb):
                done.append("coverage")
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Coverage::{author.friendly_error(e)[:300]}", flush=True)
            if is_quota(e):
                block_quota(sb)
                why = "quota"
            elif author._is(e, "UNAVAILABLE", "503", "overloaded", "high demand", "עמוסים", "INTERNAL"):
                why = "busy"
    try:  # old video files left behind by a remake (approved 23/11/2026)
        import mediastore
        if mediastore.enabled() and datetime.now(ZoneInfo("Asia/Jerusalem")).hour == 3:
            mediastore.clean(sb)
    except Exception as e:  # noqa: BLE001
        print(f"::warning title=Media clean::{str(e)[:200]}", flush=True)
    try:
        import coverage
        coverage.ready_alert(sb)
    except Exception as e:  # noqa: BLE001
        print(f"::warning title=Ready alert::{str(e)[:300]}", flush=True)
    print(f"::notice title=Queue::{len(done)} done: {'; '.join(done)[:3000] or '-'}", flush=True)
    return why


def waiting_work(sb):
    """Lessons he is waiting for (not the background fill-ins)."""
    return [r for r, _ in candidates(sb) if r["status"] != "ready"]


def repairs_left(sb):
    """Repairs he asked for (coverage state "pending", 23/11/2026) count as work he waits for: the overnight loop keeps
    going until they are done, so the next morning's course is ready."""
    try:
        import coverage
        coverage._CACHE.pop("st", None)  # fresh read
        return bool(coverage.load(sb).get("pending"))
    except Exception:  # noqa: BLE001
        return False


def loop(hours=5.5):
    """queue.yml: keep working the line inside one job - GitHub's half-hourly schedule fires only every few hours.
    Gemini busy -> wait 10 minutes and try again; quota gone -> sleep until the reset if it is inside this job;
    nothing he waits for left -> stop (fill-ins are done by the half-hourly runs). Out of time with work left ->
    start the next queue.yml."""
    sb = hub.db()
    end = time.time() + hours * 3600
    while time.time() < end:
        why = run()
        if why == "empty" and not waiting_work(sb) and not repairs_left(sb):
            print("::notice title=Queue::nothing left that he is waiting for", flush=True)
            return
        if why == "quota":
            wait = (next_reset() - datetime.now(timezone.utc)).total_seconds()
            if time.time() + wait > end:
                return  # the next schedule / app dispatch continues after the reset
            time.sleep(max(60, wait))
        elif why in ("busy", "empty"):
            time.sleep(10 * 60)
    if waiting_work(sb) or repairs_left(sb):  # 24/11: the schedule skipped hours - the loop starts the next run itself
        import course_site
        print(f"::notice title=Queue::time is up, work left -> next run: {course_site.dispatch('', workflow='queue.yml')}", flush=True)


if __name__ == "__main__":
    import sys
    loop() if "--loop" in sys.argv else run()
