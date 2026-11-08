"""Study Hub worker CLI.

  python hub.py process <lesson_id> [--no-author]   download/transcribe (or fetch a web page), then author with Gemini
  python hub.py queued                              list lessons waiting to be processed
  python hub.py fetch <lesson_id> <out_dir>         download transcript + slides (for authoring with Claude)
  python hub.py publish <lesson_id> <chapter.json>  save a chapter written elsewhere (e.g. by Claude)

Needs SUPABASE_URL and SUPABASE_SERVICE_KEY; GEMINI_API_KEY for automatic authoring.
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from supabase import create_client

import author
import course_site
import media
import notify

BUCKET = "study"


def db():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def now():
    return datetime.now(timezone.utc).isoformat()


class Job:
    def __init__(self, lesson_id):
        self.sb = db()
        self.lesson = self.sb.table("lessons").select("*").eq("id", lesson_id).single().execute().data
        self.course = self.sb.table("courses").select("*").eq("id", self.lesson["course_id"]).single().execute().data
        self.prefix = f"{self.lesson['user_id']}/lessons/{lesson_id}"
        self.mode = os.environ.get("AUTHOR_MODE", "auto")  # "full" = he asked for the full chapter of this lesson

    def update(self, **fields):
        fields["updated_at"] = now()
        self.sb.table("lessons").update(fields).eq("id", self.lesson["id"]).execute()
        self.lesson.update(fields)

    def log(self, msg):
        print(msg, flush=True)
        self.update(progress=msg)

    def label(self):
        kinds = {"lecture": "הרצאה", "practice": "תרגול", "lab": "ניסוי", "web": "מאמר", "other": "חומר"}
        num = f" {self.lesson['number']}" if self.lesson.get("number") else ""
        return f"{kinds.get(self.lesson['kind'], '')}{num} · {self.course['name']}"

    def previous_topics(self):
        rows = (self.sb.table("lessons").select("topics").eq("course_id", self.course["id"])
                .neq("id", self.lesson["id"]).eq("status", "ready").order("created_at").execute().data)
        return [t for r in rows for t in (r["topics"] or [])]


def transcript_with_markers(segments, slides):
    """Merge whisper segments into ~45s paragraphs with slide markers in place."""
    events = [(start, 0, n) for n, start, _ in slides] + [(s, 1, (s, e, txt)) for s, e, txt in segments]
    events.sort(key=lambda x: (x[0], x[1]))
    lines, para, para_start = [], [], None

    def flush():
        nonlocal para, para_start
        if para:
            lines.append(f"[{media.fmt_time(para_start)}] " + " ".join(para))
        para, para_start = [], None

    for t, kind, payload in events:
        if kind == 0:
            flush()
            lines.append(f"===== שקף {payload} (צולם ב-{media.fmt_time(t)} - מראה את מה שהוסבר עד כאן) =====")
        else:
            para_start = t if para_start is None else para_start
            para.append(payload[2])
            if payload[1] - para_start > 45:
                flush()
    flush()
    return "\n\n".join(lines)


def fetch_web(url):
    import trafilatura
    html = trafilatura.fetch_url(url)
    text = trafilatura.extract(html, include_formatting=True, include_tables=True, output_format="markdown") if html else None
    if not text:
        raise RuntimeError("לא הצלחתי לקרוא את תוכן הדף")
    return text


def cmd_process(lesson_id, do_author=True):
    job = Job(lesson_id)
    work = Path(tempfile.mkdtemp(prefix="hub_"))
    try:
        job.update(status="processing", error=None)
        slides, docs = [], []
        url = job.lesson.get("source_url") or ""
        if do_author:
            try:  # start last year's lecture N now, so it transcribes in parallel with this one
                course_site.previous_lecture(job.sb, job.lesson)
            except Exception as e:  # noqa: BLE001
                print(f"previous year lookup failed: {e}", flush=True)
        source = None
        reuse = bool(job.lesson.get("transcript")) and do_author
        if reuse:
            # A retry after the chapter step failed: reuse the transcript and snapshots instead of
            # downloading and transcribing the recording again (that takes ~0.4x its length).
            # Lessons made from a course site (course_site.py) start here: their text is the transcript.
            transcript = job.lesson["transcript"]
            from_site = transcript.startswith(course_site.SITE_NOTE)
            job.log("קורא את החומר מאתר הקורס..." if from_site else "משתמש בתמלול שכבר נעשה...")
            slides = load_slides(job, work)
            for path in course_site.FILE_REF.findall(transcript):
                data = job.sb.storage.from_(BUCKET).download(path)
                if sum(len(d) for d, _ in docs) + len(data) < 18 * 1024 * 1024:  # Gemini's inline request limit
                    docs.append((data, "application/pdf"))
            transcript = course_site.FILE_REF.sub("", transcript).replace(course_site.SITE_NOTE, "").strip()
        elif job.lesson.get("source_path"):  # a file uploaded in the app (lab booklet, prelab...)
            job.log("מוריד את הקובץ...")
            source = work / Path(job.lesson["source_path"]).name
            source.write_bytes(job.sb.storage.from_(BUCKET).download(job.lesson["source_path"]))
        elif media.is_drive(url):
            source = media.download_drive(url, work, log=job.log)

        if reuse:
            pass
        elif source is not None and not media.is_video(source):
            docs = [(source.read_bytes(), media.mime_of(source))]
            transcript = ""
        elif job.lesson["kind"] == "web":
            job.log("קורא את הדף...")
            transcript = fetch_web(url)
        elif media.is_youtube(url):
            # YouTube refuses GitHub's servers, but Gemini reads YouTube videos itself (official video input).
            transcript = media.transcribe_youtube(url, log=job.log)
        else:
            if source is not None:
                video = audio = source
                title = source.stem
            else:
                video, audio, title = media.download(url, work, log=job.log)
            length = media.duration(audio)
            if length:
                # Measured on GitHub's runners: ~0.4 minutes of processing per minute of recording.
                job.log(f"אורך ההקלטה {media.fmt_time(length)} · זמן עיבוד משוער: כ-{max(5, round(length * 0.4 / 60))} דקות")
            if media.has_video(video):
                job.log("מזהה שקפים / מצבי לוח...")
                scenes = media.detect_slides(video, log=job.log)
                slides = media.save_slides(video, scenes, work)
            else:  # sound only (e.g. a WhatsApp recording of the lecturer): straight to the transcript
                slides = []
            job.log(f"מעלה {len(slides)} צילומי לוח...")
            store = job.sb.storage.from_(BUCKET)
            for n, _, p in slides:
                store.upload(f"{job.prefix}/{p.name}", p.read_bytes(),
                             {"content-type": "image/webp", "upsert": "true"})
            job.update(slide_count=len(slides))
            segments = media.transcribe_local(audio, log=job.log)
            transcript = transcript_with_markers(segments, slides)
            # He may have named it ("חלק 1") while it was downloading: never overwrite his title.
            fresh = job.sb.table("lessons").select("title").eq("id", job.lesson["id"]).single().execute().data
            if not fresh.get("title"):
                job.update(title=title)
        if not reuse:
            job.update(transcript=transcript, status="transcribed", progress="התמלול מוכן")

        if do_author and os.environ.get("GEMINI_API_KEY"):
            transcript = with_previous_year(job, transcript)
            ch = author.author_with_gemini(job.course, job.lesson, transcript,
                                           [(n, p) for n, _, p in slides], job.previous_topics(), log=job.log, docs=docs,
                                           mode=job.mode)
            save_chapter(job, ch, "gemini")
        elif "(להשוואה)" in (job.lesson.get("title") or ""):
            job.log("התמלול מוכן - משמש להשוואה עם ההרצאה של השנה")
        else:
            job.log("התמלול מוכן - מחכה לכתיבת הפרק (Claude)")
    except Exception as e:
        job.update(status="error", error=author.friendly_error(e)[:2000])
        # GitHub annotation: readable through the API even where full logs are not.
        print(f"::error title=Lesson {lesson_id}::{str(e)[:900]}".replace("\n", " "), flush=True)
        # Overloads are retried by themselves; a background fill (queue_runner, QUIET) never pushes.
        # No push for Gemini being busy or out of quota: the queue retries those by itself (05/11/2026 - he got
        # "העיבוד נכשל" every few minutes while the queue was retrying).
        if not os.environ.get("QUIET") and not author._is(e, "UNAVAILABLE", "503", "overloaded", "high demand", "עמוסים",
                                                          "RESOURCE_EXHAUSTED", "429", "quota", "מכסה", "INTERNAL"):
            notify.send(job.sb, job.lesson["user_id"], f"⚠️ העיבוד נכשל: {job.label()}",
                        "לחץ כדי לראות מה קרה ולנסות שוב", f"/lessons/{job.lesson['id']}")
        raise
    finally:
        shutil.rmtree(work, ignore_errors=True)


COMPARE = """=== ההרצאה המקבילה משנה שעברה (אותו מרצה, אותו מספר הרצאה) - להשוואה ===
המקור העיקרי לפרק הוא ההרצאה של השנה (למעלה). השתמש בהרצאה משנה שעברה כך:
- הסבר או דוגמה משנה שעברה על **אותו נושא** שמבהירים יותר - הוסף במקום המתאים, מסומן "📼 משנה שעברה:".
- אם הנושאים שונים (הסדר השתנה) - אל תערבב; ציין זאת בסעיף ההשוואה.
- בסוף הפרק, לפני השאלות: "## 🔄 השוואה להרצאה משנה שעברה" - מה נוסף השנה, מה הושמט, מה הוסבר אחרת,
  ומה מופיע רק משנה שעברה (מסומן כך - ייתכן שלא יהיה במבחן של השנה).
