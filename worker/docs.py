"""Formula sheets built by themselves (no button): every course whose exam allows a formula sheet gets one, rebuilt
when new lessons are ready. Same document as the app's "📄 דף נוסחאות" (web/src/lib/courseDocs.ts, keep the prompt in step).

  python docs.py     (run by the daily site run, after the chapters and exercises)
"""
import os
import re
from datetime import datetime, timezone

import author

BUCKET = "study"
FILE = "formula_sheet.md"
TITLE = "📄 דף נוסחאות"
ALLOWED = re.compile(r"דף נוסחאות|דפי נוסחאות|formula sheet", re.I)

FORMULAS = """בנה דף נוסחאות למבחן בקורס, מכל החומר המצורף (תקצירים ופרקים של כל השיעורים עד עכשיו).
הדף צריך להיכנס בשני עמודי A4 (דף אחד דו-צדדי, כמו שמותר להביא למבחן), ולכן:
- מסודר לפי נושאים (כותרות ### קצרות), בסדר שבו נלמדו.
- כל הנוסחאות, ההגדרות הקצרות, היחידות, תנאי השימוש ("נכון רק כאשר...") והטריקים שהמרצה הראה לפתרון תרגילים.
- כל משוואה בשורה נפרדת $$...$$. טבלאות Markdown כשזה חוסך מקום (למשל השוואה בין מקרים).
- בלי הסברים ארוכים ובלי דוגמאות - רק מה שצריך מול תרגיל במבחן.
- רק מה שהופיע בחומר. בדוק כל נוסחה (ממדים, סימנים, מקדמים) - טעות בדף נוסחאות עולה ציון.
- בסוף: "### טעויות נפוצות" - 3-6 שורות.
החזר רק את הדף (Markdown), בלי הקדמה."""


def db():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def allows_sheet(sb, course):
    facts = sb.table("course_facts").select("text").eq("course_id", course["id"]).execute().data
    return any(ALLOWED.search(f["text"] or "") for f in facts) or bool(ALLOWED.search(course.get("notes") or ""))


def build(sb, course, lessons):
    from google.genai import types
    text = "\n\n".join(f"######## {l['kind']} {l.get('number') or ''} {l.get('title') or ''}\n{(l.get('chapter_md') or '')[:40000]}"
                       for l in lessons)

    def call(client, model):
        return client.models.generate_content(model=model, contents=[types.Content(role="user", parts=[
            types.Part.from_text(text=f"קורס: {course['name']}\n\n{FORMULAS}"), types.Part.from_text(text=text)])],
            config=types.GenerateContentConfig(http_options=types.HttpOptions(timeout=12 * 60 * 1000)))
    md = re.sub(r"^```(?:markdown|md)?\s*|\s*```$", "", (author._with_gemini(call).text or "").strip())
    if not md:
        return
    stamp = f"> נבנה {datetime.now(timezone.utc):%d/%m/%Y} מ-{len(lessons)} שיעורים (מתעדכן לבד כשנוספים שיעורים).\n\n"
    path = f"{course['user_id']}/materials/{course['id']}/{FILE}"
    sb.storage.from_(BUCKET).upload(path, (stamp + md).encode("utf-8"),
                                    {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
    if not sb.table("materials").select("id").eq("storage_path", path).execute().data:
        sb.table("materials").insert({"user_id": course["user_id"], "course_id": course["id"], "title": TITLE,
                                      "kind": "other", "storage_path": path, "mime": "text/plain"}).execute()
    print(f"::notice title=Formula sheet::{course['name']}: built from {len(lessons)} lessons", flush=True)


def run():
    sb = db()
    for course in sb.table("courses").select("id, name, user_id, notes, kind").eq("archived", False).neq("kind", "self").execute().data:
        if course["kind"] == "lab" or not allows_sheet(sb, course):
            continue
        lessons = (sb.table("lessons").select("id, kind, number, title, chapter_md, updated_at").eq("course_id", course["id"])
                   .eq("status", "ready").in_("kind", ["lecture", "practice"]).order("created_at").execute().data)
        if not lessons:
            continue
        path = f"{course['user_id']}/materials/{course['id']}/{FILE}"
        built = next((f for f in sb.storage.from_(BUCKET).list(path.rsplit("/", 1)[0], {"limit": 1000}) if f.get("name") == FILE), None)
        newest = max(l["updated_at"] for l in lessons)
        if built and (built.get("updated_at") or "") >= newest:
            continue  # up to date
        try:
            build(sb, course, lessons)
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Formula sheet {course['name']}::{str(e)[:300]}", flush=True)
            if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota", "המכסה"):
                return


if __name__ == "__main__":
    run()
