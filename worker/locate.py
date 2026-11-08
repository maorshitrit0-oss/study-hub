"""Where each exercise comes from, exactly (his request 08/11/2026: "תרשום לי מאיפה זה נלקח מאיזה קובץ ואיזה עמוד").

The exercises table knows the lesson or the file; this finds the PAGE: the exercise's words and numbers are matched
against every page of the file's PDF text (and, for a lecture exercise, against the lecture's slides file "הרצאה N"),
and slide images in a lesson exercise give the slide number. Kept in storage, no schema change:
<user>/materials/<course>/exercise_where.json = {exercise_id: "עמ' 4"}. Only new exercises are looked up.
"""
import json
import re
import tempfile
from pathlib import Path

BUCKET = "study"
WORD = re.compile(r"[א-ת]{3,}|[A-Za-z]{3,}|\d+(?:\.\d+)?")
LATEX = re.compile(r"\\[A-Za-z]+")


def _path(course):
    return f"{course['user_id']}/materials/{course['id']}/exercise_where.json"


def load(sb, course):
    try:
        return json.loads(sb.storage.from_(BUCKET).download(_path(course)).decode())
    except Exception:  # noqa: BLE001 - none yet
        return {}


def save(sb, course, where):
    sb.storage.from_(BUCKET).upload(_path(course), json.dumps(where, ensure_ascii=False).encode("utf-8"),
                                    {"content-type": "application/json", "upsert": "true"})


def tokens(text):
    text = LATEX.sub(" ", text or "")
    return [t.lower() for t in WORD.findall(text)]


def pdf_pages(data):
    """Each page's tokens (a scanned page has none)."""
    import fitz  # PyMuPDF
    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception:  # noqa: BLE001 - not a PDF
        return []
    return [set(tokens(p.get_text())) for p in doc]


def best_page(question, pages):
    """The page (1-based) that holds the question's words, or None. Rare words and numbers weigh more."""
    q = tokens(question)
    if len(q) < 4 or not pages:
        return None
    df = {}
    for p in pages:
        for t in p:
            df[t] = df.get(t, 0) + 1
    qs = set(q)
    score = []
    for p in pages:
        s = sum((2.0 if t[0].isdigit() else 1.0) / df[t] for t in qs if t in p)
        score.append(s)
    top = max(range(len(pages)), key=lambda i: score[i])
    total = sum((2.0 if t[0].isdigit() else 1.0) / df[t] for t in qs if t in df) or 1
    hit = len([t for t in qs if t in pages[top]]) / len(qs)
    if score[top] < 0.35 * total or hit < 0.3:  # not really there (scanned file, or a rewritten question)
        return None
    pages_ = [top + 1]
    if top + 1 < len(pages) and score[top + 1] > 0.6 * score[top]:  # a question that runs onto the next page
        pages_.append(top + 2)
    return pages_


def page_text(nums):
    return f"עמ' {nums[0]}" if len(nums) == 1 else f"עמ' {nums[0]}-{nums[-1]}"


def run(sb, course, log=print):
    import exercises as ex
    where = load(sb, course)
    rows = sb.table("exercises").select("id, lesson_id, material_id, title, question_md").eq("course_id", course["id"]).execute().data
    todo = [r for r in rows if r["id"] not in where]
    if not todo:
        return 0
    materials = {m["id"]: m for m in sb.table("materials").select("*").eq("course_id", course["id"]).execute().data}
    lessons = {l["id"]: l for l in sb.table("lessons").select("id, kind, number").eq("course_id", course["id"]).execute().data}
    cache = {}

    def pages_of(m):
        if m["id"] not in cache:
            try:
                data, mime = ex.blob(sb, m, Path(tempfile.mkdtemp(prefix="loc_")))
                cache[m["id"]] = pdf_pages(data) if "pdf" in (mime or "") or data[:4] == b"%PDF" else []
            except Exception as e:  # noqa: BLE001
                log(f"locate: {m['title']}: {str(e)[:150]}")
                cache[m["id"]] = []
        return cache[m["id"]]

    def slides_file(lesson):  # the lecture's slides file: "הרצאה 3.pdf" for lecture 3
        if not lesson or lesson.get("kind") != "lecture" or not lesson.get("number"):
            return None
        rx = re.compile(rf"הרצאה\s*0?{lesson['number']}(?!\d)")
        return next((m for m in materials.values() if rx.search(m["title"] or "")
                     and (m["title"] or "").lower().endswith(".pdf")), None)

    found = 0
    for r in todo:
        parts = []
        q = f"{r.get('title') or ''}\n{r['question_md']}"
        if r.get("material_id") and r["material_id"] in materials:
            nums = best_page(q, pages_of(materials[r["material_id"]]))
            if nums:
                parts.append(page_text(nums))
        if r.get("lesson_id"):
            shots = sorted({int(n) for n in re.findall(r"\(slide:(\d+)\)", r["question_md"] or "")})
            if shots:
                parts.append("צילום לוח " + ", ".join(map(str, shots)) + " מההקלטה")
            m = slides_file(lessons.get(r["lesson_id"]))
            if m:
                nums = best_page(q, pages_of(m))
                if nums:
                    parts.append(f"במצגת {m['title']}, {page_text(nums)}")
        where[r["id"]] = " · ".join(parts)  # "" = looked, nothing exact (shown with the file/lesson name only)
        found += bool(parts)
    save(sb, course, where)
    log(f"::notice title=Exercise sources::{course['name']}: {found}/{len(todo)} new exercises located to a page")
    return found
