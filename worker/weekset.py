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
  של השבוע בלי כפילות: לעולם לא שני תרגילים עם אותם נתונים או אותה שאלה (גרסה מהכיתה וגרסה מהפרק = אותו תרגיל).
  התרגילים שכותרתם מתחילה ב-"📌 מהכיתה" כבר בסט; אל תבחר תרגיל שחוזר על אחד מהם עם מספרים אחרים – רק נושאים שהם לא מכסים. עדיפות לתרגילים מהתרגול.
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


def _nums(md):
    """The numbers that identify an exercise's data (values >= 10 or decimals; 0-9 are in every exercise)."""
    return {x for x in re.findall(r"\d+(?:\.\d+)?", md or "") if "." in x or len(x) >= 2}


def same(a, b):
    """The same exercise twice (his report 15/11/2026, waves week 2: exercise 1 = exercise 3) - the class version and a
    practice / chapter version of one board exercise: the same data, or the same C/Java function, or the same text."""
    import difflib
    qa, qb = a.get("question_md") or "", b.get("question_md") or ""
    na, nb = _nums(qa), _nums(qb)
    prose = lambda t: re.sub(r"[\s$\\{}]+", " ", re.sub(r"```.*?```", " ", t, flags=re.S))[:800]  # noqa: E731
    pa, pb = prose(qa), prose(qb)
    ratio = difflib.SequenceMatcher(None, pa, pb).ratio()
    common = len(na & nb)
    if common >= 3 and common / len(na | nb) >= 0.5 or common == 2 and common / len(na | nb) >= 0.8 and ratio >= 0.5:
        return True
    inline = lambda t: " ".join(re.findall(r"`([^`\n]+)`", re.sub(r"```.*?```", " ", t, flags=re.S)))  # noqa: E731
    fa, fb = (set(re.findall(r"\b(\w+)\s*\(", inline(q))) for q in (qa, qb))
    if fa & fb - {"main", "println", "print", "printf", "if", "for", "while"}:
        return True
    return min(len(pa), len(pb)) >= 150 and ratio >= 0.7  # short generic prose ("what is printed?") is not enough


def dedupe(ids, by_id):
    """Keeps the first of each repeated exercise (class exercises come first)."""
    out = []
    for i in ids:
        if i in by_id and any(same(by_id[i], by_id[k]) for k in out if k in by_id):
            continue
        out.append(i)
    return out


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
        if old.get(str(n), {}).get("manual"):  # built by hand from lecture N + practice N (his request 19/11/2026)
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
        # ...and the rest only adds new topics: at most 4 in all when class gave few, at least 1 extra (his remark
        # 16/11/2026: 11 exercises in comm week 1, half of them the class ones again with other numbers)
        practice = cls + [i for i in practice if i not in cls][:max(1, 4 - len(cls))]
        if len(practice) < 2:  # never fewer than 2 practice exercises when the week has them
            practice += [x["id"] for x in own if x["id"] not in practice][:2 - len(practice)]
        by_id = {x["id"]: x for x in ex}
        practice = dedupe(practice, by_id)
        seen = {i for k, w in sets.items() if k.isdigit() and int(k) < n for i in w["practice"] + [e["id"] for e in w["exam"]]}
        exam = [e for e in exam if e["id"] not in seen and e["id"] in dedupe(practice + [e["id"]], by_id)]  # once per course
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


def add(sb, course, week, ex_id):
    """Puts one exercise into a week's set (e.g. the weekly open code question of micro, 19/11/2026); once."""
    data = load(sb, course)
    w = data.setdefault("weeks", {}).get(str(week))
    if w is None or ex_id in w.get("practice", []):
        return
    w.setdefault("practice", []).append(ex_id)
    sb.storage.from_(BUCKET).upload(f"{course['user_id']}/materials/{course['id']}/week_sets.json",
                                    json.dumps(data, ensure_ascii=False).encode("utf-8"),
                                    {"content-type": "application/json", "upsert": "true"})
    print(f"::notice title=Week sets::{course['name']} week {week}: added {ex_id[:8]}", flush=True)


def set_week(match, week, prefixes):
    """Week N = exactly these exercises, in this order (built by hand from lecture N + practice N, his request
    19/11/2026: only what he learned). Marked "manual": run() and clean() never touch it again."""
    sb = hub.db()
    course = hub.find_course(sb, match)
    all_ids = [x["id"] for x in sb.table("exercises").select("id").eq("course_id", course["id"]).execute().data]
    ids = []
    for p in prefixes:
        hit = [i for i in all_ids if i.startswith(p)]
        if len(hit) != 1:
            sys.exit(f"::error title=Week sets::{p}: {len(hit)} matches")
        ids.append(hit[0])
    data = load(sb, course)
    data.setdefault("weeks", {})[str(week)] = {"practice": ids, "exam": [], "manual": True}
    sb.storage.from_(BUCKET).upload(f"{course['user_id']}/materials/{course['id']}/week_sets.json",
                                    json.dumps(data, ensure_ascii=False).encode("utf-8"),
                                    {"content-type": "application/json", "upsert": "true"})
    print(f"::notice title=Week sets::{course['name']} week {week}: set by hand, {len(ids)} exercises", flush=True)


def clean(match):
    """The stored sets without Gemini: no exercise twice in a week (same()), no exam exercise in two weeks."""
    sb = hub.db()
    course = hub.find_course(sb, match)
    data = load(sb, course)
    by_id = {x["id"]: x for x in sb.table("exercises").select("id, title, question_md").eq("course_id", course["id"]).execute().data}
    seen = set()
    for k in sorted((k for k in data.get("weeks", {}) if k.isdigit()), key=int):
        w = data["weeks"][k]
        if w.get("manual"):  # a hand-built week is kept as it is
            seen |= set(w["practice"]) | {e["id"] for e in w["exam"]}
            continue
        p0, e0 = list(w["practice"]), [e["id"] for e in w["exam"]]
        w["practice"] = dedupe([i for i in w["practice"] if i in by_id], by_id)
        # class exercises + only 1-4 others (his rule 16/11/2026, for the weeks built before it too)
        cls = [i for i in w["practice"] if (by_id[i].get("title") or "").startswith("📌 מהכיתה")]
        if cls:
            w["practice"] = cls + [i for i in w["practice"] if i not in cls][:max(1, 4 - len(cls))]
        keep = dedupe(w["practice"] + [e["id"] for e in w["exam"] if e["id"] in by_id and e["id"] not in seen], by_id)
        w["exam"] = [e for e in w["exam"] if e["id"] in keep]
        seen |= set(w["practice"]) | {e["id"] for e in w["exam"]}
        gone = [i[:8] for i in p0 + e0 if i not in w["practice"] and i not in [e["id"] for e in w["exam"]]]
        if gone:
            print(f"::notice title=Week sets::{course['name']} week {k}: removed repeats {gone}", flush=True)
    sb.storage.from_(BUCKET).upload(f"{course['user_id']}/materials/{course['id']}/week_sets.json",
                                    json.dumps(data, ensure_ascii=False).encode("utf-8"),
                                    {"content-type": "application/json", "upsert": "true"})


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
    elif sys.argv[1] == "set":  # weekset.py set "<course>" <week> <id-prefix,...>
        set_week(sys.argv[2], sys.argv[3], sys.argv[4].split(","))
    elif sys.argv[1] == "clean":  # weekset.py clean "<course>"
        clean(sys.argv[2])
    else:
        run(sys.argv[1])
