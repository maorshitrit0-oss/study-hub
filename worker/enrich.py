"""Rewrite existing chapters into his structure: every topic = background -> the lecturer's explanation ->
an everyday example right there -> a worked example (if the lecture had one) -> next topic.

  python enrich.py            all ready lectures/practices not yet restructured (stops politely on quota)
  python enrich.py <lesson>   one lesson

Nothing is lost: the chapter before the rewrite is kept in storage (chapter_before_examples.md, which also marks the
lesson as done), the quiz and his answers are untouched, the fact-check section is re-attached as it was, and a
rewrite that drops content (board snapshots, much shorter text) is rejected and the old chapter stays.
"""
import os
import re
import sys

from supabase import create_client

import author

BUCKET = "study"
MARK = "chapter_before_examples.md"
VERIFY_SPLIT = "\n---\n### ✅ בדיקת עובדות"

REWRITE = """לפניך פרק קריאה קיים בעברית (Markdown) שכבר נבדק עובדתית. הסטודנט מבין רק דרך דוגמאות.
שכתב אותו כך שכל נושא וכל תת-נושא (כל כותרת ## או ###) בנוי בדיוק בסדר הזה:
1. **רקע:** למה הנושא קיים ואיזו בעיה הוא פותר - 2-3 משפטים פשוטים, בלי מונחים שעוד לא הוסברו.
2. ההסבר של המרצה - כל התוכן של הפרק על הנושא הזה, כמו שהוא.
3. > 🏠 **מהחיים:** דוגמה מחיי היום-יום שבה הנושא הזה באמת פועל (מזגן, טלפון, מטען, מחשב, רכב, רמזור, וויי-פיי...), ואיך בדיוק - ממוקמת כאן, בסוף הנושא ולפני הנושא הבא.
4. אם בפרק יש תרגיל או דוגמה פתורה על הנושא - היא באה כאן, אחרי הדוגמה מהחיים.
כללים מחייבים:
- אל תשמיט ואל תשנה שום תוכן הנדסי: כל הגדרה, נוסחה, מספר, קוד, טבלה, תמונה (![...](slide:N)), שורות ⭐ ו-⚠️, וסעיף "מהעולם האמיתי".
- מותר להוסיף רק את הרקע ואת הדוגמאות מהחיים, ולסדר מחדש לפי המבנה. שמור על הכותרות.
- דוגמאות מהחיים - רק נכונות הנדסית; אם אינך בטוח - בחר דוגמה אחרת.
- נוסחאות ב-LaTeX כמו בפרק. החזר רק את הפרק המלא, בלי הקדמה."""

CHECK = """אתה בודק עובדות קפדן בהנדסת חשמל. קיבלת פרק מקורי (נבדק) וגרסה משוכתבת שלו עם רקע ודוגמאות מחיי היום-יום.
- ודא שכל תוכן הנדסי מהמקור נמצא בגרסה החדשה ולא השתנה; החזר כל מה שחסר למקומו.
- ודא שכל רקע וכל דוגמה מהחיים נכונים הנדסית ושהנושא באמת פועל בדוגמה כפי שנכתב; תקן או החלף.
החזר רק את הגרסה המשוכתבת המתוקנת והמלאה."""


def db():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def gen(system, prompt):
    from google.genai import types

    def call(client, model):
        return client.models.generate_content(model=model, contents=prompt,
                                              config=types.GenerateContentConfig(system_instruction=system))
    text = (author._with_gemini(call).text or "").strip()
    return re.sub(r"^```(?:markdown|md)?\s*|\s*```$", "", text)


def done(sb, lesson):
    folder = f"{lesson['user_id']}/lessons/{lesson['id']}"
    try:
        return any(f.get("name") == MARK for f in sb.storage.from_(BUCKET).list(folder, {"limit": 1000}))
    except Exception:  # noqa: BLE001
        return False


def mark(sb, lesson, old_md):
    """Keeps the chapter as it was before the rewrite; its presence also marks the lesson as restructured."""
    sb.storage.from_(BUCKET).upload(f"{lesson['user_id']}/lessons/{lesson['id']}/{MARK}", old_md.encode("utf-8"),
                                    {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})


def safe(old, new):
    """Rejects a rewrite that lost content: every board snapshot kept, and not much shorter than before."""
    slides_old = set(re.findall(r"\(slide:(\d+)\)", old))
    slides_new = set(re.findall(r"\(slide:(\d+)\)", new))
    return slides_old <= slides_new and len(new) >= 0.9 * len(old) and "🏠" in new


def enrich(sb, lesson):
    md = lesson["chapter_md"] or ""
    body, _, tail = md.partition(VERIFY_SPLIT)
    tail = VERIFY_SPLIT + tail if tail else ""
    print(f"rewriting {lesson['id']} ({lesson['kind']} {lesson.get('number') or ''})", flush=True)
    new = gen(REWRITE, body)
    try:
        checked = gen(CHECK, f"=== הפרק המקורי ===\n{body}\n\n=== הגרסה המשוכתבת ===\n{new}")
        if safe(body, checked):
            new = checked
    except Exception as e:  # noqa: BLE001 - keep the first rewrite if the check itself fails
        print(f"check failed: {e}", flush=True)
    if not safe(body, new):
        print(f"rejected: rewrite of {lesson['id']} lost content - chapter kept as it was", flush=True)
        return False
    mark(sb, lesson, md)
    sb.table("lessons").update({"chapter_md": new.strip() + tail}).eq("id", lesson["id"]).execute()
    print("saved", flush=True)
    return True


def run(only=None):
    sb = db()
    q = sb.table("lessons").select("id, user_id, kind, number, chapter_md").eq("status", "ready").in_("kind", ["lecture", "practice"])
    if only:
        q = q.eq("id", only)
    lessons = q.order("created_at").execute().data
    for lesson in lessons:
        if not lesson.get("chapter_md") or done(sb, lesson):
            continue
        try:
            enrich(sb, lesson)
        except Exception as e:  # noqa: BLE001
            msg = author.friendly_error(e)
            print(f"::warning title=Enrich {lesson['id']}::{msg[:300]}", flush=True)
            if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota", "המכסה"):
                print("daily Gemini quota used up - the rest continue on the next run", flush=True)
                return


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
