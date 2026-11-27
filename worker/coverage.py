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
from pathlib import Path

import author
import hub

BUCKET = "study"
STATE = "system/coverage.json"           # {"done": {lesson_id: "rewrite"|"completion"|"skip"}, "alert": day}
PART_SEC = 40 * 60
THIN = 0.30                              # chapter shorter than 15% of the transcript = thin
HEAD = "## 🔁 השלמות מהשבועות הקודמים"
BACKUP = "chapter_before_coverage.md"
TS = re.compile(r"^\[(\d\d):(\d\d):(\d\d)\]", re.M)
SNAP = re.compile(r"===== שקף (\d+)")

RULES = """כללים מחייבים:
- עברית; מונח טכני בפעם הראשונה גם באנגלית בסוגריים. נוסחאות ב-LaTeX: $...$ בשורה, $$...$$ בשורה נפרדת. קוד - בבלוק קוד.
- כל מה שנלמד בחלק הזה, לפי הסדר: כל הגדרה, כל פיתוח צעד אחרי צעד, כל דוגמה ותרגיל פתור עם המספרים, כל הערה של המרצה
  ("חשוב למבחן", "שימו לב", טעויות נפוצות) כ-> ⭐. אסור לקצר ואסור לדלג; עדיף ארוך ומלא.
- כותרות ## לנושאים ו-### לתתי-נושאים. אין הקדמות ואין סיכום כללי.
- צילום שמראה שקופית מוקרנת עם טקסט: הבלוק שלפניו מעתיק גם את הטקסט של השקופית (כותרות והפסקאות, במלואן), ולא רק את
  מה שכתוב ביד על הלוח לידה. לא לתאר דבר שלא רואים בצילום (למשל צורה של גרף שנחתך) - מה שלא רואים: [לא נראה בצילום].
- צילומי לוח/שקפים: כל צילום מצורף שיש בו מלל, נוסחה, קוד, טבלה או שרטוט נכנס לפרק במקום שבו הוא מוסבר, בתחביר
  ![תיאור קצר](slide:N). מיד לפניו שורה **📝 מה כתוב בלוח:** ומתחתיה רק מה שבאמת רואים בצילום הזה (לא מהתמלול, לא
  משקף אחר), מסודר: טבלה / רשימה / LaTeX / קוד. מה שלא קריא - [לא קריא]. צילום בלי תוכן (רק פנים / מסך ריק) - לא להכניס.
  לוח רחב וצפוף שאי אפשר להעתיק מילה במילה - **📝 עיקרי הלוח (בתמצית):** במקום.
- אסור להשמיט שום פרט, גם אם נראה שולי: מספרים, יחידות, הנחות ותנאים, כל שלב בפתרון, כל תרגיל (גם תרגיל שניתן
  לבית או "לנסות לבד" - עם הנתונים המלאים), כל החלטה או הודעה של המרצה (מבחן, שיעורי בית, מה חשוב, מה לא ייבחן).
- מה שלא ברור בהקלטה - לכתוב שהוא לא ברור ([לא ברור בהקלטה]), לא לדלג עליו ולא לנחש.
- אחרי ההסבר של כל נושא: שורה **🏠 בחיי היום-יום:** עם דוגמה מוחשית למה הדבר הזה עושה או איפה פוגשים אותו.
- בלי שאלות של סטודנטים ובלי שיחות צד - רק החומר עצמו (אם תשובת המרצה לשאלה הוסיפה חומר - החומר נכנס).
- התמלול אוטומטי: מילה ששובשה (מונח, שם, יחידה) - כתוב אותה נכון לפי ההקשר.
- תמונות: רק צילומים שמוסיפים לחומר; לא שני צילומים של אותו דבר.
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


def name_match(key, full):
    """A course name given by part ("גלים", "Java") matches only at the start of a word of the full name - 27/11/2026:
    "גלים" (waves) matched inside "מעגלים" (linear / digital circuits), so the waves jobs worked on another course."""
    key, full = (key or "").strip(), (full or "")
    return bool(key) and bool(re.search(r"(?:^|[\s(\-–,·])" + re.escape(key), full, re.I))


def same_course(a, b):
    """Two course names (either may be a part of the other) name the same course."""
    return name_match(a, b) or name_match(b, a)


def load(sb):
    """The state, read once per process: storage downloads can be served stale (22/11/2026 the first run read an old
    copy between steps and wrote lecture 3's completions twice)."""
    if "st" not in _CACHE:
        try:
            _CACHE["st"] = json.loads(sb.storage.from_(BUCKET).download(STATE).decode())
        except Exception:  # noqa: BLE001
            _CACHE["st"] = {"done": {}}
    return _CACHE["st"]


_REMOVED = set()  # ids of repair jobs this process finished (so a full save does not bring them back)


def new_job(job):
    """A repair job added by a writer outside the queue: gets an id, so the queue's next save keeps it (25/11/2026: the
    queue reads the state once per run and its full save dropped jobs added meanwhile by a lesson's run)."""
    import uuid
    return {**job, "_id": uuid.uuid4().hex[:12]}


def drop_job(st, j):
    st["pending"].remove(j)
    if j.get("_id"):
        _REMOVED.add(j["_id"])


def save(sb, st, keys=None):
    """keys: a writer outside the queue (a lesson being processed) updates only these keys on a fresh copy, so it never
    overwrites the queue's list of repairs (23-24/11/2026 the night's list was lost that way)."""
    try:
        fresh = json.loads(sb.storage.from_(BUCKET).download(STATE).decode())
    except Exception:  # noqa: BLE001
        fresh = {}
    if not keys or "pending" in keys:  # repair jobs added meanwhile by another run are kept
        have = {j.get("_id") for j in st.get("pending") or []}
        for j in fresh.get("pending") or []:
            if j.get("_id") and j["_id"] not in have and j["_id"] not in _REMOVED:
                st.setdefault("pending", []).append(j)
    if keys:
        for k in keys:
            fresh[k] = {**(fresh.get(k) or {}), **(st.get(k) or {})} if isinstance(st.get(k), dict) else st.get(k)
        st = fresh
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
    qs = [q for q in qs or [] if (q.get("question") or "").strip() and len(q.get("options") or []) >= 2
          and isinstance(q.get("correct"), int) and 0 <= q["correct"] < len(q["options"])]
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


AUDIT_HEAD = "## 🧩 פרטים שהבדיקה מול ההקלטה הוסיפה"
VERIFY_SPLIT = "\n---\n### ✅ בדיקת עובדות"


PLACE = """לפניך רשימת הכותרות של פרק קריאה, ואחריה קטע חומר שחסר בפרק. חלק את הקטע לפי נושאים, ולכל חלק בחר את הכותרת
מהרשימה שהחלק שייך לסוף הנושא שלה (העתק אותה בדיוק כמו ברשימה). חלק שאין לו נושא מתאים - heading ריק.
אל תשנה את הטקסט של הקטע: העתק אותו כמו שהוא (כולל ![..](slide:N), נוסחאות ו-📝)."""
PLACE_SCHEMA = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "heading": {"type": "string"}, "md": {"type": "string"}}, "required": ["heading", "md"]}}}, "required": ["items"]}


def integrate(md, items):
    """Each missing piece goes to the END of its own topic (before the next heading of the same or a higher level),
    not to a separate section at the end of the chapter (his rule 24/11/2026). Pieces with no topic go before the
    fact-check, without any special title."""
    body, _, ver = md.partition(VERIFY_SPLIT)
    rest = []
    for it in items:
        h, add = (it.get("heading") or "").strip().lstrip("#").strip(), (it.get("md") or "").strip()
        if not add:
            continue
        m = re.search(r"(?m)^(#{2,4}) " + re.escape(h) + r"\s*$", body) if h else None
        if not m:
            rest.append(add)
            continue
        level = len(m.group(1))
        nxt = re.compile(r"(?m)^#{2,%d} " % level).search(body, m.end())
        at = nxt.start() if nxt else len(body)
        body = body[:at].rstrip() + "\n\n" + add + "\n\n" + body[at:]
    if rest:
        body = body.rstrip() + "\n\n" + "\n\n".join(rest)
    return author.normalize_math(body) + (VERIFY_SPLIT + ver if ver else "")


def audit(sb, lesson, course, chapter_md):
    """His rule 23-24/11/2026: no detail of a lecture / practice may be missing. Every part of the recording is compared
    with the finished chapter (the MISSING prompt) and whatever is missing is written INTO the chapter, each piece at
    the end of its own topic. Returns (chapter, questions)."""
    from google.genai import types
    md, qs = write(sb, lesson, course, chapter=body_of(chapter_md))
    if len(md.strip()) < 200:
        return chapter_md, []  # nothing missing: no extra questions either
    heads = "\n".join(re.findall(r"(?m)^#{2,4} (.+)$", body_of(chapter_md)))
    try:
        out = author._generate_json([types.Part.from_text(text="=== הכותרות ===\n" + heads),
                                     types.Part.from_text(text="=== הקטע החסר ===\n" + md)], PLACE, PLACE_SCHEMA, "LOW")
        items = out.get("items") or []
        if sum(len(i.get("md") or "") for i in items) < 0.8 * len(md):  # the placing lost text: keep it whole
            items = [{"heading": "", "md": md}]
    except Exception:  # noqa: BLE001
        items = [{"heading": "", "md": md}]
    return integrate(chapter_md, items), qs


def unfold_audit(md):
    """An old chapter with the separate "🧩" section: (chapter without it, the section's text)."""
    body, _, ver = md.partition(VERIFY_SPLIT)
    i = body.find(AUDIT_HEAD)
    if i < 0:
        return md, ""
    sec = re.sub(r"^> 📌[^\n]*\n+", "", body[i + len(AUDIT_HEAD):].strip())
    return body[:i].rstrip() + (VERIFY_SPLIT + ver if ver else ""), sec