"""


def with_previous_year(job, transcript):
    """Lecture N of a course with an imported site: add last year's lecture N (waits up to an hour for its transcript)."""
    try:
        prev = course_site.previous_lecture(job.sb, job.lesson)
    except Exception as e:  # noqa: BLE001 - the comparison is a bonus, never a reason to fail
        print(f"previous year lookup failed: {e}", flush=True)
        return transcript
    if not prev:
        return transcript
    for _ in range(60):  # it started with this job; a 3-hour Zoom takes ~65 minutes
        row = job.sb.table("lessons").select("transcript, status").eq("id", prev["id"]).single().execute().data
        if row.get("transcript") or row["status"] == "error":
            break
        job.log("מחכה לתמלול ההרצאה המקבילה משנה שעברה (להשוואה)...")
        time.sleep(60)
    if not row.get("transcript"):
        job.log("ההרצאה משנה שעברה עוד לא מוכנה - כותב בלי השוואה")
        return transcript
    # Its board snapshots are not attached here: drop their markers so no image of the wrong lecture is cited.
    prev_text = re.sub(r"^===== שקף \d+ .*$", "", row["transcript"], flags=re.M)
    return f"{transcript}\n\n{COMPARE}\n{prev_text}"


def load_slides(job, work):
    """The lesson's board snapshots from storage, as (number, start, path) like media.save_slides."""
    store, slides = job.sb.storage.from_(BUCKET), []
    for n in range(1, (job.lesson.get("slide_count") or 0) + 1):
        p = work / f"slide_{n:03d}.webp"
        try:
            p.write_bytes(store.download(f"{job.prefix}/{p.name}"))
            slides.append((n, None, p))
        except Exception:  # noqa: BLE001
            pass
    return slides


def save_exercises(job, exercises):
    """The lesson's exercises (summary mode). Ones he already marked solved stay as they are."""
    try:
        kept = (job.sb.table("exercises").select("title").eq("lesson_id", job.lesson["id"])
                .not_.is_("done_at", "null").execute().data)
        job.sb.table("exercises").delete().eq("lesson_id", job.lesson["id"]).is_("done_at", "null").execute()
    except Exception as e:  # noqa: BLE001 - database without the exercises table yet (supabase/exercises.sql)
        print(f"exercises not saved: {e}", flush=True)
        return
    done = {k["title"] for k in kept}
    rows = [{
        "user_id": job.lesson["user_id"], "course_id": job.course["id"], "lesson_id": job.lesson["id"], "source": "lesson",
        "ord": i, "title": x.get("title"), "question_md": x["question_md"], "solution_md": x.get("solution_md"),
        "topic": x.get("topic"), "exam_style": bool(x.get("exam_style")), "uncertain": bool(x.get("uncertain")),
    } for i, x in enumerate(exercises) if x.get("title") not in done]
    if rows:
        job.sb.table("exercises").insert(rows).execute()


