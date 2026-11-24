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


def load(sb):
    """The state, read once per process: storage downloads can be served stale (22/11/2026 the first run read an old
    copy between steps and wrote lecture 3's completions twice)."""
    if "st" not in _CACHE:
        try:
            _CACHE["st"] = json.loads(sb.storage.from_(BUCKET).download(STATE).decode())
        except Exception:  # noqa: BLE001
            _CACHE["st"] = {"done": {}}
    return _CACHE["st"]


def save(sb, st, keys=None):
    """keys: a writer outside the queue (a lesson being processed) updates only these keys on a fresh copy, so it never
    overwrites the queue's list of repairs (23-24/11/2026 the night's list was lost that way)."""
    if keys:
        try:
            fresh = json.loads(sb.storage.from_(BUCKET).download(STATE).decode())
        except Exception:  # noqa: BLE001
            fresh = {}
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


def audit(sb, lesson, course, chapter_md):
    """His rule 23/11/2026: no detail of a lecture / practice may be missing. Every part of the recording is compared
    with the finished chapter (the MISSING prompt) and whatever is missing is added to the SAME chapter, before he
    reads it. Returns (chapter, questions)."""
    md, qs = write(sb, lesson, course, chapter=body_of(chapter_md))
    if len(md.strip()) < 200:
        return chapter_md, []  # nothing missing: no extra questions either
    body, _, ver = chapter_md.partition(VERIFY_SPLIT)
    add = (f"\n\n{AUDIT_HEAD}\n\n> 📌 מה שנאמר או נכתב בשיעור ולא נכנס לפרק למעלה. זה חלק מהחומר - ללמוד גם אותו.\n\n"
           + author.normalize_math(md))
    return body.rstrip() + add + (VERIFY_SPLIT + ver if ver else ""), qs


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
    f = st.get("focus")
    return {k: c for k, c in courses.items() if f in (c["name"] or "")} if f else courses


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
                elif nxt:  # nothing unread after it yet: waits for his next upload
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
        j = jobs[0]
        if j.get("boards"):  # every board block against its snapshot
            board_check_course(sb, j["course"])
            j.pop("boards")
        elif j.get("fix"):  # completions: one per week, trimmed, quiz/exercises redone
            fix_course(sb, j["course"])
            j.pop("fix")
        elif j.get("rewrite"):
            rewrite_lesson(sb, j["rewrite"])
            j.pop("rewrite")
        else:
            if j.get("weeks"):
                refresh_weeks(sb, j["course"], j["weeks"])
            st["pending"].remove(j)
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
            add_questions(sb, l, course, qs)
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
            add_questions(sb, l, course, qs)
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
    f = load(sb).get("focus")
    if f and not any(f in (c["name"] or "") for c in sb.table("courses").select("name").eq("id", l["course_id"]).execute().data):
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
  פתרון מלא צעד אחרי צעד. מבחן אמריקאי - התרגיל הוא שאלה אמריקאית ברמת מבחן שנפתרת בלחיצה: בסוף question_md
  4 אפשרויות, כל אחת בפסקה משלה בדיוק כך: **א.** ... / **ב.** ... / **ג.** ... / **ד.** ...; ה-solution_md מתחיל בשורה
  "התשובה: **X**" (X = האות הנכונה) ואחריה הפתרון המלא צעד אחרי צעד ולמה כל אחת מהאחרות שגויה; מבחן פתוח - שאלה פתוחה
  עם סעיפים.
