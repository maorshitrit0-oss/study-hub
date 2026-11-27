# Study Hub

Personal study system for an electrical-engineering student who learns by reading, not by watching recordings.
The user writes in Hebrew; answer in Hebrew.

**Start every session by reading `docs/HANDOFF.md`** (who the user is, accounts, his semester, open items),
and update it in the same commit whenever something is decided or built.

- `web/` – Next.js 16 app (Vercel): courses, reading chapters, multiple-choice quizzes, per-topic progress, deadlines, course chat (Gemini). Read `web/AGENTS.md` before changing it.
- `worker/` – Python: download a Zoom recording, snapshot the board, transcribe Hebrew audio (ivrit-ai Whisper), write the chapter + quiz.
- `supabase/schema.sql` – database, row-level security, storage bucket `study` (files under `<user_id>/...`).
- `.github/workflows/process.yml` – runs `worker/hub.py process` on GitHub Actions when the app dispatches it.

## Writing a chapter with Claude (instead of Gemini)

The user may ask from the phone: "כתוב את הפרק של <lesson_id>" or "תכתוב את הפרקים שמחכים".
This needs `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in the environment (cloud environment secrets).

1. `cd worker && pip install -q -r requirements.txt`
2. `python hub.py queued` – lessons with status `transcribed` are waiting for a chapter. If a lesson is still `queued`
   (no transcript yet), run `python hub.py process <id> --no-author` first (≈ 0.4× the recording length).
3. `python hub.py fetch <id> /tmp/lesson` – writes `transcript.txt`, `meta.json` (course, lesson, earlier topics) and `slides/slide_NNN.webp`.
4. Read the whole transcript and look at the slides (they hold the formulas, code and handwritten board).
5. Write `/tmp/lesson/chapter.json` that follows `author.CHAPTER_SCHEMA` and every rule in `author.SYSTEM`
   (the kind-specific task is in `author.KIND_TASK`). Images go in the markdown as `![תיאור](slide:N)`.
6. Fact-check your own draft exactly as `author.VERIFY_SYSTEM` describes: check every definition, formula
   and number against the transcript, the slides and engineering knowledge; re-solve every quiz question from
   scratch; fix or remove anything doubtful. Record what you changed and what remains uncertain in a
   `verification` object (`fixes`, `uncertain`) in the same JSON. The student is examined on this material.
7. `python hub.py publish <id> /tmp/lesson/chapter.json` (a "✅ בדיקת עובדות" section is appended from `verification`)
8. Tell the user it is ready, with a short summary of the lesson's main points.

Do not invent content that is not in the lecture; flag lecturer mistakes with `> ⚠️`.

**His rule (23/11/2026), for every course and every lecture, practice and exercise: no detail may be missing.**
Every definition, number, unit, assumption, solution step, exercise (also ones given as homework / "try alone", with
full data) and every decision or announcement of the lecturer goes into the chapter; what cannot be heard is written
as unclear, never skipped. The pipeline enforces it: full chapters for all courses (author.summary_mode is off), a thin
chapter is rewritten part by part, and every chapter is compared with each part of its recording (coverage.audit)
before it is marked ready.

## Checks

- Web: `cd web && npx eslint src && npx next build` (needs `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` set to any value to build).
- Worker: `python -c "import hub"` from `worker/`.

## His rules for every lecture and practice (27/11/2026) – apply to everything built from now on

- Study order is lecture → practice → exercises, nothing else. No separate "extra material" and no "last year": what a
  lecture lacks from course material goes INTO it (coverage.merge_extra). No more completions (🔁) – chapters are
  written full from the start.
- One lesson = one recording. Never merge two recordings (different days / clothes) into one lesson. The same
  recording uploaded twice (link + file) is ONE lesson; the duplicate is deleted. Every lesson shows its source link.
- Details the recording check adds go INTO their own topic, never a "🧩" section at the end.
- Formulas always render as formulas: no red, no symbol inside \text, no indented lines (shown as code), board
  derivations line by line as written. Code only in programming courses, fenced and unbroken.
- Quiz after a lecture: 10–12 understanding questions covering the whole lecture. Practices: no quiz, no video.
- Exercises follow the course exam: waves open (2 double-sided formula pages allowed – build the sheet), comm open
  (+ his assignments), digital / Java / linear multiple choice, micro half multiple choice half open. Quiz stays
  multiple choice everywhere.
- Exercises of a week = the lecture's and practice's own exercises at exam level + matching exam / assignment
  exercises. Drop trivial ones (the "1+1" of the exam's material). Never 1 exercise, never one already solved.
- Everything checked for correctness before ready; nothing made up. No podcasts unless he asks. No course chat.