def next_class(sb, course_id):
    """Start of the course's next class (any kind) in the timetable, ISO; a week from now if none is set."""
    from datetime import timedelta
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("Asia/Jerusalem")
    now = datetime.now(tz)
    slots = sb.table("schedule_slots").select("weekday, start_time").eq("course_id", course_id).execute().data
    for k in range(1, 15):
        d = now + timedelta(days=k)
        todays = sorted(s["start_time"] for s in slots if s["weekday"] == (d.weekday() + 1) % 7)
        if todays:
            h, m = map(int, todays[0][:5].split(":"))
            return d.replace(hour=h, minute=m, second=0, microsecond=0).isoformat()
    return (now + timedelta(days=7)).isoformat()


def save_homework(job, items):
    """What the lecturer / TA asked to do by next time -> tasks due at the course's next class."""
    if not items:
        return
    due = next_class(job.sb, job.course["id"])
    rows = [{"user_id": job.lesson["user_id"], "course_id": job.course["id"], "kind": "assignment",
             "title": f"📝 {text[:180]}", "due_at": due, "done": False,
             "notes": f"נאמר ב{job.label()}. עד השיעור הבא (אם נאמר מועד אחר - לעדכן).",
             "external_uid": f"hw:{job.lesson['id']}:{i}"} for i, text in enumerate(items) if text.strip()]
    try:
        job.sb.table("deadlines").upsert(rows, on_conflict="user_id,external_uid", ignore_duplicates=True).execute()
    except Exception as e:  # noqa: BLE001
        print(f"homework tasks not saved: {e}", flush=True)


def mark_progress(lesson_id, text):
    db().table("lessons").update({"status": "processing", "progress": text, "error": None}).eq("id", lesson_id).execute()


def answered(job):
    """Has he answered any question of this lesson's own quiz?"""
    ids = [q["id"] for q in job.sb.table("questions").select("id").eq("lesson_id", job.lesson["id"]).execute().data]
    if not ids:
        return False
    return bool(job.sb.table("attempts").select("id").in_("question_id", ids[:500]).limit(1).execute().data)


# Courses where every new lecture gets a podcast and a video by itself (his request 08/11/2026: he listens to the
# podcast and watches the video first, then reads). Gemini TTS - the free quota is shared with the chapters.
AUTO_STUDIO = re.compile(r"(?!x)x")  # off (08/11/2026): he found our videos/podcasts poor - NotebookLM instead; was r"גלים ומערכות"


def auto_studio(job):
    """Once per lecture: a podcast and a video (lesson_media rows + media.yml), never twice for the same lesson."""
    les, course = job.lesson, job.course
    if les.get("kind") != "lecture" or not AUTO_STUDIO.search(course.get("name") or "") \
            or (les.get("transcript") or "").startswith(course_site.SITE_NOTE) or os.environ.get("QUIET"):
        return
    try:
        have = job.sb.table("lesson_media").select("id, kind, status").contains("lesson_ids", [les["id"]]).execute().data
        for kind in ("podcast", "video"):
            old = [m for m in have if m["kind"] == kind]
            if any(m["status"] != "error" for m in old):
                continue
            if old:  # it failed before (e.g. the TTS bug of 08/11/2026): the same item goes again
                job.sb.table("lesson_media").update({"status": "queued", "error": None}).eq("id", old[0]["id"]).execute()
                print(f"studio {kind} again: {course_site.dispatch_inputs('media.yml', {'media_id': old[0]['id']})}", flush=True)
                continue
            row = job.sb.table("lesson_media").insert({"user_id": les["user_id"], "course_id": course["id"], "kind": kind,
                                                       "lesson_ids": [les["id"]]}).execute().data[0]
            print(f"studio {kind}: {course_site.dispatch_inputs('media.yml', {'media_id': row['id']})}", flush=True)
    except Exception as e:  # noqa: BLE001 - the chapter is saved; the studio is an extra
        print(f"::warning title=Auto studio::{str(e)[:200]}", flush=True)


def save_chapter(job, ch, by):
    ch = author.validate(ch)
    short = bool(ch.get("exercises")) or (by != "claude" and author.summary_mode(job.lesson, job.mode, job.course))
    if short:
        save_exercises(job, ch["exercises"])
        if not (job.lesson.get("transcript") or "").startswith(author.VLSI_NOTE):  # no "homework" in self-study
            save_homework(job, [h for h in ch.get("homework") or [] if isinstance(h, str)])
    if ch["questions"] and answered(job):
        # He already answered this lesson's quiz: replacing it would delete his answers (attempts cascade) - his
        # study history is never deleted (05/11/2026). The old quiz stays.
        print("quiz kept: it already has his answers", flush=True)
    elif ch["questions"]:
        # Only the chapter's own quiz is replaced: lab entry-quiz questions (source set) stay. A summary has no quiz,
        # so an earlier quiz of the lesson is kept.
        try:
            job.sb.table("questions").delete().eq("lesson_id", job.lesson["id"]).is_("source", "null").execute()
        except Exception:  # noqa: BLE001 - database without the source column yet (supabase/entry_quiz.sql)
            job.sb.table("questions").delete().eq("lesson_id", job.lesson["id"]).execute()
        job.sb.table("questions").insert([{
            "user_id": job.lesson["user_id"], "course_id": job.course["id"], "lesson_id": job.lesson["id"],
            "topic": q.get("topic"), "question": q["question"], "options": q["options"],
            "correct": q["correct"], "explanation": q.get("explanation"), "difficulty": q.get("difficulty", 2),
        } for q in ch["questions"]]).execute()
    save_course_facts(job, ch)
    save_glossary(job, ch)
    chapter_md = ch["chapter_md"] + (author.verification_md(ch) if ch.get("verification") else "")
    count = f"{len(ch['exercises'])} תרגילים" if short else f"{len(ch['questions'])} שאלות"
    fields = dict(chapter_md=chapter_md, topics=ch["topics"], status="ready",
                  syllabus_covered=[i for i in ch.get("syllabus_covered") or [] if isinstance(i, int)],
                  progress=f"מוכן - {count}", author=by, error=None)
    if short:
        fields["summary_md"] = chapter_md  # the full chapter, if he asks for one later, replaces chapter_md only
    if (ch.get("summary_md") or "").strip():  # Claude writes both: the full chapter and a condensed summary
        fields["summary_md"] = author.fix_arabic(ch["summary_md"].strip())
    if not job.lesson.get("title") or job.lesson["kind"] == "web":
        fields["title"] = ch.get("title")
    try:
        job.update(**fields)
    except Exception:  # noqa: BLE001 - database without the syllabus_covered / summary_md column yet
        fields.pop("syllabus_covered", None)
        fields.pop("summary_md", None)
        job.update(**fields)
    try:  # written in the new structure already: enrich.py must not rewrite it
        import enrich
        enrich.mark(job.sb, job.lesson, chapter_md)
    except Exception as e:  # noqa: BLE001
        print(f"structure mark not saved: {e}")
    print(f"published: {count}", flush=True)
    auto_studio(job)
    if (job.lesson.get("transcript") or "").startswith(course_site.SITE_NOTE) or os.environ.get("QUIET"):
        return  # last year's material from the course site / a background fill: no push for each
    notify.send(job.sb, job.lesson["user_id"], f"✅ {job.label()} מוכן" + ("" if short else " לקריאה"),
                f"{ch.get('title') or ''}\n" + (f"תקציר + {count} לפתרון" if short else f"{count} בשאלון"),
                f"/lessons/{job.lesson['id']}")


