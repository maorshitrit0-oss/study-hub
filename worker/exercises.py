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
SHEET = re.compile(r"תרגיל|תרגול|exercise|problem|שאלות", re.I)
SOLUTION = re.compile(r"פתרון|פתרונות|solution", re.I)

PROMPT = """הקובץ המצורף הוא {kind} בקורס "{course}" (הנדסת חשמל). הסטודנט לומד מפתרון תרגילים בעצמו.
הוצא את **כל** התרגילים / השאלות בקובץ, לפי הסדר (כל סעיף כחלק מהשאלה שלו, לא כתרגיל נפרד):
- title: כותרת קצרה (למשל "שאלה 2 - מגבר משוב").
- question_md: הנוסח המלא בעברית (מונחים באנגלית בסוגריים), עם כל הנתונים והסעיפים. שרטוט/מעגל - תאר במילים בדיוק
  (רכיבים, ערכים, איך מחוברים). נוסחאות ב-LaTeX: משוואה מלאה בשורה נפרדת $$...$$.
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


def wanted(m):
    """Files that hold exercises (not slides, the syllabus, a lab booklet or a solution on its own)."""
    title = m["title"] or ""
    if not (FILE_TYPES.search(title) or m["storage_path"].startswith("drive:")) or SOLUTION.search(title):
        return False
    return m.get("kind") in ("past_exam", "solution") or bool(EXAM.search(title) or HOMEWORK.search(title) or SHEET.search(title))


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


def run(only=None):
    sb, start = db(), time.time()
    q = sb.table("courses").select("id, name, user_id, kind").eq("archived", False).neq("kind", "self")
    courses = q.eq("id", only).execute().data if only else q.execute().data
    for course in courses:
        materials = sb.table("materials").select("*").eq("course_id", course["id"]).order("created_at").execute().data
        done = {r["material_id"] for r in sb.table("exercises").select("material_id").eq("course_id", course["id"])
                .not_.is_("material_id", "null").execute().data} | read_list(sb, course)
        todo = [m for m in materials if m["id"] not in done and wanted(m)]
        if not todo:
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


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
