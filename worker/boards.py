"""Writes out what is written on the board before every board snapshot in existing chapters (his request,
04/11/2026: the lecturer's white-on-black handwriting is hard to read, so before each image with text - a clean
"📝 מה כתוב בלוח" in words, a table for comparisons, a code block for code). New chapters do it themselves
(author.SLIDES_RULE).

  python boards.py            every ready chapter not yet done - Java courses first (stops politely on quota)
  python boards.py <lesson>   one lesson

One Gemini call per lesson with all its snapshots. Nothing is lost: only text is inserted before images, the chapter
before is kept in storage (chapter_before_boards.md, which also marks the lesson as done), quiz and answers untouched.
"""
import os
import re
import sys
import time

from supabase import create_client

import author

BUCKET = "study"
MARK = "chapter_before_boards.md"
LABEL = "📝 מה כתוב בלוח"
IMG = re.compile(r"!\[[^\]]*\]\(slide:(\d+)\)")
JAVA = re.compile(r"ג'אווה|ג׳אווה|גאווה|java", re.I)
BUDGET_SEC = 45 * 60

PROMPT = """הצילומים המצורפים הם צילומי לוח/שקפים מהרצאה (מספר השקף לפני כל צילום), ולצידם הקטע בפרק שבו כל צילום מופיע.
כתב היד של המרצה קשה לקריאה (לרוב גיר לבן על לוח שחור), והסטודנט לא מבין אותו מהתמונה.
לכל צילום: has_text = האם יש בו מלל, טבלה, השוואה, קוד, רשימה, נוסחאות או שרטוט עם כיתוב (צילום כמעט ריק / רק פני המרצה - false).
אם כן - md: כל מה שכתוב בצילום, נקי ומסודר כך שאפשר להבין אותו בלי התמונה:
- השוואה בין דברים - טבלת Markdown; שלבים / תהליך - רשימה ממוספרת; קוד - בלוק קוד (```java וכו') עם הערות בעברית;
  נוסחאות - LaTeX בתוך $...$; שרטוט / דיאגרמה - מה יש בו ומה כל חץ אומר.
- לתרגם לעברית, ולשמור כל מונח באנגלית בסוגריים כמו שהוא כתוב. בלי כותרת - רק התוכן.
- רק מה שבאמת כתוב בצילום, בלי להוסיף הסברים משלך. מילה שבאמת לא קריאה - [לא קריא]; לא לנחש.
- אם בקטע שליד הצילום יש כבר תמלול מלא של מה שכתוב בו - has_text = false."""

SCHEMA = {"type": "object", "properties": {"boards": {"type": "array", "items": {"type": "object", "properties": {
    "n": {"type": "integer"}, "has_text": {"type": "boolean"}, "md": {"type": "string"}}, "required": ["n", "has_text"]}}},
    "required": ["boards"]}


def db():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def done(sb, lesson):
    folder = f"{lesson['user_id']}/lessons/{lesson['id']}"
    try:
        return any(f.get("name") == MARK for f in sb.storage.from_(BUCKET).list(folder, {"limit": 1000}))
    except Exception:  # noqa: BLE001
        return False


def context(md, pos):
    """The chapter text just before an image (where its explanation is)."""
    return md[max(0, pos - 1200):pos]


def add_boards(sb, lesson):
    from google.genai import types
    md = lesson["chapter_md"] or ""
    prefix = f"{lesson['user_id']}/lessons/{lesson['id']}"
    store = sb.storage.from_(BUCKET)
    parts, seen = [types.Part.from_text(text=PROMPT)], set()
    for m in IMG.finditer(md):
        n = int(m.group(1))
        if n in seen or LABEL in md[max(0, m.start() - 3000):m.start()].split("![")[-1]:
            continue
        try:
            data = store.download(f"{prefix}/slide_{n:03d}.webp")
        except Exception:  # noqa: BLE001
            continue
        seen.add(n)
        parts += [types.Part.from_text(text=f"===== שקף {n} =====\nהקטע בפרק לפני הצילום:\n{context(md, m.start())}"),
                  types.Part.from_bytes(data=data, mime_type="image/webp")]
    name = f"{lesson['kind']} {lesson.get('number') or ''} ({lesson['id']})"
    if not seen:
        store.upload(f"{prefix}/{MARK}", md.encode("utf-8"), {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
        print(f"{name}: no snapshots", flush=True)
        return 0
    out = author._generate_json(parts, None, SCHEMA, "LOW")
    boards = {b["n"]: (b.get("md") or "").strip() for b in out.get("boards") or [] if b.get("has_text") and (b.get("md") or "").strip()}

    def put(m):
        text = boards.pop(int(m.group(1)), None)  # once per snapshot, before its first appearance
        return f"**{LABEL}:**\n\n{text}\n\n{m.group(0)}" if text else m.group(0)
    new = IMG.sub(put, md)
    if len(IMG.findall(new)) != len(IMG.findall(md)) or len(new) < len(md):
        print(f"::warning title=Boards rejected::{name}", flush=True)
        return 0
    if not done(sb, lesson):  # the very first version stays the backup
        store.upload(f"{prefix}/{MARK}", md.encode("utf-8"), {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
    added = new.count(LABEL) - md.count(LABEL)
    if added:
        sb.table("lessons").update({"chapter_md": new}).eq("id", lesson["id"]).execute()
    print(f"::notice title=Boards::{name}: {added} of {len(seen)} snapshots written out", flush=True)
    return added


def run(only=None):
    sb = db()
    courses = {c["id"]: c["name"] or "" for c in sb.table("courses").select("id, name").execute().data}
    q = sb.table("lessons").select("id, user_id, course_id, kind, number, chapter_md").eq("status", "ready") \
        .in_("kind", ["lecture", "practice"])
    if only:
        q = q.eq("id", only)
    lessons = [l for l in q.order("created_at").execute().data if IMG.search(l.get("chapter_md") or "")]
    lessons.sort(key=lambda l: 0 if JAVA.search(courses.get(l["course_id"], "")) else 1)  # Java first (his request)
    todo = [l for l in lessons if only or not done(sb, l)]
    print(f"::notice title=Boards::{len(todo)} chapters with board snapshots to write out", flush=True)
    start = time.time()
    for lesson in todo:
        if time.time() - start > BUDGET_SEC:
            print("::notice title=Boards::time budget used - the rest continue on the next run", flush=True)
            return
        try:
            add_boards(sb, lesson)
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Boards {lesson['id']}::{author.friendly_error(e)[:300]}", flush=True)
            if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota", "המכסה"):
                return


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
