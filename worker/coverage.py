"""Full coverage of every lecture / practice (his rule 22/11/2026: "don't hold back material - I am examined on all of
it"; the old chapters were 3-10% of the recording, with 3-4 of ~90 snapshots).

The recording is read in parts of ~40 minutes; for each part Gemini gets the transcript and the DISTINCT board
snapshots of that part (near-identical snapshots dropped by image difference) and writes:
  - a lesson he has NOT read yet whose chapter is thin / cut -> the whole chapter again, part by part (old kept in storage);
  - a lesson he HAS read -> only what is missing from the chapter he read, placed as "🔁 השלמות מהשבועות הקודמים" at
    the top of the next lesson of that course he has not read yet (his choice: the read chapter is not touched).
Each part also brings understanding questions (no calculations) for the lesson quiz.
Order: the course he studies next by the timetable first (hub.next_class), and within a course lesson by lesson.
Called from queue_runner.run() only when no new lesson is waiting; one lesson per call; on quota/overload it stops and
the next run continues. Thursday evening: a push if a lesson he needs by Friday is still not ready.
"""
import io
import json
import re
from datetime import datetime

import author
import hub

BUCKET = "study"
STATE = "system/coverage.json"           # {"done": {lesson_id: "rewrite"|"completion"|"skip"}, "alert": day}
PART_SEC = 40 * 60
THIN = 0.15                              # chapter shorter than 15% of the transcript = thin
HEAD = "## 🔁 השלמות מהשבועות הקודמים"
BACKUP = "chapter_before_coverage.md"
TS = re.compile(r"^\[(\d\d):(\d\d):(\d\d)\]", re.M)
SNAP = re.compile(r"===== שקף (\d+)")

RULES = """כללים מחייבים:
- עברית; מונח טכני בפעם הראשונה גם באנגלית בסוגריים. נוסחאות ב-LaTeX: $...$ בשורה, $$...$$ בשורה נפרדת. קוד - בבלוק קוד.
- כל מה שנלמד בחלק הזה, לפי הסדר: כל הגדרה, כל פיתוח צעד אחרי צעד, כל דוגמה ותרגיל פתור עם המספרים, כל הערה של המרצה
  ("חשוב למבחן", "שימו לב", טעויות נפוצות) כ-> ⭐. אסור לקצר ואסור לדלג; עדיף ארוך ומלא.
- כותרות ## לנושאים ו-### לתתי-נושאים. אין הקדמות ואין סיכום כללי.
- צילומי לוח/שקפים: כל צילום מצורף שיש בו מלל, נוסחה, קוד, טבלה או שרטוט נכנס לפרק במקום שבו הוא מוסבר, בתחביר
  ![תיאור קצר](slide:N). מיד לפניו שורה **📝 מה כתוב בלוח:** ומתחתיה רק מה שבאמת רואים בצילום הזה (לא מהתמלול, לא
  משקף אחר), מסודר: טבלה / רשימה / LaTeX / קוד. מה שלא קריא - [לא קריא]. צילום בלי תוכן (רק פנים / מסך ריק) - לא להכניס.
  לוח רחב וצפוף שאי אפשר להעתיק מילה במילה - **📝 עיקרי הלוח (בתמצית):** במקום.
- אל תמציא תוכן שלא נלמד. טעות של המרצה - שורה > ⚠️ עם התיקון.
- questions: 2-4 שאלות אמריקאיות של הבנה (לא חישוב) על החלק הזה, 4 תשובות, correct = אינדקס התשובה הנכונה."""

FULL = """אתה כותב פרק קריאה מלא לסטודנט להנדסת חשמל שלא צפה בשיעור ולומד רק מהפרק. הוא ייבחן על כל מה שנלמד.
זה חלק {k} מתוך {n} של השיעור "{title}" (קורס: {course}). הכותרות שכבר נכתבו בחלקים הקודמים: {prev}
כתוב את החלק הזה בלבד, כהמשך ישיר.
""" + RULES

MISSING = """לפניך פרק שסטודנט להנדסת חשמל כבר קרא (בתחילת ההודעה), ואחריו חלק {k} מתוך {n} מהתמלול של אותו שיעור
"{title}" (קורס: {course}) עם צילומי הלוח שלו. הפרק קיצר מאוד, והסטודנט ייבחן על כל מה שנלמד.
כתוב רק את מה שנלמד בחלק הזה וחסר בפרק, או מופיע בו רק ברמז: הגדרות, פיתוחים, דוגמאות, תרגילים פתורים, לוחות,
הערות למבחן. מה שכבר מוסבר בפרק במלואו - אל תחזור עליו. אם לא חסר כלום - md ריק.
""" + RULES