def save_course_facts(job, ch):
    """Admin info the lecturer mentioned (exam, grading, reservist rules...) collects on the course page."""
    try:
        job.sb.table("course_facts").delete().eq("lesson_id", job.lesson["id"]).execute()
        facts = [f for f in ch.get("course_facts") or [] if f.get("text")]
        if facts:
            job.sb.table("course_facts").insert([{
                "user_id": job.lesson["user_id"], "course_id": job.course["id"], "lesson_id": job.lesson["id"],
                "category": f.get("category") or "other", "text": f["text"],
            } for f in facts]).execute()
        # Fill the course's exam type / weights only if the user hasn't set them.
        update = {}
        if not job.course.get("exam_type") and ch.get("exam_type") in ("mcq", "open", "mixed", "none"):
            update["exam_type"] = ch["exam_type"]
        weights = [w for w in ch.get("grade_weights") or [] if w.get("name") and w.get("weight")]
        if not job.course.get("grade_weights") and weights:
            update["grade_weights"] = weights
        if update:
            job.sb.table("courses").update(update).eq("id", job.course["id"]).execute()
    except Exception as e:  # noqa: BLE001 - the chapter matters more than the facts
        print(f"course facts not saved: {e}")


def save_glossary(job, ch):
    """English terms for the course's vocabulary quiz (the user reads English slowly)."""
    try:
        job.sb.table("glossary").delete().eq("lesson_id", job.lesson["id"]).execute()
        seen, rows = set(), []
        for g in ch.get("glossary") or []:
            key = g["en"].strip().lower()
            if key and key not in seen:
                seen.add(key)
                rows.append({"user_id": job.lesson["user_id"], "course_id": job.course["id"], "lesson_id": job.lesson["id"],
                             "en": g["en"].strip(), "he": g["he"].strip(), "explanation": (g.get("explanation") or "").strip()})
        if rows:
            job.sb.table("glossary").insert(rows).execute()
    except Exception as e:  # noqa: BLE001 - the chapter matters more than the word list
        print(f"glossary not saved: {e}")


def cmd_queued():
    rows = (db().table("lessons").select("id,kind,number,title,status,source_url,course_id,courses(name)")
            .in_("status", ["queued", "transcribed", "error"]).order("created_at").execute().data)
    for r in rows:
        print(f"{r['id']}  {r['status']:11}  {r['courses']['name']} / {r['kind']} {r['number'] or ''}  {r['source_url'] or ''}")


def cmd_fetch(lesson_id, out_dir):
    job = Job(lesson_id)
    out = Path(out_dir)
    (out / "slides").mkdir(parents=True, exist_ok=True)
    (out / "transcript.txt").write_text(job.lesson.get("transcript") or "", encoding="utf-8")
    meta = {"course": job.course, "lesson": {k: v for k, v in job.lesson.items() if k != "transcript"},
            "previous_topics": job.previous_topics()}
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    store = job.sb.storage.from_(BUCKET)
    for n in range(1, (job.lesson.get("slide_count") or 0) + 1):
        name = f"slide_{n:03d}.webp"
        try:
            (out / "slides" / name).write_bytes(store.download(f"{job.prefix}/{name}"))
        except Exception:  # noqa: BLE001 - finished chapters keep only the snapshots they show
            pass
    print(f"fetched to {out}")


def cmd_publish(lesson_id, path):
    save_chapter(Job(lesson_id), json.loads(Path(path).read_text(encoding="utf-8")), "claude")


def find_course(sb, match):
    rx = re.compile(match, re.I)
    courses = [c for c in sb.table("courses").select("*").eq("archived", False).execute().data if rx.search(c.get("name") or "")]
    if len(courses) != 1:
        raise SystemExit(f"course '{match}': {len(courses)} matches ({', '.join(c['name'] for c in courses)})")
    return courses[0]


def cmd_add(match, kind, number, title, path):
    """A lesson written by Claude without a recording (e.g. the Java self-study labs J0-J4): created once in the course
    (kind + number), then published like `publish`. Running it again updates the same lesson."""
    sb = db()
    course = find_course(sb, match)
    have = (sb.table("lessons").select("id").eq("course_id", course["id"]).eq("kind", kind).eq("number", int(number))
            .execute().data)
    if have:
        lesson_id = have[0]["id"]
    else:
        lesson_id = sb.table("lessons").insert({
            "user_id": course["user_id"], "course_id": course["id"], "kind": kind, "number": int(number), "title": title,
            "transcript": "<!-- written by Claude from course files -->", "status": "processing",
            "progress": "Claude כותב את השיעור"}).execute().data[0]["id"]
    cmd_publish(lesson_id, path)
    print(f"::notice title=Added::{course['name']} {kind} {number}: {lesson_id}", flush=True)


