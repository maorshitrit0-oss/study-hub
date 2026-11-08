"""Studio: a podcast, a video or everyday examples made from lesson chapters, inside the app.

  python studio.py <media_id>

The app inserts a `lesson_media` row (kind podcast / video / examples, lesson_ids) and dispatches media.yml.
Gemini writes a script from the (already fact-checked) chapters, a second pass checks it, and Gemini TTS
records it in Hebrew with two voices. Video = the lesson's board snapshots, each shown while it is discussed.
"""
import json
import re
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from supabase import create_client

import author
import media
import notify

BUCKET = "study"
# Hebrew is supported by the 3.8 TTS models (checked 24/10/2026); older ones are a fallback.
TTS_MODELS = ["gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts", "gemini-2.5-flash-preview-tts"]
VOICES = {"Noa": "Kore", "Dan": "Puck"}  # host who explains (female) and host who asks (male)
HEB = {"נועה": "Noa", "דן": "Dan"}
CHUNK_CHARS = 2200  # text per TTS request

SCRIPT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "segments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "speaker": {"type": "string", "enum": ["נועה", "דן"]},
                    "text": {"type": "string"},
                    "slide": {"type": "integer"},
                },
                "required": ["speaker", "text"],
            },
        },
    },
    "required": ["title", "segments"],
}

PODCAST = """אתה כותב תסריט לפודקאסט לימודי בעברית לסטודנט להנדסת חשמל, על בסיס פרקי הקריאה המצורפים (שכבר נבדקו).
שני מגישים: נועה - מסבירה ברורה ומדויקת; דן - סטודנט סקרן ששואל את השאלות שהמאזין היה שואל, ולפעמים טועה ונועה מתקנת אותו.
- כסה את כל הנושאים החשובים לפי הסדר, מהאינטואיציה ועד ההגדרות, ומה חשוב למבחן.
- לכל נושא: דוגמה מחיי היום-יום שבה זה באמת פועל (מזגן, טלפון, מטען, מחשב, רכב, וויי-פיי...) - רק דוגמאות נכונות ומדויקות.
- זה נשמע ולא נקרא: אין LaTeX, אין סימנים ואין טבלאות. נוסחה - במילים ("המתח שווה לזרם כפול ההתנגדות"), ומשתנים בשמם.
- מונחים: בעברית, ובפעם הראשונה גם המונח באנגלית.
- משפטים קצרים וטבעיים; כל קטע (segment) - 1-4 משפטים של דובר אחד.
- רק מה שבחומר ונכון. אם המרצה טעה והפרק מציין את זה - אמרו את הנכון.
- סיום: סיכום של 3-5 נקודות מפתח.
"""

VIDEO_EXTRA = """זה גם סרטון: מצורפת רשימת צילומי הלוח (מספר ותיאור מהפרק). לכל קטע ציין בשדה slide את מספר הצילום שמוצג בזמן שמדברים עליו
(אותו מספר לכמה קטעים ברצף; עוברים לצילום הבא כשעוברים לנושא שלו). השתמש רק במספרים מהרשימה."""

EXAMPLES = """לפרק הקריאה המצורף, כתוב בעברית (Markdown) רקע ודוגמאות לכל נושא מרכזי, לפי סדר הפרק. הסטודנט מבין רק דרך דוגמאות.
לכל נושא - כותרת ### עם שם הנושא, ומתחתיה:
- **רקע:** למה הנושא קיים ואיזו בעיה הוא פותר - 2-3 משפטים פשוטים, בלי מונחים שעוד לא הוסברו.
- **🏠 מהחיים:** מכשיר או מצב אמיתי שבו זה פועל בפועל (מזגן, טלפון, מטען, מחשב, רכב, רמזור, וויי-פיי...), ואיך בדיוק הנושא מופיע בו.
- **איך לזכור:** משפט אחד שמחבר את הנושא לדוגמה.
רק דוגמאות נכונות מבחינה הנדסית - אם אינך בטוח, בחר דוגמה אחרת. נוסחאות קצרות ב-$...$."""

CHECK = """אתה בודק עובדות קפדן בהנדסת חשמל. קיבלת את חומר המקור (פרקים שנבדקו) ותוצר שנכתב ממנו (תסריט או דוגמאות).
תקן כל טענה, מספר, הסבר או דוגמה מחיי היום-יום שאינם נכונים או לא תואמים למקור; הסר מה שאי אפשר לתקן בוודאות.
החזר את התוצר המתוקן המלא באותו מבנה בדיוק (אל תקצר)."""


def db():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


class Job:
    def __init__(self, media_id):
        self.sb = db()
        self.row = self.sb.table("lesson_media").select("*").eq("id", media_id).single().execute().data
        ids = self.row["lesson_ids"]
        self.lessons = (self.sb.table("lessons").select("id, kind, number, title, chapter_md, slide_count, user_id, course_id")
                        .in_("id", ids).order("created_at").execute().data)
        self.course = self.sb.table("courses").select("name").eq("id", self.row["course_id"]).single().execute().data

    def update(self, **f):
        self.sb.table("lesson_media").update(f).eq("id", self.row["id"]).execute()

    def log(self, msg):
        print(msg, flush=True)
        self.update(progress=msg)