def place_old_audits(sb, name):
    """Chapters that still have the "🧩" section: its pieces go into their topics (once per lesson)."""
    from google.genai import types
    c = [x for x in sb.table("courses").select("id, name").execute().data if name_match(name, x["name"])][0]
    for l in sb.table("lessons").select("id, user_id, title, kind, number, chapter_md").eq("course_id", c["id"]).execute().data:
        md = l.get("chapter_md") or ""
        if AUDIT_HEAD not in md:
            continue
        base, sec = unfold_audit(md)
        while AUDIT_HEAD in base:  # a second "🧩" section (two audit rounds): its text joins the first
            base, more = unfold_audit(base)
            sec += "\n\n" + more
        sec = sec.replace(AUDIT_HEAD, "")
        heads = "\n".join(re.findall(r"(?m)^#{2,4} (.+)$", body_of(base)))
        # 27/11: piece by piece (one call for a long section lost text and the section stayed at the end)
        pieces = [p for p in re.split(r"(?m)^(?=#{2,3} )", sec) if p.strip()]
        items, lost = [], False
        for piece in pieces:
            got = []
            for _ in range(2):
                try:
                    got = author._generate_json([types.Part.from_text(text="=== הכותרות ===\n" + heads),
                                                 types.Part.from_text(text="=== הקטע החסר ===\n" + piece)],
                                                PLACE, PLACE_SCHEMA, "LOW").get("items") or []
                except Exception as e:  # noqa: BLE001
                    if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota"):
                        raise
                    got = []
                if sum(len(i.get("md") or "") for i in got) >= 0.8 * len(piece.strip()):
                    break
            else:
                lost = True
                got = [{"heading": "", "md": piece}]
            items += got
        if lost:
            print(f"::notice title=Place::{(l.get('title') or '')[:30]}: a piece had no clear topic - put before the check", flush=True)
        new = integrate(base, items)
        sb.storage.from_(BUCKET).upload(f"{l['user_id']}/lessons/{l['id']}/chapter_before_place.md", md.encode(),
                                        {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
        sb.table("lessons").update({"chapter_md": new}).eq("id", l["id"]).execute()
        print(f"::notice title=Place::{l['kind']} {l.get('number')} {(l.get('title') or '')[:25]}: {len(items)} pieces placed in their topics", flush=True)


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
    for k in range(1 if now.hour >= 18 else 0, 8):  # evening: today's class is over, tomorrow's course first
        if ((now + timedelta(days=k)).weekday() + 1) % 7 in days:
            return k
    return 99


SKIP_COURSES = re.compile(r"מעבדה")  # his request 23/11/2026: lab 2 gets nothing (no completions, quizzes, videos, alerts)


def focused(st, courses):
    """He decides the order (23/11/2026: "מעגלים ספרתיים ... אני אאשר לך" the next one): with st["focus"] set, only
    that course is worked on - text, quizzes and videos - until he approves the next."""
    courses = {k: c for k, c in courses.items() if not SKIP_COURSES.search(c["name"] or "")}
    f = None if _CACHE.get("nofocus") else st.get("focus")  # the queue found nothing to do with the focus (25/11)
    return {k: c for k, c in courses.items() if any(name_match(x, c["name"]) for x in f.split("|"))} if f else courses


# His rule 25/11/2026: completions were a ONE-TIME catch-up for what he had already read. They are all finished on
# Wed 25/11; from then on no new completion is ever made - a new upload gets the normal flow (transcript, full chapter,
# self-check against the recording, boards, video, quiz, exercises) and the rest of the course is only checked.
COMPLETIONS_UNTIL = "2026-11-26T00:00:00+02:00"


def completions_over():
    from datetime import timezone
    return datetime.now(timezone.utc) >= datetime.fromisoformat(COMPLETIONS_UNTIL)


def todo(sb, st):
    """(lesson, course, target) in the order he needs them; target None = rewrite the lesson itself."""
    courses = focused(st, {c["id"]: c for c in sb.table("courses").select("id, name").eq("archived", False).execute().data})
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
            # v2 (23/11/2026): threshold 15% -> 30% (full chapters are 40-60%), and the two halves of one lecture no
            # longer share a completion title (one of them was dropped). Every thin lesson is checked once more.
            if not st.setdefault("v2", {}).get(l["id"]) and thin(l):
                if not l.get("read_at"):
                    out.append((l, courses[cid], None))
                elif nxt and not completions_over():  # nothing unread after it yet: waits for his next upload
                    out.append((l, courses[cid], nxt))
            elif not l.get("read_at") and not st.setdefault("audited", {}).get(l["id"]) and len(l.get("transcript") or "") > 10000:
                out.append((l, courses[cid], "audit"))  # every unread lesson: compared with its recording (23/11/2026)
    return out


def step(sb):
    """One lesson. Returns True if something was done (raises on Gemini quota / overload - the caller stops)."""
    st = load(sb)
    st.setdefault("done", {})
    explode_all(sb)
    fix_slides(sb)
    plan_focus(sb)
    # repairs he asked for that wait for Gemini (23/11/2026): run by the queue - the focus course's only
    jobs = [j for j in st.get("pending") or [] if _mine(st, j)]
    if jobs:
        for j in jobs:
            finished, what = run_job(sb, st, j)
            if what is None:
                continue
            if finished or not any(k in j for k in ("boards", "fix", "place", "rewrite", "weeks", "verify", "mathfix", "convert")):
                drop_job(st, j)
            save(sb, st)
            return True
    if MERGE_APPROVED:
        merge_units(sb)
    if drill(sb, st):
        return True
    jobs = todo(sb, st)
    if not jobs:
        return False
    l, course, target = jobs[0]
    store = sb.storage.from_(BUCKET)
    if target == "audit":
        new, qs = audit(sb, l, course, l.get("chapter_md") or "")
        if new != (l.get("chapter_md") or ""):
            store.upload(f"{l['user_id']}/lessons/{l['id']}/chapter_before_audit.md", (l.get("chapter_md") or "").encode(),
                         {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
            sb.table("lessons").update({"chapter_md": new}).eq("id", l["id"]).execute()
            video_now(sb, l)
        st.setdefault("audited", {})[l["id"]] = len(new) - len(l.get("chapter_md") or "")
        print(f"::notice title=Audit::{course['name'][:20]} {l['kind']} {l.get('number')} {(l.get('title') or '')[:20]}: "
              f"+{len(new) - len(l.get('chapter_md') or '')} chars", flush=True)
        save(sb, st)
        return True
    if target is None:
        top, _ = split_head(l.get("chapter_md") or "")
        md, qs = write(sb, l, course)
        st.setdefault("v2", {})[l["id"]] = "rewrite"
        old = len(body_of(split_head(l.get("chapter_md") or "")[1]))
        # never trade a chapter for a shorter one (23/11/2026: comm practice 4, 17k -> 8k); a longer one always wins
        if len(md) <= old or (len(md) < 0.6 * THIN * len(l["transcript"]) and len(md) < 1.3 * old):
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
            video_now(sb, l)
            st["done"][l["id"]] = "rewrite"
            print(f"::notice title=Coverage::{course['name']} {l['kind']} {l['number']}: rewritten in full ({len(md)} chars)", flush=True)
    else:
        base = f"{'הרצאה' if l['kind'] == 'lecture' else 'תרגול'} {l.get('number') or ''}"
        part = re.search(r"חלק [א-ת]", l.get("title") or "")
        name = base + (f" {part.group()}" if part else "")
        # what earlier completions of this lecture already gave him counts as read: only what is still missing
        have = [u["chapter_md"] or "" for u in sb.table("lessons").select("title, chapter_md").eq("course_id", l["course_id"])
                .eq("kind", "other").like("title", f"🔁 השלמה ל{base}%").execute().data]
        md, qs = write(sb, l, course, chapter="\n\n".join([body_of(l.get("chapter_md") or "")] + have))
        st.setdefault("v2", {})[l["id"]] = "completion"
        t = sb.table("lessons").select("id, user_id, number, title").eq("id", target["id"]).execute().data[0]
        if md:
            make_units(sb, t, course, name, md, src=l)  # one completion lesson per lecture (23/11/2026)
        st["done"][l["id"]] = "completion"
        print(f"::notice title=Coverage::{course['name']} {name} -> completions in {target.get('title', '')[:30]} ({len(md)} chars)", flush=True)
    save(sb, st)
    return True


# --- completions as separate short lessons, each with its own quiz and exercises (his request 22/11/2026: "כל השלמה
# משלה עם שאלון אמריקאי משלה ותרגילים משלה, לא הכל ביחד") ---
UNIT = "🔁 השלמה ל{name}"
SPLIT_AT = 9000          # a longer completion is cut into parts (at ## / ### headings)
HEB = "אבגדהוזחט"
DRILLS = Path(__file__).resolve().parent.parent / "chapters" / "drills"   # quizzes written by hand (Claude)


def chunks(md):
    """Parts of up to ~SPLIT_AT chars, cut only before a ## heading (a solved exercise stays with its solution)."""
    secs = re.split(r"(?m)^(?=## )", md.strip())
    out, cur = [], ""
    for s in secs:
        if cur and len(cur) + len(s) > SPLIT_AT and len(cur) > SPLIT_AT / 3:
            out.append(cur.strip())
            cur = ""
        cur += s
    if cur.strip():
        out.append(cur.strip())
    return out


def make_units(sb, target, course, name, md, src=None):
    """ONE completion lesson per lecture / practice (his request 23/11/2026: "השלמה להרצאה 2 - הכל במכה אחת"), placed
    right before `target`. More missing material for the same lecture is appended to it (its quiz/exercises follow
    via drill_more, its video is made again). src = the lesson the material came from (its boards are copied)."""
    base = re.sub(r"^תרגול", "הרצאה", re.sub(r" חלק [א-ת]$", "", name.strip()))  # practice N -> the week's completion
    title = UNIT.format(name=base)
    tname = f"{target.get('title') or ''}".strip() or "השיעור הבא"
    ex = (sb.table("lessons").select("id, user_id, course_id, title, chapter_md, slide_count")
          .eq("course_id", course["id"]).eq("title", title).execute().data)
    if ex:
        keep = ex[0]
        add = hub.carry_slides(sb, src, keep, md) if src else md
        sb.table("lessons").update({"chapter_md": (keep["chapter_md"] or "").rstrip() + "\n\n" + add, "read_at": None}) \
            .eq("id", keep["id"]).execute()
        st = load(sb)
        st.setdefault("drill_more", {})[keep["id"]] = add
        save(sb, st)
        print(f"::notice title=Coverage::{course['name'][:20]}: {title} += {len(add)} chars", flush=True)
        return
    note = f"> 📌 כל מה שהיה חסר בפרקים של {base} (שכבר קראת). לקרוא לפני {tname}. בסוף: שאלון ותרגילים.\n\n"
    row = sb.table("lessons").insert({"user_id": target["user_id"], "course_id": course["id"], "kind": "other",
                                      "number": max((target.get("number") or 1) - 1, 0), "title": title, "status": "ready",
                                      "author": "gemini", "chapter_md": note + md, "slide_count": 0}).execute().data[0]
    if src:
        new = hub.carry_slides(sb, src, row, row["chapter_md"])
        sb.table("lessons").update({"chapter_md": new}).eq("id", row["id"]).execute()
    print(f"::notice title=Coverage::{course['name'][:20]}: {title} ({len(md)} chars)", flush=True)


def unit_base(title):
    """Lecture N and practice N are one week -> one completion (his rule 23/11/2026)."""
    m = UNIT_SRC.match(title or "")
    return f"הרצאה {m.group(2)}" if m else None


def redo_video(sb, l):
    """The lesson changed: its old / waiting video goes, a new one is queued (made again from the whole lesson)."""
    sb.table("lesson_media").delete().contains("lesson_ids", [l["id"]]).neq("status", "ready").execute()
    if not sb.table("lesson_media").select("id").contains("lesson_ids", [l["id"]]).execute().data:
        queue_video(sb, l)


MERGE_APPROVED = True  # he approved 23/11/2026 ("יש לך אישור... תעשה מה שאתה רוצה עם זה")


def video_now(sb, l):
    """His order (23/11/2026): each lesson's video is made right after its text, lesson by lesson - not in a batch at
    the end. Practices (and their completions) get no video. An older video of the lesson is replaced."""
    title = l.get("title") or ""
    if l.get("kind") in ("practice", "lab") or title.startswith("🔁 השלמה לתרגול"):
        return
    f = None if (_CACHE.get("nofocus") or _CACHE.get("nofocus_video")) else load(sb).get("focus")  # "A|B" = several courses
    if f and not any(name_match(x, c["name"]) for x in f.split("|")
                     for c in sb.table("courses").select("name").eq("id", l["course_id"]).execute().data):
        return  # videos only for the course he is on now (comm videos stopped at his request 23/11/2026)
    sb.table("lesson_media").delete().contains("lesson_ids", [l["id"]]).execute()
    row = sb.table("lesson_media").insert({"user_id": l["user_id"], "course_id": l["course_id"], "kind": "video",
                                           "lesson_ids": [l["id"]]}).execute().data[0]
    print(f"::notice title=Video::{title[:40] or l['id'][:8]}: {hub.course_site.dispatch_inputs('media.yml', {'media_id': row['id']})}", flush=True)


def merge_units(sb):
    """Several completion lessons of one lecture (parts, or a second check) -> ONE, kept in their order: text with
    its boards, quiz questions and exercises move over; the emptied rows are removed."""
    rows = (sb.table("lessons").select("id, user_id, course_id, title, chapter_md, slide_count, created_at")
            .eq("kind", "other").like("title", "🔁 השלמה%").order("created_at").execute().data)
    groups = {}
    for u in rows:
        if unit_base(u["title"]):
            groups.setdefault((u["course_id"], unit_base(u["title"])), []).append(u)
    st = load(sb)
    for (cid, base), us in groups.items():
        if len(us) < 2:
            continue
        us.sort(key=lambda u: (not u["title"].startswith("🔁 השלמה להרצאה"), u["created_at"]))  # the lecture's first
        keep, md = us[0], re.sub(r"^> 📌[^\n]*\n+", "", us[0]["chapter_md"] or "")
        for u in us[1:]:
            part = re.sub(r"^> 📌[^\n]*\n+", "", hub.carry_slides(sb, u, keep, u["chapter_md"] or ""))
            md = md.rstrip() + "\n\n" + part
            for tb in ("questions", "exercises"):
                sb.table(tb).update({"lesson_id": keep["id"]}).eq("lesson_id", u["id"]).execute()
            sb.table("lesson_media").delete().contains("lesson_ids", [u["id"]]).execute()
            sb.table("lessons").delete().eq("id", u["id"]).execute()
            st.get("drill", {}).pop(u["id"], None)
        note = f"> 📌 כל מה שהיה חסר בפרקים של {base} ושל התרגול שלה (שכבר קראת). בסוף: שאלון ותרגילים.\n\n"
        sb.table("lessons").update({"chapter_md": note + md, "title": UNIT.format(name=base), "read_at": None}) \
            .eq("id", keep["id"]).execute()
        st.setdefault("drill", {})[keep["id"]] = st.get("drill", {}).get(keep["id"]) or "merged"
        video_now(sb, dict(keep, kind="other"))
        print(f"::notice title=Coverage::merged {len(us)} completion lessons of {base} -> one", flush=True)
    save(sb, st)


SECTION = re.compile(r"(?m)^### מתוך (.+?): מה שלא היה בפרק שקראת\s*$")


def explode(sb, lesson, course):
    """A completions block on top of a chapter (the old layout) -> separate lessons; the chapter keeps only its own."""
    top, rest = split_head(lesson.get("chapter_md") or "")
    if not top:
        return False
    sb.storage.from_(BUCKET).upload(f"{lesson['user_id']}/lessons/{lesson['id']}/chapter_before_split.md",
                                    lesson["chapter_md"].encode(), {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
    inner = top[len(HEAD):-len("\n<!-- /השלמות -->")].replace(INTRO, "")
    bits = SECTION.split(inner)
    for name, md in zip(bits[1::2], bits[2::2]):
        if md.strip():
            make_units(sb, lesson, course, name.strip(), md)
    sb.table("lessons").update({"chapter_md": rest}).eq("id", lesson["id"]).execute()
    return True


def explode_all(sb):
    courses = {c["id"]: c for c in sb.table("courses").select("id, name").execute().data}
    for l in sb.table("lessons").select("id, user_id, course_id, number, title, chapter_md").like("chapter_md", HEAD + "%").execute().data:
        if l["course_id"] in courses and explode(sb, l, courses[l["course_id"]]):
            print(f"::notice title=Coverage::{courses[l['course_id']]['name'][:20]} {l.get('title') or ''}: completions moved to separate lessons", flush=True)


DRILL = """לפניך פרק (השלמה) שסטודנט להנדסת חשמל לומד לקראת מבחן. כתוב עליו בלבד, בעברית, נוסחאות ב-LaTeX ($...$ בשורה,
$$...$$ בשורה נפרדת):
- questions: 5-6 שאלות אמריקאיות של הבנה בלבד (מילוליות, הגיון, "מה קורה אם", "למה") שמכסות את כל הנושאים בפרק,
  4 תשובות, correct = אינדקס הנכונה, explanation קצר שמסביר למה. בלי שאלות חישוב; אם בכל זאת צריך מספר - הנוסחה
  כתובה בשאלה עצמה.
- exercises: 2-3 תרגילים לתרגול בסגנון המבחן של הקורס ({exam}), שונים מהדוגמאות הפתורות בפרק (מספרים אחרים), עם
  פתרון מלא צעד אחרי צעד, שמתחיל בשורה "**הנוסחה:**" עם הנוסחה (בלוק $$, בלי הצבה). {exam_rule}
אל תמציא חומר שלא בפרק. פתור כל שאלה ותרגיל מחדש לפני שאתה כותב את התשובה."""

EXAM = {"mcq": "אמריקאי", "open": "שאלות פתוחות", "mixed": "משולב: אמריקאי ופתוח"}
DRILL_MCQ = """המבחן אמריקאי - התרגיל הוא שאלה אמריקאית ברמת מבחן שנפתרת בלחיצה: בסוף question_md
  4 אפשרויות, כל אחת בפסקה משלה בדיוק כך: **א.** ... / **ב.** ... / **ג.** ... / **ד.** ...; ה-solution_md מתחיל בשורה
  "התשובה: **X**" (X = האות הנכונה) ואחריה הפתרון המלא צעד אחרי צעד ולמה כל אחת מהאחרות שגויה."""
DRILL_OPEN = """המבחן פתוח - התרגיל הוא שאלה פתוחה ברמת מבחן (אפשר עם סעיפים א, ב, ג), **בלי אפשרויות בחירה** ובלי "התשובה: X"."""


def solved(sb, course_id):
    """Exercises he marked done in this course (his rule: every new exercise is checked against them)."""
    rows = sb.table("exercises").select("question_md").eq("course_id", course_id).not_.is_("done_at", "null").execute().data
    return "\n\n---\n".join(x["question_md"] for x in rows)[:60000]


def drill_parts(sb, l, text):
    from google.genai import types
    done = solved(sb, l["course_id"])
    p = [types.Part.from_text(text=body_of(text))]
    if done:
        p.append(types.Part.from_text(text="=== תרגילים שהסטודנט כבר פתר - אל תכתוב תרגיל זהה או דומה להם (אותו מבנה ואותה שאלה עם "
                                           "מספרים אחרים), ואל תשאל שאלה שהתשובה עליה היא אחד מהם ===\n" + done))
    return p


def drill_prompt(sb, course_id):
    try:
        e = sb.table("courses").select("exam_type").eq("id", course_id).execute().data[0].get("exam_type")
    except Exception:  # noqa: BLE001
        e = None
    rule = (DRILL_MCQ if e == "mcq" else DRILL_OPEN)  # 27/11: open exam -> open exercises only (his correction)
    return DRILL.replace("{exam}", EXAM.get(e or "", "שאלות פתוחות")).replace("{exam_rule}", rule)


DRILL_SCHEMA = {"type": "object", "properties": {
    "questions": SCHEMA["properties"]["questions"],
    "exercises": {"type": "array", "items": {"type": "object", "properties": {
        "title": {"type": "string"}, "question_md": {"type": "string"}, "solution_md": {"type": "string"},
        "topic": {"type": "string"}}, "required": ["question_md", "solution_md"]}}},
    "required": ["questions", "exercises"]}


CODELINE = re.compile(r";\s*(//.*)?$|^\s*(#include|//|/\*)|\b(printf|digitalWrite|pinMode|Serial\.|System\.out|uint\d+_t|void|int|return|if|else|for|while)\b.*[;{(]")
HEB = re.compile(r"[\u0590-\u05FF]")
MATHRUN = re.compile(r"[A-Za-z0-9\\{}_^()\[\]=+\-*/.,:;|<>!' ]+")


def wrap_math(s):
    """Gemini sometimes writes LaTeX without $ (comm quizzes 23/11/2026: raw \\frac on the page). Each run of
    non-Hebrew text that holds a LaTeX command or = becomes $...$; text that already has $ is left alone."""
    if not s or "$" in s or "\\" not in s:
        return s

    def one(m):
        run = m.group(0)
        core = run.strip(" .,:;")
        if core.startswith("-") and not core[1:2].isdigit():  # "ב-\\alpha": the hyphen belongs to the Hebrew word
            core = core[1:].lstrip()
        if not core or not re.search(r"\\[a-zA-Z]|[=^_]", core) or core.count("{") != core.count("}"):
            return run
        i = run.index(core)
        return f"{run[:i]}${core}${run[i + len(core):]}"
    out, fence = [], False
    for line in s.split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
            out.append(line)
        elif fence or CODELINE.search(line):  # 27/11: C code got "$...$" (micro exercises) - code is never math
            out.append(line)
        else:  # inline `code` stays as it is
            out.append("`".join(MATHRUN.sub(one, p) if i % 2 == 0 else p for i, p in enumerate(line.split("`"))))
    return "\n".join(out)


def put_drill(sb, l, qs, exs, uncertain):
    for q in qs:
        q["question"], q["explanation"] = wrap_math(q.get("question") or ""), wrap_math(q.get("explanation") or "")
        q["options"] = [wrap_math(o) for o in q.get("options") or []]
    for x in exs:
        x["question_md"], x["solution_md"] = wrap_math(x.get("question_md") or ""), wrap_math(x.get("solution_md") or "")
    for x in exs:  # Gemini sometimes writes "\\n" as text (comm completion 3, 23/11/2026); \\nu / \\neq are kept
        for f in ("question_md", "solution_md"):
            x[f] = re.sub(r"\\n(?![a-zA-Z])", "\n", x.get(f) or "")
    qs = [q for q in qs if len(q.get("options") or []) >= 2 and 0 <= q.get("correct", -1) < len(q["options"])]
    add_questions(sb, l, {"id": l["course_id"]}, qs)
    if exs:
        sb.table("exercises").insert([{"user_id": l["user_id"], "course_id": l["course_id"], "lesson_id": l["id"],
                                       "source": "lesson", "ord": i, "title": x.get("title"), "question_md": x["question_md"],
                                       "solution_md": x.get("solution_md") or "", "topic": x.get("topic"),
                                       "uncertain": uncertain} for i, x in enumerate(exs)]).execute()


def drill(sb, st):
    """One completion lesson without its quiz/exercises: a hand-written file in chapters/drills, else Gemini."""
    st.setdefault("drill", {})
    more = st.get("drill_more") or {}
    if more and st.get("focus") and not _CACHE.get("nofocus"):  # only the focused course's
        ok = {c["id"] for c in focused(st, {c["id"]: c for c in sb.table("courses").select("id, name").execute().data}).values()}
        ids = {l["id"] for l in sb.table("lessons").select("id, course_id").in_("id", list(more)).execute().data if l["course_id"] in ok}
        more = {k: v for k, v in more.items() if k in ids}
    if more:  # material appended to an existing completion lesson: quiz/exercises for the new part, video again
        lid, text = next(iter(more.items()))
        rows = sb.table("lessons").select("id, user_id, course_id, title").eq("id", lid).execute().data
        if rows:
            from google.genai import types
            out = author._generate_json(drill_parts(sb, rows[0], text), drill_prompt(sb, rows[0]["course_id"]), DRILL_SCHEMA, "MEDIUM")
            put_drill(sb, rows[0], out.get("questions") or [], out.get("exercises") or [], True)
            video_now(sb, dict(rows[0], kind="other"))
            print(f"::notice title=Coverage::{rows[0]['title']}: quiz + exercises for the added part", flush=True)
        st["drill_more"].pop(lid, None)
        save(sb, st)
        return True
    courses = {c["id"]: c for c in sb.table("courses").select("id, name").eq("archived", False).execute().data}
    if not st.get("videos_backfilled"):
        for u in sb.table("lessons").select("id, user_id, course_id").eq("kind", "other").like("title", "🔁 השלמה%").execute().data:
            if u["id"] in st["drill"]:
                queue_video(sb, u)
        st["videos_backfilled"] = True
        save(sb, st)
    courses = focused(st, courses)
    rows = [l for l in sb.table("lessons").select("id, user_id, course_id, title, chapter_md, created_at").eq("kind", "other")
            .like("title", "🔁 השלמה%").execute().data if l["course_id"] in courses and l["id"] not in st["drill"]]
    if not rows:
        return False
    rows.sort(key=lambda l: (study_day(sb, l["course_id"]), l["created_at"]))
    l = rows[0]
    hand = None
    for f in sorted(DRILLS.glob("*.json")) if DRILLS.exists() else []:
        d = json.loads(f.read_text(encoding="utf-8"))
        if d["title"] == l["title"] and name_match(d["course"], courses[l["course_id"]]["name"]):
            hand = d
    if hand:
        put_drill(sb, l, hand["questions"], hand["exercises"], False)
    else:
        from google.genai import types
        out = author._generate_json(drill_parts(sb, l, l["chapter_md"] or ""), drill_prompt(sb, l["course_id"]), DRILL_SCHEMA, "MEDIUM")
        put_drill(sb, l, out.get("questions") or [], out.get("exercises") or [], True)
    st["drill"][l["id"]] = "hand" if hand else "gemini"
    save(sb, st)
    video_now(sb, dict(l, kind="other"))
    print(f"::notice title=Coverage::{courses[l['course_id']]['name'][:20]} {l['title']}: quiz + exercises ({'hand' if hand else 'gemini'})", flush=True)
    return True


UNIT_SRC = re.compile(r"🔁 השלמה ל(הרצאה|תרגול) (\d+)( חלק [א-ת])?")


def source_of(sb, unit):
    """The lesson a completion came from (its snapshots slide:N are that lesson's)."""
    m = UNIT_SRC.match(unit.get("title") or "")
    if not m:
        return None
    rows = (sb.table("lessons").select("id, user_id, kind, number, title, status, transcript, slide_count")
            .eq("course_id", unit["course_id"]).eq("kind", "lecture" if m.group(1) == "הרצאה" else "practice")
            .eq("number", int(m.group(2))).execute().data)
    rows = [r for r in rows if eligible(r)]
    if m.group(3):  # "הרצאה 3 חלק א": that half only
        rows = [r for r in rows if m.group(3).strip() in (r.get("title") or "")] or rows
    return max(rows, key=lambda r: r.get("slide_count") or 0) if rows else None


def fix_slides(sb):
    """A completion lesson shows the boards of the lesson it came from: they are copied to it once (slide_count 0 ->
    the copies; the references are renumbered). Without this the site showed nothing, or another lesson's board."""
    for u in (sb.table("lessons").select("id, user_id, course_id, title, chapter_md, slide_count").eq("kind", "other")
              .like("title", "🔁 השלמה%").eq("slide_count", 0).execute().data):
        md = u.get("chapter_md") or ""
        if not hub.SLIDE_REF.search(md):
            continue
        src = source_of(sb, u)
        if not src:
            continue
        new = hub.carry_slides(sb, src, u, md)
        sb.table("lessons").update({"chapter_md": new}).eq("id", u["id"]).execute()
        print(f"::notice title=Coverage::{u['title']}: boards copied from {src['kind']} {src['number']}", flush=True)


def queue_video(sb, l):
    """A video per completion lesson (his request 23/11/2026), made by retry_studio as the voice quota allows."""
    if sb.table("lesson_media").select("id").eq("kind", "video").contains("lesson_ids", [l["id"]]).execute().data:
        return
    sb.table("lesson_media").insert({"user_id": l["user_id"], "course_id": l["course_id"], "kind": "video",
                                     "lesson_ids": [l["id"]], "status": "error", "error": hub.WAIT_MSG}).execute()


def tomorrow_courses(sb):
    from datetime import timedelta
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("Asia/Jerusalem"))
    wd = ((now + timedelta(days=1)).weekday() + 1) % 7
    ids = {s["course_id"] for s in sb.table("schedule_slots").select("course_id, weekday").eq("weekday", wd).execute().data}
    return now, [c for c in sb.table("courses").select("id, name, user_id").eq("archived", False).execute().data if c["id"] in ids]


def missing_for(sb, course, st):
    """What is not ready yet in this course: lessons in work, completions waiting, quizzes, videos."""
    from datetime import timedelta, timezone
    ls = sb.table("lessons").select("id, kind, title, status, transcript, created_at").eq("course_id", course["id"]).execute().data
    out = []
    # last year's recording kept "(להשוואה)" is transcribed only, on purpose - not a lesson in work (27/11/2026)
    busy = [l for l in ls if l["status"] in ("queued", "processing", "transcribed", "error")
            and "(להשוואה)" not in (l.get("title") or "")]
    if busy:
        out.append(f"{len(busy)} שיעורים בעיבוד")
    # 25/11: with the real state (v2 / audited) - an empty one counted every lesson again ("8 completions" on a
    # finished course), so the focus never moved on; focus None = every course is looked at
    cov = [j for j in todo(sb, {**st, "focus": None}) if j[1]["id"] == course["id"]]
    if cov:
        out.append(f"{len(cov)} השלמות בכתיבה")
    if any(course["name"] and j.get("course") and same_course(j["course"], course["name"]) for j in st.get("pending") or []):
        out.append("תיקוני שאלונים, השלמות ותרגילים")
    units = [l for l in ls if l["kind"] == "other" and (l.get("title") or "").startswith("🔁 השלמה")]
    nodrill = [u for u in units if u["id"] not in st.get("drill", {})]
    if nodrill:
        out.append(f"{len(nodrill)} שאלונים ותרגילים")
    novid = no_video(sb, course, ls)
    if novid:
        out.append(f"{len(novid)} סרטונים")
    return out


def no_video(sb, course, ls=None):
    """Lessons that should have a video and have no ready one: completions of lectures and this week's lectures (never
    practices, labs or a practice's completion - video_now makes none for them, so they were "missing" for ever)."""
    from datetime import timedelta, timezone
    if SKIP_COURSES.search(course["name"] or ""):
        return []
    if ls is None:
        ls = sb.table("lessons").select("id, user_id, course_id, kind, title, status, transcript, created_at").eq("course_id", course["id"]).execute().data
    week = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
    want = [l for l in ls if l["kind"] == "other" and (l.get("title") or "").startswith("🔁 השלמה להרצאה")] + \
           [l for l in ls if l["kind"] == "lecture" and l["status"] == "ready" and l["created_at"] >= week
            and hub.AUTO_STUDIO.search(course["name"] or "")
            and not (l.get("transcript") or "").startswith(hub.course_site.SITE_NOTE)]
    if not want:
        return []
    rows = sb.table("lesson_media").select("lesson_ids, status").eq("kind", "video").eq("course_id", course["id"]).execute().data
    ready = {i for m in rows if m["status"] == "ready" for i in (m.get("lesson_ids") or [])}
    return [l for l in want if l["id"] not in ready]


def make_missing_videos(sb, limit=2):
    """27/11/2026: a lesson whose video was never started (video_now skipped it - the focus bug of 24-25/11) has no
    media row, so nothing ever retried it. Every queue round starts up to `limit` of those (no row in work yet)."""
    from datetime import timedelta, timezone
    started = 0
    for c in sb.table("courses").select("id, name").eq("archived", False).execute().data:
        for l in no_video(sb, c):
            if started >= limit:
                return started
            rows = sb.table("lesson_media").select("status, error, created_at").eq("kind", "video").contains("lesson_ids", [l["id"]]).execute().data
            if any(r["status"] in ("queued", "processing") for r in rows):
                continue
            errs = [r for r in rows if r["status"] == "error"]
            if any(w in (r.get("error") or "") for r in errs for w in ("מכסה", "עמוסים")):
                continue  # retried by queue_runner.retry_studio after Gemini's reset
            day_ago = (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat()
            if any(r["created_at"] > day_ago for r in errs):
                continue  # failed on something else less than 12 hours ago: not again yet
            full = sb.table("lessons").select("id, user_id, course_id, kind, title").eq("id", l["id"]).execute().data
            if full:
                _CACHE["nofocus_video"] = True
                try:
                    video_now(sb, full[0])
                finally:
                    _CACHE.pop("nofocus_video", None)
                started += 1
    return started


def ready_alert(sb):
    """One push per course for tomorrow's classes (his request 23/11/2026): "✅ מוכן ללמידה" as soon as everything is
    ready, or at 21:00 what is still missing."""
    import notify
    now, courses = tomorrow_courses(sb)
    courses = [c for c in courses if not SKIP_COURSES.search(c["name"] or "")]
    st = load(sb)
    sent = st.setdefault("ready", {})
    day = now.date().isoformat()
    for c in courses:
        if sent.get(c["id"]) == day:
            continue
        miss = missing_for(sb, c, st)
        if not miss:
            notify.send(sb, c["user_id"], f"✅ מוכן למחר: {c['name']}", "קריאה, השלמות, שאלונים, תרגילים וסרטונים - הכל מוכן")
        elif now.hour >= 21:
            notify.send(sb, c["user_id"], f"⚠️ עוד לא הכל מוכן למחר: {c['name']}", "חסר: " + ", ".join(miss))
        else:
            continue
        sent[c["id"]] = day
        save(sb, st)
        print(f"::notice title=Ready alert::{c['name']}: {'ready' if not miss else ', '.join(miss)}", flush=True)


TRIM = """לפניך (1) מה שהסטודנט כבר קרא ופתר: הפרקים של השיעורים שסימן כנקראו והתרגילים שסימן כפתורים, ואחריהם (2) פרק
השלמה שנכתב לו. הוא לא רוצה לקרוא שוב מה שכבר למד (בקשתו 23/11/2026).
החזר את פרק ההשלמה אחרי שהסרת ממנו כל מה שכבר נמצא ב-(1): נושא, הסבר, הגדרה, נוסחה או דוגמה שכבר מוסברים שם, ותרגיל
שכבר פתר (גם אם הנתונים מנוסחים אחרת). השאר כל מה שחדש: נושא שלא היה, פרט/נוסחה/מקרה/הערת מבחן שלא הופיעו, תרגיל שלא
פתר. אל תשכתב ואל תקצר את מה שנשאר - העתק אותו כמו שהוא (כולל ![..](slide:N), נוסחאות, 📝 מה כתוב בלוח). כותרת שכל
התוכן שלה הוסר - הסר גם אותה. הסר גם מטרות הקורס / סילבוס / רשימת נושאי הקורס (זה לא חומר
לימוד); מידע על המבחן (מבנה, שפה, סוג שאלות) - השאר. בראש הפרק השאר את שורת ה-📌 אם יש. אם הכל כבר נלמד - md ריק."""
TRIM_SCHEMA = {"type": "object", "properties": {"md": {"type": "string"}, "removed": {"type": "array", "items": {"type": "string"}}},
               "required": ["md"]}


def trim(sb, unit):
    """A completion lesson without what he already read (lessons marked read) or solved (exercises marked done)."""
    from google.genai import types
    m = UNIT_SRC.match(unit.get("title") or "")
    if not m:
        return None
    kind, n = ("lecture" if m.group(1) == "הרצאה" else "practice"), int(m.group(2))
    read = [l for l in sb.table("lessons").select("kind, number, title, chapter_md, read_at").eq("course_id", unit["course_id"])
            .eq("number", n).execute().data if l.get("read_at") and l["kind"] in ("lecture", "practice")]
    done = [x for x in sb.table("exercises").select("question_md, done_at, lesson_id").eq("course_id", unit["course_id"])
            .not_.is_("done_at", "null").execute().data]
    known = "\n\n".join(f"=== {l['kind']} {l['number']} {l.get('title') or ''} ===\n{body_of(l['chapter_md'] or '')}" for l in read)
    known += "\n\n=== תרגילים שפתר ===\n" + "\n\n".join(x["question_md"] for x in done)[:40000]
    out = author._generate_json([types.Part.from_text(text="(1)\n" + known[:150000]),
                                 types.Part.from_text(text="(2) פרק ההשלמה:\n" + (unit["chapter_md"] or ""))], TRIM, TRIM_SCHEMA, "MEDIUM")
    md = (out.get("md") or "").strip()
    old = unit["chapter_md"] or ""
    removed = out.get("removed") or []
    # guards (23/11/2026, comm completion 3: 10.7k -> 0.8k with nothing listed, and \\cos broken into \\\\( ):
    if md and author.is_cut(md):
        return None
    if md.count("\\\\(") > old.count("\\\\("):  # \\cos broken into \\\\( (comm completion 3)
        print("::notice title=Trim guard::broken formulas", flush=True)
        return None
    if len(md) < 0.1 * len(old) and len(removed) < 2:  # 23/11: Gemini often lists nothing; only a near-wipe is refused
        print(f"::notice title=Trim guard::{len(old)} -> {len(md)} with {len(removed)} listed", flush=True)
        return None
    return md, removed


def trim_course(sb, name, only=""):
    ids = [c["id"] for c in sb.table("courses").select("id, name").execute().data if name_match(name, c["name"])]
    for u in (sb.table("lessons").select("id, user_id, course_id, title, chapter_md").in_("course_id", ids).eq("kind", "other")
              .like("title", "🔁 השלמה%").execute().data):
        if only and not any(u["title"] == f"🔁 השלמה ל{x.strip()}" for x in only.split(",")):
            continue
        res = trim(sb, u)
        if res is None:
            print(f"::warning title=Trim::{u['title']}: no usable answer - kept as is", flush=True)
            continue
        md, removed = res
        try:  # the FIRST version is kept (a second trim must not overwrite the original)
            sb.storage.from_(BUCKET).upload(f"{u['user_id']}/lessons/{u['id']}/chapter_before_trim.md", (u["chapter_md"] or "").encode(),
                                            {"content-type": "text/markdown; charset=utf-8", "upsert": "false"})
        except Exception:  # noqa: BLE001 - already there
            pass
        if not md:
            md = "> 📌 כל מה שהיה בהשלמה הזו כבר נמצא בפרקים שקראת ובתרגילים שפתרת - אין מה ללמוד כאן."
        sb.table("lessons").update({"chapter_md": author.normalize_math(md)}).eq("id", u["id"]).execute()
        redrill(sb, dict(u, chapter_md=md))  # the quiz follows the trimmed text (obvious - his remark 23/11/2026)
        print(f"::notice title=Trim::{u['title']}: {len(u['chapter_md'] or '')} -> {len(md)} chars; removed: {'; '.join(removed)[:400]}", flush=True)


def redrill(sb, u):
    """A completion that changed (trimmed): a new quiz and new exercises on what is in it now. Old questions he never
    answered and old exercises he never marked done go; answered / done ones stay (his history)."""
    from google.genai import types
    qs = sb.table("questions").select("id").eq("lesson_id", u["id"]).execute().data
    answered = {a["question_id"] for a in sb.table("attempts").select("question_id").in_("question_id", [q["id"] for q in qs]).execute().data} if qs else set()
    for q in qs:
        if q["id"] not in answered:
            sb.table("questions").delete().eq("id", q["id"]).execute()
    sb.table("exercises").delete().eq("lesson_id", u["id"]).is_("done_at", "null").execute()
    out = author._generate_json(drill_parts(sb, u, u["chapter_md"] or ""), drill_prompt(sb, u["course_id"]), DRILL_SCHEMA, "MEDIUM")
    put_drill(sb, u, out.get("questions") or [], out.get("exercises") or [], True)
    print(f"::notice title=Redrill::{u['title']}: {len(out.get('questions') or [])} questions, {len(out.get('exercises') or [])} exercises "
          f"(kept {len(answered)} answered)", flush=True)


PRUNE = """לפניך פרק השלמה ורשימת שאלות אמריקאיות (id: שאלה). החזר ב-off את ה-id של כל שאלה שהנושא שלה לא מופיע בפרק
ההשלמה (התשובה עליה לא נלמדת מהפרק הזה). שאלה על נושא שכן מופיע בפרק - לא להחזיר."""
PRUNE_SCHEMA = {"type": "object", "properties": {"off": {"type": "array", "items": {"type": "string"}}}, "required": ["off"]}


def prune_questions(sb, u):
    """Questions (also answered ones - he approved 23/11/2026) that are not about what the completion holds now go."""
    from google.genai import types
    qs = sb.table("questions").select("id, question").eq("lesson_id", u["id"]).execute().data
    if not qs:
        return
    out = author._generate_json([types.Part.from_text(text=body_of(u["chapter_md"] or "")),
                                 types.Part.from_text(text="\n".join(f"{q['id']}: {q['question']}" for q in qs))], PRUNE, PRUNE_SCHEMA, "LOW")
    off = [i for i in out.get("off") or [] if i in {q["id"] for q in qs}]
    if len(off) >= len(qs):  # never empty the whole quiz on one answer
        return
    for i in off:
        sb.table("questions").delete().eq("id", i).execute()
    print(f"::notice title=Prune::{u['title']}: {len(off)} questions not about this completion removed", flush=True)


def fix_course(sb, name, tries=4):
    """His rules for a course's completions (23/11/2026): one completion per week; each trimmed to what he has not
    read/solved (tried again until a trim passes the guards); a new quiz + exercises on what is left, never repeating a
    solved exercise; questions not about the completion removed."""
    merge_units(sb)
    ids = [c["id"] for c in sb.table("courses").select("id, name").execute().data if name_match(name, c["name"])]
    st = load(sb)
    done = st.setdefault("trimmed", {})
    for u in (sb.table("lessons").select("id, user_id, course_id, title, chapter_md").in_("course_id", ids).eq("kind", "other")
              .like("title", "🔁 השלמה%").execute().data):
        if done.get(u["id"]) != len(u["chapter_md"] or ""):
            res = None
            for k in range(tries):
                res = trim(sb, u)
                if res is not None:
                    break
                print(f"::notice title=Trim::{u['title']}: attempt {k + 1} failed the guards - again", flush=True)
            if res is None:
                print(f"::warning title=Trim::{u['title']}: {tries} attempts failed - kept as is", flush=True)
            else:
                md = res[0] or "> 📌 כל מה שהיה בהשלמה הזו כבר נמצא בפרקים שקראת ובתרגילים שפתרת - אין מה ללמוד כאן."
                try:
                    sb.storage.from_(BUCKET).upload(f"{u['user_id']}/lessons/{u['id']}/chapter_before_trim.md", (u["chapter_md"] or "").encode(),
                                                    {"content-type": "text/markdown; charset=utf-8", "upsert": "false"})
                except Exception:  # noqa: BLE001
                    pass
                md = author.normalize_math(md)
                sb.table("lessons").update({"chapter_md": md}).eq("id", u["id"]).execute()
                print(f"::notice title=Trim::{u['title']}: {len(u['chapter_md'] or '')} -> {len(md)}; removed: {'; '.join(res[1])[:300]}", flush=True)
                u["chapter_md"] = md
            done[u["id"]] = len(u["chapter_md"] or "")
            save(sb, st)
        redrill(sb, u)
        prune_questions(sb, u)


QUIZ = """לפניך פרק קריאה של שיעור. כתוב עליו שאלון אמריקאי לחזרה: 10-12 שאלות הבנה בלבד (מילוליות, הגיון, "מה קורה
אם", "למה"), שמכסות את כל הנושאים בפרק לפי הסדר, 4 תשובות באורך ובסגנון דומים, correct = אינדקס הנכונה, explanation
שמסביר למה הנכונה נכונה ולמה האחרות לא. בלי שאלות חישוב; אם בכל זאת צריך מספר - הנוסחה כתובה בשאלה. נוסחאות ב-$...$.
עברית בלבד. רק מה שבפרק."""
QUIZ_SCHEMA = {"type": "object", "properties": {"questions": SCHEMA["properties"]["questions"]}, "required": ["questions"]}


def requiz(sb, l):
    """One quiz per lecture, about what its chapter holds now (comm lecture 4A had 71 questions piled up by rewrites
    and audits, his remark 23/11/2026). Unanswered questions go; a practice gets no quiz (his rule)."""
    from google.genai import types
    qs = sb.table("questions").select("id").eq("lesson_id", l["id"]).execute().data
    answered = {a["question_id"] for a in sb.table("attempts").select("question_id").in_("question_id", [q["id"] for q in qs]).execute().data} if qs else set()
    for q in qs:
        if q["id"] not in answered:
            sb.table("questions").delete().eq("id", q["id"]).execute()
    if l["kind"] != "lecture":
        print(f"::notice title=Quiz::{l['kind']} {l.get('number')} {(l.get('title') or '')[:20]}: no quiz (practice) - {len(qs) - len(answered)} removed", flush=True)
        return
    if len(answered) >= 10:  # his rule 27/11/2026: 10-12 questions - what he already answered is the quiz
        print(f"::notice title=Quiz::lecture {l.get('number')}: {len(qs)} -> {len(answered)} (answered ones)", flush=True)
        return
    out = author._generate_json([types.Part.from_text(text=body_of(l.get("chapter_md") or ""))], QUIZ, QUIZ_SCHEMA, "MEDIUM")
    new = [q for q in out.get("questions") or [] if len(q.get("options") or []) >= 2 and 0 <= q.get("correct", -1) < len(q["options"])]
    new = new[:max(0, 12 - len(answered))]
    for q in new:
        q["question"], q["explanation"] = wrap_math(q.get("question") or ""), wrap_math(q.get("explanation") or "")
        q["options"] = [wrap_math(o) for o in q["options"]]
    add_questions(sb, l, {"id": l["course_id"]}, new)
    print(f"::notice title=Quiz::lecture {l.get('number')} {(l.get('title') or '')[:20]}: {len(qs)} -> {len(new) + len(answered)} questions", flush=True)


HOLLOW = re.compile(r"\\text\{(חישוב|ערך|שרטוט|הצבת|הסרת|ניתוק)|מחושב\S*\s*(כראוי|בנפרד|ביחידות)?\s*✅"
                    r"|\*\*תוצאה:\*\*\s*✅?\s*(חישוב|קבלת|ערך|ערכי|תוצאות|עקומת|הספק|זמני|שרטוט|סוג)"
                    r"|\*\*הצבה:\*\*\s*(הצבת|נציב את ערכי|שימוש ב|חישוב|הכפלת)[^$\n]*(\n|$)")


def hollow(x):
    """A solution that only names the steps ("**תוצאה:** ✅ ערך המשוב מחושב") - no numbers where the question has
    data. 27/11: about a hundred exam / sheet exercises were like that."""
    q, s = x.get("question_md") or "", x.get("solution_md") or ""
    return bool((len(re.findall(r"\d+(?:\.\d+)?", q)) >= 4 and not re.search(r"(=|\\approx)\s*(\\pm|[-+])?\s*\$?\s*-?\d", s)) or HOLLOW.search(s))


SOLVE = """לפניך תרגיל בקורס "{course}" (הנדסת חשמל) והפתרון השמור שלו, שהוא **חלול**: הוא רק מונה שלבים ("התוצאה מחושבת")
בלי לחשב באמת. אם צורף הקובץ המקורי (מבחן / דף תרגילים / מטלה, ואולי פתרון רשמי) - התרגיל נמצא בו; קח ממנו את כל
הנתונים והשרטוט. אם צורף שיעור - לפי הדרך של המרצה.
כתוב פתרון **מלא ומחושב** לכל סעיף, לכל שלב חישוב באותו מבנה קבוע:
  שורה של הסבר קצר למה עושים את הצעד, ואז
  **נוסחה:** $$...$$ (הנוסחה הכללית, בסימנים)
  **הצבה:** $$...$$ (אותה נוסחה עם המספרים והיחידות)
  **תוצאה:** $$...$$ (המספר הסופי עם יחידות; בתשובה הסופית של הסעיף - ✅ לפניה)
  בהוכחה או בשאלה מילולית: שלבים ממוספרים, כל שלב עם הנימוק שלו. שרטוט - תאר במילים בדיוק מה משרטטים (צירים,
  נקודות, ערכים).
""" + author.EXPLAIN_RULE.replace("{", "{{").replace("}", "}}") + """
אם התרגיל רב-ברירה (יש אפשרויות א/ב/ג/ד): השורה הראשונה "התשובה: **<אות>**", אחריה הפתרון, ובסוף "למה לא האחרות".
אם בנוסח חסר נתון שיש בקובץ - השלם אותו ב-question_md (אחרת החזר את הנוסח כמו שהוא). אל תמציא נתונים: מה שלא
ידוע - כתוב שאינו ידוע ופתור בסימנים, ו-uncertain=true. כל ביטוי מתמטי בתוך $...$, משוואה בשורה נפרדת $$...$$.
עברית בלבד. החזר תרגיל אחד ברשימה exercises."""


def resolve_hollow(sb, course, x, materials, work):
    """One hollow exercise solved again in full - from its file (exam / sheet, + the official solution) or its lesson;
    then re-solved from scratch by the checker. Kept only when the new solution is not hollow."""
    import exercises as exmod
    from google.genai import types
    parts = [types.Part.from_text(text=SOLVE.format(course=course["name"]) + exmod.exam_form(course)),
             types.Part.from_text(text=f"=== התרגיל ===\n{x.get('question_md')}\n\n=== הפתרון החלול ===\n{x.get('solution_md')}")]
    m = next((y for y in materials if y["id"] == x.get("material_id")), None)
    if m:
        data, mime = exmod.blob(sb, m, work)
        if len(data) < exmod.INLINE_LIMIT:
            parts += [types.Part.from_text(text="=== הקובץ המקורי ==="), types.Part.from_bytes(data=data, mime_type=mime)]
            sol = exmod.solution_for(m, materials)
            if sol:
                sdata, smime = exmod.blob(sb, sol, work)
                if len(sdata) + len(data) < exmod.INLINE_LIMIT:
                    parts += [types.Part.from_text(text="=== קובץ הפתרון הרשמי ==="), types.Part.from_bytes(data=sdata, mime_type=smime)]
    elif x.get("lesson_id"):
        l = sb.table("lessons").select("chapter_md, transcript").eq("id", x["lesson_id"]).execute().data
        if l:
            parts.append(types.Part.from_text(text=f"=== השיעור ===\n{body_of(l[0].get('chapter_md') or '')[:60000]}\n\n"
                                                    f"=== התמלול ===\n{(l[0].get('transcript') or '')[:80000]}"))
    found = exmod.gen(parts, None)
    if not found:
        return None
    checked = exmod.gen(parts + [types.Part.from_text(text="=== התרגיל לבדיקה ===\n" + json.dumps(found[:1], ensure_ascii=False))], exmod.CHECK)
    new = (checked or found)[0]
    if hollow(new) or len(new.get("solution_md") or "") < 300:
        return None
    return new


def fix_hollow(sb, key, dry=False, limit_min=95):
    """--hollow <course|all> [dry]: every hollow exercise of the course solved again (see resolve_hollow)."""
    import tempfile
    import time
    import exercises as exmod
    from tidy import tidy
    t0 = time.time()
    for c in sb.table("courses").select("id, name, user_id, kind, exam_type").eq("archived", False).execute().data:
        if not (key == "all" or name_match(key, c["name"])) or SKIP_COURSES.search(c["name"] or "") or c.get("kind") == "lab":
            continue
        xs = sb.table("exercises").select("id, title, source, lesson_id, material_id, question_md, solution_md") \
            .eq("course_id", c["id"]).execute().data
        bad = [x for x in xs if hollow(x) and "🔎 נבדק מחדש" not in (x.get("solution_md") or "")]
        print(f"::notice title=Hollow::{c['name']}: {len(bad)} of {len(xs)} exercises have a hollow solution", flush=True)
        if dry or not bad:
            for x in bad:
                print(f"@@H {x['id'][:8]} {x.get('source')} {(x.get('title') or '')[:50]}", flush=True)
            continue
        materials = sb.table("materials").select("id, title, storage_path, mime, kind").eq("course_id", c["id"]).execute().data
        fixed = 0
        with tempfile.TemporaryDirectory() as work:
            for x in bad:
                if time.time() - t0 > limit_min * 60:
                    print("::warning title=Hollow::time limit - run again for the rest", flush=True)
                    return
                try:
                    new = resolve_hollow(sb, c, x, materials, Path(work))
                except Exception as e:  # noqa: BLE001
                    print(f"::warning title=Hollow::{x['id'][:8]}: {str(e)[:150]}", flush=True)
                    if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota"):
                        return
                    continue
                if not new:
                    print(f"::warning title=Hollow::{x['id'][:8]} {(x.get('title') or '')[:40]}: still hollow - kept", flush=True)
                    continue
                upd = {"solution_md": tidy(wrap_math(new["solution_md"])), "uncertain": bool(new.get("uncertain"))}
                q = new.get("question_md") or ""
                if len(q) > len(x.get("question_md") or "") * 1.05:  # data the file had and the stored text lacked
                    upd["question_md"] = tidy(wrap_math(q))
                sb.table("exercises").update(upd).eq("id", x["id"]).execute()
                exmod.mark_read(sb, c, f"exp:{x['id']}")
                fixed += 1
                print(f"@@FIXED {x['id'][:8]} {(x.get('title') or '')[:50]} ({len(x.get('solution_md') or '')} -> {len(upd['solution_md'])})", flush=True)
        print(f"::notice title=Hollow::{c['name']}: {fixed} of {len(bad)} solved again", flush=True)


def reextract(sb, course, l):
    """The lesson's exercises read again from its chapter + recording (after a rewrite / audit added material).
    Exercises he marked done stay; the others are replaced."""
    import exercises as exmod
    from google.genai import types
    kind = f"{'תרגול' if l['kind'] == 'practice' else 'הרצאה'} {l.get('number') or ''}".strip()
    text = f"=== הפרק ===\n{body_of(l.get('chapter_md') or '')[:80000]}\n\n=== התמלול ===\n{(l.get('transcript') or '')[:120000]}"
    parts = [types.Part.from_text(text=exmod.LESSON_PROMPT.format(kind=kind, course=course["name"], topics=", ".join(l.get("topics") or []) or "-")
                                  + exmod.exam_form(course)),
             types.Part.from_text(text=text)]
    found = exmod.gen(parts, None)
    if not found:
        print(f"::warning title=Exercises::{kind}: none found - the old ones stay", flush=True)
        return
    checked = exmod.gen(parts + [types.Part.from_text(text="=== התרגילים לבדיקה ===\n" + json.dumps(found, ensure_ascii=False))], exmod.CHECK)
    found = checked if len(checked) >= len(found) else found
    old = sb.table("exercises").select("id").eq("lesson_id", l["id"]).is_("done_at", "null").execute().data
    if len(found) < len(old):  # 27/11: reading again never leaves a lesson with fewer exercises than it had
        print(f"::notice title=Exercises::{kind}: {len(found)} found < {len(old)} kept - the old ones stay", flush=True)
        return
    for x in old:
        sb.table("exercises").delete().eq("id", x["id"]).execute()
    sb.table("exercises").insert([{"user_id": course["user_id"], "course_id": course["id"], "lesson_id": l["id"], "source": "lesson",
                                   "ord": i, "title": x.get("title"), "question_md": exmod.tidy(x["question_md"]),
                                   "solution_md": exmod.tidy(x.get("solution_md") or ""), "topic": x.get("topic"),
                                   "exam_style": bool(x.get("exam_style")), "uncertain": bool(x.get("uncertain"))}
                                  for i, x in enumerate(found)]).execute()
    print(f"::notice title=Exercises::{kind} {(l.get('title') or '')[:20]}: {len(old)} -> {len(found)} exercises", flush=True)


def rewrite_lesson(sb, lid, part_sec=1200):
    """A chapter that stays short (comm lecture 5A: 18% of its recording after a rewrite and an audit) is written
    again in 20-minute parts - less to cover per answer, so less is skipped - then audited; kept only if longer."""
    global PART_SEC
    l = sb.table("lessons").select("id, user_id, course_id, kind, number, title, transcript, chapter_md, slide_count").eq("id", lid).execute().data[0]
    course = sb.table("courses").select("id, name, user_id").eq("id", l["course_id"]).execute().data[0]
    old, PART_SEC = PART_SEC, part_sec
    try:
        md, _ = write(sb, l, course)
    finally:
        PART_SEC = old
    body = body_of(l.get("chapter_md") or "")
    if len(md) <= len(body):
        print(f"::warning title=Rewrite::{(l.get('title') or '')[:30]}: {len(md)} <= {len(body)} - kept", flush=True)
        return
    sb.storage.from_(BUCKET).upload(f"{l['user_id']}/lessons/{l['id']}/chapter_before_rewrite20.md", (l.get("chapter_md") or "").encode(),
                                    {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
    md = author.normalize_math(md)
    new, _ = audit(sb, dict(l, chapter_md=md), course, md)
    sb.table("lessons").update({"chapter_md": new}).eq("id", l["id"]).execute()
    print(f"::notice title=Rewrite::{(l.get('title') or '')[:30]}: {len(body)} -> {len(new)} chars (20-min parts + audit)", flush=True)


def refresh_weeks(sb, name, weeks):
    """Weeks whose lessons changed (rewritten / audited): quiz per lecture, exercises read again, the week's set rebuilt."""
    import weekset
    c = [x for x in sb.table("courses").select("id, name, user_id, exam_type").execute().data if name_match(name, x["name"])][0]
    for l in (sb.table("lessons").select("id, user_id, course_id, kind, number, title, topics, chapter_md, transcript, read_at")
              .eq("course_id", c["id"]).in_("number", weeks).in_("kind", ["lecture", "practice"]).execute().data):
        if (l.get("title") or "").startswith("📦"):
            continue
        for step, fn in (("quiz", lambda: requiz(sb, l)), ("exercises", lambda: reextract(sb, c, l))):
            try:  # one lesson's failure must not stop the week (24/11/2026)
                fn()
            except Exception as e:  # noqa: BLE001
                print(f"::warning title=Week refresh::{l['kind']} {l.get('number')} {step}: {str(e)[:200]}", flush=True)
    for w in weeks:
        try:
            weekset.drop("^" + re.escape(c["name"]) + "$", str(w), ["all"])
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Week set::{w}: {str(e)[:150]}", flush=True)
    weekset.run("^" + re.escape(c["name"]) + "$", only_missing=True)


# His order by days (23/11/2026): one course at a time; at 20:00 the next one, even if not all is done (and at once
# if it is). Tuesday 24/11 starts with digital circuits.
PLAN = ["מעגלים ספרתיים", "Java", "מיקרו", "מעגלים לינאריים", "אותות אקראיים", "VLSI", "גלים", "מבוא למערכות תקשורת"]
PLAN_START = "2026-11-23T20:00:00+02:00"


# His week (24/11/2026): every completion closed this week; waves ready to study on Sunday, comm on Monday, and from
# Tuesday 01/12 only new lectures. Each course is worked on until its deadline (or until nothing is left in it);
# new uploads are processed whenever they come. After the last deadline: no focus (everything by the timetable).
# 24/11 17:00: Gemini's daily quota ran out - Java and micro move to Wednesday with linear and random signals
SCHEDULE = [(n, "2026-11-25T23:59:00+02:00") for n in (  # 25/11 morning, his request: EVERY course is finished today
    "Java", "מיקרו", "מעגלים לינאריים", "אותות אקראיים", "VLSI", "גלים", "מבוא למערכות תקשורת", "מעגלים ספרתיים")]


def plan_focus(sb):
    """The course to work on now: the first one in SCHEDULE whose deadline has not passed and that still has work."""
    from zoneinfo import ZoneInfo
    st = load(sb)
    now = datetime.now(ZoneInfo("Asia/Jerusalem"))
    courses = sb.table("courses").select("id, name, user_id").execute().data
    prev = st.get("focus")
    live = []
    for name, until in SCHEDULE:
        if now >= datetime.fromisoformat(until):
            continue
        c = [x for x in courses if name_match(name, x["name"])]
        if c and missing_for(sb, c[0], st):
            live.append((name, datetime.fromisoformat(until).date()))
    # every course due the same day as the first one is worked on together (24/11/2026: digital, Java, micro today)
    focus = "|".join(n for n, d in live if d == live[0][1]) if live else None
    st["focus"] = focus
    save(sb, st)
    if prev and prev != focus:
        try:  # he hears where things stand (23/11/2026)
            import notify
            c = [x for x in courses if name_match(prev, x["name"])]
            if c:
                left = missing_for(sb, c[0], st)
                nxt = next((x["name"] for x in courses if focus and name_match(focus.split("|")[0], x["name"])), "רק הרצאות חדשות")
                notify.send(sb, c[0]["user_id"], f"{'⏭️' if left else '✅'} {c[0]['name']}: {'הזמן נגמר' if left else 'מוכן'}",
                            (f"נשאר: {', '.join(left)}. " if left else "") + f"עכשיו: {nxt}")
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Plan push::{str(e)[:150]}", flush=True)
        print(f"::notice title=Plan::now working on {focus}", flush=True)
    return focus


def progress_push(sb, what, course=""):
    """A short push after each piece of work (his request 23/11/2026: keep me posted) - about the job's OWN course
    (27/11: it named the first focus course whatever was repaired) and never an empty one."""
    if not what or not course:
        return
    try:
        import notify
        st = load(sb)
        for c in sb.table("courses").select("id, name, user_id").execute().data:
            if same_course(course, c["name"]):
                left = missing_for(sb, c, st)
                notify.send(sb, c["user_id"], f"🔧 {c['name']}: {what}", ("נשאר: " + ", ".join(left)) if left else "הקורס מוכן")
                break
    except Exception as e:  # noqa: BLE001
        print(f"::warning title=Progress push::{str(e)[:150]}", flush=True)


def _mine(st, j):
    f = "" if _CACHE.get("nofocus") else (st.get("focus") or "")
    if not f:  # no focus (after the week's schedule): every pending repair may run
        return True
    if "|" in f:
        return any(same_course(x, j["course"]) for x in f.split("|"))
    return bool(f) and same_course(f, j["course"])


def pending_for_next_day(sb):
    """His priority is by days (23/11/2026): repairs for the course he studies next run BEFORE anything else (a new
    upload of a later course waits). Returns True if one was done."""
    st = load(sb)
    jobs = st.get("pending") or []
    if not jobs:
        return False
    plan_focus(sb)
    import time as _t  # every hour (was once per run - the quota reset inside a run went unnoticed, 25/11/2026):
    if _t.time() - (_CACHE.get("skips_cleared") or 0) > 3600:  # steps skipped for Gemini's quota are tried again
        _CACHE["skips_cleared"] = _t.time()                     # (other models / Gemma may answer now)
        for j in jobs:
            j.pop("_skip", None)
    mine = [j for j in jobs if _mine(st, j)]
    # 25/11: the focus course can still "miss" things no repair job does (a video waiting for Gemini) - then the
    # queue sat idle all night. Nothing of the focus left to repair -> the next courses' jobs, by their deadline.
    order = {n: i for i, (n, _) in enumerate(SCHEDULE)}
    rest = sorted([j for j in jobs if j not in mine],
                  key=lambda j: min([i for n, i in order.items() if same_course(n, j["course"])] or [99]))
    for j in mine + rest:
        finished, what = run_job(sb, st, j)
        if what is None:
            continue  # this job waits for Gemini - the next one
        if finished or not any(k in j for k in ("boards", "fix", "place", "rewrite", "weeks", "verify", "mathfix", "convert")):
            drop_job(st, j)
        break
    else:
        save(sb, st)
        return False
    save(sb, st)
    progress_push(sb, what, j.get("course") or "")
    return True


def trim_quiz(sb, name, keep=15):
    """Without Gemini (plan B, 23/11/2026): a lecture keeps the quiz written with its chapter (the first batch) plus
    whatever he answered, up to `keep`; the questions piled up by rewrites / audits go. A practice keeps only answered
    ones (no quiz on practices). Gemini's requiz replaces this later when it can."""
    c = [x for x in sb.table("courses").select("id, name").execute().data if name_match(name, x["name"])][0]
    for l in sb.table("lessons").select("id, kind, number, title").eq("course_id", c["id"]).in_("kind", ["lecture", "practice"]).execute().data:
        qs = sb.table("questions").select("id, created_at").eq("lesson_id", l["id"]).order("created_at").execute().data
        if not qs:
            continue
        ans = {a["question_id"] for a in sb.table("attempts").select("question_id").in_("question_id", [q["id"] for q in qs]).execute().data}
        if l["kind"] == "practice":
            drop = [q for q in qs if q["id"] not in ans]
        else:
            first = qs[0]["created_at"][:16]  # the chapter's own quiz was inserted in one go
            stay = [q for q in qs if q["id"] in ans] + [q for q in qs if q["created_at"][:16] == first and q["id"] not in ans]
            stay = stay[:max(keep, len(ans))]
            ids = {q["id"] for q in stay}
            drop = [q for q in qs if q["id"] not in ids]
        for q in drop:
            sb.table("questions").delete().eq("id", q["id"]).execute()
        print(f"::notice title=Quiz B::{l['kind']} {l.get('number')} {(l.get('title') or '')[:20]}: {len(qs)} -> {len(qs) - len(drop)}", flush=True)


BOARD_CHECK = """לפניך צילומים מהשיעור, וליד כל אחד הבלוק "📝 מה כתוב בלוח" שנכתב עליו בפרק. בדוק כל בלוק מול הצילום שלו
ותקן אותו כך שיתאים בדיוק למה שרואים בצילום (הסטודנט לומד מהבלוק במקום מהתמונה):
- שקופית מוקרנת עם טקסט: העתק את הטקסט שלה - כותרות ופסקאות במלואן, נוסחאות ב-LaTeX ($...$ בשורה, $$...$$ בשורה נפרדת).
- כתב יד על הלוח: העתק אותו (רשימה / נוסחאות / תיאור קצר של שרטוט שבאמת נראה).
- אל תכתוב דבר שלא רואים בצילום (גרף שנחתך, צורה שמנחשים). מה שלא קריא - [לא קריא].
- בלוק שכבר מדויק - החזר אותו כמו שהוא. בלי הקדמות. עברית, מונחים באנגלית כמו שהם.
החזר לכל צילום n את md - תוכן הבלוק בלבד (בלי השורה "📝 מה כתוב בלוח")."""
BOARD_SCHEMA = {"type": "object", "properties": {"blocks": {"type": "array", "items": {"type": "object", "properties": {
    "n": {"type": "integer"}, "md": {"type": "string"}}, "required": ["n", "md"]}}}, "required": ["blocks"]}


def board_check(sb, l):
    """His rule 23/11/2026: every board block matches its snapshot (a slide's own text too, nothing that is not seen).
    Checked after a chapter is written, and once for every existing chapter. Returns the number of blocks rewritten."""
    import boards
    from google.genai import types
    md = l.get("chapter_md") or ""
    bl = boards.blocks(md)
    if not bl:
        return 0
    store = sb.storage.from_(BUCKET)
    total = 0
    for i in range(0, len(bl), 12):  # 12 snapshots per request
        chunk, parts = bl[i:i + 12], [types.Part.from_text(text=BOARD_CHECK)]
        for n, s, e, text in chunk:
            try:
                data = store.download(f"{l['user_id']}/lessons/{l['id']}/slide_{n:03d}.webp")
            except Exception:  # noqa: BLE001
                continue
            body = text.split("\n", 1)[1] if "\n" in text else ""
            parts += [types.Part.from_text(text=f"===== צילום {n} =====\nהבלוק:\n{body.strip()}"),
                      types.Part.from_bytes(data=data, mime_type="image/webp")]
        if len(parts) == 1:
            continue
        out = author._generate_json(parts, None, BOARD_SCHEMA, "LOW")
        fixed = {b["n"]: author.normalize_math(b["md"].strip()) for b in out.get("blocks") or [] if (b.get("md") or "").strip()}
        for n, s, e, text in sorted(chunk, key=lambda b: -b[1]):  # from the end, so offsets stay valid
            if n in fixed and fixed[n] != text.split("\n", 1)[-1].strip():
                md = md[:s] + f"**📝 מה כתוב בלוח:**\n{fixed[n]}\n\n" + md[e:]
                total += 1
        bl = boards.blocks(md) if total else bl
    if total:
        try:
            store.upload(f"{l['user_id']}/lessons/{l['id']}/chapter_before_boardcheck.md", (l.get("chapter_md") or "").encode(),
                         {"content-type": "text/markdown; charset=utf-8", "upsert": "false"})
        except Exception:  # noqa: BLE001
            pass
        sb.table("lessons").update({"chapter_md": md}).eq("id", l["id"]).execute()
    print(f"::notice title=Boards::{l.get('kind')} {l.get('number')} {(l.get('title') or '')[:25]}: {total} of {len(boards.blocks(md))} blocks fixed", flush=True)
    return total


def board_check_course(sb, name):
    st = load(sb)
    done = st.setdefault("boards_checked", {})
    c = [x for x in sb.table("courses").select("id, name").execute().data if name_match(name, x["name"])][0]
    for l in (sb.table("lessons").select("id, user_id, course_id, kind, number, title, chapter_md").eq("course_id", c["id"])
              .eq("status", "ready").execute().data):
        if done.get(l["id"]) or (l.get("title") or "").startswith("📦"):
            continue
        board_check(sb, l)
        done[l["id"]] = 1
        save(sb, st)


GEMINI_ONLY = ("boards", "rewrite")


def quota_out():
    """Gemini's daily quota is marked as used up (queue state, set by the queue runner)."""
    try:
        import queue_runner
        return queue_runner.quota_blocked(hub.db())
    except Exception:  # noqa: BLE001
        return False  # need images / long recordings: only Gemini can do them


def run_job(sb, st, j):
    """One step of a pending repair job; returns (finished, what was done). A step that needs Gemini when its quota is
    out is skipped for now (kept in the job) and the text steps go on with the free backup (24/11/2026)."""
    steps = [("boards", lambda: board_check_course(sb, j["course"]), "כל בלוקי 'מה כתוב בלוח' נבדקו מול הצילומים"),
             ("fix", lambda: fix_course(sb, j["course"]), "ההשלמות קוצרו וקיבלו שאלון ותרגילים חדשים"),
             ("place", lambda: place_old_audits(sb, j["course"]), "פרטים מההשוואה מול ההקלטה שולבו בתוך הפרקים"),
             ("rewrite", lambda: rewrite_lesson(sb, j["rewrite"]), "פרק קצר נכתב מחדש"),
             ("weeks", lambda: refresh_weeks(sb, j["course"], j["weeks"]), "שאלונים ותרגילים של השבועות סודרו"),
             ("verify", lambda: verify_exercises(sb, j["course"]), "הפתרונות של התרגילים נבדקו בפתרון מחדש"),
             ("mathfix", lambda: math_fix(sb, j["course"]), "נוסחאות שבורות תוקנו בכל הפרקים, השאלונים והתרגילים"),
             ("convert", lambda: convert_exercises(sb, j["course"]), "התרגילים בפורמט המבחן (לחיצים אם המבחן אמריקאי), עם הנוסחה")]
    skipped = set(j.get("_skip") or [])
    for key, fn, what in steps:
        if not j.get(key) or key in skipped:
            continue
        try:
            res = fn()
        except Exception as e:  # noqa: BLE001
            gemini = author._is(e, "RESOURCE_EXHAUSTED", "429", "quota", "UNAVAILABLE", "503", "עמוסים", "המכסה")
            if key in GEMINI_ONLY and gemini:
                j["_skip"] = sorted(skipped | {key})  # after Gemini's reset (the skip list is cleared then)
                print(f"::notice title=Repairs::{j['course']} {key}: waits for Gemini - the other steps go on", flush=True)
                return False, ""
            if gemini:
                raise
            # 27/11/2026: any other error (a bug, bad data) - two tries, then the step is dropped and the job goes on;
            # before, the same failing step ran again every round and every job behind it waited for ever
            fails = j.setdefault("_fail", {})
            fails[key] = fails.get(key, 0) + 1
            print(f"::warning title=Repairs::{j['course']} {key} failed ({fails[key]}/2): {str(e)[:200]}", flush=True)
            if fails[key] >= 2:
                j.pop(key)
            return False, ""
        # 27/11/2026: the exam-format step converted only part of the exercises (Java 11 of 32) and was then "done" -
        # it goes again while each round still converts some (at most 5 rounds)
        if key == "convert" and isinstance(res, tuple) and 0 < res[0] < res[1] and j.get("_rounds", 0) < 5:
            j["_rounds"] = j.get("_rounds", 0) + 1
            return False, what
        j.pop(key)
        return False, what
    if any(j.get(k) for k in skipped):
        return False, None  # only Gemini steps are left: nothing to do until its reset
    return True, ""


VERIFY_EX = """לפניך שאלות אמריקאיות מתרגילים בהנדסת חשמל. פתור כל אחת בעצמך מההתחלה, צעד אחרי צעד, בלי להסתמך על שום
פתרון, והחזר לכל id את האות של התשובה הנכונה (א/ב/ג/ד/ה/ו). אם אף אפשרות לא נכונה או שהשאלה לא חד-משמעית - letter ריק."""
VERIFY_SCHEMA = {"type": "object", "properties": {"answers": {"type": "array", "items": {"type": "object", "properties": {
    "id": {"type": "string"}, "letter": {"type": "string"}}, "required": ["id", "letter"]}}}, "required": ["answers"]}
ANS = re.compile(r"התשובה(?:\s+הנכונה)?(?:\s+היא)?\s*:?\s*\*\*\s*\(?([אבגדהו])|התשובה\s+הנכונה(?:\s+היא)?\s*:?\s*\(?([אבגדהו])['׳]?(?![\u0590-\u05FF])")


def verify_exercises(sb, name):
    """His rule 24/11/2026: an exercise Gemini wrote is checked by solving it again independently. A multiple-choice
    exercise whose stated answer differs from the second solution is marked uncertain and gets a visible warning."""
    from google.genai import types
    c = [x for x in sb.table("courses").select("id, name").execute().data if name_match(name, x["name"])][0]
    rows = [x for x in sb.table("exercises").select("id, question_md, solution_md, uncertain, done_at").eq("course_id", c["id"])
            .execute().data if re.search(r"(?m)^\s*(\*\*)?\(?[א][.)]|אפשרויות\s*:?\s*\(?א[.)]", x["question_md"] or "")]
    stated, unstated = {}, []
    for x in rows:
        m = ANS.search(author.fix_arabic(x.get("solution_md") or ""))
        if m:
            stated[x["id"]] = m.group(1) or m.group(2)
        elif (x.get("solution_md") or "").strip() and "🔎 נבדק מחדש" not in x["solution_md"]:
            unstated.append(x)  # options but no stated letter (exam files): it cannot be clicked
    rows = [x for x in rows if x["id"] in stated and "⚠️ הפתרון לא אומת" not in (x.get("solution_md") or "")
            and "🔎 נבדק מחדש" not in (x.get("solution_md") or "")]  # 27/11: settled by Claude - not re-flagged
    for i in range(0, len(unstated), 8):  # the letter the solution leads to, so the question becomes clickable
        chunk = unstated[i:i + 8]
        out = author._generate_json([types.Part.from_text(text="\n\n".join(
            f"=== id: {x['id']} ===\n{x['question_md']}\n--- הפתרון ---\n{x['solution_md']}" for x in chunk))],
            VERIFY_EX + " לכל שאלה מצורף פתרון: החזר את האות שהפתרון מגיע אליה; אם הפתרון שגוי - את האות הנכונה.", VERIFY_SCHEMA, "HIGH")
        got = {a["id"]: (a.get("letter") or "").strip().strip("'׳") for a in out.get("answers") or []}
        for x in chunk:
            g = got.get(x["id"])
            if g and g in "אבגדהו":
                sb.table("exercises").update({"solution_md": f"התשובה: **{g}**\n\n" + x["solution_md"]}).eq("id", x["id"]).execute()
    print(f"::notice title=Verify::{c['name']}: {len(unstated)} exercises got their answer letter (clickable now)", flush=True)
    bad = 0
    for i in range(0, len(rows), 8):
        chunk = rows[i:i + 8]
        out = author._generate_json([types.Part.from_text(text="\n\n".join(f"=== id: {x['id']} ===\n{x['question_md']}" for x in chunk))],
                                    VERIFY_EX, VERIFY_SCHEMA, "HIGH")
        got = {a["id"]: (a.get("letter") or "").strip().strip("'׳") for a in out.get("answers") or []}
        # 27/11: Gemini alone was wrong on 39 of 46 disagreements (he would see false warnings). A disagreement goes
        # to a second, independent model; it is marked only if that one does not confirm the stated answer either.
        odd = [x for x in chunk if got.get(x["id"]) and got[x["id"]] != stated[x["id"]]]
        second = {}
        if odd:
            try:
                o2 = author._backup_json([types.Part.from_text(text="\n\n".join(f"=== id: {x['id']} ===\n{x['question_md']}"
                                                                                for x in odd))], VERIFY_EX, VERIFY_SCHEMA) or {}
                second = {a["id"]: (a.get("letter") or "").strip().strip("'׳") for a in o2.get("answers") or []}
            except Exception as e:  # noqa: BLE001
                print(f"::notice title=Verify::second opinion failed: {str(e)[:120]}", flush=True)
        for x in chunk:
            g = got.get(x["id"])
            if g and g != stated[x["id"]] and second.get(x["id"]) == stated[x["id"]]:
                print(f"::notice title=Verify::{x['id'][:8]}: second model confirms {stated[x['id']]} - kept", flush=True)
                continue
            if g and g != stated[x["id"]]:
                bad += 1
                note = f"> ⚠️ הפתרון לא אומת: בפתרון מחדש יצאה תשובה {g} ולא {stated[x['id']]}. לבדוק לפני שסומכים עליו.\n\n"
                sb.table("exercises").update({"uncertain": True, "solution_md": note + (x.get("solution_md") or "")}).eq("id", x["id"]).execute()
    print(f"::notice title=Verify::{c['name']}: {len(rows)} multiple-choice solutions re-solved, {bad} disagree (marked ⚠️)", flush=True)


FIXTEX = """לפניך טקסט מפרק לימוד (עברית + נוסחאות LaTeX), ואחריו רשימת המקומות שבהם הנוסחאות נשברות בתצוגה. תקן רק את
הנוסחאות השבורות: כל נוסחה בתוך $...$ (בתוך משפט) או בבלוק שבו $$ בשורה לבד לפני ואחרי. עברית לא בתוך נוסחה (אם צריך
מילה בתוך נוסחה - \\text{} באנגלית או מחוץ לנוסחה). פקודה ששובשה (\\fle, \\root, \\n באמצע) - הפקודה הנכונה לפי ההקשר
(\\le, \\sqrt, ירידת שורה...). "\\n" שכתוב כטקסט - ירידת שורה אמיתית. אל תשנה שום מילה אחרת, אל תקצר ואל תוסיף.
החזר את כל הטקסט המתוקן ב-text."""
FIXTEX_SCHEMA = {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}
SITE_CHECK = Path(__file__).resolve().parent.parent / "web" / "site-check.mjs"


def render_errors(texts):
    """The site's own renderer (web/site-check.mjs) on each text -> list of error lines per text ([] = clean).
    None when node / the web packages are not available here."""
    import subprocess
    import tempfile
    if not SITE_CHECK.exists() or not (SITE_CHECK.parent / "node_modules").exists():
        return None
    out = []
    d = Path(tempfile.mkdtemp())
    for i, x in enumerate(texts):
        f = d / f"{i}.md"
        f.write_text(x or "", encoding="utf-8")
        r = subprocess.run(["node", "--experimental-strip-types", str(SITE_CHECK), str(f)], cwd=str(SITE_CHECK.parent),
                           capture_output=True, text=True, timeout=120)
        out.append([l for l in r.stdout.splitlines() if l.startswith(("ERR", "RAW"))])
    return out


def _literal_newlines(s):
    return re.sub(r"\\n(?![a-zA-Z])", "\n", s or "")


def fix_text(text, errs):
    from google.genai import types
    out = author._generate_json([types.Part.from_text(text=text),
                                 types.Part.from_text(text="=== המקומות השבורים ===\n" + "\n".join(errs[:30]))], FIXTEX, FIXTEX_SCHEMA, "LOW")
    return (out.get("text") or "").strip()


def math_fix(sb, name):
    """Every chapter, question and exercise of the course through the site's renderer; what shows red is repaired by
    Gemini (formulas only) and kept only if it renders with fewer errors and lost no text (his screenshots 24/11/2026)."""
    c = [x for x in sb.table("courses").select("id, name").execute().data if name_match(name, x["name"])][0]
    items = []  # (table, id, field, value)
    for l in sb.table("lessons").select("id, chapter_md").eq("course_id", c["id"]).execute().data:
        items.append(("lessons", l["id"], "chapter_md", l.get("chapter_md") or ""))
    for x in sb.table("exercises").select("id, question_md, solution_md").eq("course_id", c["id"]).execute().data:
        items += [("exercises", x["id"], "question_md", x.get("question_md") or ""), ("exercises", x["id"], "solution_md", x.get("solution_md") or "")]
    for q in sb.table("questions").select("id, question, explanation, options").eq("course_id", c["id"]).execute().data:
        items += [("questions", q["id"], "question", q.get("question") or ""), ("questions", q["id"], "explanation", q.get("explanation") or "")]
        items += [("questions", q["id"], f"option{k}", o) for k, o in enumerate(q.get("options") or [])]
    # literal "\n" in exercises - no Gemini needed
    items = [(tb, i, f, _literal_newlines(v) if tb == "exercises" else v) for tb, i, f, v in items]
    errs = render_errors([v for *_, v in items])
    if errs is None:
        print("::warning title=Math fix::the site renderer is not available here", flush=True)
        return
    fixed = 0
    opts = {}
    for (tb, i, f, v), e in zip(items, errs):
        new = v
        if e:
            try:
                cand = fix_text(v, e)
            except Exception as ex:  # noqa: BLE001
                print(f"::warning title=Math fix::{tb} {i[:8]} {f}: {str(ex)[:120]}", flush=True)
                cand = ""
            if cand and len(cand) > 0.9 * len(v):
                e2 = render_errors([cand])[0]
                if len(e2) < len(e):
                    new = cand
        if f.startswith("option"):
            opts.setdefault(i, {})[int(f[6:])] = new
            continue
        if new != (sb.table(tb).select(f).eq("id", i).execute().data or [{}])[0].get(f):
            sb.table(tb).update({f: new}).eq("id", i).execute()
            fixed += 1
    for i, o in opts.items():
        cur = (sb.table("questions").select("options").eq("id", i).execute().data or [{}])[0].get("options") or []
        new = [o.get(k, x) for k, x in enumerate(cur)]
        if new != cur:
            sb.table("questions").update({"options": new}).eq("id", i).execute()
            fixed += 1
    print(f"::notice title=Math fix::{c['name']}: {sum(1 for e in errs if e)} broken texts, {fixed} fields fixed", flush=True)


CONVERT = """לפניך תרגילים מהשיעורים בקורס שהמבחן בו {exam}, כל אחד עם הפתרון המלא שלו. אל תכתוב את הפתרון מחדש - הוא
נשאר כמו שהוא. לכל id החזר רק:
- question_md: באמריקאי - השאלה (אותם נתונים ואותו נושא) ואחריה 4 אפשרויות, כל אחת בפסקה משלה בדיוק כך:
  **א.** ... / **ב.** ... / **ג.** ... / **ד.** ... - אחת מהן התוצאה של הפתרון, והשאר טעויות נפוצות. תרגיל עם כמה סעיפים -
  הסעיף העיקרי כשאלה. בפתוח - השאלה כמו שהיא (אפשר רק לסדר לסעיפים כמו במבחן).
- answer: באמריקאי - האות של האפשרות הנכונה (א/ב/ג/ד), לפי הפתרון. בפתוח - ריק.
- formula_md: הנוסחה / הנוסחאות שצריך לשאלה, בבלוק $$ ... $$ (שורה לבד לפני ואחרי), בלי הצבה ובלי התוצאה.
- others_md: באמריקאי - שורה קצרה לכל אפשרות שגויה: למה היא שגויה. בפתוח - ריק.
החזר פריט לכל id שקיבלת. נוסחאות ב-LaTeX: $...$ בשורה. עברית."""
CONVERT_SCHEMA = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "id": {"type": "string"}, "question_md": {"type": "string"}, "answer": {"type": "string"},
    "formula_md": {"type": "string"}, "others_md": {"type": "string"}},
    "required": ["id", "question_md", "formula_md"]}}}, "required": ["items"]}
MCQ_SHAPE = re.compile(r"(?m)^\s*(\*\*)?\(?[א][.)]|אפשרויות\s*:?\s*\(?א[.)]")


TOOPEN = """לפניך תרגילים מקורס שהמבחן בו בשאלות פתוחות, אבל הם נכתבו בטעות כשאלות אמריקאיות. הפוך כל אחד לתרגיל פתוח
כמו במבחן, לכל id:
- question_md: אותה שאלה, אותם נתונים ואותו נושא, כשאלה פתוחה: "חשב...", "מצא...", "הסבר...", "הראה..." (אפשר סעיפים
  א/ב/ג). בלי אפשרויות בחירה ובלי רמז לתשובה. שאלה בסגנון "איזו טענה נכונה" - שאלה פתוחה על אותו עניין ("הסבר
  מדוע...", "מה קורה ל-... כאשר..."). קטע קוד - "מה יודפס? הסבר".
- solution_md: הפתרון המלא שהיה, צעד אחרי צעד, עם כל המספרים, הנוסחאות וההסברים - בלי שורת "התשובה: X", בלי "למה לא
  האחרות" ובלי הפניה לאותיות של אפשרויות. מתחיל בשורה "**הנוסחה:**" עם בלוק $$ (אם כבר יש - כמו שהוא), ומסתיים
  בתוצאה הסופית. אל תקצר: כל שלב ומספר שהיו נשארים. נוסחאות ב-LaTeX ($...$ בשורה, $$ בשורה לבד). עברית.
החזר פריט לכל id שקיבלת."""
TOOPEN_SCHEMA = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "id": {"type": "string"}, "question_md": {"type": "string"}, "solution_md": {"type": "string"}},
    "required": ["id", "question_md", "solution_md"]}}}, "required": ["items"]}
