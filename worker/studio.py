"""Studio: a podcast, a video or everyday examples made from lesson chapters, inside the app.

  python studio.py <media_id>

The app inserts a `lesson_media` row (kind podcast / video / examples, lesson_ids) and dispatches media.yml.
Gemini writes a script from the (already fact-checked) chapters, a second pass checks it, and Gemini TTS
records it in Hebrew with two voices. Video = the lesson's board snapshots, each shown while it is discussed.
"""
import json
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


def tts(lines, work, n):
    """Records one chunk of 'Noa: ...' lines with two voices; returns a WAV path."""
    from google import genai
    from google.genai import types
    text = "קראו את השיחה הבאה בעברית, בטון חם, טבעי ולימודי:\n" + "\n".join(lines)
    cfg = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
            speaker_voice_configs=[types.SpeakerVoiceConfig(
                speaker=name, voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=v)))
                for name, v in VOICES.items()])))
    last = None
    for key in author._keys():
        client = genai.Client(api_key=key)
        for model in TTS_MODELS:
            for attempt in range(3):
                try:
                    resp = client.models.generate_content(model=model, contents=text, config=cfg)
                    pcm = resp.candidates[0].content.parts[0].inline_data.data
                    raw = work / f"chunk_{n:03d}.pcm"
                    raw.write_bytes(pcm)
                    wav = work / f"chunk_{n:03d}.wav"
                    media.run_ffmpeg(["-f", "s16le", "-ar", "24000", "-ac", "1", "-i", str(raw), str(wav)])
                    return wav
                except Exception as e:  # noqa: BLE001
                    last = e
                    if author._is(e, "UNAVAILABLE", "503", "overloaded") and attempt < 2:
                        time.sleep(5 * (attempt + 1) ** 2)
                        continue
                    if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota", "NOT_FOUND", "404", "not supported", "INVALID_ARGUMENT"):
                        print(f"tts {model}: {str(e)[:150]} -> next", flush=True)
                        break
                    raise
    raise RuntimeError(author.friendly_error(last))


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

        slides = slide_list(job, work) if kind == "video" else {}
        if kind == "video" and not slides:
            raise RuntimeError("לשיעור הזה אין צילומי לוח בפרק, אז אין ממה לבנות סרטון - אפשר ליצור פודקאסט")
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
                   duration_sec=media.duration(out), progress="מוכן")
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