def label(lesson):
    kinds = {"lecture": "הרצאה", "practice": "תרגול", "lab": "ניסוי", "web": "מאמר", "other": "חומר"}
    return f"{kinds.get(lesson['kind'], '')} {lesson.get('number') or ''}".strip() + (f" - {lesson['title']}" if lesson.get("title") else "")


def source_text(job):
    parts = [f"קורס: {job.course['name']}"]
    for l in job.lessons:
        parts.append(f"\n\n######## {label(l)}\n{l['chapter_md'] or ''}")
    return "".join(parts)


def gen_json(system, prompt, schema):
    from google.genai import types
    return author._generate_json([types.Part.from_text(text=prompt)], system, schema, "LOW")


def gen_text(system, prompt):
    from google.genai import types

    def call(client, model):
        return client.models.generate_content(model=model, contents=prompt,
                                              config=types.GenerateContentConfig(system_instruction=system))
    return (author._with_gemini(call).text or "").strip()


VOICE_ENGINE = {"name": None}  # set by the first chunk; the rest of the file uses the same voices


def tts(lines, work, n):
    """Records one chunk of 'Noa: ...' lines with two voices; returns a WAV path.
    Plain REST, not the SDK: google-genai 3.0 sends speech_config in a shape the API rejects
    ("Unknown name speechConfig at generation_config", his screenshot 08/11/2026); the REST body below works."""
    import base64
    import requests
    text = "קראו את השיחה הבאה בעברית, בטון חם, טבעי ולימודי:\n" + "\n".join(lines)
    body = {"contents": [{"parts": [{"text": text}]}], "generationConfig": {
        "responseModalities": ["AUDIO"],
        "speechConfig": {"multiSpeakerVoiceConfig": {"speakerVoiceConfigs": [
            {"speaker": name, "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": v}}} for name, v in VOICES.items()]}}}}
    def body_for(model):
        """2.5 models take the whole dialogue as one text; 3.x models want one part per line, each marked with its
        speaker (speechMetadata.speaker); no system instruction allowed (API error texts, 08/11/2026)."""
        if not model.startswith("gemini-3"):
            return body
        parts = []
        for ln in lines:
            who, _, said = ln.partition(":")
            parts.append({"text": said.strip(), "speechMetadata": {"speaker": who.strip() if who.strip() in VOICES else "Noa"}})
        return {"contents": [{"role": "user", "parts": parts}], "generationConfig": body["generationConfig"]}

    last = None
    if VOICE_ENGINE["name"] == "edge":
        return edge_tts(lines, work, n)
    for key in author._keys():
        for model in TTS_MODELS:
            for attempt in range(3):
                try:
                    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                      params={"key": key}, json=body_for(model), timeout=600)
                    if not r.ok:
                        raise RuntimeError(f"{r.status_code} {r.text[:300]}")
                    part = r.json()["candidates"][0]["content"]["parts"][0]
                    pcm = base64.b64decode(part["inlineData"]["data"])
                    raw = work / f"chunk_{n:03d}.pcm"
                    raw.write_bytes(pcm)
                    wav = work / f"chunk_{n:03d}.wav"
                    media.run_ffmpeg(["-f", "s16le", "-ar", "24000", "-ac", "1", "-i", str(raw), str(wav)])
                    VOICE_ENGINE["name"] = "gemini"
                    return wav
                except Exception as e:  # noqa: BLE001
                    last = e
                    if author._is(e, "UNAVAILABLE", "503", "500", "overloaded", "disconnected", "timed out", "Connection reset") and attempt < 2:
                        time.sleep(5 * (attempt + 1) ** 2)
                        continue
                    if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota", "NOT_FOUND", "404", "not supported", "INVALID_ARGUMENT", "400"):
                        print(f"tts {model}: {str(e)[:150]} -> next", flush=True)
                        break
                    raise
    # Gemini's free speech quota is gone (08/11/2026: every podcast/video failed on it): Microsoft's free neural
    # Hebrew voices (edge-tts, no key, no daily quota) - Hila for Noa, Avri for Dan.
    if VOICE_ENGINE["name"] == "gemini":  # Gemini ran out half way: never mix voices - the file waits for the reset
        raise RuntimeError(author.friendly_error(last))
    try:
        wav = edge_tts(lines, work, n)
        VOICE_ENGINE["name"] = "edge"
        return wav
    except Exception as e:  # noqa: BLE001
        print(f"edge-tts: {str(e)[:200]}", flush=True)
    raise RuntimeError(author.friendly_error(last))


EDGE_VOICES = {"Noa": "he-IL-HilaNeural", "Dan": "he-IL-AvriNeural"}