def cmd_exercises(match, path):
    """Corrects exercises Claude checked against the lecture's own slides (his screenshot 08/11/2026: an exercise said
    "from lecture 1" but its data was not the lecture's). JSON list of {kind, number, find, title, question_md,
    solution_md}: the exercise of that lesson whose title contains `find` gets the new text; whether he marked it
    solved is kept. Nothing else is touched."""
    sb = db()
    course = find_course(sb, match)
    fields = ("title", "question_md", "solution_md", "topic", "exam_style", "uncertain")
    for fx in json.loads(Path(path).read_text(encoding="utf-8")):
        if fx.get("id"):  # by id (from exercises.json of `hub.py materials`)
            got = sb.table("exercises").update({k: fx[k] for k in fields if k in fx}).eq("id", fx["id"]) \
                .eq("course_id", course["id"]).execute().data
            print(f"::notice title=Exercise {'fixed' if got else 'NOT FOUND'}::{fx.get('title') or fx['id']}", flush=True)
            continue
        if fx.get("add"):  # an exercise the lesson had and the app was missing
            les = (sb.table("lessons").select("id").eq("course_id", course["id"]).eq("kind", fx["kind"])
                   .eq("number", int(fx["number"])).execute().data)
            if len(les) != 1:
                print(f"::warning title=Exercise add::{fx['kind']} {fx['number']}: {len(les)} lessons", flush=True)
                continue
            last = sb.table("exercises").select("ord").eq("lesson_id", les[0]["id"]).order("ord", desc=True).limit(1).execute().data
            sb.table("exercises").insert({"user_id": course["user_id"], "course_id": course["id"], "lesson_id": les[0]["id"],
                                          "source": "lesson", "ord": (last[0]["ord"] + 1) if last else 0,
                                          **{k: fx[k] for k in fields if k in fx}}).execute()
            print(f"::notice title=Exercise added::{fx['kind']} {fx['number']}: {fx.get('title')}", flush=True)
            continue
        lessons = (sb.table("lessons").select("id").eq("course_id", course["id"]).eq("kind", fx["kind"])
                   .eq("number", int(fx["number"])).execute().data)
        hit = [x for l in lessons for x in sb.table("exercises").select("id, title").eq("lesson_id", l["id"]).execute().data
               if fx["find"] in (x.get("title") or "")]
        if len(hit) != 1:
            print(f"::warning title=Exercise fix::{fx['kind']} {fx['number']} '{fx['find']}': {len(hit)} matches", flush=True)
            continue
        sb.table("exercises").update({k: fx[k] for k in ("title", "question_md", "solution_md") if fx.get(k)}) \
            .eq("id", hit[0]["id"]).execute()
        print(f"::notice title=Exercise fixed::{fx['kind']} {fx['number']}: {fx.get('title') or hit[0]['title']}", flush=True)


def cmd_core(match, path):
    """The weekly core exercises (3-5 a week, his request 08/11/2026) of a course: chapters/<course>_core.json ->
    <user>/materials/<course>/exercise_core.json, read by the course's exercises page (the rest is an optional bank)."""
    sb = db()
    course = find_course(sb, match)
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    sb.storage.from_(BUCKET).upload(f"{course['user_id']}/materials/{course['id']}/exercise_core.json",
                                    json.dumps(data, ensure_ascii=False).encode("utf-8"),
                                    {"content-type": "application/json", "upsert": "true"})
    print(f"::notice title=Core exercises::{course['name']}: " + ", ".join(f"week {w}: {len(v)}" for w, v in data["weeks"].items()), flush=True)


def cmd_task(match, title, due_local):
    """A task (deadline) in the course, e.g. a reminder he asked for; due_local 'YYYY-MM-DDTHH:MM' Israel time."""
    from zoneinfo import ZoneInfo
    from datetime import datetime as dt
    sb = db()
    course = find_course(sb, match)
    due = dt.fromisoformat(due_local).replace(tzinfo=ZoneInfo("Asia/Jerusalem")).isoformat()
    sb.table("deadlines").insert({"user_id": course["user_id"], "course_id": course["id"], "kind": "other", "title": title,
                                  "due_at": due, "done": False, "notes": "תזכורת שביקשת מ-Claude"}).execute()
    print(f"::notice title=Task added::{title} ({due_local})", flush=True)


def cmd_drive(match, path):
    """Course files that live in a public Drive folder (e.g. the students' past-exam folder): a materials row per file
    (storage_path "drive:<id>", as the app's "add from Drive" does), once each. JSON list of {id, title, kind}."""
    sb = db()
    course = find_course(sb, match)
    have = {m["storage_path"] for m in sb.table("materials").select("storage_path").eq("course_id", course["id"]).execute().data}
    for f in json.loads(Path(path).read_text(encoding="utf-8")):
        sp = f"drive:{f['id']}"
        if sp in have:
            print(f"already there: {f['title']}", flush=True)
            continue
        sb.table("materials").insert({"user_id": course["user_id"], "course_id": course["id"], "title": f["title"],
                                      "kind": f.get("kind", "other"), "storage_path": sp, "mime": "application/pdf"}).execute()
        print(f"::notice title=Drive file added::{f['title']}", flush=True)


def cmd_studio_retry():
    """Every podcast / video that ended in an error goes again (after a TTS fix)."""
    sb = db()
    names = {c["id"]: c["name"] or "" for c in sb.table("courses").select("id, name").execute().data}
    for m in sb.table("lesson_media").select("id, kind, course_id").eq("status", "error").execute().data:
        if not AUTO_STUDIO.search(names.get(m["course_id"], "")):
            continue  # only the course he asked for (waves)
        sb.table("lesson_media").update({"status": "queued", "error": None}).eq("id", m["id"]).execute()
        print(f"::notice title=Studio retry::{m['kind']} {m['id'][:8]}: {course_site.dispatch_inputs('media.yml', {'media_id': m['id']})}", flush=True)


