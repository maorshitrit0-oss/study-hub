"""Writes ahead of time the "📖 מה כל שורה עושה" under every code block (his screenshot, 06/11/2026: the explanation was
asked from Gemini only when he opened the page, so on a day the free quota was gone he got a red error instead of it).
Same prompt as web/src/app/api/explain-code/route.ts; stored where that route looks first
(<user_id>/codelines/<hash>.json), so the page shows it at once on every device. Blocks already written are skipped.

  python codelines.py            chapters, summaries and exercises of ready lessons - newest first (stops on quota)
  python codelines.py <lesson>   one lesson
"""
import json
import os
import re
import sys
import time

from supabase import create_client

import author

BUCKET = "study"
BUDGET_SEC = 30 * 60
SKIP_LANGS = {"wave", "text", "txt", "output", "console"}
FENCE = re.compile(r"^([ \t]*)(`{3,}|~{3,})[ \t]*([^\s`]*)[^\n]*\n(.*?)^[ \t]*\2[ \t]*$", re.M | re.S)

SYSTEM = """אתה מסביר קוד לסטודנט להנדסת חשמל שלא חזק בתכנות (מכיר מעט מושגים ב-C++).
קיבלת קטע קוד (Java / C / אסמבלי / SystemVerilog / Python וכו'). לכל שורה בקוד, לפי הסדר - "he": מה השורה עושה, בעברית פשוטה,
משפט או שניים: מה היא עושה ולמה היא שם. כל מילה שמורה, טיפוס, פונקציה או סימן (למשל public, static, int, ;, {}, ++, %, ==)
שמופיעים בפעם הראשונה - מה הם אומרים. שורה ריקה או רק סוגר } - הסבר קצר מה נסגר. מונחים באנגלית בסוגריים.
"code": השורה עצמה כמו שהיא (בלי רווחים בהתחלה). רק נכון; אם זה פלט ולא קוד - הסבר מה רואים בו."""

SCHEMA = {"type": "object", "properties": {"lines": {"type": "array", "items": {"type": "object", "properties": {
    "code": {"type": "string"}, "he": {"type": "string"}}, "required": ["code", "he"]}}}, "required": ["lines"]}


def code_hash(code):
    """Same as web/src/lib/codeHash.ts: djb2 over UTF-16 code units of the block without trailing whitespace, base 36."""
    s = code.rstrip().encode("utf-16-le")
    h = 5381
    for i in range(0, len(s), 2):
        h = ((h << 5) + h + int.from_bytes(s[i:i + 2], "little")) & 0xFFFFFFFF
    digits, out = "0123456789abcdefghijklmnopqrstuvwxyz", ""
    while True:
        h, r = divmod(h, 36)
        out = digits[r] + out
        if not h:
            return out


def blocks(md):
    """(code, lang) of every fenced code block, as the page's markdown renderer gives it."""
    out = []
    for m in FENCE.finditer(md or ""):
        indent, lang, body = len(m.group(1)), m.group(3).lower(), m.group(4)
        if indent:
            body = "\n".join(re.sub(rf"^[ \t]{{0,{indent}}}", "", line) for line in body.split("\n"))
        if body.strip() and lang not in SKIP_LANGS and len(body) <= 12000:
            out.append((body, lang))
    return out


def db():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def existing(sb, user_id):
    try:
        return {f["name"] for f in sb.storage.from_(BUCKET).list(f"{user_id}/codelines", {"limit": 10000})}
    except Exception:  # noqa: BLE001 - none yet
        return set()


def explain(sb, user_id, code, lang):
    from google.genai import types
    out = author._generate_json([types.Part.from_text(text=f"שפה: {lang or 'לא ידוע'}\n\n{code}")], SYSTEM, SCHEMA, "LOW")
    lines = [l for l in out.get("lines") or [] if (l.get("code") or "").strip() and (l.get("he") or "").strip()]
    if lines:
        sb.storage.from_(BUCKET).upload(f"{user_id}/codelines/{code_hash(code)}.json",
                                        json.dumps({"lines": lines}, ensure_ascii=False).encode("utf-8"),
                                        {"content-type": "application/json", "upsert": "true"})
    return bool(lines)


def run(only=None):
    sb = db()
    q = sb.table("lessons").select("id, user_id, chapter_md, summary_md").eq("status", "ready")
    lessons = (q.eq("id", only) if only else q).order("created_at", desc=True).execute().data
    try:
        ex = sb.table("exercises").select("lesson_id, question_md, solution_md").execute().data
    except Exception:  # noqa: BLE001 - no exercises table
        ex = []
    todo, seen = [], {}
    for l in lessons:
        have = seen.setdefault(l["user_id"], existing(sb, l["user_id"]))
        mds = [l.get("chapter_md"), l.get("summary_md")] + \
              [x.get(k) for x in ex if x["lesson_id"] == l["id"] for k in ("question_md", "solution_md")]
        for md in mds:
            for code, lang in blocks(md):
                name = f"{code_hash(code)}.json"
                if name not in have:
                    have.add(name)
                    todo.append((l["user_id"], code, lang))
    print(f"::notice title=Code lines::{len(todo)} code blocks to explain", flush=True)
    start, done = time.time(), 0
    for user_id, code, lang in todo:
        if time.time() - start > BUDGET_SEC:
            print("::notice title=Code lines::time budget used - the rest continue tomorrow", flush=True)
            break
        try:
            done += explain(sb, user_id, code, lang)
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Code lines::{author.friendly_error(e)[:300]}", flush=True)
            if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota", "המכסה"):
                break
    print(f"::notice title=Code lines::{done} written", flush=True)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