def edge_tts(lines, work, n):
    """The same chunk with Microsoft's Hebrew voices, line by line, joined into one WAV (24 kHz mono, like Gemini's)."""
    import asyncio
    import edge_tts as et
    parts = []
    for i, ln in enumerate(lines):
        who, _, said = ln.partition(":")
        said = said.strip()
        if not said:
            continue
        voice = EDGE_VOICES.get(who.strip(), EDGE_VOICES["Noa"])
        # Formulas / markdown give the service nothing to say ("No audio was received"): clean, split into sentences,
        # and a piece that still fails is skipped instead of failing the whole podcast.
        clean = re.sub(r"[$\\{}_^*#`|<>\[\]]", " ", said)
        clean = re.sub(r"\s+", " ", clean).strip()
        for j, piece in enumerate(re.split(r"(?<=[.!?…])\s+", clean)):
            if not re.search(r"[\w\u0590-\u05FF]", piece):
                continue
            mp3 = work / f"edge_{n:03d}_{i:03d}_{j:02d}.mp3"
            try:
                asyncio.run(et.Communicate(piece, voice, rate="+5%").save(str(mp3)))
                if mp3.exists() and mp3.stat().st_size > 0:
                    parts.append(mp3)
            except Exception as e:  # noqa: BLE001
                print(f"edge-tts skipped a piece ({str(e)[:60]}): {piece[:60]}", flush=True)
    if not parts:
        raise RuntimeError("no text")
    lst = work / f"edge_{n:03d}.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    wav = work / f"chunk_{n:03d}.wav"
    media.run_ffmpeg(["-f", "concat", "-safe", "0", "-i", str(lst), "-ar", "24000", "-ac", "1", str(wav)])
    print(f"tts chunk {n}: edge-tts ({len(parts)} lines)", flush=True)
    return wav


def chunks(segments, by_slide):
    """Groups segments into TTS requests: by size, and for video also whenever the slide changes."""
    out, cur, size, slide = [], [], 0, None
    for s in segments:
        line = f"{HEB.get(s['speaker'], 'Noa')}: {s['text'].strip()}"
        new_slide = by_slide and s.get("slide") and s["slide"] != slide and cur
        if cur and (size + len(line) > CHUNK_CHARS or new_slide):
            out.append((slide, cur))
            cur, size = [], 0
        if by_slide and s.get("slide"):
            slide = s["slide"]
        cur.append(line)
        size += len(line)
    if cur:
        out.append((slide, cur))
    return out


def slide_list(job, work):
    """Board snapshots the chapters show (number -> local file, description)."""
    import re
    found = {}
    lesson = job.lessons[0]
    for m in re.finditer(r"!\[([^\]]*)\]\(slide:(\d+)\)", lesson["chapter_md"] or ""):
        n = int(m[2])
        if n in found:
            continue
        p = work / f"slide_{n:03d}.webp"
        try:
            p.write_bytes(job.sb.storage.from_(BUCKET).download(f"{lesson['user_id']}/lessons/{lesson['id']}/slide_{n:03d}.webp"))
            found[n] = (p, m[1])
        except Exception:  # noqa: BLE001
            pass
    return found


def pdf_slides(job, work):
    """The pages of the lecture's slides file in the course files ("הרצאה 2.pdf" for lecture 2): number -> (image,
    the page's first words). Used for the video when the recording has no board snapshots."""
    import re
    import fitz  # PyMuPDF
    import requests
    lesson = job.lessons[0]
    if not lesson.get("number"):
        return {}
    rx = re.compile(rf"הרצאה\s*{lesson['number']}(?!\d)")
    mats = [m for m in job.sb.table("materials").select("title, storage_path").eq("course_id", lesson["course_id"]).execute().data
            if rx.search(m["title"] or "") and (m["title"] or "").lower().endswith(".pdf")]
    if not mats:
        return {}
    path = mats[0]["storage_path"]
    if path.startswith("drive:"):
        data = requests.get("https://drive.google.com/uc", params={"export": "download", "id": path[6:]}, timeout=300).content
    else:
        data = job.sb.storage.from_(BUCKET).download(path)
    doc = fitz.open(stream=data, filetype="pdf")
    found = {}
    for i, page in enumerate(doc, start=1):
        if i > 80:
            break
        img = work / f"page_{i:03d}.png"
        zoom = 1280 / max(page.rect.width, 1)
        page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)).save(str(img))
        words = " ".join(page.get_text().split())[:140] or f"שקף {i}"
        found[i] = (img, words)
    print(f"video from the slides file '{mats[0]['title']}': {len(found)} pages", flush=True)
    return found


def make_script(job, kind, slides):
    src = source_text(job)
    system = PODCAST + (VIDEO_EXTRA if kind == "video" else "")
    minutes = 8 if len(job.lessons) == 1 else min(25, 6 + 4 * len(job.lessons))
    prompt = f"{src}\n\nאורך: כ-{minutes} דקות דיבור (בערך {minutes * 130} מילים)."
    if kind == "video":
        prompt += "\n\nצילומי הלוח:\n" + "\n".join(f"{n}: {d}" for n, (_, d) in sorted(slides.items()))
    job.log("כותב תסריט...")
    script = gen_json(system, prompt, SCRIPT_SCHEMA)
    job.log("בודק את התסריט מול הפרקים...")
    try:
        checked = gen_json(CHECK, f"=== המקור ===\n{src}\n\n=== התוצר (JSON) ===\n{json.dumps(script, ensure_ascii=False)}", SCRIPT_SCHEMA)
        if checked.get("segments"):
            script = checked
    except Exception as e:  # noqa: BLE001 - keep the first script rather than fail
        print(f"script check failed: {e}", flush=True)
    segs = [s for s in script.get("segments") or [] if s.get("text")]
    if kind == "video":
        for s in segs:
            if s.get("slide") not in slides:
                s.pop("slide", None)
    return script.get("title") or "", segs