def cmd_studio_list(drop=""):
    """Every podcast / video with its course, status and length; ids in `drop` (comma list) are removed (row + file)."""
    sb = db()
    names = {c["id"]: c["name"] for c in sb.table("courses").select("id, name").execute().data}
    for m in sb.table("lesson_media").select("id, course_id, kind, status, duration_sec, storage_path, error, created_at").order("created_at").execute().data:
        if drop and m["id"][:8] in drop.split(","):
            if m.get("storage_path"):
                sb.storage.from_(BUCKET).remove([m["storage_path"]])
            sb.table("lesson_media").delete().eq("id", m["id"]).execute()
            print(f"::notice title=Studio removed::{m['kind']} {m['id'][:8]} {names.get(m['course_id'])}", flush=True)
            continue
        real = ""
        if m.get("storage_path") and m["status"] == "ready":
            try:
                p = Path(tempfile.mkdtemp()) / Path(m["storage_path"]).name
                p.write_bytes(sb.storage.from_(BUCKET).download(m["storage_path"]))
                import media as _m
                real = f" file={_m.duration(str(p)):.0f}s size={p.stat().st_size // 1024}KB"
            except Exception as e:  # noqa: BLE001
                real = f" file? {str(e)[:80]}"
        print(f"::notice title=Studio {m['id'][:8]}::{names.get(m['course_id'])} | {m['kind']} | {m['status']} | "
              f"db={m.get('duration_sec')}s{real} | {m['created_at'][:16]} | {(m.get('error') or '')[:80]}", flush=True)


def cmd_studio_backfill(match):
    """A podcast and a video for every ready lecture of the course that has none yet (auto_studio for old lectures)."""
    sb = db()
    course = find_course(sb, match)
    for les in sb.table("lessons").select("*").eq("course_id", course["id"]).eq("kind", "lecture").eq("status", "ready").execute().data:
        class J:  # the bits of a process job auto_studio reads
            pass
        j = J()
        j.sb, j.lesson, j.course = sb, les, course
        print(f"lecture {les.get('number')}:", flush=True)
        auto_studio(j)


def cmd_studio_new(match, number, kind):
    """One podcast / video for lecture N of the course, now (a test or his request)."""
    sb = db()
    course = find_course(sb, match)
    les = (sb.table("lessons").select("id, user_id").eq("course_id", course["id"]).eq("kind", "lecture")
           .eq("number", int(number)).eq("status", "ready").execute().data)
    if not les:
        raise SystemExit(f"no ready lecture {number}")
    row = sb.table("lesson_media").insert({"user_id": les[0]["user_id"], "course_id": course["id"], "kind": kind,
                                           "lesson_ids": [les[0]["id"]]}).execute().data[0]
    print(f"::notice title=Studio new::{kind} lecture {number}: {course_site.dispatch_inputs('media.yml', {'media_id': row['id']})}", flush=True)


def cmd_tts():
    """Which Gemini speech (TTS) models exist for our keys now, and does a two-voice Hebrew line work on each."""
    import asyncio
    try:
        import edge_tts as et
        for v, t in [("he-IL-HilaNeural", "שלום, זו בדיקה."), ("he-IL-AvriNeural", "שלום, זו בדיקה."), ("en-US-AriaNeural", "Hello test.")]:
            for rate in (None, "+5%"):
                out = Path(tempfile.mkdtemp()) / "e.mp3"
                try:
                    c = et.Communicate(t, v, rate=rate) if rate else et.Communicate(t, v)
                    asyncio.run(c.save(str(out)))
                    print(f"::notice title=edge {v} {rate}::ok {out.stat().st_size}B", flush=True)
                except Exception as e:  # noqa: BLE001
                    print(f"::warning title=edge {v} {rate}::{str(e)[:200]}", flush=True)
        print(f"::notice title=edge voices::{[x['ShortName'] for x in asyncio.run(et.list_voices()) if x['Locale'].startswith('he')]}", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"::warning title=edge import::{e}", flush=True)
    from google import genai
    import studio
    client = genai.Client(api_key=author._keys()[0])
    allm = [m.name.split("/")[-1] for m in client.models.list(config={"page_size": 200})]
    print(f"::notice title=All models ({len(allm)})::{', '.join(allm)[:3500]}", flush=True)
    names = [n for n in allm if "tts" in n.lower() or "audio" in n.lower() or "speech" in n.lower()]
    names = names or list(studio.TTS_MODELS)
    import requests
    import google.genai as gg
    print(f"::notice title=SDK::google-genai {getattr(gg, '__version__', '?')}; client has interactions: {hasattr(client, 'interactions')}", flush=True)
    key = author._keys()[0]
    single = {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}}
    probes = [
        ("v1beta", "gemini-3.8-flash-tts", {"responseModalities": ["AUDIO"], "speechConfig": single}),
        ("v1alpha", "gemini-3.8-flash-tts", {"responseModalities": ["AUDIO"], "speechConfig": single}),
        ("v1beta", "gemini-3.8-flash-tts", {"responseModalities": ["AUDIO"]}),
        ("v1beta", "gemini-omni-flash-preview", {"responseModalities": ["AUDIO"]}),
        ("v1beta", "gemini-omni-flash-preview", {"responseModalities": ["AUDIO"], "speechConfig": single}),
    ]
    for ver, model, gc in probes:
        r = requests.post(f"https://generativelanguage.googleapis.com/{ver}/models/{model}:generateContent?key={key}",
                          json={"contents": [{"parts": [{"text": "אמור בעברית: שלום, זו בדיקה."}]}], "generationConfig": gc}, timeout=120)
        body = r.text
        ok = '"inlineData"' in body
        print(f"::notice title=probe {ver} {model} {list(gc)}::{r.status_code} audio={ok} {body[:300] if not ok else ''}", flush=True)
    for ep in ("v1beta/interactions", "v1alpha/interactions"):
        r = requests.post(f"https://generativelanguage.googleapis.com/{ep}?key={key}",
                          json={"model": "gemini-3.8-flash-tts", "input": "שלום, זו בדיקה.", "response_modalities": ["AUDIO"],
                                "generation_config": {"speech_config": [{"voice": "Kore", "language": "he"}]}}, timeout=120)
        print(f"::notice title=probe {ep}::{r.status_code} {r.text[:400]}", flush=True)
    work = Path(tempfile.mkdtemp())
    for name in names[:8]:
        studio.TTS_MODELS[:] = [name]
        try:
            studio.tts(["נועה: שלום, זו בדיקה.", "דן: מעולה, שומעים אותך."], work, 0)
            print(f"::notice title=TTS ok::{name}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=TTS fail {name}::{' '.join(str(e).split())[:600]}", flush=True)


