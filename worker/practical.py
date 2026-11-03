"""The lab's practical exam (midterm = experiments 1-5, final = all): a question bank built from everything the lab has -
experiment chapters, his and his partner's summary reports, the lecturer's recorded remarks, entry-quiz questions,
and files of past practical-exam questions. Stored as practical.json next to the course files; the app's
"🧪 מבחן מעשי" page practises from it and draws mock exams of 3 questions (graph, theory, build).

  python practical.py [course_id]   rebuild when something new came in (all lab courses when no id)
"""
import io
import json
import os
import re
import sys

import author

BUCKET = "study"
FILE = "practical.json"
INLINE_LIMIT = 16 * 1024 * 1024
REPORT = re.compile(r"דוח|report", re.I)
PAST = re.compile(r"מבחן|מועד|שאלות|exam", re.I)

PROMPT = """אתה מדריך מעבדה בהנדסת חשמל. בנה מאגר שאלות להכנה למבחן המעשי של המעבדה, מכל החומר המצורף:
פרקי הניסויים, הדוחות המסכמים של הסטודנט ושל השותפה, מה שהמרצה אמרה על המבחן (הקלטות), שאלות בוחני הכניסה,
ושאלות ממבחנים מעשיים קודמים (אם צורפו - כל שאלה מהם נכנסת, מסומנת source="מבחן קודם").

מבנה המבחן המעשי (מבחן אמצע = ניסויים 1-5 כולל, מבחן סוף = כל הניסויים), 3 שאלות:
1. graph - מראים גרף (תגובת תדר / אות בזמן) ושואלים עליו (תדר ברך / קטעון, הגבר, פאזה, מה המעגל, מה ישתנה אם...).
2. theory - שאלה תיאורטית / מושג (למשל slew rate: מה זה ומה המשמעות במדידה).
3. build - בנייה על המטריצה: נותנים כניסות ומבקשים יציאה (דוגמה אמיתית: שני גלי סינוס -> גל אחד - מגבר סוכם);
   צריך לזהות איזה מעגל, לבנות אותו, להגדיר ספקים (מתחים, הגבלת זרם), מחולל אותות וסקופ, ולהראות שהוא עובד.

לכל ניסוי שיש עליו חומר: 2 שאלות graph, 3 theory, 2 build (יותר אם יש שאלות ממבחנים קודמים / דגשים של המרצה).
- question_md: השאלה כפי שתישאל במבחן. answer_md: תשובה מלאה ונכונה - שלבים, נוסחה ← הצבה ← תוצאה, ומאיפה כל נוסחה.
- graph: לשאלת graph - הגרף שיצויר (האפליקציה מחשבת אותו מהפרמטרים, אל תשאיר אותו ריק בשאלת graph):
  kind = lowpass / highpass / bandpass / bandstop (תגובת תדר מסדר ראשון / שני) עם fc (Hz), f0 (Hz, למעבר/חסימת פס), q,
  gain_db (הגבר בפס המעבר); או kind = time עם signals: [{shape: sine/square/triangle, amp (V), freq (Hz), offset (V),
  phase_deg, label}] על פני duration_ms. title - כותרת הגרף. בשאלות אחרות - בלי graph.
- build (רק בשאלת build): goal; circuit_md - איזה מעגל ולמה, שרטוט במילים, ערכי רכיבים (מחושבים, עם הנוסחה);
  wiring_steps - חיווט על המטריצה צעד אחרי צעד (איזו רגל של ה-IC לאן, ספקים, אדמה משותפת, איפה הכניסה והיציאה);
  instruments - הגדרות: ספק (מתחים ±, הגבלת זרם), מחולל (צורת גל, תדר, משרעת, offset), סקופ (ערוצים, VOLT/DIV,
  TIME/DIV, טריגר), מולטימטר; expected - מה אמור להופיע בסקופ ואיך יודעים שזה עובד; mistakes - טעויות נפוצות.
- experiment: מספר הניסוי. source: "פרק הניסוי" / "דוח מסכם" / "המרצה" / "בוחן כניסה" / "מבחן קודם".
hints: כל דגש שהמרצה נתנה על המבחן המעשי (משפט לכל אחד).
experiments: רשימת הניסויים שיש עליהם חומר: n ושם.
רק על בסיס החומר וידע הנדסי נכון; בדוק כל ערך ונוסחה. כל ביטוי מתמטי בתוך $...$ או $$...$$. עברית בלבד."""

SIGNAL = {"type": "object", "properties": {"shape": {"type": "string"}, "amp": {"type": "number"}, "freq": {"type": "number"},
                                           "offset": {"type": "number"}, "phase_deg": {"type": "number"}, "label": {"type": "string"}}}
SCHEMA = {
    "type": "object",
    "properties": {
        "experiments": {"type": "array", "items": {"type": "object", "properties": {"n": {"type": "integer"}, "title": {"type": "string"}},
                                                   "required": ["n", "title"]}},
        "hints": {"type": "array", "items": {"type": "string"}},
        "questions": {"type": "array", "items": {"type": "object", "properties": {
            "experiment": {"type": "integer"}, "type": {"type": "string", "enum": ["graph", "theory", "build"]},
            "source": {"type": "string"}, "question_md": {"type": "string"}, "answer_md": {"type": "string"},
            "graph": {"type": "object", "properties": {
                "kind": {"type": "string"}, "title": {"type": "string"}, "fc": {"type": "number"}, "f0": {"type": "number"},
                "q": {"type": "number"}, "gain_db": {"type": "number"}, "duration_ms": {"type": "number"},
                "signals": {"type": "array", "items": SIGNAL}}},
            "build": {"type": "object", "properties": {
                "goal": {"type": "string"}, "circuit_md": {"type": "string"},
                "wiring_steps": {"type": "array", "items": {"type": "string"}},
                "instruments": {"type": "array", "items": {"type": "string"}},
                "expected": {"type": "string"}, "mistakes": {"type": "array", "items": {"type": "string"}}}},
        }, "required": ["experiment", "type", "source", "question_md", "answer_md"]}},
    },
    "required": ["experiments", "hints", "questions"],
}


