"""The course page's "מידע על הקורס" without repeats (his request, 04/11/2026: micro showed the same facts many times -
every lesson, last year's site and the syllabus each said them again). Nothing is deleted: the original rows stay in
course_facts (the page can still show them); a merged list is kept next to the course files and shown instead.

  python facts.py [course_id]   merge where the facts changed since the last merge (all courses when no id)
"""
import hashlib
import json
import os
import re
import sys

import author

BUCKET = "study"
FILE = "facts_merged.json"
CATEGORIES = ["exam", "exam_hint", "grading", "reservist", "assignments", "attendance", "materials", "industry", "other"]

PROMPT = """לפניך רשימת פריטי מידע מנהלי על קורס באוניברסיטה (מבחן, ציון, מטלות, נוכחות, חומרים...), שנאספו אוטומטית
מכל השיעורים, מהסילבוס, מאתר המרצה (שנה שעברה) וממה שהסטודנט הוסיף. הרבה פריטים חוזרים על אותו מידע במילים אחרות.
אחד אותם לרשימה בלי כפילויות:
- פריטים שאומרים את אותו דבר (גם בניסוח אחר) - פריט אחד. ids = כל המספרים שאוחדו בו.
- פריט שמוסיף פרט (תאריך, אחוז, תנאי) - שמור את הפרט במשפט המאוחד. אל תאבד שום מידע.
- סתירה (למשל משקל שונה, או "שנה שעברה" מול השנה): העדף את המקור החדש יותר / של השנה, וכתוב בסוגריים מה נאמר
  קודם ומאיפה, למשל "(בסילבוס נכתב 30%)".
- כל מספר חייב להופיע בדיוק בפריט אחד. אל תמציא מידע. עברית, משפט קצר וברור לכל פריט.
- category: אחד מ: exam, exam_hint, grading, reservist, assignments, attendance, materials, industry, other.
- מידע שהסטודנט הוסיף בעצמו (מסומן "ידני") - שמור את הניסוח שלו."""

SCHEMA = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {
    "category": {"type": "string"}, "text": {"type": "string"}, "ids": {"type": "array", "items": {"type": "integer"}}},
    "required": ["category", "text", "ids"]}}}, "required": ["items"]}


def db():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def signature(facts):
    """Same as web/src/lib/facts.ts factsSignature: sorted ids."""
    return hashlib.sha1(",".join(sorted(f["id"] for f in facts)).encode()).hexdigest()


def norm(text):
    return re.sub(r"[\s.,;:!?\"'()\-–]+", " ", text or "").strip().lower()


def exact_merge(facts):
    """Fallback without Gemini: identical texts (ignoring spaces and punctuation) become one item."""
    groups = {}
    for f in facts:
        groups.setdefault((f["category"], norm(f["text"])), []).append(f)
    return [{"category": g[0]["category"], "text": g[-1]["text"], "ids": [f["id"] for f in g]} for g in groups.values()]


def merge(sb, course, facts):
    from google.genai import types
    lessons = {l["id"]: l for l in sb.table("lessons").select("id, kind, number, title, created_at")
               .eq("course_id", course["id"]).execute().data}

    def origin(f):
        if f.get("source") == "manual":
            return "ידני"
        if f.get("source") == "syllabus":
            return "סילבוס"
        l = lessons.get(f.get("lesson_id") or "")
        if not l:
            return "לא ידוע"
        site = l["kind"] == "web"
        return f"{'אתר המרצה (שנה שעברה)' if site else l['kind']} {l.get('number') or ''} {(l.get('created_at') or '')[:10]}"

    listing = "\n".join(f"{i}. [{f['category']}] ({origin(f)}) {f['text']}" for i, f in enumerate(facts))
    out = author._generate_json([types.Part.from_text(text=f"קורס: {course['name']}\n\n{PROMPT}"),
                                 types.Part.from_text(text=listing)], None, SCHEMA, "LOW")
    items, seen = [], set()
    for it in out.get("items") or []:
        ids = [i for i in it.get("ids") or [] if isinstance(i, int) and 0 <= i < len(facts) and i not in seen]
        if not ids or not (it.get("text") or "").strip():
            continue
        seen.update(ids)
        cat = it.get("category") if it.get("category") in CATEGORIES else facts[ids[0]]["category"]
        items.append({"category": cat, "text": it["text"].strip(), "ids": [facts[i]["id"] for i in ids]})
    # Nothing may get lost: a fact the merge left out stays as its own item.
    items += [{"category": f["category"], "text": f["text"], "ids": [f["id"]]} for i, f in enumerate(facts) if i not in seen]
    return items


def run(only=None, force=False):
    sb = db()
    q = sb.table("courses").select("id, name, user_id").eq("archived", False)
    courses = (q.eq("id", only) if only else q).execute().data
    report = []
    for course in courses:
        try:
            facts = sb.table("course_facts").select("*").eq("course_id", course["id"]).order("created_at").execute().data
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Facts {course['name']}::{e}", flush=True)
            continue
        if len(facts) < 2:
            continue
        path = f"{course['user_id']}/materials/{course['id']}/{FILE}"
        sig = signature(facts)
        if not force:
            try:
                if json.loads(sb.storage.from_(BUCKET).download(path).decode()).get("sig") == sig:
                    continue  # merged already for exactly these facts
            except Exception:  # noqa: BLE001 - not merged yet
                pass
        try:
            items = merge(sb, course, facts)
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Facts {course['name']}::{author.friendly_error(e)[:200]} - exact duplicates only", flush=True)
            items = exact_merge(facts)
        sb.storage.from_(BUCKET).upload(path, json.dumps({"sig": sig, "items": items}, ensure_ascii=False).encode("utf-8"),
                                        {"content-type": "application/json", "upsert": "true"})
        report.append(f"{course['name']}: {len(facts)} -> {len(items)}")
    print(f"::notice title=Facts merged::{'; '.join(report) or 'nothing changed'}", flush=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--force"]
    run(args[0] if args else None, "--force" in sys.argv)
