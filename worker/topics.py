"""One name per topic (his request, 04/11/2026, like the course info): the same topic shows up under several names
("קלט עם Scanner", "מחלקת Scanner", "קלט בעזרת מחלקת Scanner וממשק ה-API"), so "איפה אני עומד" split one topic into
many. Nothing is renamed in the database: a map original -> merged name is kept next to the course files
(topics_merged.json) and the app counts by it (web/src/lib/topics.ts).

  python topics.py [course_id]   (all courses when no id; only where the topic list changed)
"""
import hashlib
import json
import os
import sys

import author

BUCKET = "study"
FILE = "topics_merged.json"

PROMPT = """לפניך רשימת שמות של נושאים בקורס אוניברסיטאי (מתוך שאלונים, תרגילים ושיעורים). הרבה שמות הם אותו נושא
בניסוח אחר. קבץ אותם: כל קבוצה = נושא אחד, עם name קצר וברור בעברית (מונח באנגלית בסוגריים אם צריך) ו-members = כל
השמות המקוריים שלו בדיוק כפי שהם כתובים. אחד רק שמות שהם באמת אותו נושא לימודי (למשל "לולאות" ו-"לולאות for ו-while");
נושאים קרובים אבל שונים (למשל "לולאות" ו-"מערכים") - נפרדים. כל שם מקורי חייב להופיע בדיוק בקבוצה אחת."""

SCHEMA = {"type": "object", "properties": {"groups": {"type": "array", "items": {"type": "object", "properties": {
    "name": {"type": "string"}, "members": {"type": "array", "items": {"type": "string"}}}, "required": ["name", "members"]}}},
    "required": ["groups"]}


def db():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def course_topics(sb, cid):
    names = set()
    for r in sb.table("questions").select("topic").eq("course_id", cid).execute().data:
        names.add(r.get("topic") or "")
    try:
        for r in sb.table("exercises").select("topic").eq("course_id", cid).execute().data:
            names.add(r.get("topic") or "")
    except Exception:  # noqa: BLE001
        pass
    for r in sb.table("lessons").select("topics").eq("course_id", cid).execute().data:
        names.update(r.get("topics") or [])
    return sorted(n.strip() for n in names if n and n.strip())


def run(only=None, force=False):
    from google.genai import types
    sb = db()
    q = sb.table("courses").select("id, name, user_id").eq("archived", False)
    courses = (q.eq("id", only) if only else q).execute().data
    report = []
    for course in courses:
        names = course_topics(sb, course["id"])
        if len(names) < 2:
            continue
        sig = hashlib.sha1("\n".join(names).encode()).hexdigest()
        path = f"{course['user_id']}/materials/{course['id']}/{FILE}"
        if not force:
            try:
                if json.loads(sb.storage.from_(BUCKET).download(path).decode()).get("sig") == sig:
                    continue
            except Exception:  # noqa: BLE001
                pass
        try:
            out = author._generate_json([types.Part.from_text(text=f"קורס: {course['name']}\n\n{PROMPT}"),
                                         types.Part.from_text(text="\n".join(names))], None, SCHEMA, "LOW")
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Topics {course['name']}::{author.friendly_error(e)[:200]}", flush=True)
            if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota", "המכסה"):
                break
            continue
        mapping = {}
        for g in out.get("groups") or []:
            name = (g.get("name") or "").strip()
            for m in g.get("members") or []:
                if name and m in names and m not in mapping:
                    mapping[m] = name
        for n in names:  # a name the grouping left out keeps its own name
            mapping.setdefault(n, n)
        sb.storage.from_(BUCKET).upload(path, json.dumps({"sig": sig, "map": mapping}, ensure_ascii=False).encode("utf-8"),
                                        {"content-type": "application/json", "upsert": "true"})
        report.append(f"{course['name']}: {len(names)} -> {len(set(mapping.values()))}")
    print(f"::notice title=Topics merged::{'; '.join(report) or 'nothing changed'}", flush=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--force"]
    run(args[0] if args else None, "--force" in sys.argv)