def concat_audio(wavs, out):
    lst = out.parent / "list.txt"
    lst.write_text("".join(f"file '{w}'\n" for w in wavs))
    media.run_ffmpeg(["-f", "concat", "-safe", "0", "-i", str(lst), "-c:a", "libmp3lame", "-b:a", "64k", "-ac", "1", str(out)])


EXPLAINER = """אתה מורה מצוין שבונה סרטון הסבר (כמו Video Overview של NotebookLM) בעברית, לסטודנט להנדסת חשמל שלא ראה את ההרצאה,
על בסיס הפרקים המצורפים (נבדקו). הסרטון הוא רצף שקפים; לכל שקף כותרת, עד 4 נקודות קצרות, נוסחה אחת לכל היותר, ודיבור.
- לפחות 12 שקפים (עד 18), כ-6-8 דקות דיבור: פתיחה (מה נלמד ולמה זה חשוב) ← לכל נושא 2-3 שקפים: אינטואיציה עם דימוי
  מהחיים, הגדרה + נוסחה (ומה כל אות בה), ודוגמה מספרית שפותרים צעד אחר צעד (מהתרגילים המצורפים כשיש) ← שקף "טעויות
  נפוצות" ← סיכום "מה חשוב למבחן". אסור שקף של "שאלות ראיון" או מידע מנהלי - רק החומר עצמו.
- bullets: משפטים קצרים מאוד (עד 8 מילים), בעברית; מונח באנגלית בסוגריים.
- formula: נוסחת LaTeX אחת (בלי $), או ריק.
- page: מספר מרשימת העמודים/צילומים המצורפת אם יש עמוד שמראה בדיוק את הנושא (שרטוט, גרף, טבלה), אחרת 0.
- visual: תיאור **באנגלית** של איור המחשה לשקף (כמו ב-NotebookLM): סצנה או תרשים ברור שממחיש את הרעיון - למשל
  "a clean infographic: a plane wave traveling along z, red E-field arrows along x, blue H-field arrows along y, wavefronts",
  או דימוי מהחיים ("a microwave oven heating food, waves penetrating a few centimeters"). בלי טקסט ובלי אותיות באיור. ריק = בלי איור.
- diagram: קוד Python קצר (matplotlib) שמצייר שרטוט הנדסי מדויק שממחיש את השקף - גל מישורי עם חיצי E ו-H, דעיכה
  e^{-alpha z} עם עומק החדירה מסומן, אליפסת קיטוב, גל פוגע/מוחזר/עובר בממשק, וקטורים ומכפלה וקטורית, גרף של פונקציה וכו'.
  כבר מוגדרים: np, plt, fig, ax (רקע כהה כבר מוגדר). מציירים רק על ax (או ax3d = fig.add_subplot(projection='3d') אם צריך תלת-ממד).
  תוויות באנגלית בלבד (בלי עברית); כל סימון מתמטי בתווית חייב להיות בתוך $...$ (למשל r'$\\vec{E}$', r'$e^{-\\alpha z}$'),
  בלי \\text ובלי \\boldsymbol (matplotlib לא מכיר - השתמש ב-\\mathrm). צבעים בהירים, קווים עבים. בלי import, בלי קבצים, בלי show/savefig. ריק = בלי שרטוט.
  בשקף שיש בו diagram לא צריך visual.
- steps: בשקף של דוגמה פתורה - 3-6 שלבים קצרים שמופיעים אחד אחרי השני על המסך (כל שלב: משוואת LaTeX עם הצבה ותוצאה,
  בלי $). בשקף רגיל - ריק. הדיבור בשקף כזה עובר על השלבים לפי הסדר.
- narration: מה שהמורה אומר בזמן השקף, 4-7 משפטים טבעיים, כמו מורה טוב שמסביר לחבר - מסביר למה, לא רק מה. זה **נשמע** ולא נקרא:
  * בלי סימנים, בלי LaTeX, בלי קיצורים. נוסחה במילים ("השדה המגנטי שווה לשדה החשמלי חלקי אטא").
  * כל מילה באותיות עבריות כמו שהיא נשמעת: "פאזור", "וקטור פוינטינג", "מקסוול", "אטא", "בטא", "אלפא", "סיגמא", "אפסילון", "מיו", "גאמא".
    בלי מילים באותיות לטיניות בכלל - גם לא שמות משתנים (במקום E כתוב "אי" או "השדה החשמלי").
  * מספרים במילים כשהם קצרים ("שלוש מאות שבעים ושבעה אוהם").
- רק מה שבחומר ונכון; אם המרצה טעה והפרק מציין - אומרים את הנכון."""

EXPLAINER_SCHEMA = {"type": "object", "properties": {"title": {"type": "string"}, "slides": {"type": "array", "minItems": 12, "items": {
    "type": "object", "properties": {"title": {"type": "string"}, "bullets": {"type": "array", "items": {"type": "string"}},
                                     "formula": {"type": "string"}, "page": {"type": "integer"}, "narration": {"type": "string"},
                                     "visual": {"type": "string"}, "diagram": {"type": "string"},
                                     "steps": {"type": "array", "items": {"type": "string"}}},
    "required": ["title", "bullets", "narration"]}}}, "required": ["title", "slides"]}