def cmd_sheet(match, path):
    """His course help sheet ("📄 דף נוסחאות" / Java syntax sheet) written by Claude; docs.py later only adds to it."""
    import docs
    sb = db()
    course = find_course(sb, match)
    docs.save(sb, course, Path(path).read_text(encoding="utf-8"), "נכתב ע״י Claude")


def cmd_materials(match, title_rx, out_dir):
    """Downloads a course's files whose title matches (e.g. a practice booklet) into out_dir, with a list."""
    sb = db()
    course = find_course(sb, match)
    rx = re.compile(title_rx, re.I)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = sb.table("materials").select("title, storage_path, created_at").eq("course_id", course["id"]).order("created_at").execute().data
    listing = []
    for m in rows:
        listing.append(f"{m['created_at'][:16]} | {m['title']} | {m['storage_path'][:12]}")
        if rx.search(m["title"] or "") and not m["storage_path"].startswith("drive:"):
            try:
                (out / Path(m["storage_path"]).name).write_bytes(sb.storage.from_(BUCKET).download(m["storage_path"]))
            except Exception as e:  # noqa: BLE001
                listing.append(f"   download failed: {e}")
    lessons = sb.table("lessons").select("id, kind, number, title, status, chapter_md, summary_md").eq("course_id", course["id"]).order("created_at").execute().data
    # Every ready lesson's text and exercises, and the course sheets - for a sheet Claude writes from the whole course.
    (out / "lessons").mkdir(exist_ok=True)
    for l in lessons:
        if l["status"] != "ready":
            continue
        ex = sb.table("exercises").select("title, question_md, solution_md").eq("lesson_id", l["id"]).order("ord").execute().data
        body = (l.get("chapter_md") or "") + ("\n\n# תקציר\n" + l["summary_md"] if l.get("summary_md") and l["summary_md"] != l.get("chapter_md") else "")
        body += "".join(f"\n\n# תרגיל: {x['title']}\n{x['question_md']}\n## פתרון\n{x.get('solution_md') or ''}" for x in ex)
        (out / "lessons" / f"{l['kind']}_{l.get('number') or 0}_{l['id'][:8]}.md").write_text(body, encoding="utf-8")
    for name in ("formula_sheet.md", "formula_notes.json"):
        try:
            (out / name).write_bytes(sb.storage.from_(BUCKET).download(f"{course['user_id']}/materials/{course['id']}/{name}"))
        except Exception:  # noqa: BLE001
            pass
    # Every exercise of the course (from lessons and from files), to check and rewrite (hub.py exercises).
    mats = {m["id"]: m["title"] for m in sb.table("materials").select("id, title").eq("course_id", course["id"]).execute().data}
    by_lesson = {l["id"]: f"{l['kind']} {l.get('number') or 0}" for l in lessons}
    ex_all = (sb.table("exercises").select("id, lesson_id, material_id, source, ord, title, question_md, solution_md, topic, "
                                           "exam_style, uncertain, done_at").eq("course_id", course["id"]).order("ord").execute().data)
    for x in ex_all:
        x["lesson"] = by_lesson.get(x.pop("lesson_id") or "", "")
        x["material"] = mats.get(x.pop("material_id") or "", "")
    (out / "exercises.json").write_text(json.dumps(ex_all, ensure_ascii=False, indent=1), encoding="utf-8")
    for l in lessons:
        l.pop("chapter_md", None), l.pop("summary_md", None)
    (out / "course.json").write_text(json.dumps({"course": course, "files": listing, "lessons": lessons}, ensure_ascii=False,
                                                indent=1, default=str), encoding="utf-8")


def cmd_ping():
    """Is Gemini answering right now? One tiny call per model and key (no retries)."""
    from google import genai
    for k, key in enumerate(author._keys()):
        client = genai.Client(api_key=key)
        for model in author._models():
            t = time.time()
            try:
                r = client.models.generate_content(model=model, contents="ענה במילה אחת: שלום")
                res = f"OK {(r.text or '').strip()[:20]}"
            except Exception as e:  # noqa: BLE001
                res = f"FAIL {str(e)[:160]}"
            print(f"::notice title=Ping key{k + 1} {model}::{res} ({time.time() - t:.1f}s)", flush=True)


def cmd_stuck():
    """Every lesson that is not ready: course, kind/number/title, status, progress, error, last update."""
    sb = db()
    names = {c["id"]: c["name"] for c in sb.table("courses").select("id, name").execute().data}
    rows = (sb.table("lessons").select("id, course_id, kind, number, title, status, progress, error, updated_at, source_url")
            .neq("status", "ready").order("updated_at").execute().data)
    for r in rows[:45]:
        print(f"::notice title=Stuck {r['id'][:8]}::{names.get(r['course_id'], '')} | {r['kind']} {r.get('number') or ''} "
              f"{(r.get('title') or '')[:60]} | {r['status']} | {(r.get('progress') or '')[:80]} | "
              f"{(r.get('error') or '')[:160]} | {r['updated_at'][:16]} | {(r.get('source_url') or '')[:40]}".replace("\n", " "),
              flush=True)


def cmd_archive(match):
    """Hides courses whose name matches (archived = true). Nothing is deleted; un-archive from the courses page."""
    sb = db()
    rx = re.compile(match, re.I)
    hit = [c for c in sb.table("courses").select("id, name").eq("archived", False).execute().data if rx.search(c["name"] or "")]
    for c in hit:
        sb.table("courses").update({"archived": True}).eq("id", c["id"]).execute()
    print(f"::notice title=Archived::{'; '.join(c['name'] for c in hit) or 'nothing matched'}", flush=True)


