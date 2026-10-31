"""Exercises from course files: homework, past exams and exercise sheets -> the `exercises` table, with solutions.

  python exercises.py              every course, files not read yet (stops politely on the Gemini quota)
  python exercises.py <course_id>  one course

Each file is read once (rows keep material_id). A solution file ("פתרון ...") with the same number is sent along,
so the official solution is used when there is one; otherwise Gemini solves and a second pass re-solves every one.
"""
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

import author
import media

BUCKET = "study"
BUDGET_SEC = 40 * 60
INLINE_LIMIT = 18 * 1024 * 1024
FILE_TYPES = re.compile(r"\.(pdf|png|jpe?g|webp)$", re.I)
EXAM = re.compile(r"מבחן|מועד|בוחן|exam|quiz", re.I)
HOMEWORK = re.compile(r"מטלה|עבודת בית|תרגיל בית|שיעורי בית|homework|\bhw\b|assignment", re.I)
SHEET = re.compile(r"תרגיל|תרגול|חוברת|שאלות|דף עבודה|exercise|problem|tutorial|worksheet", re.I)
SOLUTION = re.compile(r"פתרון|פתרונות|solution", re.I)

PROMPT = """הקובץ המצורף הוא {kind} בקורס "{course}" (הנדסת חשמל). הסטודנט לומד מפתרון תרגילים בעצמו.
הוצא את **כל** התרגילים / השאלות בקובץ, לפי הסדר (כל סעיף כחלק מהשאלה שלו, לא כתרגיל נפרד):
- title: כותרת קצרה (למשל "שאלה 2 - מגבר משוב").
- question_md: הנוסח המלא בעברית (מונחים באנגלית בסוגריים), עם כל הנתונים והסעיפים. שרטוט/מעגל - תאר במילים בדיוק
  (רכיבים, ערכים, איך מחוברים). כל ביטוי מתמטי בתוך $...$, ומשוואה מלאה בשורה נפרדת $$...$$ - אף פעם לא LaTeX בלי $.
- solution_md: פתרון מלא שלב אחרי שלב לכל סעיף, עם ההסבר למה, כל ההצבות והתשובה הסופית ביחידות.
  אם צורף קובץ פתרון רשמי - לפיו (ותקן טעויות עם > ⚠️). אם אין - פתור בעצמך.
- topic: הנושא של התרגיל. אם הוא מתאים לאחד מהנושאים שנלמדו בקורס (ברשימה למטה) - כתוב אותו בדיוק כמו ברשימה.
- exam_style: true אם זה ממבחן או שכתוב שזה בסגנון מבחן. uncertain: true אם אינך בטוח בפתרון.
נושאים שנלמדו בקורס עד עכשיו: {topics}"""

CHECK = """אתה בודק קפדן בהנדסת חשמל. לפניך תרגילים שהוצאו מהקובץ המצורף, עם פתרונות.
פתור כל תרגיל מחדש מאפס בלי להסתכל על הפתרון, והשווה. תקן כל טעות (הצבה, חישוב, יחידות, תשובה סופית), וודא שבנוסח יש
את כל הנתונים מהקובץ. פתרון שאינך בטוח בו - uncertain=true. אל תשמיט תרגילים. החזר את כל הרשימה המתוקנת."""

SCHEMA = {"type": "object", "properties": {"exercises": {"type": "array", "items": author.EXERCISE}}, "required": ["exercises"]}


def db():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def _read_path(course):
    return f"{course['user_id']}/materials/{course['id']}/exercises_read.json"


def read_list(sb, course):
    """Files already read for exercises (also those that had none)."""
    try:
        return set(json.loads(sb.storage.from_(BUCKET).download(_read_path(course)).decode()))
    except Exception:  # noqa: BLE001 - none read yet
        return set()


def mark_read(sb, course, material_id):
    ids = sorted(read_list(sb, course) | {material_id})
    sb.storage.from_(BUCKET).upload(_read_path(course), json.dumps(ids).encode(),
                                    {"content-type": "application/json", "upsert": "true"})


def source_of(m):
    title = m["title"] or ""
    if m.get("kind") == "past_exam" or EXAM.search(title):
        return "exam"
    if HOMEWORK.search(title):
        return "homework"
    return "sheet"


SLIDES = re.compile(r"הרצאה|שיעור|lecture|\blec\b|slides|מצגת", re.I)
NOT_EXERCISES = re.compile(r"syllabus|סילבוס|דוח|report|הנחיות|נוסחאות|formula|datasheet|manual|pinout|guide", re.I)