OTHERS = re.compile(r"\n[#*\s]*(?:❌\s*)?\**למה (?:לא האחרות|האחרות שגויות|התשובות האחרות|האפשרויות האחרות)[^\n]*\n.*?(?=\n\s*💡|\n\s*🔎|\Z)", re.S)


def is_mcq(x):
    """A multiple-choice exercise: options from א and a stated answer letter. An open question with parts א/ב/ג has no
    "התשובה: **X**" line, so it is not one."""
    return bool(MCQ_SHAPE.search(x.get("question_md") or "") and ANS.search(author.fix_arabic(x.get("solution_md") or "")))


EXTRA = """לפניך פרק קריאה של הרצאה (בתחילת ההודעה), ואחריו "חומר נוסף" של הקורס על אותו שבוע (דף מאתר הקורס / סיכום /
חומר משנה קודמת). הסטודנט לומד רק מההרצאה, התרגול והתרגילים - חומר נוסף הוא לא קורא. כתוב רק את מה שמופיע בחומר
הנוסף וחסר בפרק (או מופיע בו רק ברמז): הגדרות, נוסחאות, פיתוחים, דוגמאות, קוד, טבלאות, הערות למבחן - מלא ומדויק,
באותו סגנון של הפרק. מה שכבר מוסבר בפרק - אל תחזור עליו. מה שסותר את ההרצאה - אל תוסיף (ההרצאה קובעת). כל קטע
שאתה כותב מתחיל בשורה "> 📎 מחומר הקורס (לא נאמר בהרצאה)". אם לא חסר כלום - md ריק. נוסחאות ב-LaTeX ($...$ בשורה,
$$ בשורה לבד). עברית."""
EXTRA_SCHEMA = {"type": "object", "properties": {"md": {"type": "string"}}, "required": ["md"]}


