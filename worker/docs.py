"""Formula sheets built by themselves (no button): every course whose exam allows a formula sheet gets one, rebuilt
when new lessons are ready. Same document as the app's "📄 דף נוסחאות" (web/src/lib/courseDocs.ts, keep the prompt in step).

  python docs.py              (run by the daily site run, after the chapters and exercises)
  python docs.py <course_id>   that course only; when its sheet is up to date, only its PDF is made again

Every save also renders the sheet as a PDF to print (sheet_pdf.py, his request 08/11/2026). A sheet Claude wrote
(stamp "נכתב ע״י Claude") is never rewritten by Gemini: new lessons only ADD to it (FORMULAS_UPDATE), like Java's.
"""
import json
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


# Code courses (Java, 04/11/2026): the sheet is a syntax help sheet - templates of how to write each thing - written
# by Claude (hub.py sheet); new lessons only ADD to it.
CODE = re.compile(r"ג'אווה|ג׳אווה|java", re.I)
CODE_UPDATE = """לפניך דף עזר תחביר למבחן בקורס תכנות (Java), ולפניו כל השיעורים עד עכשיו.
עדכן את הדף: הוסף כל תחביר, תבנית, מתודת ספרייה, כלל או טעות נפוצה שנלמדו בשיעורים וחסרים בדף - באותו סגנון
(בלוק קוד קצר עם הערה בעברית בסוף כל שורה, או שורה קצרה), במקום המתאים לפי הנושא.
אל תמחק ואל תקצר שום דבר שכבר בדף. הדף צריך להישאר בשני עמודי A4. בדוק שכל קוד נכון ומתהדר.
החזר רק את הדף המלא (Markdown), בלי הקדמה."""


FORMULAS_UPDATE = """לפניך דף נוסחאות למבחן פתוח בקורס, שנכתב ונבדק בקפידה, ולפניו כל השיעורים עד עכשיו.
עדכן אותו רק בתוספות: כל נוסחה, הגדרה, תנאי שימוש או טריק משיעור שעוד לא נמצאים בדף - בסעיף המתאים לפי הנושא,
עם תג המקור בסוגריים כמו בדף (ה4 = הרצאה 4, ת4 = תרגול 4). לכל סוג תרגיל חדש שנפתר בשיעורים - שורה בטבלה
"מה שואלים ← מה עושים" (נותנים/שואלים | הדרך | מקור). טעות של המרצה או המתרגל - שורה עם ⚠️ ומה נכון.
אל תמחק, אל תקצר ואל תנסח מחדש שום דבר שכבר בדף. בלי כפילויות: מה שכבר כתוב (גם בסימון אחר) לא נוסף שוב.
כל משוואה ב-$$...$$ בשורה נפרדת וקצרה (משוואה ארוכה - לפצל לשתי שורות). בדוק כל נוסחה (ממדים, סימנים, מקדמים).
החזר רק את הדף המלא (Markdown), בלי הקדמה."""
CLAUDE_MARK = "נכתב ע״י Claude"


def db():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def allows_sheet(sb, course):
    facts = sb.table("course_facts").select("text").eq("course_id", course["id"]).execute().data
    return any(ALLOWED.search(f["text"] or "") for f in facts) or bool(ALLOWED.search(course.get("notes") or ""))


def formula_notes(sb, course):
    """Formulas read from the course files (worker/exercises.py), by file."""
    try:
        return json.loads(sb.storage.from_(BUCKET).download(f"{course['user_id']}/materials/{course['id']}/formula_notes.json").decode())
    except Exception:  # noqa: BLE001
        return {}