def wanted(m):
    """Files that hold exercises: homework, past exams, exercise sheets, and lecture slides (their worked examples).
    Not the syllabus, reports, formula sheets, datasheets, code or a solution file on its own."""
    title = m["title"] or ""
    if not (FILE_TYPES.search(title) or m["storage_path"].startswith("drive:")) or SOLUTION.search(title) or NOT_EXERCISES.search(title):
        return False
    return (m.get("kind") in ("past_exam", "solution", "slides")
            or bool(EXAM.search(title) or HOMEWORK.search(title) or SHEET.search(title) or SLIDES.search(title)))


def solution_for(m, materials):
    """"פתרון מטלה 2" for "מטלה 2" (same number, or the same name with פתרון)."""
    nums = re.findall(r"\d+", m["title"] or "")
    stem = re.sub(r"\.\w+$", "", m["title"] or "").strip()
    for s in materials:
        t = s["title"] or ""
        if s["id"] != m["id"] and SOLUTION.search(t) and (stem in t or (nums and re.findall(r"\d+", t)[:1] == nums[:1]
                                                                          and source_of(s) == source_of(m))):
            return s
    return None


def blob(sb, m, work):
    path = m["storage_path"]
    if path.startswith("drive:"):
        f = media.download_drive(f"https://drive.google.com/file/d/{path[6:]}/view", work)
        return Path(f).read_bytes(), media.mime_of(f)
    data = sb.storage.from_(BUCKET).download(path)
    return data, m.get("mime") or media.mime_of(path)


def gen(parts, system):
    return author.validate(author._generate_json(parts, system, SCHEMA, "MEDIUM")).get("exercises") or []


def read_file(sb, course, m, materials, topics, work):
    from google.genai import types
    data, mime = blob(sb, m, work)
    if len(data) > INLINE_LIMIT:
        print(f"::warning title=Exercises::{m['title']} is over 18 MB - skipped", flush=True)
        return []
    kind = {"exam": "מבחן קודם", "homework": "מטלת בית", "sheet": "דף תרגילים"}[source_of(m)]
    if source_of(m) == "sheet" and (m.get("kind") == "slides" or SLIDES.search(m["title"] or "")) and not SHEET.search(m["title"] or ""):
        kind = "מצגת הרצאה - הוצא את הדוגמאות הפתורות והתרגילים שבשקפים (לא את ההסברים)"
    parts = [types.Part.from_text(text=PROMPT.format(kind=kind, course=course["name"], topics=", ".join(topics) or "-")),
             types.Part.from_bytes(data=data, mime_type=mime)]
    sol = solution_for(m, materials)
    if sol:
        sdata, smime = blob(sb, sol, work)
        if len(sdata) + len(data) < INLINE_LIMIT:
            parts += [types.Part.from_text(text="קובץ הפתרון הרשמי:"), types.Part.from_bytes(data=sdata, mime_type=smime)]
    found = gen(parts, None)
    if found:
        checked = gen(parts + [types.Part.from_text(text="=== התרגילים לבדיקה ===\n" + json.dumps(found, ensure_ascii=False))], CHECK)
        if len(checked) >= len(found):
            found = checked
    return found


LESSON_PROMPT = """לפניך שיעור ({kind}) בקורס "{course}" - הפרק שנכתב עליו ותמלול ההקלטה. הסטודנט לומד מפתרון תרגילים בעצמו.
הוצא את **כל** התרגילים, הדוגמאות המספריות, השאלות וההוכחות שנפתרו או ניתנו בשיעור, לפי הסדר:
- title: כותרת קצרה. question_md: נוסח מלא שאפשר לפתור בלי ההקלטה - כל הנתונים, ושרטוט/מעגל מתואר במילים.
- solution_md: פתרון מלא שלב אחרי שלב (לפי הדרך של המרצה אם פתר; אחרת פתור), עם ההצבות והתשובה ביחידות.
- topic: אחד מהנושאים של השיעור: {topics}. exam_style: true אם נאמר שזה בסגנון מבחן. uncertain: true אם אינך בטוח.
כל ביטוי מתמטי בתוך $...$, ומשוואה מלאה בשורה נפרדת $$...$$ - אף פעם לא LaTeX בלי $. אם לא היו תרגילים - רשימה ריקה."""


