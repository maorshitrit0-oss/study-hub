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
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from supabase import create_client

import author
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
            lines.append(f"===== שקף {payload} ({media.fmt_time(t)}) =====")
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
        source = None
        if job.lesson.get("source_path"):  # a file uploaded in the app (lab booklet, prelab...)
            job.log("מוריד את הקובץ...")
            source = work / Path(job.lesson["source_path"]).name
            source.write_bytes(job.sb.storage.from_(BUCKET).download(job.lesson["source_path"]))
        elif media.is_drive(url):
            source = media.download_drive(url, work, log=job.log)

        if source is not None and not media.is_video(source):
            docs = [(source.read_bytes(), media.mime_of(source))]
            transcript = ""
        elif job.lesson["kind"] == "web":
            job.log("קורא את הדף...")
            transcript = fetch_web(url)
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
            job.log("מזהה שקפים / מצבי לוח...")
            scenes = media.detect_slides(video, log=job.log)
            slides = media.save_slides(video, scenes, work)
            job.log(f"מעלה {len(slides)} צילומי לוח...")
            store = job.sb.storage.from_(BUCKET)
            for n, _, p in slides:
                store.upload(f"{job.prefix}/{p.name}", p.read_bytes(),
                             {"content-type": "image/webp", "upsert": "true"})
            job.update(slide_count=len(slides))
            segments = media.transcribe_local(audio, log=job.log)
            transcript = transcript_with_markers(segments, slides)
            if not job.lesson.get("title"):
                job.update(title=title)
        job.update(transcript=transcript, status="transcribed", progress="התמלול מוכן")

        if do_author and os.environ.get("GEMINI_API_KEY"):
            ch = author.author_with_gemini(job.course, job.lesson, transcript,
                                           [(n, p) for n, _, p in slides], job.previous_topics(), log=job.log, docs=docs)
            save_chapter(job, ch, "gemini")
        else:
            job.log("התמלול מוכן - מחכה לכתיבת הפרק (Claude)")
    except Exception as e:
        job.update(status="error", error=str(e)[:2000])
        notify.send(job.sb, job.lesson["user_id"], f"⚠️ העיבוד נכשל: {job.label()}",
                    "לחץ כדי לראות מה קרה ולנסות שוב", f"/lessons/{job.lesson['id']}")
        raise
    finally:
        shutil.rmtree(work, ignore_errors=True)


def save_chapter(job, ch, by):
    ch = author.validate(ch)
    job.sb.table("questions").delete().eq("lesson_id", job.lesson["id"]).execute()
    if ch["questions"]:
        job.sb.table("questions").insert([{
            "user_id": job.lesson["user_id"], "course_id": job.course["id"], "lesson_id": job.lesson["id"],
            "topic": q.get("topic"), "question": q["question"], "options": q["options"],
            "correct": q["correct"], "explanation": q.get("explanation"), "difficulty": q.get("difficulty", 2),
        } for q in ch["questions"]]).execute()
    save_course_facts(job, ch)
    chapter_md = ch["chapter_md"] + (author.verification_md(ch) if ch.get("verification") else "")
    fields = dict(chapter_md=chapter_md, topics=ch["topics"], status="ready",
                  syllabus_covered=[i for i in ch.get("syllabus_covered") or [] if isinstance(i, int)],
                  progress=f"מוכן - {len(ch['questions'])} שאלות", author=by, error=None)
    if not job.lesson.get("title") or job.lesson["kind"] == "web":
        fields["title"] = ch.get("title")
    try:
        job.update(**fields)
    except Exception:  # noqa: BLE001 - database without the syllabus_covered column yet
        fields.pop("syllabus_covered", None)
        job.update(**fields)
    print(f"published: {len(ch['questions'])} questions", flush=True)
    notify.send(job.sb, job.lesson["user_id"], f"✅ {job.label()} מוכן לקריאה",
                f"{ch.get('title') or ''}\n{len(ch['questions'])} שאלות בשאלון".strip(), f"/lessons/{job.lesson['id']}")


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
        (out / "slides" / name).write_bytes(store.download(f"{job.prefix}/{name}"))
    print(f"fetched to {out}")


def cmd_publish(lesson_id, path):
    save_chapter(Job(lesson_id), json.loads(Path(path).read_text(encoding="utf-8")), "claude")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("process"); p.add_argument("lesson_id"); p.add_argument("--no-author", action="store_true")
    sub.add_parser("queued")
    p = sub.add_parser("fetch"); p.add_argument("lesson_id"); p.add_argument("out_dir")
    p = sub.add_parser("publish"); p.add_argument("lesson_id"); p.add_argument("chapter_json")
    a = ap.parse_args()
    if a.cmd == "process":
        cmd_process(a.lesson_id, not a.no_author)
    elif a.cmd == "queued":
        cmd_queued()
    elif a.cmd == "fetch":
        cmd_fetch(a.lesson_id, a.out_dir)
    else:
        cmd_publish(a.lesson_id, a.chapter_json)
    sys.exit(0)