SLIDE_CSS = """*{box-sizing:border-box}html,body{overflow:hidden}body{margin:0;width:1280px;height:720px;position:relative;background:linear-gradient(135deg,#0b1d3a,#06142a);
color:#eef2fb;font-family:Heebo,'DejaVu Sans',Arial,sans-serif;direction:rtl;display:flex;flex-direction:column;padding:48px 64px}
h1{font-size:46px;margin:0 0 26px;color:#9fc3ff;border-bottom:3px solid #2b4466;padding-bottom:14px}
.row{display:flex;gap:36px;flex:1;min-height:0;padding-bottom:96px}.txt{flex:1;min-width:0;display:flex;flex-direction:column;justify-content:center;overflow:hidden}
ul{margin:0;padding-right:30px}li{font-size:33px;line-height:1.45;margin:8px 0}
.f{direction:ltr;text-align:center;font-size:40px;margin-top:26px;background:#0e2547;border-radius:16px;padding:18px}
.s{font-size:30px;margin-top:12px;padding:10px}.s:last-child{border:2px solid #f5b84b}
.img{flex:0 0 500px;width:500px;display:flex;align-items:center;justify-content:center;overflow:hidden}.img img{max-width:500px;max-height:440px;object-fit:contain;border-radius:12px}
.sub{position:absolute;left:0;right:0;bottom:0;min-height:92px;padding:14px 60px;background:rgba(0,0,0,.72);color:#fff;font-size:28px;
line-height:1.35;text-align:center;display:flex;align-items:center;justify-content:center}
.n{position:absolute;bottom:22px;left:40px;font-size:18px;color:#6f86ad}"""