def build(sb, course, lessons):
    from google.genai import types
    text = "\n\n".join(f"######## {l['kind']} {l.get('number') or ''} {l.get('title') or ''}\n{(l.get('chapter_md') or '')[:40000]}"
                       for l in lessons)
    notes = formula_notes(sb, course)
    if notes:
        text += "\n\n######## נוסחאות מקבצי הקורס (מצגות, חוברות, מבחנים)\n" + "\n".join(
            f"[{name}] {f}" for name, fs in notes.items() for f in fs)

    claude = CLAUDE_MARK in stamp(sb, course)
    base = current(sb, course) if CODE.search(course["name"] or "") or claude else ""
    update = CODE_UPDATE if CODE.search(course["name"] or "") else FORMULAS_UPDATE
    prompt = f"{update}\n\n=== הדף הנוכחי ===\n{base}" if base else FORMULAS

    def call(client, model):
        return client.models.generate_content(model=model, contents=[types.Content(role="user", parts=[
            types.Part.from_text(text=f"קורס: {course['name']}\n\n{prompt}"), types.Part.from_text(text=text)])],
            config=types.GenerateContentConfig(http_options=types.HttpOptions(timeout=12 * 60 * 1000)))
    md = re.sub(r"^```(?:markdown|md)?\s*|\s*```$", "", (author._with_gemini(call).text or "").strip())
    if not md:
        return
    if base and len(md) < 0.9 * len(base):  # the update lost content: keep the sheet as it is
        print(f"::warning title=Formula sheet {course['name']}::update rejected (shorter than the sheet)", flush=True)
        return
    save(sb, course, md, f"{CLAUDE_MARK} + תוספות מ-{len(lessons)} שיעורים" if claude else f"מ-{len(lessons)} שיעורים")


def stamp(sb, course):
    """The sheet's first line ("> נבנה <date> <how>"), or ''."""
    try:
        return sb.storage.from_(BUCKET).download(f"{course['user_id']}/materials/{course['id']}/{FILE}").decode().split("\n", 1)[0]
    except Exception:  # noqa: BLE001
        return ""


def current(sb, course):
    """The sheet as it is now, without its date line."""
    try:
        md = sb.storage.from_(BUCKET).download(f"{course['user_id']}/materials/{course['id']}/{FILE}").decode()
    except Exception:  # noqa: BLE001
        return ""
    return re.sub(r"^> נבנה .*\n\n", "", md)


def save(sb, course, md, how):
    stamp = f"> נבנה {datetime.now(timezone.utc):%d/%m/%Y} {how} (מתעדכן לבד כשנוספים שיעורים).\n\n"
    path = f"{course['user_id']}/materials/{course['id']}/{FILE}"
    sb.storage.from_(BUCKET).upload(path, (stamp + md).encode("utf-8"),
                                    {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
    if not sb.table("materials").select("id").eq("storage_path", path).execute().data:
        sb.table("materials").insert({"user_id": course["user_id"], "course_id": course["id"], "title": TITLE,
                                      "kind": "other", "storage_path": path, "mime": "text/plain"}).execute()
    print(f"::notice title=Formula sheet::{course['name']}: {how}", flush=True)
    pdf(sb, course, md)


def pdf(sb, course, md):
    """The printable PDF next to it; a failure here never loses the sheet."""
    try:
        import sheet_pdf
        sheet_pdf.publish(sb, course, md)
    except Exception as e:  # noqa: BLE001
        print(f"::warning title=Formula sheet PDF {course['name']}::{str(e)[:300]}", flush=True)


def run(only=None):
    sb = db()
    q = sb.table("courses").select("id, name, user_id, notes, kind").eq("archived", False).neq("kind", "self")
    for course in (q.eq("id", only) if only else q).execute().data:
        if course["kind"] == "lab" or not allows_sheet(sb, course):
            continue
        lessons = (sb.table("lessons").select("id, kind, number, title, chapter_md, updated_at").eq("course_id", course["id"])
                   .eq("status", "ready").in_("kind", ["lecture", "practice"]).order("created_at").execute().data)
        if not lessons:
            continue
        path = f"{course['user_id']}/materials/{course['id']}/{FILE}"
        listing = sb.storage.from_(BUCKET).list(path.rsplit("/", 1)[0], {"limit": 1000})
        built = next((f for f in listing if f.get("name") == FILE), None)
        notes = next((f for f in listing if f.get("name") == "formula_notes.json"), None)
        # Rebuilt when a lesson or a file with formulas came after the last build.
        newest = max([l["updated_at"] for l in lessons] + ([notes.get("updated_at") or ""] if notes else []))
        if built and (built.get("updated_at") or "") >= newest:
            have_pdf = any(f.get("name") == "formula_sheet.pdf" for f in listing)
            if only or not have_pdf:  # asked for this course, or the PDF is missing: make the PDF again
                pdf(sb, course, current(sb, course))
            continue  # up to date
        try:
            build(sb, course, lessons)
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Formula sheet {course['name']}::{str(e)[:300]}", flush=True)
            if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota", "המכסה"):
                return


if __name__ == "__main__":
    import sys
    run(sys.argv[1] if len(sys.argv) > 1 else None)