def cmd_summaries(out_dir):
    """Timetable + each course's grade / exam / formula-sheet summary (facts.py) -> summaries.json, for a picture."""
    sb = db()
    courses = sb.table("courses").select("id, name, user_id, kind, exam_type, grade_weights").eq("archived", False).execute().data
    slots = sb.table("schedule_slots").select("course_id, title, kind, weekday, start_time, end_time").execute().data
    for c in courses:
        try:
            c["summary"] = json.loads(sb.storage.from_(BUCKET).download(
                f"{c['user_id']}/materials/{c['id']}/facts_merged.json").decode()).get("summary") or {}
        except Exception:  # noqa: BLE001
            c["summary"] = {}
        c.pop("user_id", None)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    (Path(out_dir) / "summaries.json").write_text(json.dumps({"courses": courses, "slots": slots}, ensure_ascii=False, indent=1),
                                                  encoding="utf-8")


def cmd_flat():  # noqa: D401
    """Every ready lesson whose chapter is squashed onto a few lines (author.is_flat) - to write again."""
    sb = db()
    names = {c["id"]: c["name"] for c in sb.table("courses").select("id, name").execute().data}
    rows = sb.table("lessons").select("id, course_id, kind, number, chapter_md").eq("status", "ready").execute().data
    flat = [r for r in rows if author.is_flat(r.get("chapter_md"))]
    print(f"::notice title=Flat::{len(flat)} squashed chapters: " + "; ".join(
        f"{r['id']} {names.get(r['course_id'], '')} {r['kind']} {r.get('number') or ''}" for r in flat)[:3500], flush=True)


def cmd_inspect(match, kind, number):
    """Diagnostics for a lesson's text (no content printed beyond a short sample): line breaks, odd separators."""
    sb = db()
    course = find_course(sb, match)
    for l in (sb.table("lessons").select("id, title, status, author, chapter_md, summary_md, transcript, error, progress, updated_at").eq("course_id", course["id"])
              .eq("kind", kind).eq("number", int(number)).execute().data):
        for f in ("chapter_md", "summary_md"):
            t = l.get(f) or ""
            print(f"::notice title=Inspect {l['id']} {f}::len={len(t)} lf={t.count(chr(10))} cr={t.count(chr(13))} "
                  f"u2028={t.count(chr(0x2028))} u2029={t.count(chr(0x2029))} lit_bs_n={t.count(chr(92) + 'n')} "
                  f"author={l.get('author')} status={l['status']} updated={l.get('updated_at')} error={(l.get('error') or '')[:200]!r} "
                  f"progress={(l.get('progress') or '')[:80]!r} transcript={(l.get('transcript') or '')[:60]!r} "
                  f"sample={t[:160]!r}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("process"); p.add_argument("lesson_id"); p.add_argument("--no-author", action="store_true")
    sub.add_parser("queued")
    p = sub.add_parser("fetch"); p.add_argument("lesson_id"); p.add_argument("out_dir")
    p = sub.add_parser("publish"); p.add_argument("lesson_id"); p.add_argument("chapter_json")
    p = sub.add_parser("add"); p.add_argument("course"); p.add_argument("kind"); p.add_argument("number")
    p.add_argument("title"); p.add_argument("chapter_json")
    p = sub.add_parser("sheet"); p.add_argument("course"); p.add_argument("md")
    p = sub.add_parser("exercises"); p.add_argument("course"); p.add_argument("fixes_json")
    p = sub.add_parser("drive"); p.add_argument("course"); p.add_argument("files_json")
    p = sub.add_parser("core"); p.add_argument("course"); p.add_argument("core_json")
    p = sub.add_parser("task"); p.add_argument("course"); p.add_argument("title"); p.add_argument("due")
    sub.add_parser("flat")
    sub.add_parser("stuck")
    sub.add_parser("ping")
    sub.add_parser("tts")
    sub.add_parser("studio-retry")
    p = sub.add_parser("studio-new"); p.add_argument("course"); p.add_argument("number"); p.add_argument("kind")
    p = sub.add_parser("studio-backfill"); p.add_argument("course")
    p = sub.add_parser("studio-list"); p.add_argument("drop", nargs="?", default="")
    p = sub.add_parser("materials"); p.add_argument("course"); p.add_argument("title"); p.add_argument("out_dir")
    p = sub.add_parser("archive"); p.add_argument("match")
    p = sub.add_parser("summaries"); p.add_argument("out_dir")
    p = sub.add_parser("inspect"); p.add_argument("course"); p.add_argument("kind"); p.add_argument("number")
    a = ap.parse_args()
    if a.cmd == "process":
        cmd_process(a.lesson_id, not a.no_author)
    elif a.cmd == "queued":
        cmd_queued()
    elif a.cmd == "fetch":
        cmd_fetch(a.lesson_id, a.out_dir)
    elif a.cmd == "add":
        cmd_add(a.course, a.kind, a.number, a.title, a.chapter_json)
    elif a.cmd == "task":
        cmd_task(a.course, a.title, a.due)
    elif a.cmd == "core":
        cmd_core(a.course, a.core_json)
    elif a.cmd == "drive":
        cmd_drive(a.course, a.files_json)
    elif a.cmd == "exercises":
        cmd_exercises(a.course, a.fixes_json)
    elif a.cmd == "materials":
        cmd_materials(a.course, a.title, a.out_dir)
    elif a.cmd == "studio-list":
        cmd_studio_list(a.drop)
    elif a.cmd == "studio-backfill":
        cmd_studio_backfill(a.course)
    elif a.cmd == "studio-new":
        cmd_studio_new(a.course, a.number, a.kind)
    elif a.cmd == "studio-retry":
        cmd_studio_retry()
    elif a.cmd == "tts":
        cmd_tts()
    elif a.cmd == "ping":
        cmd_ping()
    elif a.cmd == "stuck":
        cmd_stuck()
    elif a.cmd == "archive":
        cmd_archive(a.match)
    elif a.cmd == "summaries":
        cmd_summaries(a.out_dir)
    elif a.cmd == "flat":
        cmd_flat()
    elif a.cmd == "inspect":
        cmd_inspect(a.course, a.kind, a.number)
    elif a.cmd == "sheet":
        cmd_sheet(a.course, a.md)
    else:
        cmd_publish(a.lesson_id, a.chapter_json)
    sys.exit(0)