def render_slides(slides, pages, work, katex=None):
    """Each slide as a 1280x720 PNG (title, points, one formula in KaTeX, and the lecture page/board picture if given)."""
    import base64
    import html as h
    from playwright.sync_api import sync_playwright
    # KaTeX from a local copy (media.yml unpacks it; 08/11/2026 the CDN did not load in time and formulas showed as code)
    katex = katex or ("file://" + os.environ["KATEX_DIR"] if os.environ.get("KATEX_DIR") else "https://cdn.jsdelivr.net/npm/katex@0.16.47/dist")
    out = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get("PW_CHROMIUM") or None)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        for i, sl in enumerate(slides):
            pic = sl.get("_img") and (sl["_img"], "") or pages.get(sl.get("page") or 0)
            img = ""
            if pic:
                mime = "image/webp" if str(pic[0]).endswith(".webp") else "image/png"
                img = f'<div class="img"><img src="data:{mime};base64,{base64.b64encode(Path(pic[0]).read_bytes()).decode()}"></div>'
            bullets = "".join(f"<li>{h.escape(b)}</li>" for b in (sl.get("bullets") or [])[:4])
            formula = (sl.get("formula") or "").strip()
            fdiv = f'<div class="f" id="f">{h.escape(formula)}</div>' if formula else ""
            if sl.get("_steps") is not None:  # a worked example: the first k steps, each rendered by KaTeX
                bullets = ""
                fdiv = "".join(f'<div class="f s">{h.escape(x)}</div>' for x in sl["_steps"])
            html_file = work / f"xs_{i:03d}.html"
            html_file.write_text(f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;700&display=swap">
<link rel="stylesheet" href="{katex}/katex.min.css"><script src="{katex}/katex.min.js"></script>
<style>{SLIDE_CSS}</style></head><body><h1>{h.escape(sl.get('title') or '')}</h1>
<div class="row"><div class="txt"><ul>{bullets}</ul>{fdiv}</div>{img}</div>
{f'<div class="sub">{h.escape(sl["_sub"])}</div>' if sl.get("_sub") else ""}
<script>for (const f of document.querySelectorAll('.f')) {{ try {{ katex.render(f.textContent, f, {{displayMode:true, throwOnError:false}}); }} catch(e) {{}} }}
document.fonts.ready.then(()=>document.body.dataset.ready='1');</script></body></html>""", encoding="utf-8")
            page.goto(f"file://{html_file}", wait_until="load")
            try:  # KaTeX and the font from the CDN; a slow CDN must not stop the video
                page.wait_for_function("document.body.dataset.ready === '1'", timeout=20000)
            except Exception as e:  # noqa: BLE001
                print(f"slide {i + 1}: not fully ready ({str(e)[:80]}) - shot anyway", flush=True)
            png = work / f"xs_{i:03d}.png"
            page.screenshot(path=str(png))
            out.append(png)
        browser.close()
    return out


def make_explainer(job, pages, work, out):
    """The video: an explainer slide deck (made here, not from raw board photos) with one narrator, slide by slide."""
    src = source_text(job)
    try:  # the lesson's exercises with their (checked) solutions: worked examples for the video
        ex = job.sb.table("exercises").select("title, question_md, solution_md").in_("lesson_id", [l["id"] for l in job.lessons]).execute().data
        if ex:
            src += "\n\n######## תרגילים פתורים\n" + "\n\n".join(f"### {x['title']}\n{x['question_md']}\n{(x.get('solution_md') or '')[:3000]}" for x in ex[:6])
    except Exception:  # noqa: BLE001
        pass
    listing = "\n".join(f"{n}: {d}" for n, (_, d) in sorted(pages.items()))
    job.log("כותב את סרטון ההסבר...")
    script = gen_json(EXPLAINER, f"{src}\n\nעמודים/צילומים שאפשר להציג (מספר: תיאור):\n{listing or 'אין'}", EXPLAINER_SCHEMA)
    job.log("בודק את התסריט מול הפרקים...")
    try:
        checked = gen_json(CHECK, f"=== המקור ===\n{src}\n\n=== התוצר (JSON) ===\n{json.dumps(script, ensure_ascii=False)}", EXPLAINER_SCHEMA)
        if len(checked.get("slides") or []) >= len(script.get("slides") or []) * 0.8:
            script = checked
    except Exception as e:  # noqa: BLE001
        print(f"explainer check failed: {e}", flush=True)
    slides = [s for s in script.get("slides") or [] if (s.get("narration") or "").strip()]
    if not slides:
        raise RuntimeError("התסריט יצא ריק - לנסות שוב")
    job.log("מקליט את הקריינות...")
    wavs = narrate(slides, work)  # natural Gemini voice only; raises on quota (the video waits for the reset)
    job.log("מצייר שרטוטים...")
    for i, sl in enumerate(slides):
        if (sl.get("diagram") or "").strip() and not sl.get("steps"):
            img = draw_diagram(sl["diagram"], work / f"dia_{i:03d}.png")
            if img:
                sl["_img"] = img
    made = 0
    for i, sl in enumerate(slides):
        if sl.get("_img"):
            continue
        if (sl.get("visual") or "").strip() and made < 10 and not sl.get("steps"):
            img = illustrate(sl["visual"], work / f"ill_{i:03d}.png")
            if img:
                sl["_img"], made = img, made + 1
    job.log("מעצב שקפים...")
    shots, audio, PAD = [], [], 0.5
    for i, (sl, wav) in enumerate(zip(slides, wavs)):
        steps = [x for x in (sl.get("steps") or []) if x.strip()][:6]
        sents = [x.strip() for x in re.split(r"(?<=[.!?…])\s+", sl["narration"].strip()) if x.strip()] or [sl["narration"]]
        frames = []
        for j, sent in enumerate(sents):  # subtitles: one sentence at a time; example steps appear over the sentences
            f = dict(sl, _sub=sent)
            if steps:
                f["_steps"] = steps[:min(len(steps), 1 + j * len(steps) // len(sents))]
            frames.append(f)
        pngs = render_slides(frames, pages, _mk(work / f"r{i:03d}"))
        dur = media.duration(wav) or 1
        weights = [max(len(x), 8) for x in sents]
        bounds = [0.0] + split_points(wav, dur, weights, window=2.5, min_gap=0.6) + [dur]  # subtitle changes at real pauses
        bounds[-1] = dur + PAD
        padded = work / f"pad_{i:03d}.wav"  # the slide's voice + a short breath, same format for every piece
        media.run_ffmpeg(["-i", str(wav), "-af", f"apad=pad_dur={PAD}", "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", str(padded)])
        audio.append(padded)
        for j, png in enumerate(pngs):
            shots.append((png, bounds[j + 1] - bounds[j]))
    # ONE image track with exact cumulative times and ONE continuous audio track, muxed once: gluing ~100 short AAC clips
    # drifted by tens of ms per clip (seconds by the end) - his remark 08/11/2026 "המלל לא בקצב של המצגות".
    vl = work / "ximgs.txt"
    vl.write_text("".join(f"file '{p}'\nduration {d:.3f}\n" for p, d in shots) + f"file '{shots[-1][0]}'\n")
    al = work / "xaudio.txt"
    al.write_text("".join(f"file '{a}'\n" for a in audio))
    media.run_ffmpeg(["-f", "concat", "-safe", "0", "-i", str(vl), "-f", "concat", "-safe", "0", "-i", str(al),
                      "-map", "0:v", "-map", "1:a", "-vf", "fps=10,scale=1280:720,setsar=1,format=yuv420p",
                      "-c:v", "libx264", "-tune", "stillimage", "-g", "20", "-c:a", "aac", "-b:a", "96k", "-ar", "24000",
                      "-ac", "1", "-shortest", "-movflags", "+faststart", str(out)])
    md = "\n\n".join(f"**{i + 1}. {s['title']}**\n\n{s['narration']}" for i, s in enumerate(slides))
    return script.get("title") or "", md


def _mk(d):
    d.mkdir(parents=True, exist_ok=True)
    return d


DIAGRAM_RUNNER = """
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"figure.facecolor": "#0b1d3a", "axes.facecolor": "#0b1d3a", "savefig.facecolor": "#0b1d3a",
    "text.color": "#eef2fb", "axes.labelcolor": "#eef2fb", "xtick.color": "#9fb3d6", "ytick.color": "#9fb3d6",
    "axes.edgecolor": "#3a5682", "font.size": 15, "lines.linewidth": 3})
