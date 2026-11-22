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


# ---- the full check (his remark 22/11/2026: "what is written here and what is really on the board are not the same") ----
FIX_MARK = "chapter_before_boardfix.md"


def blocks(md):
    """Every "📝 מה כתוב בלוח" block and the snapshot right after it: [(n, start, end, text)]; start..end = the block up to
    the image line (the label line included)."""
    out, prev = [], 0
    for m in IMG.finditer(md):
        seg = md[prev:m.start()]
        i = seg.rfind("מה כתוב בלוח")
        if i >= 0:
            ls = seg.rfind("\n", 0, i) + 1
            lead = re.sub(r"[*#\s📝]|^\d+\.", "", seg[ls:i])
            if lead:  # the label sits after other text on its line (e.g. "... **📝 מה כתוב בלוח:**"): keep that text
                j = seg.rfind("**", ls, i)
                ls = j if j >= 0 and not re.sub(r"[\s📝]", "", seg[j + 2:i]) else i
            start = prev + ls
            end = m.start()
            h = re.search(r"\n#{1,6} ", md[prev + i:end])  # chapter text after the block (a heading): not part of it
            if h:
                end = prev + i + h.start() + 1
            out.append((int(m.group(1)), start, end, md[start:end]))
        prev = m.end()
    return out


def dump(out_dir):
    """Every block + its snapshot, for Claude to compare one by one -> boards.json + slides/<lesson>_<n>.webp."""
    from pathlib import Path
    import json
    sb = db()
    courses = {c["id"]: c["name"] for c in sb.table("courses").select("id, name").eq("archived", False).execute().data}
    out = Path(out_dir)
    (out / "slides").mkdir(parents=True, exist_ok=True)
    rows = []
    for l in sb.table("lessons").select("id, user_id, course_id, kind, number, title, chapter_md").eq("status", "ready") \
            .order("created_at").execute().data:
        if l["course_id"] not in courses:
            continue
        store = sb.storage.from_(BUCKET)
        for n, s, e, text in blocks(l.get("chapter_md") or ""):
            name = f"{l['id'][:8]}_{n:03d}.webp"
            try:
                (out / "slides" / name).write_bytes(store.download(f"{l['user_id']}/lessons/{l['id']}/slide_{n:03d}.webp"))
            except Exception:  # noqa: BLE001
                name = None
            rows.append({"lesson_id": l["id"], "course": courses[l["course_id"]], "kind": l["kind"], "number": l["number"],
                         "title": l["title"], "n": n, "block": text, "img": name})
    (out / "boards.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(rows)} blocks")


def fix(path):
    """Applies Claude's corrections: JSON [{lesson_id, n, md}] - the block before snapshot n becomes exactly md (what is
    really on the board); md "" removes the block (the image stays). The chapter before the first fix is kept."""
    import json
    sb = db()
    by = {}
    for f in json.loads(open(path, encoding="utf-8").read()):
        by.setdefault(f["lesson_id"], []).append(f)
    for lid, fixes in by.items():
        l = sb.table("lessons").select("id, user_id, kind, number, chapter_md").eq("id", lid).execute().data[0]
        md = l["chapter_md"] or ""
        prefix = f"{l['user_id']}/lessons/{lid}"
        store = sb.storage.from_(BUCKET)
        if not any(x.get("name") == FIX_MARK for x in store.list(prefix, {"limit": 1000})):
            store.upload(f"{prefix}/{FIX_MARK}", md.encode("utf-8"), {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
        done_n = 0
        for f in fixes:
            hit = [b for b in blocks(md) if b[0] == int(f["n"])]
            if not hit:
                print(f"::warning title=Boardfix::{lid[:8]} slide {f['n']}: no block found", flush=True)
                continue
            n, s, e, _ = hit[0]
            new = f"**{f.get('label') or LABEL}:**\n\n{f['md'].strip()}\n\n" if f["md"].strip() else ""
            if s > 0 and md[s - 1] != "\n":  # mid-line label: the block starts on its own paragraph
                new = "\n\n" + new if new else "\n\n"
            if f.get("drop_img"):  # the snapshot shows nothing (a black screen, only a face): it goes too
                im = IMG.match(md, e)
                e = im.end() if im else e
            md = md[:s] + new + md[e:]
            done_n += 1
        sb.table("lessons").update({"chapter_md": md}).eq("id", lid).execute()
        print(f"::notice title=Boardfix::{l['kind']} {l['number']} ({lid[:8]}): {done_n} blocks corrected", flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "dump":
        dump(sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == "fix":
        fix(sys.argv[2])
    else:
        run(sys.argv[1] if len(sys.argv) > 1 else None)