SCHEMA = {"type": "object", "properties": {
    "md": {"type": "string"},
    "questions": {"type": "array", "items": {"type": "object", "properties": {
        "question": {"type": "string"}, "options": {"type": "array", "items": {"type": "string"}},
        "correct": {"type": "integer"}, "explanation": {"type": "string"}, "topic": {"type": "string"}},
        "required": ["question", "options", "correct", "explanation"]}}},
    "required": ["md"]}


_CACHE = {}


def load(sb):
    """The state, read once per process: storage downloads can be served stale (22/11/2026 the first run read an old
    copy between steps and wrote lecture 3's completions twice)."""
    if "st" not in _CACHE:
        try:
            _CACHE["st"] = json.loads(sb.storage.from_(BUCKET).download(STATE).decode())
        except Exception:  # noqa: BLE001
            _CACHE["st"] = {"done": {}}
    return _CACHE["st"]


def save(sb, st):
    _CACHE["st"] = st
    sb.storage.from_(BUCKET).upload(STATE, json.dumps(st).encode(), {"content-type": "application/json", "upsert": "true"})


INTRO = "> 📌 חומר מהשיעורים שכבר קראת, שהיה חסר בפרקים שלהם. לקרוא לפני השיעור הזה."
SEC = re.compile(r"^### מתוך (.+?): מה שלא היה בפרק שקראת$", re.M)


def dedupe(md):
    """Keeps the first completions section per source lesson in the block at the top."""
    top, rest = split_head(md)
    if not top:
        return md
    pieces = re.split(r"(?=^### מתוך .+?: מה שלא היה בפרק שקראת$)", top, flags=re.M)
    seen, keep = set(), []
    for p in pieces:
        m = SEC.match(p)
        if m:
            if m.group(1) in seen:
                continue
            seen.add(m.group(1))
        keep.append(p)
    out = "".join(keep)
    if out.count(INTRO) > 1:  # each insertion used to add the note again (his screenshot 22/11/2026)
        first = out.index(INTRO) + len(INTRO)
        out = out[:first] + re.sub(r"\n*" + re.escape(INTRO) + r"\n*", "\n\n", out[first:])
    if not out.rstrip().endswith("<!-- /השלמות -->"):
        out = out.rstrip() + "\n<!-- /השלמות -->"
    return out + "\n\n" + rest


def dedupe_all(sb):
    for l in sb.table("lessons").select("id, chapter_md").like("chapter_md", HEAD + "%").execute().data:
        new = dedupe(l["chapter_md"])
        if new != l["chapter_md"]:
            sb.table("lessons").update({"chapter_md": new}).eq("id", l["id"]).execute()
            print(f"::notice title=Coverage::{l['id'][:8]}: duplicate completions removed ({len(l['chapter_md'])} -> {len(new)})", flush=True)


def body_of(md):
    return (md or "").split("\n---\n### ✅ בדיקת עובדות")[0]


def parts(tr):
    """The transcript in ~40-minute parts (by its [hh:mm:ss] marks)."""
    cuts, nxt = [0], PART_SEC
    for m in TS.finditer(tr):
        sec = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
        if sec >= nxt:
            cuts.append(m.start())
            nxt = sec + PART_SEC
    cuts.append(len(tr))
    return [tr[a:b] for a, b in zip(cuts, cuts[1:]) if tr[a:b].strip()]


def snapshots(sb, lesson, text, prev=None):
    """The distinct snapshots of this part: [(n, bytes)], near-identical consecutive ones dropped."""
    from PIL import Image, ImageChops, ImageStat
    store, out = sb.storage.from_(BUCKET), []
    for n in dict.fromkeys(int(x) for x in SNAP.findall(text)):
        try:
            data = store.download(f"{lesson['user_id']}/lessons/{lesson['id']}/slide_{n:03d}.webp")
            im = Image.open(io.BytesIO(data)).convert("L").resize((160, 90))
        except Exception:  # noqa: BLE001
            continue
        if prev is None or ImageStat.Stat(ImageChops.difference(im, prev)).mean[0] > 6:
            out.append((n, data))
            prev = im
    return out[:30], prev