COMPLETE = """לפניך פרק קריאה של הרצאה (בתחילת ההודעה), ואחריו "השלמה" שנכתבה עליו - מה שהפרק לא כיסה מההקלטה. כתוב
רק את מה שבהשלמה וחסר בפרק (או מופיע בו רק ברמז), **מועתק כמו שהוא** - כל הגדרה, נוסחה, פיתוח, מספר, דוגמה, תרגיל
פתור והערה למבחן, בלי לקצר ובלי לנסח מחדש. מה שכבר מוסבר בפרק במלואו - השמט (זו כפילות). בלי שאלות חזרה ובלי
"תרגילים לתרגול" של ההשלמה. אם לא חסר כלום - md ריק."""


def merge_completions(sb, c, dry=False):
    """His rule 27/11/2026: no completions - a chapter is full. Each "🔁 השלמה להרצאה N" gives lecture N what it lacks
    (each piece at the end of its topic, duplicates dropped); its exercises join the lecture; it is hidden."""
    from google.genai import types
    ls = sb.table("lessons").select("id, user_id, kind, number, title, status, chapter_md").eq("course_id", c["id"]).execute().data
    for x in ls:
        m = re.match(r"🔁 השלמה ל(?:הרצאה|מפגש) (\d+)", x.get("title") or "")
        if not m or not (x.get("chapter_md") or "").strip():
            continue
        n = int(m.group(1))
        tg = [l for l in ls if l["kind"] == "lecture" and l.get("number") == n and l["status"] == "ready"
              and not (l.get("title") or "").startswith("📦") and (l.get("chapter_md") or "").strip()]
        if not tg:
            continue
        t = max(tg, key=lambda l: len(l["chapter_md"]))
        print(f"::notice title=Completion::{c['name']}: {x['id'][:8]} ({len(x['chapter_md'])}) -> lecture {n} {t['id'][:8]} "
              f"({len(t['chapter_md'])})", flush=True)
        if dry:
            continue
        body = re.split(r"(?m)^#{2,3} .*(?:שאלות חזרה|תרגילים לתרגול|תרגול עצמי).*$", body_of(x["chapter_md"]))[0]
        out = author._generate_json([types.Part.from_text(text="=== הפרק של ההרצאה ===\n" + body_of(t["chapter_md"])),
                                     types.Part.from_text(text="=== ההשלמה ===\n" + body)], COMPLETE, EXTRA_SCHEMA, "MEDIUM")
        md = (out.get("md") or "").strip()
        if len(md) >= 80:
            heads = "\n".join(re.findall(r"(?m)^#{2,4} (.+)$", body_of(t["chapter_md"])))
            items = []
            for piece in [p for p in re.split(r"(?m)^(?=#{2,3} )", md) if p.strip()]:
                try:
                    got = author._generate_json([types.Part.from_text(text="=== הכותרות ===\n" + heads),
                                                 types.Part.from_text(text="=== הקטע החסר ===\n" + piece)],
                                                PLACE, PLACE_SCHEMA, "LOW").get("items") or []
                except Exception:  # noqa: BLE001
                    got = []
                items += got if sum(len(i.get("md") or "") for i in got) >= 0.8 * len(piece.strip()) else [{"heading": "", "md": piece}]
            sb.storage.from_("study").upload(f"{t['user_id']}/lessons/{t['id']}/chapter_before_completion.md",
                                             t["chapter_md"].encode("utf-8"),
                                             {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
            t["chapter_md"] = integrate(t["chapter_md"], items)
            sb.table("lessons").update({"chapter_md": t["chapter_md"]}).eq("id", t["id"]).execute()
        sb.table("exercises").update({"lesson_id": t["id"]}).eq("lesson_id", x["id"]).execute()
        qs = sb.table("questions").select("id").eq("lesson_id", x["id"]).execute().data
        ans = {a["question_id"] for a in sb.table("attempts").select("question_id").in_("question_id", [q["id"] for q in qs]).execute().data} if qs else set()
        for q in qs:
            if q["id"] not in ans:
                sb.table("questions").delete().eq("id", q["id"]).execute()
        sb.table("lessons").update({"title": f"📦 (שולב בהרצאה {n}) {x.get('title') or ''}"}).eq("id", x["id"]).execute()
        print(f"::notice title=Completion::{c['name']}: lecture {n} +{len(md) if len(md) >= 80 else 0} chars (of "
              f"{len(body)}), completion hidden", flush=True)


def is_extra(l):
    """Material he does not study by itself (his rule 27/11/2026, every course: lecture -> practice -> exercises only):
    course-site pages and other material that is not a lecture, practice, completion or last year's comparison."""
    t = l.get("title") or ""
    return (l.get("kind") in ("web", "other") and not t.startswith(("📦", "🔁", "מפגש ")) and "(להשוואה)" not in t
            and l.get("status") == "ready")


MARK_RX = re.compile(r"(?:^> 📎 מחומר הקורס \(לא נאמר בהרצאה\)[ \t]*\n(?:[ \t]*\n)*){2,}", re.M)


def clean_marks(md):
    """The placing split one piece into parts, each with its own "📎" line: one line per piece, none left dangling."""
    md = MARK_RX.sub("> 📎 מחומר הקורס (לא נאמר בהרצאה)\n\n", md)
    return re.sub(r"(?m)^> 📎 מחומר הקורס \(לא נאמר בהרצאה\)[ \t]*\n(?:[ \t]*\n)*(?=#{2,4} |\Z)(?!#{2,4} )", "", md)


def merge_extra(sb, c, dry=False):
    """His rule 27/11/2026: "חומר נוסף" is never studied on its own. Each extra lesson of week N gives lecture N of this
    year whatever it has that the lecture's chapter lacks (each piece at the end of its own topic), and is then hidden
    ("📦 (שולב ב...)"). An extra with no lecture yet (a later week / no week) waits, hidden from his lists by the app."""
    from google.genai import types
    ls = sb.table("lessons").select("id, user_id, kind, number, title, status, chapter_md").eq("course_id", c["id"]).execute().data
    done = 0
    for x in ls:
        if not is_extra(x) or not (x.get("chapter_md") or "").strip() or not x.get("number"):
            continue
        tg = [l for l in ls if l["kind"] == "lecture" and l.get("number") == x["number"] and l["status"] == "ready"
              and not (l.get("title") or "").startswith("📦") and (l.get("chapter_md") or "").strip()]
        if not tg:
            continue
        t = max(tg, key=lambda l: len(l["chapter_md"]))
        print(f"::notice title=Extra::{c['name']}: {x['id'][:8]} '{(x.get('title') or '')[:50]}' -> lecture {t['number']} "
              f"({t['id'][:8]})", flush=True)
        if dry:
            continue
        out = author._generate_json([types.Part.from_text(text="=== הפרק של ההרצאה ===\n" + body_of(t["chapter_md"])),
                                     types.Part.from_text(text="=== החומר הנוסף ===\n" + body_of(x["chapter_md"]))],
                                    EXTRA, EXTRA_SCHEMA, "MEDIUM")
        md = (out.get("md") or "").strip()
        if len(md) >= 80:
            heads = "\n".join(re.findall(r"(?m)^#{2,4} (.+)$", body_of(t["chapter_md"])))
            try:
                items = author._generate_json([types.Part.from_text(text="=== הכותרות ===\n" + heads),
                                               types.Part.from_text(text="=== הקטע החסר ===\n" + md)],
                                              PLACE, PLACE_SCHEMA, "LOW").get("items") or []
                if sum(len(i.get("md") or "") for i in items) < 0.8 * len(md):
                    items = [{"heading": "", "md": md}]
            except Exception:  # noqa: BLE001
                items = [{"heading": "", "md": md}]
            sb.storage.from_("study").upload(f"{t['user_id']}/lessons/{t['id']}/chapter_before_extra.md",
                                             t["chapter_md"].encode("utf-8"),
                                             {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
            t["chapter_md"] = clean_marks(integrate(t["chapter_md"], items))
            sb.table("lessons").update({"chapter_md": t["chapter_md"]}).eq("id", t["id"]).execute()
        sb.table("lessons").update({"title": f"📦 (שולב בהרצאה {t['number']}) {x.get('title') or ''}"}).eq("id", x["id"]).execute()
        print(f"::notice title=Extra::{c['name']}: lecture {t['number']} +{len(md) if len(md) >= 80 else 0} chars from "
              f"{x['id'][:8]} (hidden now)", flush=True)
        done += 1
    return done


def merge_extra_all(sb, dry=False):
    for c in sb.table("courses").select("id, name, kind").eq("archived", False).execute().data:
        if c.get("kind") in ("lab", "self") or SKIP_COURSES.search(c["name"] or ""):
            continue
        try:
            merge_extra(sb, c, dry)
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Extra::{c['name']}: {str(e)[:150]}", flush=True)
            if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota"):
                return


def to_open(sb, c, only=None):
    """His correction 27/11/2026: a course whose exam is open has OPEN exercises - none multiple choice (the quiz after a
    lecture stays multiple choice). Every exercise of the course in that shape is rewritten as an open one; done marks
    are kept. `only`: these exercise ids (the mixed-exam balance). Returns (done, total)."""
    from google.genai import types
    rows = [x for x in sb.table("exercises").select("id, question_md, solution_md").eq("course_id", c["id"]).execute().data
            if is_mcq(x) and (only is None or x["id"] in only)]
    done = 0
    for i in range(0, len(rows), 3):
        chunk = rows[i:i + 3]
        try:
            out = author._generate_json([types.Part.from_text(text="\n\n".join(
                f"=== id: {x['id']} ===\n{x['question_md']}\n--- פתרון ---\n{x.get('solution_md') or ''}" for x in chunk))],
                TOOPEN, TOOPEN_SCHEMA, "MEDIUM")
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=To open::{str(e)[:150]}", flush=True)
            if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota"):
                raise
            continue
        got = {it["id"]: it for it in out.get("items") or []}
        for x in chunk:
            it = got.get(x["id"]) or {}
            q, sol = (it.get("question_md") or "").strip(), (it.get("solution_md") or "").strip()
            base = OTHERS.sub("", x.get("solution_md") or "")
            opts = [ln.strip() for ln in (x["question_md"] or "").splitlines() if re.match(r"\s*(\*\*)?\(?[אבגד][.)]", ln)]
            sol = re.sub(r"(?m)^[#\s]*התשובה(?:\s+הנכונה)?(?:\s+היא)?\s*:?\s*\*\*\s*\(?[א-ו][^\n]*\n+", "", sol)
            why = ("no answer" if not it else "still has options" if not q or sum(o in q for o in opts) >= 2
                   else "solution cut" if len(sol) < 0.6 * len(base) else "")
            if why:
                print(f"::notice title=To open::{x['id'][:8]} kept: {why}", flush=True)
                continue
            if "הנוסחה" not in sol:
                m = re.search(r"\*\*הנוסחה:?\*\*:?\s*\$\$.*?\$\$", x.get("solution_md") or "", re.S)
                sol = (m.group(0) + "\n\n" if m else "") + sol
            sb.table("exercises").update({"question_md": wrap_math(q), "solution_md": wrap_math(sol)}).eq("id", x["id"]).execute()
            done += 1
    print(f"::notice title=To open::{c['name']}: {done} of {len(rows)} multiple-choice exercises are open now", flush=True)
    return done, len(rows)


def balance_mixed(sb, c):
    """His rule 27/11/2026: micro's exam is half multiple choice, half open - so are its exercises. When more than 60%
    of the open-to-study exercises are multiple choice, every second one of each lesson (by order) becomes open."""
    rows = sb.table("exercises").select("id, lesson_id, ord, question_md, solution_md, done_at").eq("course_id", c["id"]) \
        .is_("done_at", "null").execute().data
    mcq = [x for x in rows if is_mcq(x)]
    if rows and len(mcq) < 0.4 * len(rows):  # too few: every second open exercise of each lesson becomes multiple choice
        by = {}
        for x in sorted([x for x in rows if not is_mcq(x)], key=lambda x: (str(x.get("lesson_id")), x.get("ord") or 0)):
            by.setdefault(x.get("lesson_id"), []).append(x)
        pick = []
        for xs in by.values():
            pick += xs[1::2]
        pick = {x["id"] for x in pick[:len(rows) // 2 - len(mcq)]}
        print(f"::notice title=Mixed::{c['name']}: {len(mcq)} of {len(rows)} multiple choice - {len(pick)} open become multiple choice", flush=True)
        convert_exercises(sb, c["name"], only=pick)
        return
    if not rows or len(mcq) <= 0.6 * len(rows):
        print(f"::notice title=Mixed::{c['name']}: {len(mcq)} of {len(rows)} multiple choice - balanced", flush=True)
        return
    need = len(mcq) - len(rows) // 2
    by = {}
    for x in sorted(mcq, key=lambda x: (str(x.get("lesson_id")), x.get("ord") or 0)):
        by.setdefault(x.get("lesson_id"), []).append(x)
    pick = []
    for xs in by.values():
        pick += xs[1::2]
    pick = {x["id"] for x in pick[:need]}
    print(f"::notice title=Mixed::{c['name']}: {len(mcq)} of {len(rows)} multiple choice - {len(pick)} become open", flush=True)
    to_open(sb, c, only=pick)


def convert_exercises(sb, name, only=None):
    """His rule 24/11/2026, every course: the exercises after a lecture / practice / completion are in the course's exam
    format - multiple choice (clickable) when the exam is, open otherwise - and each solution carries its formula
    ("📐 הנוסחה לשאלה"). Exercises he marked done stay as they are; the original text is kept in a backup field."""
    from google.genai import types
    c = [x for x in sb.table("courses").select("id, name, exam_type").execute().data if name_match(name, x["name"])][0]
    exam = c.get("exam_type") or "open"
    if exam == "open" and only is None:
        to_open(sb, c)
    if exam == "mixed" and only is None:
        balance_mixed(sb, c)
    if only is not None:  # the mixed-exam balance: these open exercises become multiple choice
        rows = sb.table("exercises").select("id, question_md, solution_md, done_at, source").in_("id", list(only)).execute().data
        exam = "mcq"
    else:
        rows = [x for x in sb.table("exercises").select("id, question_md, solution_md, done_at, source").eq("course_id", c["id"])
                .eq("source", "lesson").is_("done_at", "null").execute().data]
    want_mcq = exam == "mcq"
    todo = [x for x in rows if (want_mcq and not MCQ_SHAPE.search(x["question_md"] or ""))
            or "הנוסחה" not in (x.get("solution_md") or "")]
    if exam == "open":  # still multiple choice (kept above) - not for the formula pass, which would keep the options
        todo = [x for x in todo if not is_mcq(x)]
    label = {"mcq": "אמריקאי", "mixed": "משולב (חצי אמריקאי, חצי פתוח)"}.get(exam, "שאלות פתוחות")
    done = 0
    for i in range(0, len(todo), 3):  # 3 at a time: with 5 the answer left some out (27/11/2026)
        chunk = todo[i:i + 3]
        try:
            out = author._generate_json([types.Part.from_text(text="\n\n".join(
                f"=== id: {x['id']} ===\n{x['question_md']}\n--- פתרון ---\n{x.get('solution_md') or ''}" for x in chunk))],
                CONVERT.replace("{exam}", label), CONVERT_SCHEMA, "MEDIUM")
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Convert::{str(e)[:150]}", flush=True)
            if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota"):
                raise
            continue
        got = {it["id"]: it for it in out.get("items") or []}
        for x in chunk:
            it = got.get(x["id"])
            if not it or not (it.get("formula_md") or "").strip():
                print(f"::notice title=Convert::{x['id'][:8]} kept: {'no answer' if not it else 'no formula'}", flush=True)
                continue
            old = x.get("solution_md") or ""
            q = x["question_md"] or ""
            head = ""
            if want_mcq and not MCQ_SHAPE.search(q):
                letter = (it.get("answer") or "").strip().strip("*.")[:1]
                if not MCQ_SHAPE.search(it.get("question_md") or "") or letter not in "אבגד" or not letter:
                    print(f"::notice title=Convert::{x['id'][:8]} kept: no options א-ד / no answer letter", flush=True)
                    continue
                q = it["question_md"]
                if not re.search(r"התשובה[^\n]{0,20}\*\*[א-ו]", old):
                    head = f"התשובה: **{letter}**\n\n"
            sol = head + ("" if "הנוסחה" in old else f"**הנוסחה:**\n\n{it['formula_md'].strip()}\n\n") + old
            if want_mcq and (it.get("others_md") or "").strip() and "למה" not in old[-600:]:
                sol += f"\n\n**למה לא האחרות:**\n\n{it['others_md'].strip()}"
            sb.table("exercises").update({"question_md": wrap_math(q), "solution_md": wrap_math(sol)}).eq("id", x["id"]).execute()
            done += 1
    print(f"::notice title=Convert::{c['name']} ({label}): {done} of {len(todo)} exercises in the exam's format, with their formula", flush=True)
    return done, len(todo)


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
    if "--trim-quiz" in sys.argv:
        trim_quiz(s, sys.argv[sys.argv.index("--trim-quiz") + 1])
    elif "--pending" in sys.argv:  # '{"course": "...", "weeks": [4,5], "rewrite": "<lesson id>"}' -> done by the queue
        st = load(s)
        arg = json.loads(sys.argv[sys.argv.index("--pending") + 1])
        for job in (arg if isinstance(arg, list) else [arg]):  # one job or a list of jobs (27/11/2026)
            job = new_job(job)
            if job.pop("first", False):  # the course he studies next goes first
                st.setdefault("pending", []).insert(0, job)
            else:
                st.setdefault("pending", []).append(job)
        save(s, st)
        print(f"::notice title=Pending::{st['pending']}", flush=True)
    elif "--rewrite" in sys.argv:
        rewrite_lesson(s, sys.argv[sys.argv.index("--rewrite") + 1])
    elif "--refresh-weeks" in sys.argv:  # "<course>|4,5"
        name, ws = sys.argv[sys.argv.index("--refresh-weeks") + 1].split("|", 1)
        refresh_weeks(s, name, [int(x) for x in ws.split(",")])
    elif "--mathfix" in sys.argv:
        math_fix(s, sys.argv[sys.argv.index("--mathfix") + 1])
    elif "--fix-course" in sys.argv:
        fix_course(s, sys.argv[sys.argv.index("--fix-course") + 1])
    elif "--redrill" in sys.argv:  # "<course>|הרצאה 1,הרצאה 2"
        name, only = sys.argv[sys.argv.index("--redrill") + 1].split("|", 1)
        ids = [c["id"] for c in s.table("courses").select("id, name").execute().data if name_match(name, c["name"])]
        for u in s.table("lessons").select("id, user_id, course_id, title, chapter_md").in_("course_id", ids).like("title", "🔁 השלמה%").execute().data:
            if any(u["title"] == f"🔁 השלמה ל{x.strip()}" for x in only.split(",")):
                redrill(s, u)
    elif "--trim" in sys.argv:  # completions without what he already read / solved (23/11/2026)
        arg = sys.argv[sys.argv.index("--trim") + 1]  # "<course>" or "<course>|הרצאה 2,הרצאה 3"
        trim_course(s, *arg.split("|", 1))
    elif "--unverified" in sys.argv:  # 27/11: the multiple-choice answers re-solving disagreed with, for Claude to settle
        import json as _j
        for x in s.table("courses").select("id, name").eq("archived", False).execute().data:
            for e in s.table("exercises").select("id, title, question_md, solution_md, source, lesson_id, material_id, uncertain, done_at") \
                    .eq("course_id", x["id"]).execute().data:
                if "⚠️ הפתרון לא אומת" in (e.get("solution_md") or ""):
                    print("@@EX " + _j.dumps({"course": x["name"], **e}, ensure_ascii=False), flush=True)
        for lid in [a for a in sys.argv[sys.argv.index("--unverified") + 1:] if len(a) == 36]:  # the lessons' chapters too
            l = s.table("lessons").select("id, title, kind, number, chapter_md").eq("id", lid).execute().data
            for ln in ((l[0]["chapter_md"] or "") if l else "").splitlines():
                print("@@MD " + lid[:8] + " " + ln, flush=True)
        for mid in [a[4:] for a in sys.argv if a.startswith("mat:")]:  # a material's title + path
            print("@@MAT " + _j.dumps(s.table("materials").select("id, title, kind, storage_path").eq("id", mid).execute().data,
                                      ensure_ascii=False), flush=True)
    elif "--exdump" in sys.argv:  # every exercise of a course as JSON lines (read only)
        import json as _j
        for x in s.table("courses").select("id, name").execute().data:
            if name_match(sys.argv[sys.argv.index("--exdump") + 1], x["name"]):
                for e in s.table("exercises").select("id, title, source, lesson_id, done_at, question_md, solution_md") \
                        .eq("course_id", x["id"]).execute().data:
                    print("@@EX " + _j.dumps({"course": x["name"], **e}, ensure_ascii=False), flush=True)
    elif "--lessons" in sys.argv:  # a course's lessons and where each came from (read only; a link shows its host only)
        import json as _j
        from urllib.parse import urlparse
        for x in s.table("courses").select("id, name").execute().data:
            if name_match(sys.argv[sys.argv.index("--lessons") + 1], x["name"]):
                for l in s.table("lessons").select("id, kind, number, title, status, source_url, source_path, created_at, author, "
                                                   "read_at, chapter_md, transcript").eq("course_id", x["id"]).order("created_at").execute().data:
                    u = l.pop("source_url") or ""
                    l["source"] = (urlparse(u).netloc or u[:40]) if u else ""
                    l["chapter_len"] = len(l.pop("chapter_md") or "")
                    t = l.pop("transcript") or ""
                    l["transcript_len"], l["transcript_head"] = len(t), t[:400]
                    print("@@L " + _j.dumps({"course": x["name"], **l}, ensure_ascii=False), flush=True)
    elif "--thinex" in sys.argv:  # 27/11: lessons with a long chapter and < 3 exercises: read the exercises again, then
        # the course's exam format + formula (convert) and the week sets
        import weekset
        for c in s.table("courses").select("*").eq("archived", False).execute().data:
            if c.get("kind") in ("lab", "self") or SKIP_COURSES.search(c["name"] or ""):
                continue
            ls = s.table("lessons").select("id, kind, number, title, status, topics, chapter_md, transcript").eq("course_id", c["id"]) \
                .in_("kind", ["lecture", "practice"]).eq("status", "ready").execute().data
            n_ex = {}
            for e in s.table("exercises").select("lesson_id").eq("course_id", c["id"]).execute().data:
                n_ex[e["lesson_id"]] = n_ex.get(e["lesson_id"], 0) + 1
            hit = 0
            for l in ls:
                if (l.get("title") or "").startswith("📦") or n_ex.get(l["id"], 0) >= 3 or len(l.get("chapter_md") or "") < 6000:
                    continue
                try:
                    reextract(s, c, l)
                    hit += 1
                except Exception as e:  # noqa: BLE001
                    print(f"::warning title=Exercises::{c['name']} {l['kind']} {l.get('number')}: {str(e)[:150]}", flush=True)
                    if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota"):
                        break
            if hit:
                try:
                    convert_exercises(s, c["name"])
                except Exception as e:  # noqa: BLE001
                    print(f"::warning title=Convert::{c['name']}: {str(e)[:150]}", flush=True)
        weekset.fill_missing(s)
    elif "--merged" in sys.argv:  # 27/11: every merged part and the lesson it went into, with the dates (read only)
        cs = {c["id"]: c["name"] for c in s.table("courses").select("id, name").execute().data}
        ls = s.table("lessons").select("id, course_id, kind, number, title, created_at, source_url, source_path, chapter_md, transcript") \
            .execute().data
        for x in ls:
            t = x.get("title") or ""
            if not t.startswith("📦 (שולב ב") or "בהרצאה" in t[:20]:
                continue
            head = re.sub(r"^.*?·\s*", "", re.sub(r"^📦 \(שולב ב.*?\) ", "", t))
            into = [l for l in ls if l["course_id"] == x["course_id"] and l["id"] != x["id"]
                    and f"\n# {head}\n" in (l.get("chapter_md") or "")]
            def first_ts(l):
                m = re.search(r"\[(\d\d:\d\d:\d\d)\]", l.get("transcript") or "")
                return m.group(1) if m else "-"
            print(f"::notice title=Merged::{cs.get(x['course_id'])} | part {x['id'][:8]} created {x['created_at'][:16]} "
                  f"src={'link' if x.get('source_url') else 'file' if x.get('source_path') else '-'} tr={len(x.get('transcript') or '')} | "
                  + " ; ".join(f"into {l['kind']} {l.get('number')} {l['id'][:8]} created {l['created_at'][:16]} "
                               f"tr={len(l.get('transcript') or '')}" for l in into) + f" | {t[:70]}", flush=True)
            print(f"@@PART {x['id']} " + " ".join(l["id"] for l in into), flush=True)
            for l in [x] + into:
                print(f"@@TR {l['id'][:8]} " + re.sub(r"\s+", " ", (l.get("transcript") or "")[:600]), flush=True)
                for h in re.findall(r"(?m)^#{1,2} (.+)$", l.get("chapter_md") or ""):
                    print(f"@@H {l['id'][:8]} {h[:90]}", flush=True)
    elif "--thin" in sys.argv:  # 27/11: chapters far shorter than their recording are written again in full
        # ("--thin <course|all> [dry]"); after a rewrite: the lecture's quiz and the lesson's exercises again
        import time
        key = sys.argv[sys.argv.index("--thin") + 1]
        dry = sys.argv[-1] == "dry"
        t0 = time.time()
        for c in s.table("courses").select("*").eq("archived", False).execute().data:
            if not (key == "all" or name_match(key, c["name"])) or SKIP_COURSES.search(c["name"] or "") or c.get("kind") in ("lab", "self"):
                continue
            ls = s.table("lessons").select("id, kind, number, title, status, transcript, chapter_md").eq("course_id", c["id"]) \
                .in_("kind", ["lecture", "practice"]).eq("status", "ready").execute().data
            for l in sorted(ls, key=lambda l: (l.get("number") or 0)):
                tr, ch = len(l.get("transcript") or ""), len(body_of(l.get("chapter_md") or ""))
                if (l.get("title") or "").startswith("📦") or tr < 15000 or ch >= 0.2 * tr:
                    continue
                print(f"::notice title=Thin::{c['name']} {l['kind']} {l.get('number')} {l['id'][:8]}: chapter {ch} / recording {tr}", flush=True)
                if dry or time.time() - t0 > 95 * 60:
                    continue
                try:
                    rewrite_lesson(s, l["id"])
                    full = s.table("lessons").select("*").eq("id", l["id"]).execute().data[0]
                    if l["kind"] == "lecture":
                        requiz(s, full)
                    reextract(s, c, full)
                except Exception as e:  # noqa: BLE001
                    print(f"::warning title=Thin::{l['id'][:8]}: {str(e)[:150]}", flush=True)
                    if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota"):
                        sys.exit(0)
    elif "--codefix" in sys.argv:  # 27/11: code that the math step wrapped as formulas -> fenced code again
        from google.genai import types
        CODEFIX = ("לפניך טקסט של תרגיל בקורס תכנות/מיקרו-בקרים. שלב עיבוד שגוי עטף שורות קוד (C/Java) כנוסחאות: "
                   "$...$, $$...$$ סביב קוד, נקודה-פסיק שנעלמה, \\& במקום &. שחזר: כל קטע קוד בבלוק ```c (או ```java) "
                   "שורה אחרי שורה כמו קוד אמיתי, בלי $ בתוך הקוד; קוד קצר בתוך משפט - `כך`. נוסחאות מתמטיות אמיתיות "
                   "נשארות ב-$. אל תשנה שום מילה אחרת, אל תקצר ואל תוסיף. החזר את כל הטקסט ב-text.")
        bad = re.compile(r"\$\$\s*\n[^$]*(;|uint\d+_t|\|=|&=|\^=|<<)[^$]*\n\$\$|printf\([^)]*\$|\$\\&=\$|\$[^$\n]*\\n\$")
        for c in s.table("courses").select("id, name").eq("archived", False).execute().data:
            if not re.search(r"Java|מיקרו|VLSI|SystemVerilog|תכנות", c["name"] or ""):
                continue  # 27/11: only programming courses - in waves / linear it turned formulas into "code"
            for e in s.table("exercises").select("id, question_md, solution_md").eq("course_id", c["id"]).execute().data:
                for f in ("question_md", "solution_md"):
                    v = e.get(f) or ""
                    if not bad.search(v):
                        continue
                    try:
                        out = author._generate_json([types.Part.from_text(text=v)], CODEFIX, FIXTEX_SCHEMA, "LOW")
                    except Exception as ex:  # noqa: BLE001
                        print(f"::warning title=Code fix::{e['id'][:8]}: {str(ex)[:120]}", flush=True)
                        continue
                    t = (out.get("text") or "").strip()
                    fences = re.findall(r"```[a-z]*\n(.*?)```", t, re.S)
                    ok = t and len(t) > 0.8 * len(v) and not bad.search(t) and not any("$" in b for b in fences)
                    if ok:
                        s.table("exercises").update({f: t}).eq("id", e["id"]).execute()
                    print(f"::notice title=Code fix::{c['name']} {e['id'][:8]} {f}: {'fixed' if ok else 'kept (check failed)'}", flush=True)
    elif "--completions" in sys.argv:  # 27/11: completions into their lectures ("--completions <course|all> [dry]")
        key = sys.argv[sys.argv.index("--completions") + 1]
        for x in s.table("courses").select("id, name").eq("archived", False).execute().data:
            if (key == "all" or name_match(key, x["name"])) and not SKIP_COURSES.search(x["name"] or ""):
                try:
                    merge_completions(s, x, dry=sys.argv[-1] == "dry")
                except Exception as e:  # noqa: BLE001
                    print(f"::warning title=Completion::{x['name']}: {str(e)[:150]}", flush=True)
                    if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota"):
                        break
    elif "--hollow" in sys.argv:  # 27/11: exercises whose solution only names the steps, solved again in full
        fix_hollow(s, sys.argv[sys.argv.index("--hollow") + 1], dry=sys.argv[-1] == "dry")
    elif "--quizfix" in sys.argv:  # 27/11: every lecture's quiz 10-12 questions, no quiz on a practice (every course)
        for c in s.table("courses").select("id, name, kind").eq("archived", False).execute().data:
            if c.get("kind") in ("lab",) or SKIP_COURSES.search(c["name"] or ""):
                continue
            ls = s.table("lessons").select("id, user_id, course_id, kind, number, title, status, chapter_md").eq("course_id", c["id"]) \
                .in_("kind", ["lecture", "practice"]).eq("status", "ready").execute().data
            n, k0 = {}, 0
            while True:  # paginated: a course can hold more than 1000 questions
                page = s.table("questions").select("id, lesson_id").eq("course_id", c["id"]).order("id").range(k0, k0 + 999).execute().data
                for q in page:
                    n[q["lesson_id"]] = n.get(q["lesson_id"], 0) + 1
                if len(page) < 1000:
                    break
                k0 += 1000
            for l in ls:
                k = n.get(l["id"], 0)
                if (l.get("title") or "").startswith("📦") or (l["kind"] == "lecture" and 10 <= k <= 12) or (l["kind"] == "practice" and not k):
                    continue
                try:
                    requiz(s, l)
                except Exception as e:  # noqa: BLE001
                    print(f"::warning title=Quiz::{c['name']} {l['kind']} {l.get('number')}: {str(e)[:150]}", flush=True)
                    if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota"):
                        sys.exit(0)
    elif "--place" in sys.argv:  # the "🧩" sections into their topics: one course, or every course when empty
        key = sys.argv[sys.argv.index("--place") + 1] if len(sys.argv) > sys.argv.index("--place") + 1 else ""
        for x in s.table("courses").select("id, name").eq("archived", False).execute().data:
            if (not key or name_match(key, x["name"])) and not SKIP_COURSES.search(x["name"] or ""):
                try:
                    place_old_audits(s, x["name"])
                except Exception as e:  # noqa: BLE001
                    print(f"::warning title=Place::{x['name']}: {str(e)[:150]}", flush=True)
    elif "--unmerge" in sys.argv:  # 27/11: undo a wrong merge. JSON {into, src, cut, src_kind, src_number, src_title,
        # move_ex_from: [lesson ids whose exercises go to src], hide: [{id, title}]}
        import json as _j
        ops = _j.loads(Path(sys.argv[sys.argv.index("--unmerge") + 1]).read_text(encoding="utf-8"))
        for op in (ops if isinstance(ops, list) else [ops]):
            if op.get("move_ex"):  # {"move_ex": from_id, "to": id}: a duplicate's exercises join the lesson that stays
                n = s.table("exercises").update({"lesson_id": op["to"]}).eq("lesson_id", op["move_ex"]).execute().data
                print(f"::notice title=Unmerge::{len(n)} exercises {op['move_ex'][:8]} -> {op['to'][:8]}", flush=True)
                continue
            if op.get("renumber"):  # {"renumber": id, "kind", "number"}: a lesson filed under the wrong number
                s.table("lessons").update({"kind": op["kind"], "number": op["number"]}).eq("id", op["renumber"]).execute()
                print(f"::notice title=Unmerge::{op['renumber'][:8]} -> {op['kind']} {op['number']}", flush=True)
                continue
            into = s.table("lessons").select("id, user_id, chapter_md").eq("id", op["into"]).execute().data[0]
            md = into["chapter_md"] or ""
            k = 1 if op.get("first") and op["cut"] in md else md.count(op["cut"])
            if k != 1:
                print(f"::error title=Unmerge::{op['into'][:8]}: cut marker found {k} times - skipped", flush=True)
                continue
            s.storage.from_("study").upload(f"{into['user_id']}/lessons/{into['id']}/chapter_before_unmerge.md", md.encode("utf-8"),
                                            {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
            s.table("lessons").update({"chapter_md": md.split(op["cut"])[0].rstrip().rstrip("-").rstrip()}).eq("id", into["id"]).execute()
            if op.get("src"):
                s.table("lessons").update({"kind": op["src_kind"], "number": op["src_number"], "title": op["src_title"]}).eq("id", op["src"]).execute()
            if op.get("src") and op.get("move_new_ex"):  # exercises the merge moved over: made after the part arrived
                since = op.get("since") or s.table("lessons").select("created_at").eq("id", op["src"]).execute().data[0]["created_at"]
                n = s.table("exercises").update({"lesson_id": op["src"]}).eq("lesson_id", into["id"]).gte("created_at", since).execute().data
                print(f"::notice title=Unmerge::{len(n)} exercises back to {op['src'][:8]}", flush=True)
            for lid in op.get("move_ex_from") or []:
                n = s.table("exercises").update({"lesson_id": op["src"]}).eq("lesson_id", lid).execute().data
                print(f"::notice title=Unmerge::{len(n)} exercises {lid[:8]} -> {op['src'][:8]}", flush=True)
            for h in op.get("hide") or []:
                s.table("lessons").update({"kind": "other", "number": None, "title": h["title"]}).eq("id", h["id"]).execute()
            print(f"::notice title=Unmerge::{op['into'][:8]} cut ({len(md)} -> {len(md.split(op['cut'])[0])}), "
                  f"{(op.get('src') or '-')[:8]} restored as {op.get('src_kind')} {op.get('src_number')}", flush=True)
    elif "--replace" in sys.argv:  # exact text replacements Claude checked: JSON [{"id": lesson, "find": ..., "repl": ...}]
        import json as _j
        for f in _j.loads(Path(sys.argv[sys.argv.index("--replace") + 1]).read_text(encoding="utf-8")):
            md = (s.table("lessons").select("chapter_md").eq("id", f["id"]).execute().data or [{}])[0].get("chapter_md") or ""
            k = md.count(f["find"])
            if f.get("all") and k > 1:
                k = 1
            if k == 1:
                s.table("lessons").update({"chapter_md": md.replace(f["find"], f["repl"])}).eq("id", f["id"]).execute()
            print(f"::notice title=Replace::{f['id'][:8]}: {'done' if k == 1 else f'NOT DONE ({k} matches)'}", flush=True)
    elif "--textsym" in sys.argv:  # 27/11: every text field of every course without "\\text{\\symbol}" (shown red)
        n = 0
        for tb, cols in (("lessons", ["chapter_md", "summary_md"]), ("exercises", ["question_md", "solution_md"]),
                         ("questions", ["question", "explanation", "options"])):
            rows, k = [], 0
            while True:  # past the API's 1000-row page
                got = s.table(tb).select("id, " + ", ".join(cols)).order("id").range(k, k + 999).execute().data
                rows += got
                k += 1000
                if len(got) < 1000:
                    break
            print(f"::notice title=Text symbols::{tb}: {len(rows)} rows read", flush=True)
            for r in rows:
                upd = {}
                for f in cols:
                    v = r.get(f)
                    new = [author.fix_text_symbols(o) for o in v] if isinstance(v, list) else author.fix_text_symbols(v) if v else v
                    if new != v:
                        upd[f] = new
                if upd:
                    s.table(tb).update(upd).eq("id", r["id"]).execute()
                    n += 1
        print(f"::notice title=Text symbols::{n} rows fixed", flush=True)
    elif "--audit" in sys.argv:  # 27/11: per lesson - quiz size, exercises, code blocks, red formulas, Greek spelled out
        import json as _j
        import weekset
        GREEK = re.compile(r"(?<![\\a-zA-Z])(gamma|theta|alpha|beta|lambda|omega|delta|sigma|epsilon|varepsilon|eta|mu|phi|psi|rho|tau|"
                           r"Gamma|Omega|Delta)(?![a-zA-Z])|גמא|תטא|אלפא|למדא|אומגה|דלתא|סיגמא|אפסילון")
        for c in s.table("courses").select("*").execute().data:
            if not name_match(sys.argv[sys.argv.index("--audit") + 1], c["name"]):
                continue
            ls = s.table("lessons").select("id, kind, number, title, status, chapter_md").eq("course_id", c["id"]).execute().data
            ls = [l for l in ls if not (l.get("title") or "").startswith("📦")]
            qn = {}
            for q in s.table("questions").select("lesson_id").eq("course_id", c["id"]).execute().data:
                qn[q["lesson_id"]] = qn.get(q["lesson_id"], 0) + 1
            en = {}
            for e in s.table("exercises").select("lesson_id").eq("course_id", c["id"]).execute().data:
                en[e["lesson_id"]] = en.get(e["lesson_id"], 0) + 1
            errs = render_errors([l.get("chapter_md") or "" for l in ls]) or [[] for _ in ls]
            for l, e in sorted(zip(ls, errs), key=lambda z: (z[0].get("number") or 99, z[0]["kind"])):
                md = l.get("chapter_md") or ""
                langs = re.findall(r"(?m)^```(\w*)", md)[::2]
                print("@@A " + _j.dumps({"id": l["id"], "kind": l["kind"], "n": l.get("number"), "title": (l.get("title") or "")[:60],
                      "len": len(md), "quiz": qn.get(l["id"], 0), "ex": en.get(l["id"], 0), "code": langs,
                      "red": len(e), "red_sample": e[:3], "greek": len(GREEK.findall(md)),
                      "greek_sample": list({m.group(0) for m in GREEK.finditer(md)})[:8]}, ensure_ascii=False), flush=True)
            try:
                ws = weekset.load(s, c) if hasattr(weekset, "load") else None
            except Exception as ex:  # noqa: BLE001
                ws = str(ex)[:100]
            print("@@W " + _j.dumps(ws, ensure_ascii=False)[:6000], flush=True)
    elif "--extra-clean" in sys.argv:  # one pass over chapters that got extra material before clean_marks existed
        for l in s.table("lessons").select("id, chapter_md").like("chapter_md", "%📎 מחומר הקורס%").execute().data:
            new = clean_marks(l["chapter_md"])
            if new != l["chapter_md"]:
                s.table("lessons").update({"chapter_md": new}).eq("id", l["id"]).execute()
                print(f"::notice title=Extra::{l['id'][:8]}: marks cleaned ({l['chapter_md'].count('📎')} -> {new.count('📎')})", flush=True)
    elif "--extra" in sys.argv:  # 27/11: extra material into its lecture ("--extra dry" = only the plan)
        merge_extra_all(s, dry=sys.argv[-1] == "dry")
    elif "--toopen" in sys.argv:  # 27/11: open-exam course -> its multiple-choice exercises become open ones
        for x in s.table("courses").select("id, name, exam_type").execute().data:
            if name_match(sys.argv[sys.argv.index("--toopen") + 1], x["name"]) and x.get("exam_type") == "mixed":
                balance_mixed(s, x)  # micro: half multiple choice, half open
            elif name_match(sys.argv[sys.argv.index("--toopen") + 1], x["name"]) and x.get("exam_type") == "open":
                for _ in range(3):  # a round that kept some (cut / no answer) is tried again
                    d, t = to_open(s, x)
                    if d == t or d == 0:
                        break
    elif "--status" in sys.argv:  # 25/11: what is still missing per course + the repair jobs left (read only)
        st = load(s)
        cs = s.table("courses").select("id, name").execute().data
        for name, until in SCHEDULE:
            c = [x for x in cs if name_match(name, x["name"])]
            if c:
                print(f"::notice title=Status::{name} ({until[:10]}): {'; '.join(missing_for(s, c[0], st)) or 'ready'}", flush=True)
        print(f"::notice title=Status::focus = {st.get('focus')}", flush=True)
        for x in s.table("courses").select("id, name, exam_type").eq("archived", False).execute().data:
            if SKIP_COURSES.search(x["name"] or ""):
                continue
            ex = s.table("exercises").select("question_md, solution_md").eq("course_id", x["id"]).eq("source", "lesson") \
                .is_("done_at", "null").execute().data
            bad = [e for e in ex if (x.get("exam_type") == "mcq" and not MCQ_SHAPE.search(e["question_md"] or ""))
                   or "הנוסחה" not in (e.get("solution_md") or "")]
            if x.get("exam_type") == "open":
                allq = s.table("exercises").select("question_md, solution_md, done_at").eq("course_id", x["id"]).execute().data
                mc = [e for e in allq if is_mcq(e)]
                print(f"::notice title=Exercises::{x['name']}: {len(mc)} multiple-choice exercises in an OPEN-exam course "
                      f"({sum(1 for e in mc if e['done_at'])} of them marked done)", flush=True)
            print(f"::notice title=Exercises::{x['name']} ({x.get('exam_type') or 'open'}): {len(bad)} of {len(ex)} open "
                  f"exercises not yet in the exam's format / without the formula", flush=True)
            unv = [e for e in ex if "⚠️ הפתרון לא אומת" in (e.get("solution_md") or "")]
            print(f"::notice title=Exercises::{x['name']}: {len(unv)} answers marked unverified (⚠️)", flush=True)
        import queue_runner
        for r, mode in queue_runner.candidates(s):
            if r["status"] != "ready":
                print(f"::notice title=Waiting lesson::{r['id']} {r['kind']} {r['status']} {mode} upd={r['updated_at'][:16]} "
                      f"{(r.get('error') or '')[:150]} | {(r.get('progress') or '')[:80]}", flush=True)
        for l in s.table("lessons").select("id, kind, number, title, status, error, updated_at").in_(
                "status", ["queued", "processing", "transcribed", "error"]).execute().data:
            print(f"::notice title=Busy lesson::{l['id']} {l['kind']} {l.get('number')} {(l.get('title') or '')[:30]} "
                  f"{l['status']} {l['updated_at'][:16]} {(l.get('error') or '')[:120]}", flush=True)
        for j in st.get("pending") or []:
            print(f"::notice title=Pending::{j.get('course')}: {', '.join(k for k in j if not k.startswith('_') and k != 'course')}"
                  f"{' (skip ' + ','.join(j['_skip']) + ')' if j.get('_skip') else ''}", flush=True)
    elif "--focus" in sys.argv:  # --focus "<part of a course name>" | --focus "" (all)
        st = load(s)
        st["focus"] = sys.argv[sys.argv.index("--focus") + 1] or None
        save(s, st)
        print(f"::notice title=Focus::{st['focus'] or 'all courses'}", flush=True)
    elif "--drop-videos" in sys.argv:  # his request 23/11/2026: waiting / failed videos of a course are dropped
        name = sys.argv[sys.argv.index("--drop-videos") + 1]
        ids = [c["id"] for c in s.table("courses").select("id, name").execute().data if name_match(name, c["name"])]
        rows = s.table("lesson_media").select("id").in_("course_id", ids).neq("status", "ready").execute().data
        for r in rows:
            s.table("lesson_media").delete().eq("id", r["id"]).execute()
        print(f"::notice title=Videos dropped::{name}: {len(rows)} waiting videos removed", flush=True)
    elif "--restore" in sys.argv:  # a lesson's chapter from before the coverage rewrite (when that one was longer)
        lid = sys.argv[sys.argv.index("--restore") + 1]
        name = BACKUP
        if ":" in lid:  # "<id>:<backup file>" (e.g. chapter_before_trim.md)
            lid, name = lid.split(":", 1)
        l = s.table("lessons").select("id, user_id, chapter_md").eq("id", lid).execute().data[0]
        old = s.storage.from_(BUCKET).download(f"{l['user_id']}/lessons/{lid}/{name}").decode()
        if len(old) > len(l["chapter_md"] or ""):
            s.storage.from_(BUCKET).upload(f"{l['user_id']}/lessons/{lid}/chapter_rewrite_shorter.md", (l["chapter_md"] or "").encode(),
                                           {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
            s.table("lessons").update({"chapter_md": old}).eq("id", lid).execute()
            st = load(s)
            st.setdefault("audited", {}).pop(lid, None)
            save(s, st)
            print(f"::notice title=Restore::{lid[:8]}: {len(l['chapter_md'] or '')} -> {len(old)} chars (audit again)", flush=True)
    elif "--explode" in sys.argv:
        explode_all(s)
    elif "--dedupe" in sys.argv:
        dedupe_all(s)
    elif "--list" in sys.argv:
        for l, c, t in todo(s, load(s)):
            print(c["name"][:20], l["kind"], l["number"], "read" if l.get("read_at") else "unread", "->", (t or {}).get("title", "rewrite")[:30])
    else:
        for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1):
            if not step(s):
                break
