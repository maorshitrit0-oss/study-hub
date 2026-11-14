"""The week's exercise set (his request 11/11/2026): week N = lecture N + practice N, 3-6 exercises in one list -
2-4 practice exercises on what lecture N / practice N taught (easy -> harder), then 2 exam exercises on the same
material that can be solved with ONLY what lectures 1..N taught (an exam exercise that needs later material waits for
its week). Chosen by Gemini (free), saved as week_sets.json next to the course files; the exercises tab shows only
this set. Nothing is deleted: the other exercises stay in the database.

  python weekset.py "<course regex>"     (all weeks of the course; run again after a new lecture / file)
"""
import json
import re
import sys
from datetime import datetime, timezone

from google.genai import types

import author
import hub

BUCKET = "study"
SYSTEM = """אתה מתרגל בהנדסת חשמל שבונה לסטודנט סט תרגילים שבועי. שבוע N = הרצאה N + תרגול N.
הסטודנט בונה ידע בהדרגה: הוא יודע רק את מה שנלמד בהרצאות ובתרגולים 1 עד N.
בחר:
- practice: 2 עד 4 תרגילים מתוך "תרגילי השבוע" (מההרצאה והתרגול של שבוע N), מהקל לקשה, שמכסים את הנושאים העיקריים
  של השבוע בלי כפילות. עדיפות לתרגילים מהתרגול.
- exam: עד 2 תרגילים מתוך "תרגילי מבחן ומטלות", שעוסקים בנושאים של שבוע N, ושאפשר לפתור אותם במלואם רק עם החומר
  של הרצאות 1 עד N. אם תרגיל דורש נושא שעוד לא נלמד (מופיע רק בהרצאות מאוחרות או לא מופיע ברשימה) - אל תבחר אותו.
  עדיף פחות תרגילים מאשר תרגיל שהסטודנט לא יכול לפתור.
  רמה: הסטודנט רק עכשיו למד את החומר. תרגיל מבחן מתאים רק אם הוא קצר (עד 3 סעיפים), ישיר (נוסחה ← הצבה ← תוצאה,
  או שאלת הבנה אחת), ולא דורש קפיצות הבנה גדולות או שילוב של הרבה נושאים. שאלה ארוכה עם הרבה סעיפים - לא. why: משפט אחד - על מה התרגיל ולמה הוא מתאים עכשיו.
סה"כ 3 עד 6 תרגילים. רק מזהים (id) מהרשימות. עברית בלבד."""
SCHEMA = {"type": "object", "properties": {
    "practice": {"type": "array", "items": {"type": "string"}},
    "exam": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "string"}, "why": {"type": "string"}},
                                        "required": ["id", "why"]}}},
    "required": ["practice", "exam"]}


def short(md, n=500):
    md = re.sub(r"\s+", " ", md or "")
    return md[:n] + ("…" if len(md) > n else "")


def load(sb, course):
    try:
        return json.loads(sb.storage.from_(BUCKET).download(f"{course['user_id']}/materials/{course['id']}/week_sets.json").decode())
    except Exception:  # noqa: BLE001 - none yet
        return {"weeks": {}}