def ask(prompt, chapter, text, snaps):
    from google.genai import types
    p = []
    if chapter is not None:
        p.append(types.Part.from_text(text="=== הפרק שהסטודנט קרא ===\n" + chapter[:60000]))
    p.append(types.Part.from_text(text="=== התמלול של החלק הזה ===\n" + text))
    for n, data in snaps:
        p += [types.Part.from_text(text=f"צילום slide:{n}"), types.Part.from_bytes(data=data, mime_type="image/webp")]
    out = author._generate_json(p, prompt, SCHEMA, "MEDIUM")
    md = (out.get("md") or "").strip()
    qs = [q for q in out.get("questions") or [] if len(q.get("options") or []) >= 2 and 0 <= q.get("correct", -1) < len(q["options"])]
    return md, qs


def write(sb, lesson, course, chapter=None):
    """All parts of one lesson -> (markdown, questions). chapter=None: full chapter; else only what is missing."""
    tr = lesson["transcript"]
    ps, md, qs, heads, prev = parts(tr), [], [], [], None
    for k, text in enumerate(ps, 1):
        snaps, prev = snapshots(sb, lesson, text, prev)
        fmt = dict(k=k, n=len(ps), title=lesson.get("title") or "", course=course["name"], prev="; ".join(heads[-12:]) or "-")
        part, q = ask((MISSING if chapter is not None else FULL).format(**fmt), chapter, text, snaps)
        if part:
            md.append(part)
            heads += re.findall(r"^## (.+)$", part, re.M)
        qs += q
        print(f"::notice title=Coverage::{(lesson.get('title') or '')[:40]} part {k}/{len(ps)}: {len(part)} chars, "
              f"{len(snaps)} boards", flush=True)
    return "\n\n".join(md), qs


def add_questions(sb, lesson, course, qs):
    if qs:
        sb.table("questions").insert([{
            "user_id": lesson["user_id"], "course_id": course["id"], "lesson_id": lesson["id"], "topic": q.get("topic"),
            "question": q["question"], "options": q["options"], "correct": q["correct"],
            "explanation": q.get("explanation"), "difficulty": 2} for q in qs]).execute()


def split_head(md):
    """(the completions block at the top, the rest)."""
    if md.startswith(HEAD):
        i = md.find("\n<!-- /השלמות -->")
        if i > 0:
            j = i + len("\n<!-- /השלמות -->")
            return md[:j], md[j:].lstrip()
    return "", md


def thin(l):
    tr, ch = l.get("transcript") or "", body_of(split_head(l.get("chapter_md") or "")[1])
    return len(tr) > 10000 and (len(ch) < THIN * len(tr) or author.is_cut(ch))


def eligible(l):
    tr = l.get("transcript") or ""
    return (l["status"] == "ready" and l["kind"] in ("lecture", "practice") and not (l.get("title") or "").startswith("📦")
            and not tr.startswith(("<!-- course-site -->", author.VLSI_NOTE, "<!-- written by Claude")))


def order_key(l):
    return (l.get("number") or 0, l["kind"] != "lecture", l["created_at"])


def study_day(sb, course_id):
    """Days until the course's next class INCLUDING today (he studies today's course today: waves on Sunday 22/11)."""
    from datetime import timedelta
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("Asia/Jerusalem"))
    days = {s["weekday"] for s in sb.table("schedule_slots").select("weekday").eq("course_id", course_id).execute().data}
    for k in range(0, 8):
        if ((now + timedelta(days=k)).weekday() + 1) % 7 in days:
            return k
    return 99


def todo(sb, st):
    """(lesson, course, target) in the order he needs them; target None = rewrite the lesson itself."""
    courses = {c["id"]: c for c in sb.table("courses").select("id, name").eq("archived", False).execute().data}
    rows = (sb.table("lessons").select("id, user_id, course_id, kind, number, title, status, transcript, chapter_md, "
                                       "read_at, created_at").in_("course_id", list(courses)).execute().data)
    by = {}
    for l in rows:
        if eligible(l):
            by.setdefault(l["course_id"], []).append(l)
    out = []
    for cid in sorted(by, key=lambda c: study_day(sb, c)):
        ls = sorted(by[cid], key=order_key)
        # completions go to the first unread lesson AFTER the furthest week he has read (waves: read up to lecture 4,
        # in the middle of practice 4 -> they open lecture 5, as he asked)
        top_read = max([x.get("number") or 0 for x in ls if x.get("read_at")] or [0])
        nxt = next((x for x in ls if not x.get("read_at") and (x.get("number") or 0) > top_read), None)
        for l in ls:
            if st["done"].get(l["id"]) or not thin(l):
                continue
            if not l.get("read_at"):
                out.append((l, courses[cid], None))
            else:
                if nxt:  # nothing unread after it yet: waits for his next upload
                    out.append((l, courses[cid], nxt))
    return out


