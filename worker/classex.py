"""The exercises solved IN CLASS (his request 14/11/2026, waves: "the exam is built from exercises we saw in the lectures
and the practices"): every exercise worked in a lecture / practice chapter becomes an exercise of that lesson, titled
"📌 מהכיתה: ...", with the full solution as it was done in class (re-checked). Gemini (free) reads each chapter once;
exercises already taken are skipped by title. The week set (weekset.py) then puts all of them first.

  python classex.py "<course regex>"
"""
import json
import re
import sys

from google.genai import types

import author
import hub
from tidy import tidy

MARK = "📌 מהכיתה: "
SYSTEM = """לפניך פרק קריאה של שיעור (הרצאה או תרגול) בהנדסת חשמל. מצא את **כל התרגילים שנפתרו בשיעור עצמו** (דוגמאות מספריות,
תרגילים מהלוח, שאלות מבחן שנפתרו בכיתה) – לא שאלות שאלון ולא שאלות ראיון.
לכל תרגיל:
- title: שם קצר של התרגיל (בלי מספר שיעור).
- question_md: השאלה המלאה עם כל הנתונים, כפי שהוצגה בשיעור.
- solution_md: פתרון מלא שלב אחרי שלב, באותה דרך שנפתר בשיעור: לכל שלב הסבר קצר למה, ואז **נוסחה:** $$...$$ ← **הצבה:** $$...$$
  ← **תוצאה:** $$...$$ עם יחידות, ו-✅ לתשובה הסופית של כל סעיף. **חשב מחדש כל מספר**; אם בפרק יש טעות – תקן וכתוב > ⚠️ תוקן: ... .
  בסוף: 💡 **הרעיון:** משפט אחד.
- topic: הנושא.
אם אין בשיעור תרגילים פתורים – רשימה ריקה. כל ביטוי מתמטי בתוך $...$ או $$...$$. עברית בלבד."""
SCHEMA = {"type": "object", "properties": {"exercises": {"type": "array", "items": {"type": "object", "properties": {
    "title": {"type": "string"}, "question_md": {"type": "string"}, "solution_md": {"type": "string"}, "topic": {"type": "string"}},
    "required": ["title", "question_md", "solution_md"]}}}, "required": ["exercises"]}


def run(match):
    sb = hub.db()
    course = hub.find_course(sb, match)
    lessons = sb.table("lessons").select("id, kind, number, title, chapter_md, status").eq("course_id", course["id"]) \
        .in_("kind", ["lecture", "practice"]).eq("status", "ready").execute().data
    for l in sorted(lessons, key=lambda l: (l.get("number") or 99, l["kind"])):
        if (l.get("title") or "").startswith("📦") or not l.get("chapter_md"):
            continue
        have = {x["title"] for x in sb.table("exercises").select("title").eq("lesson_id", l["id"]).execute().data}
        if any((t or "").startswith(MARK) for t in have):
            continue  # this lesson was done already
        try:
            got = author._generate_json([types.Part.from_text(text=l["chapter_md"])], SYSTEM, SCHEMA, "MEDIUM").get("exercises") or []
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Class exercises::{l['kind']} {l.get('number')}: {str(e)[:200]}", flush=True)
            continue
        rows = [{"user_id": course["user_id"], "course_id": course["id"], "lesson_id": l["id"], "source": "lesson",
                 "ord": -100 + i, "title": MARK + x["title"].strip(), "question_md": tidy(x["question_md"]),
                 "solution_md": tidy(x["solution_md"]), "topic": x.get("topic"), "exam_style": True, "uncertain": False}
                for i, x in enumerate(got) if x.get("question_md") and x.get("solution_md")]
        if rows:
            sb.table("exercises").insert(rows).execute()
            # these are already in their final form: the reformat pass of exercises.py must not rewrite them
            import exercises as exmod
            ids = [r["id"] for r in sb.table("exercises").select("id, title").eq("lesson_id", l["id"]).execute().data
                   if (r["title"] or "").startswith(MARK)]
            for i in ids:
                exmod.mark_read(sb, course, f"exp:{i}")
                exmod.mark_read(sb, course, f"code:{i}")
        print(f"::notice title=Class exercises::{course['name']} {l['kind']} {l.get('number')}: {len(rows)} from class", flush=True)


if __name__ == "__main__":
    run(sys.argv[1])