def from_lessons(sb, course, budget_end):
    """Lessons written before summaries came with exercises (30/10/2026): read their exercises once."""
    from google.genai import types
    read = read_list(sb, course)
    have = {r["lesson_id"] for r in sb.table("exercises").select("lesson_id").eq("course_id", course["id"])
            .not_.is_("lesson_id", "null").execute().data}
    lessons = (sb.table("lessons").select("id, user_id, kind, number, title, topics, chapter_md, transcript")
               .eq("course_id", course["id"]).eq("status", "ready").in_("kind", ["lecture", "practice"])
               .order("created_at").execute().data)
    for l in lessons:
        # "lesson:" marks before 31/10/2026 were also written for lessons that gave none: those get one more try.
        retry_zero = f"lesson:{l['id']}" in read and f"lesson0:{l['id']}" not in read and l["id"] not in have
        if l["id"] in have or (f"lesson:{l['id']}" in read and not retry_zero):
            continue
        if retry_zero:
            read.add(f"lesson0:{l['id']}")
            mark_read(sb, course, f"lesson0:{l['id']}")
        if time.time() > budget_end:
            return False
        kind = f"{'תרגול' if l['kind'] == 'practice' else 'הרצאה'} {l.get('number') or ''}".strip()
        text = f"=== הפרק ===\n{(l.get('chapter_md') or '')[:60000]}\n\n=== התמלול ===\n{(l.get('transcript') or '')[:120000]}"
        parts = [types.Part.from_text(text=LESSON_PROMPT.format(kind=kind, course=course["name"],
                                                               topics=", ".join(l.get("topics") or []) or "-")),
                 types.Part.from_text(text=text)]
        try:
            found = gen(parts, None)
            if found:
                checked = gen(parts + [types.Part.from_text(text="=== התרגילים לבדיקה ===\n" + json.dumps(found, ensure_ascii=False))], CHECK)
                if len(checked) >= len(found):
                    found = checked
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Exercises {course['name']} {kind}::{str(e)[:300]}", flush=True)
            if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota", "המכסה"):
                raise
            continue
        rows = [{"user_id": course["user_id"], "course_id": course["id"], "lesson_id": l["id"], "source": "lesson",
                 "ord": i, "title": x.get("title"), "question_md": x["question_md"], "solution_md": x.get("solution_md"),
                 "topic": x.get("topic"), "exam_style": bool(x.get("exam_style")), "uncertain": bool(x.get("uncertain"))}
                for i, x in enumerate(found)]
        if rows:
            sb.table("exercises").insert(rows).execute()
        elif f"lesson0:{l['id']}" not in read:
            mark_read(sb, course, f"lesson0:{l['id']}")  # none found: one more try on the next run
            print(f"::notice title=Exercises::{course['name']} / {kind}: none found - will try once more", flush=True)
            continue
        mark_read(sb, course, f"lesson:{l['id']}")
        print(f"::notice title=Exercises::{course['name']} / {kind}: {len(rows)} from the lesson", flush=True)
    return True


ASSIGN = """לפניך השיעורים שנלמדו עד עכשיו בקורס "{course}" (לפי הסדר, עם מה שנלמד בכל אחד), התרגילים שנפתרו בכיתה,
ותרגילים מקבצים (שיעורי בית, מבחנים קודמים, חוברות). לכל תרגיל מקובץ קבע:
- lesson: המספר (מהרשימה) של השיעור **המוקדם ביותר** שאחריו אפשר לפתור את התרגיל **כולו** - כל סעיף, כל נושא שהוא דורש
  נלמד בשיעור הזה או לפניו. היה מחמיר: אם חסר נושא אחד שעוד לא נלמד - 0 ("עוד לא"). מבחן שלם / עבודת בית על נושא
  מאוחר - 0. בתחילת הסמסטר רוב התרגילים צריכים להיות 0.
- duplicate: true אם זה אותו תרגיל (אותם נתונים ושאלה) כמו אחד שנפתר בכיתה.
החזר את כל התרגילים, לפי id."""

ASSIGN_SCHEMA = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "id": {"type": "integer"}, "lesson": {"type": "integer"}, "duplicate": {"type": "boolean"}},
    "required": ["id", "lesson", "duplicate"]}}}, "required": ["items"]}