fig = plt.figure(figsize=(7.5, 6), dpi=110)
ax = fig.add_subplot(111)
exec(open(__import__("sys").argv[1], encoding="utf-8").read())
fig.tight_layout()
fig.savefig(__import__("sys").argv[2])
"""


def draw_diagram(code, out):
    """Runs the slide's matplotlib code in a separate process with NO environment (no keys) and a time limit."""
    src = out.with_suffix(".py")
    src.write_text(code, encoding="utf-8")
    runner = out.parent / "diagram_runner.py"
    runner.write_text(DIAGRAM_RUNNER, encoding="utf-8")
    try:
        p = subprocess.run([sys.executable, str(runner), str(src), str(out)], env={"PATH": "/usr/bin:/bin", "MPLBACKEND": "Agg",
                           "HOME": str(out.parent)}, capture_output=True, text=True, timeout=60)
        if p.returncode == 0 and out.exists() and out.stat().st_size > 2000:
            return out
        print(f"diagram failed: {p.stderr[-300:]}", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"diagram failed: {str(e)[:200]}", flush=True)
    return None


def illustrate(prompt, out):
    """An illustration for a slide (Gemini image model, free tier); None when there is no quota / no image."""
    import base64
    import requests
    full = ("Educational illustration for an electrical-engineering lecture video, clean modern flat style, dark navy background, "
            "bright accent colors, no text, no letters, no numbers. " + prompt)
    for key in author._keys():
        for model in ("gemini-2.5-flash-image", "gemini-3.1-flash-image", "gemini-nano-banana-2.1"):
            try:
                r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                  params={"key": key}, timeout=240, json={"contents": [{"parts": [{"text": full}]}],
                                                                          "generationConfig": {"responseModalities": ["IMAGE"]}})
                if not r.ok:
                    print(f"image {model}: {r.status_code} {' '.join(r.text.split())[:400]}", flush=True)
                    continue
                for part in r.json()["candidates"][0]["content"]["parts"]:
                    if "inlineData" in part:
                        out.write_bytes(base64.b64decode(part["inlineData"]["data"]))
                        return out
            except Exception as e:  # noqa: BLE001
                print(f"image {model}: {str(e)[:100]}", flush=True)
    return None


def split_points(wav, total, lens, window=None, min_gap=1.0):
    """Where one recording of several slides should be cut: at the real pauses (ffmpeg silencedetect) closest to where
    each slide 'should' end by its share of the text (08/11/2026: proportional cuts drifted off the slides)."""
    guesses, acc = [], 0
    for ln in lens[:-1]:
        acc += ln
        guesses.append(total * acc / sum(lens))
    if not guesses:
        return []
    p = subprocess.run([media.FFMPEG, "-hide_banner", "-i", str(wav), "-af", "silencedetect=noise=-38dB:d=0.25", "-f", "null", "-"],
                       capture_output=True, text=True, errors="ignore")
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", p.stderr)]
    gaps = [((a + b) / 2, b - a) for a, b in zip(starts, ends)]
    win = window or max(6.0, 0.25 * total / len(lens))
    cuts, last = [], 0.0
    for g in guesses:  # the paragraph break between slides is the longest pause: prefer long pauses near the guess
        near = [(m, d) for m, d in gaps if m > last + min_gap and abs(m - g) < win]
        c = min(near, key=lambda x: abs(x[0] - g) - 3 * x[1])[0] if near else g
        cuts.append(c)
        last = c
    return cuts


def narrate(slides, work):
    """One natural Gemini voice for the whole video, a few slides per request (the free quota counts requests); each slide's
    share of a request is cut out by its length. No robotic fallback (his remark 08/11/2026): on quota the video fails and
    is made again after the reset."""
    groups, cur, size = [], [], 0
    for i, sl in enumerate(slides):
        t = sl["narration"].strip()
        if cur and size + len(t) > 1800:
            groups.append(cur)
            cur, size = [], 0
        cur.append(i)
        size += len(t)
    if cur:
        groups.append(cur)
    out = [None] * len(slides)
    for g, idx in enumerate(groups):
        text = "\n\n".join(slides[i]["narration"].strip() for i in idx)
        wav = tts_one(text, work, 100 + g, allow_edge=False)
        total = media.duration(wav) or 1
        lens = [len(slides[i]["narration"]) for i in idx]
        cuts = split_points(wav, total, lens)
        bounds = [0.0] + cuts + [total]
        for k, i in enumerate(idx):
            piece = work / f"nar_{i:03d}.wav"
            media.run_ffmpeg(["-ss", f"{bounds[k]:.3f}", "-t", f"{bounds[k + 1] - bounds[k]:.3f}", "-i", str(wav), str(piece)])
            out[i] = piece
    return out