def run(match, only_missing=False):
    sb = hub.db()
    course = hub.find_course(sb, match)
    old = load(sb, course).get("weeks", {})
    lessons = sb.table("lessons").select("id, kind, number, title, topics, chapter_md").eq("course_id", course["id"]).execute().data
    week = {}
    for l in lessons:
        t = l.get("title") or ""
        if t.startswith("📦") or not l.get("number"):
            continue
        if l["kind"] in ("lecture", "practice") or t.startswith("מפגש "):
            week[l["id"]] = l["number"]
    if not week:
        print(f"::notice title=Week sets::{course['name']}: no numbered lectures", flush=True)
        return
    last = max(week.values())
    ex = sb.table("exercises").select("id, lesson_id, material_id, title, question_md, topic, exam_style, duplicate") \
        .eq("course_id", course["id"]).execute().data
    files = [x for x in ex if not x.get("lesson_id") and not x.get("duplicate")]

    def topics_of(n):
        out = []
        for l in lessons:
            if week.get(l["id"]) == n:
                heads = re.findall(r"^##+ (.+)$", l.get("chapter_md") or "", re.M)
                out.append(f"{author.KIND_NAME.get(l['kind'], '')} {n}: " + "; ".join(
                    [str(t) for t in (l.get("topics") or [])] + [h for h in heads if "בדיקת" not in h and "העולם" not in h])[:900])
        return "\n".join(out)

    sets = dict(old)  # a week whose call fails keeps its earlier set
    for n in range(1, last + 1):
        if only_missing and str(n) in old:
            continue
        own = [x for x in ex if x.get("lesson_id") and week.get(x["lesson_id"]) == n]
        if not own and not files:
            continue
        taught = "\n".join(topics_of(k) for k in range(1, n + 1))
        later = "\n".join(topics_of(k) for k in range(n + 1, last + 1))
        prompt = (f"קורס: {course['name']}\nשבוע {n}.\n\n=== מה נלמד עד עכשיו (הרצאות ותרגולים 1-{n}) ===\n{taught}\n\n"
                  f"=== נושאים של הרצאות מאוחרות (עוד לא נלמדו) ===\n{later or 'אין'}\n\n=== תרגילי השבוע ===\n"
                  + "\n".join(f"[{x['id']}] {x['title']} | {x.get('topic') or ''} | {short(x['question_md'])}" for x in own)
                  + "\n\n=== תרגילי מבחן ומטלות ===\n"
                  + "\n".join(f"[{x['id']}] {x['title']} | {x.get('topic') or ''} | {short(x['question_md'], 400)}" for x in files))
        try:
            got = author._generate_json([types.Part.from_text(text=prompt)], SYSTEM, SCHEMA, "LOW")
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Week sets::{course['name']} week {n}: {str(e)[:200]}", flush=True)
            continue
        ids_own, ids_files = {x["id"] for x in own}, {x["id"] for x in files}
        practice = [i for i in got.get("practice", []) if i in ids_own][:4]
        exam = [e for e in got.get("exam", []) if e.get("id") in ids_files][:2]
        # the exercises solved in class come first, all of them (classex.py; waves: "the exam is built from them")
        cls = [x["id"] for x in own if (x.get("title") or "").startswith("📌 מהכיתה")]
        practice = (cls + [i for i in practice if i not in cls])[:10]
        if len(practice) < 2:  # never fewer than 2 practice exercises when the week has them
            practice += [x["id"] for x in own if x["id"] not in practice][:2 - len(practice)]
        sets[str(n)] = {"practice": practice, "exam": exam}
        print(f"::notice title=Week sets::{course['name']} week {n}: {len(practice)} practice + {len(exam)} exam", flush=True)
    sb.storage.from_(BUCKET).upload(f"{course['user_id']}/materials/{course['id']}/week_sets.json",
                                    json.dumps({"weeks": sets, "built_at": datetime.now(timezone.utc).isoformat()},
                                               ensure_ascii=False).encode("utf-8"),
                                    {"content-type": "application/json", "upsert": "true"})


def drop(match, week, ids):
    """Removes exercises from a week's set (Claude checked them: wrong or not taught yet); "all" drops the week so the
    queue builds it again."""
    sb = hub.db()
    course = hub.find_course(sb, match)
    data = load(sb, course)
    w = data.get("weeks", {}).get(str(week))
    if w is None:
        return
    if ids == ["all"]:
        data["weeks"].pop(str(week))
    else:
        w["practice"] = [i for i in w["practice"] if not any(i.startswith(x) for x in ids)]
        w["exam"] = [e for e in w["exam"] if not any(e["id"].startswith(x) for x in ids)]
    sb.storage.from_(BUCKET).upload(f"{course['user_id']}/materials/{course['id']}/week_sets.json",
                                    json.dumps(data, ensure_ascii=False).encode("utf-8"),
                                    {"content-type": "application/json", "upsert": "true"})
    print(f"::notice title=Week sets::{course['name']} week {week}: dropped {ids}", flush=True)


def fill_missing(sb):
    """Weeks with no set yet (a Gemini failure, a new lecture) in every active course - run by the queue."""
    for c in sb.table("courses").select("id, name, user_id, kind").eq("archived", False).execute().data:
        if c.get("kind") in ("lab", "self"):
            continue
        nums = [l["number"] for l in sb.table("lessons").select("number, kind, title").eq("course_id", c["id"]).execute().data
                if l.get("number") and l["kind"] in ("lecture", "practice") and not (l.get("title") or "").startswith("📦")]
        have = load(sb, c).get("weeks", {})
        if nums and any(str(n) not in have for n in range(1, max(nums) + 1)):
            run("^" + re.escape(c["name"]) + "$", only_missing=True)


if __name__ == "__main__":
    if sys.argv[1] == "drop":  # weekset.py drop "<course>" <week> <id-prefix,...|all>
        drop(sys.argv[2], sys.argv[3], sys.argv[4].split(","))
    else:
        run(sys.argv[1])