def db():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def docx_text(data):
    from docx import Document
    doc = Document(io.BytesIO(data))
    parts = [p.text for p in doc.paragraphs if p.text.strip()]
    for t in doc.tables:
        for row in t.rows:
            parts.append(" | ".join(c.text.strip() for c in row.cells))
    return "\n".join(parts)


def sources(sb, course):
    """Text and file parts from everything the lab has, newest-first within a size budget."""
    from google.genai import types
    texts, files, size = [], [], 0
    for l in (sb.table("lessons").select("kind, number, title, chapter_md").eq("course_id", course["id"]).eq("status", "ready")
              .order("number").execute().data):
        label = f"הקלטה של המרצה: {l.get('title') or ''}" if (l.get("title") or "").startswith("🎙️") else \
            f"ניסוי {l.get('number') or ''} {l.get('title') or ''}"
        texts.append(f"######## {label}\n{(l.get('chapter_md') or '')[:15000]}")
    facts = sb.table("course_facts").select("category, text").eq("course_id", course["id"]).execute().data
    if facts:
        texts.append("######## מידע על הקורס\n" + "\n".join(f"- {f['text']}" for f in facts))
    try:
        qs = (sb.table("questions").select("experiment, question, options, correct").eq("course_id", course["id"])
              .not_.is_("source", "null").execute().data)
        if qs:
            texts.append("######## שאלות בוחני כניסה\n" + "\n".join(
                f"ניסוי {q['experiment']}: {q['question']} -> {q['options'][q['correct']]}" for q in qs))
    except Exception:  # noqa: BLE001 - before supabase/entry_quiz.sql
        pass
    for m in sb.table("materials").select("*").eq("course_id", course["id"]).order("created_at", desc=True).execute().data:
        title = m["title"] or ""
        if not (REPORT.search(title) or PAST.search(title)) or m["storage_path"].startswith("drive:"):
            continue
        try:
            data = sb.storage.from_(BUCKET).download(m["storage_path"])
        except Exception:  # noqa: BLE001
            continue
        if title.lower().endswith(".docx"):
            texts.append(f"######## {title}\n{docx_text(data)[:30000]}")
        elif title.lower().endswith(".pdf") and size + len(data) < INLINE_LIMIT:
            size += len(data)
            files += [types.Part.from_text(text=f"######## {title}"), types.Part.from_bytes(data=data, mime_type="application/pdf")]
    return texts, files


def build(sb, course):
    from google.genai import types
    texts, files = sources(sb, course)
    if not texts and not files:
        return False
    parts = [types.Part.from_text(text=PROMPT), types.Part.from_text(text="\n\n".join(texts))] + files
    out = author._generate_json(parts, None, SCHEMA, "MEDIUM")
    qs = [q for q in out.get("questions") or [] if (q.get("question_md") or "").strip()]
    for i, q in enumerate(qs):
        q["id"] = i
    data = {"experiments": out.get("experiments") or [], "hints": out.get("hints") or [], "questions": qs}
    path = f"{course['user_id']}/materials/{course['id']}/{FILE}"
    sb.storage.from_(BUCKET).upload(path, json.dumps(data, ensure_ascii=False).encode("utf-8"),
                                    {"content-type": "application/json", "upsert": "true"})
    print(f"::notice title=Practical exam {course['name']}::{len(qs)} questions over {len(data['experiments'])} experiments", flush=True)
    return True


def stale(sb, course):
    """Rebuilt when a lesson, a file or an entry-quiz report came after the last build."""
    folder = f"{course['user_id']}/materials/{course['id']}"
    built = next((f for f in sb.storage.from_(BUCKET).list(folder, {"limit": 1000}) if f.get("name") == FILE), None)
    if not built:
        return True
    since = built.get("updated_at") or ""
    newest = [r["updated_at"] for r in sb.table("lessons").select("updated_at").eq("course_id", course["id"]).execute().data]
    newest += [r["created_at"] for r in sb.table("materials").select("created_at").eq("course_id", course["id"]).execute().data]
    try:
        newest += [r["created_at"] for r in sb.table("entry_reports").select("created_at").eq("course_id", course["id"]).execute().data]
    except Exception:  # noqa: BLE001
        pass
    return any(t > since for t in newest)


def run(only=None, force=False):
    sb = db()
    q = sb.table("courses").select("id, name, user_id").eq("kind", "lab").eq("archived", False)
    for course in (q.eq("id", only) if only else q).execute().data:
        if force or stale(sb, course):
            try:
                build(sb, course)
            except Exception as e:  # noqa: BLE001
                print(f"::warning title=Practical exam {course['name']}::{str(e)[:300]}", flush=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--force"]
    run(args[0] if args else None, "--force" in sys.argv)