אל תמציא חומר שלא בפרק. פתור כל שאלה ותרגיל מחדש לפני שאתה כותב את התשובה."""

EXAM = {"mcq": "אמריקאי", "open": "שאלות פתוחות", "mixed": "משולב: אמריקאי ופתוח"}


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
    return DRILL.replace("{exam}", EXAM.get(e or "", "שאלות פתוחות"))


DRILL_SCHEMA = {"type": "object", "properties": {
    "questions": SCHEMA["properties"]["questions"],
    "exercises": {"type": "array", "items": {"type": "object", "properties": {
        "title": {"type": "string"}, "question_md": {"type": "string"}, "solution_md": {"type": "string"},
        "topic": {"type": "string"}}, "required": ["question_md", "solution_md"]}}},
    "required": ["questions", "exercises"]}


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
    return "\n".join(MATHRUN.sub(one, line) if not line.lstrip().startswith("```") else line for line in s.split("\n"))


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
    if more and st.get("focus"):  # only the focused course's
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
        if d["title"] == l["title"] and d["course"] in courses[l["course_id"]]["name"]:
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
    busy = [l for l in ls if l["status"] in ("queued", "processing", "transcribed", "error")]
    if busy:
        out.append(f"{len(busy)} שיעורים בעיבוד")
    cov = [j for j in todo(sb, {"done": st.get("done", {})}) if j[1]["id"] == course["id"]]
    if cov:
        out.append(f"{len(cov)} השלמות בכתיבה")
    if any(course["name"] and j.get("course") and j["course"] in course["name"] for j in st.get("pending") or []):
        out.append("תיקוני שאלונים, השלמות ותרגילים")
    units = [l for l in ls if l["kind"] == "other" and (l.get("title") or "").startswith("🔁 השלמה")]
    nodrill = [u for u in units if u["id"] not in st.get("drill", {})]
    if nodrill:
        out.append(f"{len(nodrill)} שאלונים ותרגילים")
    week = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
    want = units + [l for l in ls if l["kind"] == "lecture" and l["status"] == "ready" and l["created_at"] >= week
                    and hub.AUTO_STUDIO.search(course["name"] or "")
                    and not (l.get("transcript") or "").startswith(hub.course_site.SITE_NOTE)]
    if want:
        ready = {i for m in sb.table("lesson_media").select("lesson_ids").eq("kind", "video").eq("status", "ready")
                 .eq("course_id", course["id"]).execute().data for i in (m.get("lesson_ids") or [])}
        novid = [l for l in want if l["id"] not in ready]
        if novid:
            out.append(f"{len(novid)} סרטונים")
    return out


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
    ids = [c["id"] for c in sb.table("courses").select("id, name").execute().data if name in (c["name"] or "")]
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
    ids = [c["id"] for c in sb.table("courses").select("id, name").execute().data if name in (c["name"] or "")]
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
    out = author._generate_json([types.Part.from_text(text=body_of(l.get("chapter_md") or ""))], QUIZ, QUIZ_SCHEMA, "MEDIUM")
    new = [q for q in out.get("questions") or [] if len(q.get("options") or []) >= 2 and 0 <= q.get("correct", -1) < len(q["options"])]
    for q in new:
        q["question"], q["explanation"] = wrap_math(q.get("question") or ""), wrap_math(q.get("explanation") or "")
        q["options"] = [wrap_math(o) for o in q["options"]]
    add_questions(sb, l, {"id": l["course_id"]}, new)
    print(f"::notice title=Quiz::lecture {l.get('number')} {(l.get('title') or '')[:20]}: {len(qs)} -> {len(new) + len(answered)} questions", flush=True)


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
    c = [x for x in sb.table("courses").select("id, name, user_id, exam_type").execute().data if name in (x["name"] or "")][0]
    for l in (sb.table("lessons").select("id, user_id, course_id, kind, number, title, topics, chapter_md, transcript, read_at")
              .eq("course_id", c["id"]).in_("number", weeks).in_("kind", ["lecture", "practice"]).execute().data):
        if (l.get("title") or "").startswith("📦"):
            continue
        requiz(sb, l)
        reextract(sb, c, l)
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
SCHEDULE = [("מעגלים ספרתיים", "2026-11-24T20:00:00+02:00"), ("Java", "2026-11-25T14:00:00+02:00"),
            ("מיקרו", "2026-11-25T23:00:00+02:00"), ("מעגלים לינאריים", "2026-11-26T14:00:00+02:00"),
            ("אותות אקראיים", "2026-11-26T23:00:00+02:00"), ("גלים", "2026-11-28T20:00:00+02:00"),
            ("מבוא למערכות תקשורת", "2026-11-29T20:00:00+02:00")]


def plan_focus(sb):
    """The course to work on now: the first one in SCHEDULE whose deadline has not passed and that still has work."""
    from zoneinfo import ZoneInfo
    st = load(sb)
    now = datetime.now(ZoneInfo("Asia/Jerusalem"))
    courses = sb.table("courses").select("id, name, user_id").execute().data
    prev = st.get("focus")
    focus = None
    for name, until in SCHEDULE:
        if now >= datetime.fromisoformat(until):
            continue
        c = [x for x in courses if name in (x["name"] or "")]
        if c and missing_for(sb, c[0], st):
            focus = name
            break
    st["focus"] = focus
    save(sb, st)
    if prev and prev != focus:
        try:  # he hears where things stand (23/11/2026)
            import notify
            c = [x for x in courses if prev in (x["name"] or "")]
            if c:
                left = missing_for(sb, c[0], st)
                nxt = next((x["name"] for x in courses if focus and focus in (x["name"] or "")), "רק הרצאות חדשות")
                notify.send(sb, c[0]["user_id"], f"{'⏭️' if left else '✅'} {c[0]['name']}: {'הזמן נגמר' if left else 'מוכן'}",
                            (f"נשאר: {', '.join(left)}. " if left else "") + f"עכשיו: {nxt}")
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Plan push::{str(e)[:150]}", flush=True)
        print(f"::notice title=Plan::now working on {focus}", flush=True)
    return focus


def _mine(st, j):
    f = st.get("focus") or ""
    if not f:  # no focus (after the week's schedule): every pending repair may run
        return True
    return bool(f) and (f in j["course"] or j["course"] in f)


def pending_for_next_day(sb):
    """His priority is by days (23/11/2026): repairs for the course he studies next run BEFORE anything else (a new
    upload of a later course waits). Returns True if one was done."""
    st = load(sb)
    jobs = st.get("pending") or []
    if not jobs:
        return False
    plan_focus(sb)
    mine = [j for j in jobs if _mine(st, j)]
    if not mine:
        return False
    j = mine[0]
    if j.get("boards"):
        board_check_course(sb, j["course"])
        j.pop("boards")
        what = "כל בלוקי 'מה כתוב בלוח' נבדקו מול הצילומים"
    elif j.get("fix"):
        fix_course(sb, j["course"])
        j.pop("fix")
        what = "ההשלמות קוצרו וקיבלו שאלון ותרגילים חדשים"
    elif j.get("rewrite"):
        rewrite_lesson(sb, j["rewrite"])
        j.pop("rewrite")
        what = "פרק קצר נכתב מחדש"
    else:
        if j.get("weeks"):
            refresh_weeks(sb, j["course"], j["weeks"])
        st["pending"].remove(j)
        what = f"שאלונים ותרגילים של שבועות {', '.join(map(str, j['weeks']))} סודרו"
    save(sb, st)
    progress_push(sb, what)
    return True


def trim_quiz(sb, name, keep=15):
    """Without Gemini (plan B, 23/11/2026): a lecture keeps the quiz written with its chapter (the first batch) plus
    whatever he answered, up to `keep`; the questions piled up by rewrites / audits go. A practice keeps only answered
    ones (no quiz on practices). Gemini's requiz replaces this later when it can."""
    c = [x for x in sb.table("courses").select("id, name").execute().data if name in (x["name"] or "")][0]
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
    c = [x for x in sb.table("courses").select("id, name").execute().data if name in (x["name"] or "")][0]
    for l in (sb.table("lessons").select("id, user_id, course_id, kind, number, title, chapter_md").eq("course_id", c["id"])
              .eq("status", "ready").execute().data):
        if done.get(l["id"]) or (l.get("title") or "").startswith("📦"):
            continue
        board_check(sb, l)
        done[l["id"]] = 1
        save(sb, st)


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
        job = json.loads(sys.argv[sys.argv.index("--pending") + 1])
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
    elif "--fix-course" in sys.argv:
        fix_course(s, sys.argv[sys.argv.index("--fix-course") + 1])
    elif "--redrill" in sys.argv:  # "<course>|הרצאה 1,הרצאה 2"
        name, only = sys.argv[sys.argv.index("--redrill") + 1].split("|", 1)
        ids = [c["id"] for c in s.table("courses").select("id, name").execute().data if name in (c["name"] or "")]
        for u in s.table("lessons").select("id, user_id, course_id, title, chapter_md").in_("course_id", ids).like("title", "🔁 השלמה%").execute().data:
            if any(u["title"] == f"🔁 השלמה ל{x.strip()}" for x in only.split(",")):
                redrill(s, u)
    elif "--trim" in sys.argv:  # completions without what he already read / solved (23/11/2026)
        arg = sys.argv[sys.argv.index("--trim") + 1]  # "<course>" or "<course>|הרצאה 2,הרצאה 3"
        trim_course(s, *arg.split("|", 1))
    elif "--focus" in sys.argv:  # --focus "<part of a course name>" | --focus "" (all)
        st = load(s)
        st["focus"] = sys.argv[sys.argv.index("--focus") + 1] or None
        save(s, st)
        print(f"::notice title=Focus::{st['focus'] or 'all courses'}", flush=True)
    elif "--drop-videos" in sys.argv:  # his request 23/11/2026: waiting / failed videos of a course are dropped
        name = sys.argv[sys.argv.index("--drop-videos") + 1]
        ids = [c["id"] for c in s.table("courses").select("id, name").execute().data if name in (c["name"] or "")]
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