def step(sb):
    """One lesson. Returns True if something was done (raises on Gemini quota / overload - the caller stops)."""
    st = load(sb)
    st.setdefault("done", {})
    jobs = todo(sb, st)
    if not jobs:
        return False
    l, course, target = jobs[0]
    store = sb.storage.from_(BUCKET)
    if target is None:
        top, _ = split_head(l.get("chapter_md") or "")
        md, qs = write(sb, l, course)
        if len(md) < 0.6 * THIN * len(l["transcript"]):
            print(f"::warning title=Coverage::{l['title'][:40]}: rewrite came out short ({len(md)}) - kept the old chapter", flush=True)
            st["done"][l["id"]] = "short"
        else:
            store.upload(f"{l['user_id']}/lessons/{l['id']}/{BACKUP}", (l.get("chapter_md") or "").encode(),
                         {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
            new = (top + "\n\n" if top else "") + md
            upd = {"chapter_md": new}
            try:
                upd["summary_md"] = author.summary_from_chapter(new)
            except Exception:  # noqa: BLE001 - the summary is a nice-to-have
                pass
            sb.table("lessons").update(upd).eq("id", l["id"]).execute()
            add_questions(sb, l, course, qs)
            st["done"][l["id"]] = "rewrite"
            print(f"::notice title=Coverage::{course['name']} {l['kind']} {l['number']}: rewritten in full ({len(md)} chars)", flush=True)
    else:
        md, qs = write(sb, l, course, chapter=body_of(l.get("chapter_md") or ""))
        t = sb.table("lessons").select("id, user_id, chapter_md").eq("id", target["id"]).execute().data[0]
        top, rest = split_head(t.get("chapter_md") or "")
        name = f"{'הרצאה' if l['kind'] == 'lecture' else 'תרגול'} {l.get('number') or ''}"
        if md and f"### מתוך {name}: מה שלא היה בפרק שקראת" in top:
            md = ""  # already there (a second run of the same lesson)
        if md:
            sec = f"### מתוך {name}: מה שלא היה בפרק שקראת\n\n{md}"
            inner = top[len(HEAD):-len("\n<!-- /השלמות -->")].replace(INTRO, "").strip() if top else ""
            top = f"{HEAD}\n\n> 📌 חומר מהשיעורים שכבר קראת, שהיה חסר בפרקים שלהם. לקרוא לפני השיעור הזה.\n\n" \
                  f"{(inner + chr(10) * 2) if inner else ''}{sec}\n<!-- /השלמות -->"
            sb.table("lessons").update({"chapter_md": top + "\n\n" + rest}).eq("id", t["id"]).execute()
            add_questions(sb, t, course, qs)
        st["done"][l["id"]] = "completion"
        print(f"::notice title=Coverage::{course['name']} {name} -> completions in {target.get('title', '')[:30]} ({len(md)} chars)", flush=True)
    save(sb, st)
    return True


def thursday_alert(sb):
    """Thursday evening: anything he needs by Friday that is not ready -> one push."""
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("Asia/Jerusalem"))
    if now.weekday() != 3 or now.hour < 18:
        return
    st = load(sb)
    day = now.date().isoformat()
    if st.get("alert") == day:
        return
    waiting = sb.table("lessons").select("user_id, title, status").in_("status", ["queued", "processing", "error", "transcribed"]).execute().data
    left = len(todo(sb, {"done": st.get("done", {})}))
    if waiting or left:
        import notify
        body = (f"{len(waiting)} שיעורים עוד לא מוכנים" if waiting else "") + (f"; {left} השלמות עוד בתור" if left else "")
        uid = (waiting[0]["user_id"] if waiting else sb.table("lessons").select("user_id").limit(1).execute().data[0]["user_id"])
        notify.send(sb, uid, "⚠️ לא הכל מוכן לשישי", body.strip("; "))
    st["alert"] = day
    save(sb, st)


if __name__ == "__main__":
    import sys
    s = hub.db()
    if "--dedupe" in sys.argv:
        dedupe_all(s)
    elif "--list" in sys.argv:
        for l, c, t in todo(s, load(s)):
            print(c["name"][:20], l["kind"], l["number"], "read" if l.get("read_at") else "unread", "->", (t or {}).get("title", "rewrite")[:30])
    else:
        step(s)