def assign(sb, course):
    """File exercises not placed yet -> the earliest lesson after which each can be fully solved (or not yet)."""
    from google.genai import types
    try:
        todo = (sb.table("exercises").select("id, title, question_md").eq("course_id", course["id"])
                .is_("lesson_id", "null").is_("fits_lesson_id", "null").eq("duplicate", False).execute().data)
    except Exception as e:  # noqa: BLE001 - database without the columns yet (supabase/exercises_assign.sql)
        print(f"assign skipped: {e}", flush=True)
        return
    lessons = (sb.table("lessons").select("id, kind, number, title, topics, summary_md, chapter_md").eq("course_id", course["id"])
               .eq("status", "ready").in_("kind", ["lecture", "practice"]).order("created_at").execute().data)
    if not todo or not lessons:
        return
    taught = sb.table("exercises").select("title").eq("course_id", course["id"]).not_.is_("lesson_id", "null").execute().data
    listing = "\n\n".join(
        f"[{i + 1}] {'תרגול' if l['kind'] == 'practice' else 'הרצאה'} {l.get('number') or ''}: {', '.join(l.get('topics') or [])}\n"
        f"{(l.get('summary_md') or l.get('chapter_md') or '')[:1500]}" for i, l in enumerate(lessons))
    for k in range(0, len(todo), 60):
        batch = todo[k:k + 60]
        ex = "\n".join(f"id {j}: {x.get('title') or ''} - {(x['question_md'] or '')[:350]}" for j, x in enumerate(batch))
        parts = [types.Part.from_text(text=ASSIGN.format(course=course["name"])),
                 types.Part.from_text(text=f"=== השיעורים ===\n{listing}\n\n=== נפתרו בכיתה ===\n"
                                           + "\n".join(t["title"] or "" for t in taught)[:6000]
                                           + f"\n\n=== התרגילים מקבצים ===\n{ex}")]
        items = author._generate_json(parts, None, ASSIGN_SCHEMA, "MEDIUM").get("items") or []
        placed = 0
        for it in items:
            if not (0 <= it.get("id", -1) < len(batch)):
                continue
            row = batch[it["id"]]
            if it.get("duplicate"):
                sb.table("exercises").update({"duplicate": True}).eq("id", row["id"]).execute()
            elif 1 <= it.get("lesson", 0) <= len(lessons):
                sb.table("exercises").update({"fits_lesson_id": lessons[it["lesson"] - 1]["id"]}).eq("id", row["id"]).execute()
                placed += 1
        print(f"::notice title=Exercises {course['name']}::placed {placed} of {len(batch)} file exercises in a lesson", flush=True)


def run(only=None):
    sb, start = db(), time.time()
    # Labs are out: he does the experiments and entry quizzes himself (30/10/2026).
    q = sb.table("courses").select("id, name, user_id, kind").eq("archived", False).neq("kind", "self").neq("kind", "lab")
    courses = q.eq("id", only).execute().data if only else q.execute().data
    for course in courses:
        materials = sb.table("materials").select("*").eq("course_id", course["id"]).order("created_at").execute().data
        done = {r["material_id"] for r in sb.table("exercises").select("material_id").eq("course_id", course["id"])
                .not_.is_("material_id", "null").execute().data} | read_list(sb, course)
        todo = [m for m in materials if m["id"] not in done and wanted(m)]
        skipped = [m["title"] for m in materials if m["id"] not in done and not wanted(m)]
        print(f"::notice title=Exercises {course['name']}::{len(todo)} files to read; not exercise files: "
              f"{', '.join(skipped)[:600] or '-'}", flush=True)
        try:
            if not from_lessons(sb, course, start + BUDGET_SEC):
                print("::notice title=Exercises::time budget used - the rest continue tomorrow", flush=True)
                return
        except Exception:  # noqa: BLE001 - quota: stop for today
            return
        if not todo:
            try:
                assign(sb, course)
            except Exception as e:  # noqa: BLE001
                print(f"::warning title=Exercises assign {course['name']}::{str(e)[:300]}", flush=True)
            continue
        topics = sorted({t for l in sb.table("lessons").select("topics").eq("course_id", course["id"]).execute().data
                         for t in (l.get("topics") or [])})
        for m in todo:
            if time.time() - start > BUDGET_SEC:
                print("::notice title=Exercises::time budget used - the rest continue tomorrow", flush=True)
                return
            work = Path(tempfile.mkdtemp(prefix="ex_"))
            try:
                found = read_file(sb, course, m, materials, topics, work)
            except Exception as e:  # noqa: BLE001
                print(f"::warning title=Exercises {m['title']}::{str(e)[:300]}", flush=True)
                if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota", "המכסה"):
                    return
                continue
            src = source_of(m)
            rows = [{"user_id": course["user_id"], "course_id": course["id"], "material_id": m["id"], "source": src,
                     "ord": i, "title": x.get("title"), "question_md": x["question_md"], "solution_md": x.get("solution_md"),
                     "topic": x.get("topic"), "exam_style": src == "exam" or bool(x.get("exam_style")),
                     "uncertain": bool(x.get("uncertain"))} for i, x in enumerate(found)]
            if rows:
                sb.table("exercises").insert(rows).execute()
            mark_read(sb, course, m["id"])  # also a file with no exercises: never read again
            print(f"::notice title=Exercises::{course['name']} / {m['title']}: {len(rows)}", flush=True)
        try:
            assign(sb, course)
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Exercises assign {course['name']}::{str(e)[:300]}", flush=True)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