def tts_one(text, work, n, allow_edge=True):
    """One narrator for the whole video: Gemini 'Kore' (single voice), or Microsoft's Hila for all of it."""
    import base64
    import requests
    if VOICE_ENGINE["name"] != "edge":
        body = {"contents": [{"parts": [{"text": text}]}], "generationConfig": {"responseModalities": ["AUDIO"],
                "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}}}}
        for key in author._keys():
            for model in TTS_MODELS:
                try:
                    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                                      params={"key": key}, json=body, timeout=600)
                    if not r.ok:
                        raise RuntimeError(f"{r.status_code} {r.text[:200]}")
                    pcm = base64.b64decode(r.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
                    raw, wav = work / f"n_{n:03d}.pcm", work / f"n_{n:03d}.wav"
                    raw.write_bytes(pcm)
                    media.run_ffmpeg(["-f", "s16le", "-ar", "24000", "-ac", "1", "-i", str(raw), str(wav)])
                    VOICE_ENGINE["name"] = "gemini"
                    return wav
                except Exception as e:  # noqa: BLE001
                    print(f"tts {model}: {str(e)[:120]}", flush=True)
        if VOICE_ENGINE["name"] == "gemini":
            raise RuntimeError("המכסה של Gemini נגמרה באמצע הסרטון - הוא ייווצר מחדש אחרי האיפוס (כדי לא לערבב קולות)")
    if not allow_edge:
        raise RuntimeError("המכסה היומית של קול Gemini נגמרה - הסרטון ייווצר מחדש לבד אחרי האיפוס (בסביבות 10:00), בקול הטבעי")
    VOICE_ENGINE["name"] = "edge"
    return edge_tts([f"Noa: {text}"], work, n)


def make_video(groups, wavs, slides, out):
    """One clip per group: its slide (or the previous one) for as long as its audio, then concatenated."""
    clips, last = [], None
    first = next(iter(sorted(slides.items())))[1][0]
    for i, ((slide, _), wav) in enumerate(zip(groups, wavs)):
        img = slides[slide][0] if slide in slides else (last or first)
        last = img
        clip = out.parent / f"clip_{i:03d}.mp4"
        media.run_ffmpeg(["-loop", "1", "-i", str(img), "-i", str(wav), "-c:v", "libx264", "-tune", "stillimage",
                          "-r", "2", "-vf", "scale=min(1280\\,iw):-2,pad=ceil(iw/2)*2:ceil(ih/2)*2",
                          "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "64k", "-shortest", str(clip)])
        clips.append(clip)
    lst = out.parent / "clips.txt"
    lst.write_text("".join(f"file '{c}'\n" for c in clips))
    media.run_ffmpeg(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(out)])


def run(media_id):
    job = Job(media_id)
    kind = job.row["kind"]
    uid = job.row["user_id"]
    work = Path(tempfile.mkdtemp(prefix="studio_"))
    try:
        job.update(status="processing", error=None)
        if not job.lessons or not any(l.get("chapter_md") for l in job.lessons):
            raise RuntimeError("אין עדיין פרק קריאה מוכן לשיעורים שנבחרו")
        if kind == "examples":
            job.log("כותב דוגמאות מחיי היום-יום...")
            src = source_text(job)
            md = gen_text(EXAMPLES, src)
            job.log("בודק את הדוגמאות...")
            try:
                md = gen_text(CHECK, f"=== המקור ===\n{src}\n\n=== התוצר ===\n{md}") or md
            except Exception as e:  # noqa: BLE001
                print(f"examples check failed: {e}", flush=True)
            job.update(status="ready", script=md, progress="מוכן")
            notify.send(job.sb, uid, "🏠 דוגמאות מהחיים מוכנות", label(job.lessons[0]), f"/lessons/{job.lessons[0]['id']}")
            return

        if kind == "video":  # an explainer deck with one narrator (08/11/2026: the board-photo videos were poor)
            pages = slide_list(job, work) or pdf_slides(job, work)
            out = work / "out.mp4"
            title, script_md = make_explainer(job, pages, work, out)
            path = f"{uid}/media/{media_id}.mp4"
            job.sb.storage.from_(BUCKET).upload(path, out.read_bytes(), {"content-type": "video/mp4", "upsert": "true"})
            job.update(status="ready", storage_path=path, title=job.row.get("title") or title, script=script_md,
                       duration_sec=round(media.duration(out)), progress="מוכן")
            notify.send(job.sb, uid, "🎬 הסרטון מוכן", title or job.course["name"], f"/lessons/{job.lessons[0]['id']}")
            return
        slides = {}
        title, segs = make_script(job, kind, slides)
        if not segs:
            raise RuntimeError("התסריט יצא ריק - לנסות שוב")
        groups = chunks(segs, kind == "video")
        wavs = []
        for i, (_, lines) in enumerate(groups):
            job.log(f"מקליט ({i + 1}/{len(groups)})...")
            wavs.append(tts(lines, work, i))
        out = work / ("out.mp4" if kind == "video" else "out.mp3")
        job.log("מרכיב את הקובץ...")
        if kind == "video":
            make_video(groups, wavs, slides, out)
        else:
            concat_audio(wavs, out)
        path = f"{uid}/media/{media_id}.{out.suffix[1:]}"
        job.sb.storage.from_(BUCKET).upload(path, out.read_bytes(),
                                            {"content-type": "video/mp4" if kind == "video" else "audio/mpeg", "upsert": "true"})
        script_md = "\n\n".join(f"**{s['speaker']}:** {s['text']}" for s in segs)
        job.update(status="ready", storage_path=path, title=job.row.get("title") or title, script=script_md,
                   duration_sec=round(media.duration(out)), progress="מוכן")
        where = f"/lessons/{job.lessons[0]['id']}" if len(job.lessons) == 1 else f"/courses/{job.row['course_id']}"
        notify.send(job.sb, uid, f"{'🎬 הסרטון' if kind == 'video' else '🎙️ הפודקאסט'} מוכן", title or job.course["name"], where)
    except Exception as e:
        job.update(status="error", error=author.friendly_error(e)[:1500])
        print(f"::error title=Studio {media_id}::{str(e)[:900]}".replace("\n", " "), flush=True)
        raise
    finally:
        subprocess.run(["rm", "-rf", str(work)])


if __name__ == "__main__":
    run(sys.argv[1])
