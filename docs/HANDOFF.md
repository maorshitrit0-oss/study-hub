# Handoff: everything a new Claude session needs

Read this first in every new session. Keep it up to date: when something is decided, built or changed,
add it here in the same commit. The conversation that built the app will not be available.

## The user
- Maor Shitrit, 3rd-year electrical engineering student, Ariel University. Writes Hebrew; always answer in Hebrew.
  09/11/2026, until he says otherwise: replies ONLY in Hebrew - no English words or terms in the text either (say
  "מאגר" not repo, "מפתח גישה" not token, "סודות" not Secrets); a command he must type goes in a code block, explained in Hebrew.
- Learns by **reading**, not watching recordings. Wants accuracy above all: he is examined on what the app teaches.
- Not a programmer. Explain setup steps one at a time, exactly what to click; prefer one step per message
  when he says he didn't understand. He uses an iPhone 15 Pro and a Windows laptop (Dell 14 Plus).
- **Never ask him to paste secrets** (API keys, tokens, service keys) into the chat. He once posted keys in
  screenshots; remind him to hide them.
- Do **not** quiz him in the Claude chat: Claude Code is responsible for the app, not for testing his knowledge.
- Pays only for Claude Pro (and has a free Google AI Plus student plan). Everything else must stay free.
- Reservist (מילואים) status changes between semesters; the app has a toggle in settings.
- "בשם ה' נעשה ונצליח" must appear at the top right of every screen; "פותח על ידי Maor Shitrit" credit on every screen.

## Accounts and where things live
| What | Where |
|---|---|
| Code | GitHub `maorshitrit0-oss/study-hub` (private), branch `main`; pushing to main deploys |
| App | Vercel project `study-hub`, root `web/`, region `dub1`: https://study-hub-tawny-mu-63.vercel.app |
| Database, auth, files | Supabase project `study-hub`, region eu-west-1: https://yreemrahsvdhdmlxxlpq.supabase.co |
| Lecture processing | GitHub Actions `process.yml` (dispatched by the app), `notify.yml` (cron push notifications) |
| AI | Gemini API free tier (`GEMINI_API_KEY`, model `GEMINI_MODEL` or `gemini-flash-latest`) |

Secrets: GitHub repo secrets `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `GEMINI_API_KEY`; Vercel env
`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `GEMINI_API_KEY`, `GITHUB_REPO`, `GITHUB_TOKEN`
(fine-grained PAT, Actions read/write on this repo only). Claude Code cannot write repo secrets through
its proxy, but can dispatch workflows with `gh api -X POST .../actions/workflows/<file>/dispatches`.

## Database changes
There is no migration runner. `supabase/schema.sql` is the full schema for a new project; each later change
also has its own file in `supabase/` that the user pastes into **Supabase → SQL Editor → New query → Run**.
Give him the SQL inline in a code block (he copies from chat more easily than from files).
Make migrations idempotent (`if not exists`) and make app/worker code tolerate a not-yet-migrated column.

## His semester (א תשפ"ז, 2026/27) – entered via SQL on 2026-10-22
- Java (002-4366110-01) – Wed 13–16 lecture, 16–17 practice. Prof. Yoel Retzabi / Alon Avraham. Exam: MCQ online in class, 80% exam 20% assignments.
- גלים ומערכות מפולגות (002-4331710-01) – Sun 17–21, 21–22. Dr. Daniel Rozban / Roni Poliakov.
- מעגלים ספרתיים / Digital electronic circuits (002-4337410-03) – Tue 13–16, 16–17. Dr. Netanel Ofer / Matan Rasuli.
- מעגלים ליניאריים (002-4331810-04) – Thu 09–13, practice 16–17. Prof. Gadi Golan / Hodaya Perlman. Attendance at lectures mandatory.
- מעבדה 2 (digital lab) – usually Tue 09–13, Tomer Blisha & Talia Mandelbrot. Attendance mandatory, entry quiz
  every meeting, weekly prelab + summary report (Word). No Zoom recordings for the lab. Experiment 2 on Wed 28/10/2026.
- אותות אקראיים ורעש – exam מועד ג 22/12/2026 (retake: he failed - exam 39, final 48 with 100% on assignments).
  09/11: he studies it Thursday evenings (half day linear, half random signals); tasks added for each Thursday
  12/11-17/12. Course row exists (year 2 sem ב) but is EMPTY - waiting for him to upload past exams, his exam,
  lectures/recordings, formula sheet, drive link. Then: topic-based core (not by weeks) aimed at 22/12.
  09/11: his Drive links (Bar-Ilan 83-302 materials: exams 1999-2026, solutions, formula sheets) - recent exams pulled with
  the new fetch mode `drive:<id,id>` (hub.py drivefiles; the session proxy blocks Google downloads). chapters/rnd_drive.json
  registered as materials; chapters/fixes/rnd_core.py = 19 exam exercises solved in full (added by material: hub.py
  exercises "add"+"material"); chapters/rnd_core.json weeks 3-8 = Thursdays 12/11..17/12 (key = studyWeek that Thursday):
  vectors+MMSE / WSS / LTI+PSD / Wiener+matched / Poisson / Gaussian+full questions. Official-solution errors flagged:
  tashpad A Q3 final (a+y)/(a+b+N), tashpad B Q4 conditional density 1/(2sqrt(1-y^2)). Tashpav reconstructions are
  ambiguous (R_Y=3R_Z vs 1/3; a sign in Q2) - marked uncertain.
  HIS exam (OFFICIAL form + lecturer's solution uploaded 10/11; the 09/11 notebook reconstruction was WRONG - ignore
  it): Ariel 04322110, Hodaya Halevi / Daniel Rozban, summer 5786 moed B 26/10/2026, grade 39. 90 min; answer ALL
  questions; reservists may choose between Q3 and Q4, but answering both gives double credit on the two best sections
  (so attempt both). 4 pages allowed, reservists 6; the form itself includes an official formula sheet (pp. 3-5).
  Q1 (30) X[n]=A+nB, A,B indep zero-mean: R=sA^2+n1n2 sB^2 not WSS; Y[n]=X[n+1]-X[n]=B WSS. Q2 (30) S_X=2 on |f|<=1,
  H=1-|f|: S_Y=2(1-|f|)^2 (range!), P=4/3, H2=0 on |f|<=1 and 1 outside gives zero output. Q3 (20) Poisson: 0 failures
  in next 2h given 3 last hour = e^{-2 lambda}; one every 20 min -> lambda=3. Q4 (20) X~Exp(3), N~U[-1,1], Y=X+N:
  E[Y]=1/3, Var=4/9, Xhat=1/4+Y/4. His 4 exercises updated BY ID (they live in the session lessons).
  may bring 3 sheets = 6 pages (reservist). The Bar-Ilan material is a higher level than Ariel ("רמה יותר גבוה
  מאצלנו" in the Ariel students' Drive) - Ariel old exams: Asher Yahalom / Itzhak Kalet folders in drive t_1qoRAKRMW.
  Formula sheet chapters/rnd-formula-sheet.md (large print: sheet_pdf LARGE when the md has <!-- print: large -->,
  one column 13.5pt, 5 pages).
  09/11: exam is 1.5h (about 2h with his extra time), 4.5 credits, he wants 100. Lecturer Hodaya Tova Halevi taught at
  Bar-Ilan and the Technion; he suspects she adapts Bar-Ilan questions - consistent with what we saw (same 4 question
  types, simpler numbers). Study method agreed: per Thursday learn the topic from solved questions -> solve alone with
  ONLY the sheet -> check; from 10/12 timed mock exams (1.5h) with the sheet.
  He starts from ZERO (09/11). Core reordered: one exam question type per Thursday, simplest first: week 3 estimation
  (Q4), 4 WSS (Q1), 5 PSD+filters (Q2), 6 Poisson (Q3), 7-8 timed mocks (8 = his own exam again). Scheduled task every
  Tuesday 19:37 writes a from-zero reading chapter (+ video) for that Thursday as a lesson of the course.
  09/11 he asked for 6 SESSIONS (one page per Thursday with everything inside): lessons OTHER 1-6 of the course
  (MISTAKE fixed: first published as lecture 1-6, which overwrote the chapters of his recorded lectures 1-6 uploaded
  that morning - re-authored from their transcripts via process.yml (hit the Gemini quota 09/11, queue redoes after the
  reset; check-in scheduled 10/11 13:07 also regenerates their videos, which were made from the session text);
  never reuse kind+number of real lessons)
  (chapters/fixes/rnd_sessions.py -> chapters/rnd_s{n}.json, hub add): steps + from-zero summary + quiz; the core
  exercises were moved into them (chapters/rnd_moves.json, hub exercises "to_lesson"); AUTO_STUDIO += אקראיים so each
  session gets the explainer video. The Tuesday task now only checks that week's session/video and reminds him.
  UI: a lesson whose title starts with "מפגש " is a session (lib/types isSession): shown by its title, in its own
  group "📅 מפגשים" at the top of חומר הקורס.
- אותות אקראיים ורעש exam also on 26/10/2026 (time unknown); course registration 25/10/2026.
- Exams: waves 12/1 & 10/2/2027, Java 17/1 & 25/2, linear 19/1 & 14/2, digital 25/1 & 18/2 (times unknown, 09:00 placeholders).
- Added 25/10/2026 (`supabase/add_micro_comm.sql`, moved from year 4 semester A so year 4 is lighter - 21.5 credits
  there, 25 now): מיקרו מעבדים (002-4371710, Dr. Roi Yozevitch, 100% theoretical final, exam 18/1/2027) and
  מבוא למערכות תקשורת (002-4330610, Prof. Yosef Pinhasi, analog: AM/SSB/superheterodyne/FM, noise figure, SNR;
  exam 2/2/2027). Weekly times and מועד ב not known yet. He may drop micro if behind by week 4-5 - check the drop window.
- Full timetable from the university system (26/10/2026) -> `supabase/schedule_full.sql`: Sun waves 17-21 + 21-22;
  Mon communication 09-12 (lecturer this semester: Mr. Avraham Yehonatan; material Prof. Pinhasi) + practice 13-14;
  Tue lab 2 09-13, digital 13-16 + 16-17; Wed Java 13-16 + 16-17, micro 17-20 + practice 21-22 (Lior Brown);
  Thu linear 09-13 + 16-17. Exams added: micro B 17/2, communication B 24/2; semester ב: control 27/6 & 21/7,
  semiconductor physics 8/7 & 27/7, electromagnetics 11/7 & 1/8/2027.
- מבוא לבקרה exams: 27/6 and 21/7/2027 (from the university system).

## Free-tier limits (watch these)
- Supabase allows 50 MB per uploaded file: bigger course files are added as a shared Google Drive link
  (`materials.storage_path = "drive:<id>"`); files over 15 MB reach Gemini through its Files API (`web/src/lib/files.ts`).
- **Never delete his study data** (snapshots, transcripts, chapters, files): he needs everything until the end of the
  degree. Storage pressure is handled by moving big files to Google Drive, not by deleting.
- `worker/usage.py` (morning run of notify.yml) writes `usage_snapshot` and pushes an alert at 75% of a free limit,
  with the recommended fix; the app shows it on home and in settings.
- **Storage alert 11/11/2026 (128% of 1 GB):** 1.31 GB = media 878 MB (explainer videos: VLSI 299, random signals 227,
  comm 110...), materials 319 MB (his uploads - untouched), lessons 110 MB (slides). Fix: a fresh backup first
  (backup.yml), then `publish.yml inspect=shrink` (worker/shrink.py) re-encoded every video >3 MB with crf 27 / g 100 /
  AAC 48k: ~30% of the size, SSIM 0.998, same length; nothing deleted. studio.py now encodes new videos the same way.
  `inspect=storage` (worker/storage_report.py) prints what fills the storage; `inspect=shrink-dry` + number = test N.
- **Egress, 12/11/2026:** the org usage page showed egress 5.98 / 5 GB (120%) and cached egress 106% for the cycle
  22/10-22/11, while storage (as Supabase bills it) was only 39%. Our own downloads were most of it: backups (full copy
  each run: 07/11, 08/11, 11/11 = ~2 GB), shrink (0.9 GB). Backups are now incremental (backup.py dump <dir> <since>).
  Avoid whole-storage jobs (shrink, full backup, `where --again` on big courses) until the cycle resets on the 22nd.
  Quotas are per ORGANIZATION: a media project must be in its own free org to get its own 1 GB / 5 GB.
- **Media project (12/11/2026):** his second free org "study-media", project zpjjrsgosphapghxlbsl (Mumbai), public
  bucket "media". worker/mediastore.py (GitHub secret MEDIA_SUPABASE_KEY, an sb_secret_ key; the URL is in code).
  New videos / podcasts go there (storage_path "m:<path>"; web/src/lib/studio.ts builds the public URL; CSP media-src
  allows the host). usage.py pings it daily. TODO after 22/11 (main egress resets): move the existing ~300 MB of
  media/ files there (download from main, upload, update storage_path; never delete before the copy is verified).
- Supabase DB 500 MB: text only, ~15 MB per semester. Free projects pause after 7 idle days; the daily cron touches the DB.
- GitHub Actions 2,000 min/month for a private repo; a 80-min lecture takes ~35 min. If it runs short, the repo can be
  made public (no secrets in code; data lives in Supabase) for unlimited minutes – ask the user first.
- Gemini free tier: daily request limits; ~3 calls per lecture (write, verify, search check).

## Lab (מעבדה 2)
- Partner: Shirel (failed the lab in summer, repeating it with him). Her and her former partner Yehonatan's summary
  reports are uploaded as `prev_report`; the lab chat compares them with the current booklet and lists exact changes,
  marking measurements to replace with their own.
- Final exam of the lab is PRACTICAL (told 2026-10-26), on the whole semester's experiments. Lab 1's was 3 questions:
  (1) theory/graph question, (2) verbal question, (3) build a circuit on the breadboard and show it on the scope -
  e.g. two input waves -> summing op-amp. Last year there was a hands-on practice day; this year there is none, so he
  wants to practise at home. Plan (near the end of the semester, when all experiments are known): a "מבחן מעשי"
  page per lab - for every experiment, build-it tasks (which circuit, component values, breadboard wiring steps,
  generator/scope/multimeter settings, expected waveform, common mistakes) + the theory/verbal questions, and practice
  in a free browser simulator with breadboard + function generator + oscilloscope + multimeter (Tinkercad Circuits;
  Falstad for quick op-amp/RC behaviour). Not built yet.
- LAB 2 PAGE (03/11/2026) - only what he uses: 🧪 practical exam, 🎯 entry quizzes, 📝 summary reports, 🎙️ lecturer
  recordings, course info, files, tasks (lessons/exercises/summaries hidden, not deleted; `page.tsx` early return).
  - Reports: `LabUploads` - experiment N + "שלי"/"של השותפה", saved as "דוח מסכם ניסוי N - ....docx". On the day of
    experiment N he hands in report N-1. `lib/labTasks.ts`: lab day i (Nth Tuesday from SEMESTER_START; a week with no
    lab would shift it) -> tasks "📝 להעלות דוח מסכם ניסוי N-1" (labrep:) and "🎯 לרשום מה שאלו בבוחן הכניסה של ניסוי
    N-1" (labq:), closing themselves when the file / an entry report exists. After a report upload: link to its quiz.
  - Lecturer remarks: WhatsApp voice recordings (.opus/.ogg/...) -> lesson kind other titled "🎙️ המרצה על המבחן
    (date)", transcribed; `build_prompt` writes every exam remark as ⭐ + exam_hint facts.
  - `worker/practical.py` -> practical.json: question bank per experiment (graph / theory / build) from experiment
    chapters, reports (.docx via python-docx), lecturer recordings, entry questions, past practical-exam files (title
    with מבחן/מועד/שאלות). Rebuilt when anything newer exists (exercises.yml after every upload, daily site run).
  - `/courses/[id]/practical`: practice (filter by experiment / type) and mock exams of 3 (graph, theory, build):
    midterm = experiments 1-5, final = all; "🎲 מבחן אחר". Graph questions drawn by `LabGraph` from parameters
    (1st-order LP/HP, 2nd-order BP/BS on a log axis, or time signals). Build questions: `VirtualLab` = Falstad
    CircuitJS in an iframe (CSP frame-src www.falstad.com), empty board - he builds; the answer gives the circuit,
    breadboard wiring steps, instrument settings, expected scope picture, mistakes. (Gemini does not write CircuitJS
    files: a broken one would mislead.) Option B, a real breadboard simulator, was declined as too big/risky.
  - `/courses/[id]/entry/print`: every reported entry-quiz question by experiment with answers, printable / PDF to share.
- Entry quiz (בוחן כניסה, 2026-10-26): every experiment opens with a 3-question MCQ on the prelab + Multisim
  simulations. His group is Tuesday; Sunday/Monday groups tell what they were asked. `/courses/[id]/entry`
  (lab courses: "🎯 בוחן כניסה" card; lab lesson page links to it): paste/screenshot a report -> `processReport`
  (`web/src/lib/entryQuiz.ts`, one Gemini call with the experiment's chapter + booklet) -> the reported questions
  rebuilt as MCQs (`questions.source = 'entry_reported'`) + 6-8 similar ones (`entry_practice`), `experiment` = N,
  doubtful answers prefixed "⚠️ לא בטוח". "📂 לקרוא בחני כניסה מהקבצים" reads course files named בוחן/כניסה once each
  (`entry_reports.material_id`). Mock quiz = 3 questions, reported first. Chapter re-saves keep these questions
  (hub deletes only `source is null`); the chapter quiz hides them. Push: "🎯" line the evening before and the
  morning of a lab slot day (`notify.entry_quiz_lines`). Needs `supabase/entry_quiz.sql`.
- Course files can be uploaded as ZIPs; they are unpacked on the device and typed by file name (`web/src/lib/zip.ts`).

## Gemini quota (important)
- Free tier: about **20 requests/day per model per project** on the newest Flash (seen 2026-10-22). `web/src/lib/gemini.ts`
  and `worker/author.py` fall back across models (flash → 2.5-flash → flash-lite → 2.5-flash-lite) on 429/404 and
  retry on 503; `GEMINI_API_KEY` may hold several comma-separated keys from different Google Cloud projects to
  multiply the quota. Chat starts on flash-lite to save the stronger model for chapters.
- Semester start for "missing recordings": `SEMESTER_START` in `web/src/lib/recordings.ts` (2026-10-18) – update each semester.

## Security (2026-10-22)
- Security headers + CSP in `web/next.config.ts` (no framing, HTTPS only). If a new outside service is used from the
  browser, add it to `connect-src`/`img-src` there or it will be blocked.
- Optional two-step sign-in (TOTP, e.g. Google Authenticator): enabled in settings (`TwoFactor.tsx`); `proxy.ts` sends
  aal1 sessions of such accounts to `/mfa`; `supabase/security.sql` adds restrictive RLS so the DB also requires aal2.
- Signup needs a 10+ character password. Workflow inputs are validated (no shell injection); chat requests are bounded.
- Asked the user to: run `security.sql`, turn off "Allow new users to sign up" in Supabase, enable 2FA, and rotate the
  GitHub PAT and Gemini key he once showed in screenshots.

## English (2026-10-22)
- He is weak in English: chapters, quizzes and chat must be fully Hebrew (English terms only in parentheses).
- Each chapter carries a `glossary` (en/he/explanation) saved to the `glossary` table (`supabase/glossary.sql`);
  the "אנגלית" tab (`/words`) lists the words and quizzes them (missed words come back first, kept in localStorage).
  Chapters written before this get their words with the "להוציא מילים" button (one Gemini call, `web/src/lib/glossary.ts`).

## Grades, tasks without a date (2026-10-22)
- `grades` table + `/grades` page (link on Courses): his sheet from 07/10/2026 is in `supabase/grades_data.sql`.
  The average formula (numeric grades × credits / credits, failed included, "עבר" and 0-credit excluded) was checked to
  match the official 90.92 / 76.64 / 82.86. Failed: תורת החשמל ואלקטרומגנטיקה (26) – the page flags it.
  Never store his ID number, address or phone from such documents.
- `deadlines.check_due`: a task with no published submission date. Its `due_at` is a placeholder (+120 days); the app
  shows "אין עדיין מועד הגשה" and reminds to check it, and the morning push lists them on Sundays and Wednesdays.
- "לנסות שוב" on a lesson that already has a transcript skips download/transcription and only rewrites the chapter.
- iOS auto-zoom on inputs left the bottom nav floating mid-screen: viewport maximumScale 1 + 16px inputs.
- He wants industry/career knowledge too: chapters end with "מהעולם האמיתי: תעשייה וראיונות עבודה" (what the lecturer
  said, marked 🎙️, plus a short verified enrichment with interview questions); such remarks are also collected as
  course facts with category `industry` ("💼 מהתעשייה ולראיונות עבודה" on the course page).
- Prep tasks: every lecture/practice gets a task "📖 ללמוד את ... לפני ההרצאה/התרגול הבא" (`external_uid` prep:<lesson>),
  due at the course's next class of that kind; closed when the chapter is marked read (`web/src/lib/prep.ts`,
  synced when home or tasks load). His linear course is spelled "מעגלים לינאריים" (no second yod) - match both.
- Degree audit (22/10/2026): 162.5 credits, major VLSI + minor computers; 35 credits in progress, 43.5 not started.
  `web/src/lib/degreePlan.ts` loads the rest of the degree into `grades` once (year 'יתרת התואר'). Electromagnetics
  is now 32 (not 26) - still failed and mandatory; the audit average 83.14 matches. VHDL course counts in both majors.
- His study plan (22/10/2026) for year 3B and year 4 is in `degreePlan.ts` (audit credits win where they differ).
  It omits the mandatory electromagnetics retake (kept as "עוד לא משובץ"). A retaken course's new grade REPLACES the
  failed one at Ariel (he confirmed) - `forProjection` drops the failed row from future averages.
- He retakes electromagnetics in year 3 semester B. Realistic forecast (`web/src/lib/predict.ts`): per course, his
  average in the same category of past courses, adjusted by quiz accuracy (>=15 answers) and reading vs class;
  shown on /grades with the reasons. Projected 22/10/2026 with no quiz data: ~85.7 end of year 3, ~85.3 end of degree.
- Field rules (department file for תשפ"ז, 25/10/2026): primary VLSI + secondary computers; per field 2 core + lab +
  2 electives, +2 more electives, + pre-project. His electives: Java, Python, sources & detectors (sem A only),
  optoelectronic devices (sem A only), reliability + VLSI design (sem B, need VLSI devices). He refuses
  "תקשורת מחשבים וסייבר" (lecturer) and embedded systems (too much code). File codes differ from the audit for the two
  labs (analog VLSI 4379210 vs 4365130, VHDL lab 4371930 vs 4364130) - audit codes kept. Digital circuits (now) is a
  prerequisite of VLSI devices, the analog VLSI lab, reliability and VLSI design.
- Target average (goal 90+): `GradeGoal` on /grades and a chip on each course page (`web/src/lib/gradeGoal.ts`).
  Current courses are added to `grades` (academic year 'תשפ"ז', credits 0 until he fills them). 82.86 over 73.5 credits:
  90 is out of reach this semester; ~96 on all remaining ~84 credits (if the degree is 160 - verify). Retaking
  תורת החשמל (26, 3.5 credits) to 90 would lift the average to ~85.9 if the new grade replaces the old one (verify).
- Spaced repetition (`/review`, `web/src/lib/review.ts`): computed from `attempts` only (Leitner: 1,3,7,14,30,60 days
  by correct streak; wrong -> next day). Home card + morning push count (`worker/notify.py` reviews_due).
- He wants lectures and practices shown **separately** everywhere (except the lab).

## Self-study: digital design / VLSI / SystemVerilog (2026-10-22)
- He studies RTL/VLSI on his own (aiming at student hardware jobs; mentor at NVIDIA). Tab "לימוד עצמי" (`/self`).
- A track is a course with kind `self`; its `notes` hold his context and teaching rules (verbatim, they bind the tutor).
  `skills` table = roadmap topics + project steps with his levels 0-4 (`web/src/lib/skills.ts`).
- The course chat becomes a tutor (`TUTOR` in `api/chat/route.ts`): one topic, one MCQ, wait, demand reasoning,
  no flattery, ASCII waveforms; also a free AI chat that quizzes after each explanation (1-4 answer buttons in the UI);
  "➕ נושא חדש: <title>" adds a topic to the map; it ends with "📈 התקדמות: <title> → <0-4> | note" lines that update `skills`.
- Syllabus (`web/src/lib/vlsiSyllabus.ts`, 9 modules / 50 topics) is merged into his roadmap once by /self/[id];
  module headers live in `courses.syllabus_topics` as "firstOrd|title|goal".
- Lessons can be edited (kind, number, title) on the lesson page. New lessons are numbered per kind (practices
  were numbered after the lectures until 22/10/2026; the first waves practice was renumbered to 1).
- Seed: `supabase/self_study.sql` + `supabase/self_study_vlsi.sql`. Exam freeze 10-25/1/2027 (no new development).

## Cadence tracks (2026-10-24)
- He has Cadence online courses (English videos). Never log into his Cadence account or accept his password.
  `web/src/lib/cadenceTracks.ts` creates 3 self-study tracks once (on /self): SystemVerilog for Design and
  Verification, Genus Synthesis (Stylus Common UI), Xcelium Simulator - syllabi from Cadence's public course pages;
  each track's notes carry his teaching rules. `TrackTabs` switches between tracks (map and tutor).

## Notification times (2026-10-24)
- He wants: Sun-Thu 08:00 and 20:00, Fri 08:00 only, Sat 20:00 only (Israel). GitHub cron ran 3-4 hours late
  (morning arrived ~12:30, evening ~01:30), so notify.yml has no schedule any more. Supabase pg_cron
  (`supabase/notify_cron.sql`) calls `/api/cron/notify` at 05/06/17/18 UTC; `web/src/lib/notifySchedule.ts` decides
  (DST-safe) and the route dispatches notify.yml at most once per slot. Evening = recordings to upload + tomorrow.

## Course chat (2026-10-24)
- Several chats per course (`chat_threads`, `chat_messages.thread_id`; `supabase/chat_threads.sql`): tabs at the top
  of the chat ("ראשי" = messages without a thread), "＋ צ'אט חדש", a new chat is named after its first question.
- "🔍 לאמת את התשובה" under each answer: `/api/chat/verify` re-checks it against the chapters (+ Google Search),
  re-solving calculations; on demand only, to save the free quota.
- He does NOT want NotebookLM: everything inside the app. Studio (`worker/studio.py`, `.github/workflows/media.yml`,
  table `lesson_media` in `supabase/studio.sql`, UI `web/src/components/Studio.tsx`): podcast (two hosts, Gemini writes
  the script from the chapters, a second pass fact-checks it, Gemini 3.8 Flash TTS records Hebrew with two voices),
  video (the lesson's board snapshots shown while discussed, ffmpeg), everyday examples (markdown). On a lesson page
  for that lesson; on a course page for picked lessons. Not yet run with a real key (TTS quota unknown).
- He learns ONLY through examples. Chapter structure for every topic and subtopic: background -> the lecturer's
  explanation -> "> 🏠 **מהחיים:**" right there (not at the top) -> worked example if the lecture had one -> next topic.
  New chapters are written so (author.SYSTEM); old ones are rewritten by `worker/enrich.py` (workflow enrich.yml,
  dispatched every morning by /api/cron/notify until all are done; stops on quota). The pre-rewrite chapter is kept in
  storage as `chapter_before_examples.md` (also the "done" mark); quizzes/answers untouched; content-losing rewrites
  are rejected.
- Timing diagrams are never drawn by the AI: ```wave blocks (JSON: inputs per half-cycle) are rendered by
  `web/src/components/Wave.tsx`, and Q is simulated in `web/src/lib/wave.ts` (none / sync / async reset). The tutor's
  ASCII waveforms were wrong and confused him (24/10/2026).
- CSP needs `media-src` for Supabase storage, or studio audio/video can't play (fixed 24/10/2026).

## Timing diagrams - not trusting the AI (03/11/2026)
- Gemini put "עלייה 1..4" marks on ticks 1,3,5,7 = falling edges, and drew D changing exactly on a rising edge.
  `lib/wave.ts`: marks take {"edge": n} (rising edge n); a tick mark whose label names a rising edge snaps to it.
  `Wave.tsx`: an input change on a rising edge is drawn SKEW px after it (the flip-flop samples the old value, as the
  simulation does), marks are numbered, and under every flip-flop diagram a COMPUTED table "מה הדלגלג ראה בכל עליית
  שעון": inputs just before each edge -> Q. Prompts (tutor, chapters) say: marks on edges via "edge", and the text must
  match the table. He finds Gemini weak here; a paid model is not an option (everything free) - correctness comes
  from computing, not from the model.

## Formulas (2026-10-23)
- KaTeX CSS must match the KaTeX that rehype-katex renders with (pinned katex 0.16.47; a 0.19 CSS broke \vec arrows).
- `web/src/lib/math.ts`: long inline $...$ become display math, and long display equations split at "=" into aligned
  lines (applies to old chapters too). Quiz text renders math via `Rich` (Chapter.tsx). Prompts ask for short inline math.
- Chat errors never show an empty "⚠️": `friendlyGeminiError` falls back to a message; an empty stream says so.

## Course sites (2026-10-26)
- Micro (Dr. Yozevitch) lives on a public Notion site: https://roi.notion.site/Micro-Controllers-Course-for-EE-CE-2027-327e0f376194801c9db4e823a019b259
  (weekly topics with slides/code, review-questions page, 2 past exams, 2026 recordings on YouTube/Zoom, TA page).
- `worker/course_site.py` + `.github/workflows/site.yml`: reads a public Notion page through Notion's own JSON
  endpoints (loadPageChunk; syncRecordValues is refused on notion.site, so closed toggles load as their own chunks;
  files via getSignedFileUrls). `show <url>` = dry run; `import <course> <url>` = files -> materials
  (`<user>/materials/<course>/site_<block>_<name>`, videos and >50 MB skipped), all text -> `site.md` material (first
  line "מקור: <url>"), and a `web` lesson per "Week N" section (+ its sub-page, its PDFs attached via `[[file:path]]`
  lines in the transcript), per long extra page (review questions -> solved), per past-exam PDF -> solved.
  Lessons start with `<!-- course-site -->` in `transcript`; `hub.cmd_process` reads them through the reuse path.
- Course page: "🌐 ייבוא אתר הקורס" (`SiteImport.tsx`, `importSite` action). Daily cron dispatches `site.yml` with no
  inputs = `pending`: re-import every site (new weeks/files only, dedupe by source_url / storage_path) and continue
  chapters until the Gemini quota ends.
- This container cannot reach notion.site and cannot download Actions logs: test with `site.yml` (course_id empty)
  and read the output from the job's annotations (`check-runs/<job>/annotations`).
- Recordings on the site: headings "<year> ... Recordings (EE Group)" (his group EE; CE lists ignored when an EE one
  exists). The newest year's links -> `lecture` lessons numbered in order (skipped if that number exists - he may
  upload the Zoom himself) and process.yml is started for each (`actions: write`, GITHUB_TOKEN). Lists saved as
  `site_recordings.json` next to `site.md`. When lecture N of such a course is authored, `hub.with_previous_year`
  takes last year's lecture N (exercise sessions dropped from the numbering), creating it as an `other` lesson
  "שנה שעברה · הרצאה N (להשוואה)" transcribed without a chapter, waits up to 30 min for it, and the chapter adds
  "📼 משנה שעברה" explanations + a "🔄 השוואה" section. The repo is public: Actions minutes are not limited.
- Lesson edit (title/number/kind, e.g. "חלק 1") is at the top of the lesson page; two parts with the same number
  count as one meeting; hub never overwrites a title he set while the recording downloaded.
- addLesson also accepts YouTube links; media.download merges best video+audio for YouTube. VERIFIED 2026-10-26:
  YouTube refuses GitHub runners ("Sign in to confirm you're not a bot"). Fix: repo secret `YT_COOKIES` (cookies.txt
  of a signed-in YouTube session, ideally a spare Google account) -> `media.youtube_cookies()`. Until it exists,
  course_site skips YouTube recordings (they are created the morning after the secret is added). Test with site.yml
  url=<youtube link>, course_id empty. Do NOT try to get around YouTube's bot check (other player clients, proxies) -
  refused as circumvention.
- YouTube WORKS through Gemini's official YouTube video input (verified 2026-10-27 on micro lecture 1, Hebrew):
  `media.transcribe_youtube` - no download; 30-minute segments (videoMetadata offsets, media resolution LOW,
  ~92 tokens/s -> ~165k tokens per call, 20 s pause), verbatim transcript with timestamps + "===== על המסך =====" blocks
  (slides/code written out, since there are no board snapshots). Stops at "END"/past the end. Free tier allows
  8 h of YouTube per day. A 3 h lecture = ~6 calls + authoring; with last year's lecture for comparison ~15 calls.
  gemini-2.5-flash is gone for new keys (404 -> next model); gemini-flash-latest worked; gemini-3.8-flash added.
  Segments are 15 min (~83k tokens). URLs normalised to youtube.com/watch?v=ID. If the first segment comes back empty
  / "END" (a lite fallback that cannot watch video, after the daily quota ran out) it is a quota failure. Lessons that
  failed on the quota are re-dispatched by the half-hourly `check` run between 10:30-11:00 Israel (after the reset).
- 27/10: micro lecture 1 (YouTube) transcribed in ~30 min, then a chapter call hung until the 2.5 h job limit. Now:
  every structured Gemini call has a 12-min HTTP timeout (5 min for the search check) -> retry / next model; last
  year's lecture is started at the START of the job (parallel) and waited for up to 60 min; process.yml 240 min.
- site.yml also runs every 30 minutes on a schedule -> `course_site.py check` (re-read every imported site, no
  chapter writing): new files/weeks are added and a new recording (YouTube included) starts process.yml at once.

## Study week and weekly tasks (2026-10-26)
- He studies ONE WEEK BEHIND the semester on purpose (recordings take days to come out; he does not watch live).
  `STUDY_LAG = 1` in `web/src/lib/week.ts` and `worker/notify.py`. Semester week 1 = SEMESTER_START (Sunday 18/10).
  Deadlines stay real.
- `/week` (home card "📅 השבוע שלי"): his study week's meetings per course (from the timetable via `classMeetings`,
  which now also returns the matched lesson / "none" mark), with uploaded/read state; "להשלים" = earlier meetings not
  uploaded or not read; "⚡ להגביר קצב" = assignments due within 14 days whose material (semester week of the due
  date - 1) is beyond his study week (also a morning push line).
- `syncWeekTasks` (home + tasks load): "📹 להעלות: <kind> שבוע N (dd/mm) · <course>" per held meeting without a
  recording (`external_uid upload:<slot>:<date>`, due +2 days 20:00, closes itself when uploaded/marked); for a
  course with an imported site, when his study week has no lecture of that number this year -> "📼 ... לקרוא את
  החומר משנה שעברה" (`site-week:<lesson>`). Everything depends on the timetable being complete.
- Site lessons (`kind web`, source_url on notion) = last year's material: own group on the course page, not counted
  as unread (home, plan, morning push), no push per chapter (hub), one "📼 נוספו X פרקים" line in the morning.
  Week lessons carry `number` = week N (backfilled by the daily site run).

## Collapsed sections (2026-10-27)
- He wants course pages short: every section of a course page (state vs class, syllabus, course info, add lesson,
  course material, where I stand, studio, files, tasks) and of a self-study track is a `Fold`
  (`web/src/components/Fold.tsx`): one line with title + short summary, closed by default, open/closed remembered per
  section id in localStorage (same section in every course), opens itself on `#<id>` (e.g. `#add`).

## Practice first (2026-10-30) - how he studies now
- He does NOT read long chapters or answer MCQ quizzes (useless for calculation/proof courses). He learns by solving.
  Deep courses (he listens to lectures + practices himself and solves): digital circuits, micro, lab 2, Java.
  Summary courses (short summary of each lesson, then exercises/homework/exam practice): waves, linear, communication.
- Lectures/practices are now authored in SUMMARY mode (`author.SUMMARY_SYSTEM`, `summary_mode`): chapter_md = a short
  summary (🎯 message, main points + formulas, ⭐ what the lecturer stressed, 🏭 why it matters), `lessons.summary_md`
  = the same, NO questions, and `exercises` (every exercise of the lesson with question_md + full solution_md, checked by
  re-solving in the verify pass). Labs, site material and "📖 פרק מלא" (process.yml input mode=full,
  `requestFullChapter`) still get the full chapter; the full chapter replaces chapter_md only (summary_md kept).
- `exercises` table (`supabase/exercises.sql`): from lessons (source lesson) and from files (`worker/exercises.py`:
  homework / past exams / exercise sheets, official solution file "פתרון ..." sent along, else solved + re-solved;
  each file once - `exercises_read.json` next to the course files). Runs daily after the site run and on demand
  (exercises.yml, button on the exercises page).
- `/courses/[id]/exercises?w=` (course card "✍️ תרגילים"): the week's lesson exercises + file exercises on the topics
  taught that week (`lib/exercises.ts`, week = week of the class the lesson recorded); `?files=1` all file exercises.
  Solutions hidden until opened; "✓ פתרתי" (`done_at`). Task per course and study week "✍️ לפתור: ..." (`ex:<course>:<w>`),
  closes when all are solved. Automatic tasks link to what they are about (DeadlineRow `taskHref`).
- Course documents (`lib/courseDocs.ts`, `/courses/[id]/doc/formulas|practical`): formula sheet for 2 A4 pages (print CSS
  `.formula-sheet`, two columns) for every course; for a lab, "🧪 המבחן המעשי" - per experiment theory/verbal questions,
  circuits to build with wiring + instrument settings, must-build list, 3 mock exams. Rebuilt on request; stored as
  course files (the chat sees them).
- Board snapshots: taken at the END of a scene, now marked in the transcript at that moment ("מראה את מה שהוסבר עד
  כאן") and the prompts say a snapshot shows what was said BEFORE its marker; verify checks image/topic match. Old
  transcripts keep the old (start-time) markers.
- Summary flavour by course (`author.summary_task`, `PRACTICE_ONLY` = waves / linear / communication): those he never
  watches - the summary gives everything needed to solve exercises (formulas, methods, step order); the others (Java,
  micro, digital) he watches - a short "סיכומון" to confirm he got the message. Lab 2: nothing for him except the
  practical-exam page (he does the experiments and entry quizzes himself / with GPT).
- Homework said in class (`homework` in the summary JSON) -> tasks "📝 ..." due at the course's next class
  (`hub.save_homework`, uid `hw:<lesson>:<i>`). Homework/exam files: the exercises tab shows per file "אפשר לפתור אחרי
  שבוע N" (last week that taught one of its topics, `fileReadyWeek`).
- Lab practical exams: MIDTERM = experiments 1-5 (incl. 5), FINAL = all; same structure (theory/graph, verbal, build).
  His lab-1 example: two sine inputs -> make a triangle -> summing amplifier. The practical page has mock exams for both.
- 30/10 feedback round: exercises are read AUTOMATICALLY - on every file upload (`addMaterial` dispatches exercises.yml),
  daily, and lessons written before summaries get their exercises extracted once (`exercises.from_lessons`, key
  `lesson:<id>` in exercises_read.json). Each run annotates per course which files were skipped as "not exercise files".
  Every exercise shows its source ("מקור: 🎓 הרצאה 2" / "📄 <file>").
- 31/10: file exercises matched by topic flooded every week (whole exam + homework 3 in week 1). Now each file exercise
  is placed in ONE lesson (`exercises.assign`, `fits_lesson_id`, `duplicate` - supabase/exercises_assign.sql): the
  earliest lesson after which it can be solved entirely, strict (most are "not yet" early on), re-checked daily as
  lessons come; duplicates of class exercises are hidden from the weeks. Unplaced ones show only under "מכל הקבצים".
- Lecture slide PDFs ("הרצאה 2-0 - הדיודה.pdf", kind slides) are exercise sources too (their worked examples) - digital
  circuits had none because only its slides existed. A lesson that gave 0 exercises gets one more try (`lesson0:`).
  Lab courses are skipped. Gemini 2.5 models are gone for new keys (404): lists use flash-latest, 3.8-flash,
  flash-lite-latest, 3.5-flash-lite.
- Nothing to press (31/10): every uploaded file is read by itself (exercises.yml on upload + daily). Reading a file
  also saves its exam hints as course facts (`exam_hint`, "(מתוך <file>)") and its formulas to
  `formula_notes.json`; docs.py includes those notes and rebuilds the sheet when a lesson or a file with formulas is
  newer than it. The exercises-page button is gone.
- Every solution (all courses, 02/11): per part and per calculation step "**נוסחה:** $$..$$ / **הצבה:** $$..$$ /
  **תוצאה:** $$..$$" (✅ before each part's final answer); proofs = numbered steps with reasons. Prompts + verify pass
  enforce it; older solutions are restructured once (`exercises.reformat`, `fmt:<id>`). Display: every $$...$$ gets its
  own line (Gemini put them mid-sentence or glued "$$$$" -> red KaTeX errors), Arabic words stripped (`lib/math.ts`).
- Week of a lesson (exercises): lecture N = the course's Nth lecture meeting in the timetable, practice N = its Nth
  practice (02/11: by upload date lecture 2 showed in week 3, since he uploads a week late). Unnumbered -> upload week.
- Nothing is obvious in a solution (02/11, he could not follow "X_DC = A sinc(f0T)cos(theta)", "sinc(0.5)=2/pi"):
  `author.EXPLAIN_RULE` in every exercise prompt and check - where each formula comes from (short derivation or
  "📘 נוסחה מההרצאה על ..."), every function defined, every intermediate value, "💡 הרעיון" at the end. All existing
  solutions are expanded once (`exercises.reformat`, key `exp:<id>`, 6 per call). Prompts in exercises.py go through
  .format(): the rule's LaTeX braces are doubled there.
- Gemini overload (503 UNAVAILABLE on every model, 02/11): longer waits between attempts (20 s, 80 s); the lesson is
  retried by the half-hourly site check (`retry_after_overload`, lessons from the last 2 days, every 25+ min) and no
  failure push is sent for an overload.
- Formula sheets build themselves (`worker/docs.py`, daily + after exercises.yml) for courses whose facts/notes mention
  "דף נוסחאות"; rebuilt when lessons are newer than the sheet. The app page still has "🔄 לעדכן".
- Home: reminders are about submissions/exams/entry quizzes, not reading; the deadlines card hides automatic
  prep/ex/site-week/upload tasks; "🎯 היום מעבדה" card on lab days; "חזרה יומית" explains itself (spaced repetition of
  quiz questions he answered: 1/3/7/14/30/60 days, wrong -> tomorrow). He hardly uses the course chat (only admin info).
- Course chat: images can be pasted (onPaste on the text box) or picked, several, with thumbnails and ×; an image can
  be sent without text (default question: explain / solve it).
- WeekGrid short names: "מעגלים" contains "גלים" - digital/linear are matched before waves, waves only as a word.
- Timetable: `WeekGrid` - days across (Sunday on the right), hours down, short course names - for the phone; the full
  list + editing is folded below.
- Later (end of semester): exam variations per course as files, from past exams and each lecturer's style.

## Self-study on Friday / Saturday night, code, order of courses (03/11/2026)
- Self-study happens Friday 10:00-12:00 and Saturday night 20:30-22:00 (`lib/selfPlan.ts` SELF_SLOTS, added once to
  the timetable for the main track - VLSI - and editable there), only when nothing is left to catch up on
  (overdue upload / prep / exercise / lab-report tasks). The track page shows the next sessions with one topic each
  (next topics with level < 3, in roadmap order; exam freeze skipped); home shows "🎓 היום לימוד עצמי" on those days;
  pushes: Friday morning and Saturday evening (`notify.self_study_line`).
- The tutor (TUTOR in api/chat/route.ts) asks OPEN interview-style questions and hands-on tasks in real tools (EDA
  Playground + EPWave for SV/Verilog, Compiler Explorer / OnlineGDB for C/C++) - no multiple choice; he needs to solve
  open questions in interviews, with AI and without.
- He is NOT strong in code (a few C++ notions; Java and micro start 04/11): CODE_RULE in the course chat, the tutor,
  summaries and every exercise solution - every line of code explained, new syntax defined, built up gradually, run
  through by hand. Existing solutions with code get one more pass (`code:<id>`).
- "🎓 לימוד VLSI" (/self, 03/11/2026, approved): ONE place - a guided 12-week program (`lib/vlsiProgram.ts`, 24
  sessions: Friday + Saturday night from 06/11/2026, exam freeze skipped) - each session: goal, set-up steps (EDA
  Playground / DigitalJS in the browser, an OpenLane Colab notebook in week 11 - nothing to install), roadmap topics,
  hands-on task with what should come out, interview questions, optional Cadence chapter. "📖 להתחיל מפגש" opens a new
  tutor chat named after the session and sends the session plan (Chat `autoPrompt`); "✓ סיימתי" marks its task
  (`vlsi:<week>-<n>`, due at the slot's end, created by `syncVlsiTasks`); undone sessions carry over. The topic map
  and the Cadence tracks are links from there. Home card / Friday + Saturday pushes show the next session.
- VLSI session lessons (03/11/2026, his wish: "like the university - slides/summary, exercises, MCQ quiz"): each
  session has a lesson in the VLSI course (kind lecture, number = session index + 1, transcript = the session plan
  marked `<!-- vlsi-session -->`), created by `ensureSessionLesson` (current + next session automatically, others on
  "📄 להכין את השיעור") and written by the worker (author.py VLSI_NOTE / VLSI_TASK: full lecture-like summary, 4-8
  exercises with solutions, 8-12 MCQ; no homework matching). The tutor chat is only "💬 להרחיב עם המורה".
- Interview questions must have a real source (his rule, 03/11/2026: "say where it is from, with a link to the question
  on that site - not invented"): `Interview = {q, src, url}` in vlsiProgram.ts, every link found by web search and shown
  next to the question ("🔗 site"). The tutor (route.ts) and VLSI_TASK may only present a question as an interview
  question with a real link; their own questions are labelled "שאלת תרגול (לא מראיון)". Some links are explanations
  of the topic (ChipVerify, Nayuki...) rather than an interview listing - the src label says which.
- Board snapshots written out (04/11/2026, his request - the Java lecturer writes white chalk on black and he can't
  read it): before every snapshot with text, "**📝 מה כתוב בלוח:**" and its content in clean words (comparison -> table,
  steps -> list, code -> code block, [לא קריא] where unreadable). New chapters: author.SLIDES_RULE + VERIFY_SYSTEM.
  Existing chapters: `worker/boards.py` (one Gemini call per lesson, Java courses first, backup
  `chapter_before_boards.md` that also marks it done), first step of enrich.yml (every morning, until all are done).
- Quiz "🤷 לא יודע - תראה לי את התשובה" (04/11/2026, he was guessing on questions he didn't know): shows the right
  answer + explanation, recorded as a miss (attempts.chosen = -1) so the topic counts as weak and comes back in review.
  In every quiz (lesson, review, practice, lab entry quizzes - all use components/Quiz.tsx).
- Course page "חומר הקורס" (04/11/2026): one list "הרצאות ותרגולים" in study order - lecture N (its parts by "חלק 1/2"
  or "חלק א/ב" in the title, then upload time), then practice N, then lecture N+1... (`byMeeting`); other material
  and last year's site after it.
- iPhone rendering bug (04/11/2026, dark blurred rectangles over long pages while scrolling): `.card` had
  backdrop-blur; WebKit tiles tall blurred layers and left stale tiles. Removed the blur from cards (card bg 0.93);
  only the small bottom nav keeps it. Don't put backdrop-filter back on large elements.
- "📖 מה כל שורה עושה" (04/11/2026, he can't read code yet): under EVERY code block rendered by components/Chapter
  (chapters, exercise questions and solutions, docs, chat) a table code line -> what it does in Hebrew
  (components/CodeLines.tsx -> /api/explain-code, one Gemini call per block when it scrolls into view, cached in
  localStorage). ```wave and ```text/output blocks are skipped.
- Java J0-J4 (04/11/2026): the lecturer told them to complete these alone - they are Sang Shin's javapassion labs
  (J1 = LAB-1001 environment, J2 = LAB-1002 basics; he uploaded J1+J2 zips in the session). Claude wrote "תרגול 0 ·
  השלמה J0–J4" (chapters/java-j1-j2.json: chapter + 6 exercises incl. the labs' homework + 11 MCQ). J0, J3, J4 still
  missing - when he uploads them, extend the same JSON and re-run publish (same lesson is updated).
- Content Claude writes in a session without DB keys goes through `.github/workflows/publish.yml` (dispatch:
  course regex + chapters/*.json -> `hub.py add`, chapters/*.md -> `hub.py sheet`).
- Java help sheet (his request: one page allowed in the exam, "how to write a class" templates): chapters/java-sheet.md,
  saved as the course's formula_sheet.md ("📄 דף נוסחאות" button). For Java, docs.py / courseDocs.ts only ADD new
  syntax to it (CODE_UPDATE, rejected if shorter) - never rebuild from scratch.
- Arabic letters in Hebrew (04/11/2026, quiz showed "لבין", "وטיפוסי"): Gemini glues an Arabic prefix letter to a
  Hebrew word. `fixArabic` (lib/math.ts; used by Chapter, Rich, CodeLines) and `author.fix_arabic` (in validate, so
  new content is saved clean) turn و ل ب ك ه م ش before a Hebrew letter into ו ל ב כ ה מ ש and drop other Arabic.
- Squashed chapters (04/11/2026, Java practice 2: 4.4k chars on 6 lines - headings, lists, "🏠" all run together):
  `author.is_flat`; a squashed draft is written again once, and the verify pass may not squash or cut the chapter
  (<70% of the draft -> the draft's chapter is kept). `hub.py flat` lists squashed ready chapters (publish.yml
  inspect=flat); found Java practice 2 + micro web 7, re-dispatched through process.yml.
- Java = always the full reading chapter (04/11/2026, practice 2 came out as a short summary, "not what I expect"):
  `author.FULL_COURSES`; summary_mode(lesson, mode, course) is False for it, and a full chapter clears summary_md so the
  lesson page shows the chapter first (exercises already saved stay).
- Claude writing a chapter from a cloud session (no DB keys): `fetch.yml` (lesson_id + a one-time RSA public key) runs
  `hub.py fetch`, encrypts it and pushes it to branch fetch/<id>; the session decrypts it, writes chapters/<name>.json and
  runs `publish.yml` (course + kind + number -> `hub.py add` updates the existing lesson), which also deletes fetch/*.
  Done first for Java practice 2 (04/11/2026, chapters/java-practice-2.json: EX1, EX3-EX6 from the screen + EX2).
- Micro environment (04/11/2026, done with him, works - "Am Israel Chai" in the simulator): VS Code + PlatformIO IDE +
  Wokwi Simulator (free 30-day license, renew by "Wokwi: Request a New License"; his runs to 4/12/2026), board
  Espressif ESP32-S3-DevKitC-1-N8 (`esp32-s3-devkitc-1`), framework Arduino, the TA's wokwi.toml + diagram.json
  (github.com/Brown-Programming-Academy/microcontroller-public). Projects live in C:\esp - the default
  OneDrive\מסמכים path broke the linker (Hebrew in the path). Course is theoretical: buying hardware is optional
  (site suggests an ESP32-S3 dev board + an electronics kit).
- "מידע על הקורס" without repeats (04/11/2026, micro had the same facts many times - each lesson, last year's site,
  the syllabus repeat them): `worker/facts.py` merges a course's facts with Gemini (every row in exactly one merged line,
  contradictions -> newer kept + "(earlier: ...)"; fallback = exact-text merge) into facts_merged.json {sig, items[ids]}.
  Rows are NOT deleted; lib/facts.ts shows the merged lines (deleted rows drop out, newer rows shown as is), ✕ on a
  line deletes its rows (deleteFacts). Runs daily (enrich.yml) and on demand (publish.yml inspect=facts).
- One name per topic (04/11/2026, same as the facts): `worker/topics.py` groups a course's topic names (questions,
  exercises, lessons.topics) with Gemini into topics_merged.json {sig, map original -> merged}; lib/topics.ts applies it
  in topicStats ("איפה אני עומד", home, exams, plan) and in the practice page's ?topic= filter. DB names untouched.
  Daily in enrich.yml, on demand publish.yml inspect=topics.
- Lesson page: exercises come AFTER the summary / chapter, just before the quiz (04/11/2026).
- Code blocks never wrap (04/11/2026, "like the formulas"): `.chapter pre` white-space: pre + sideways scroll, .82em;
  CodeLines shows each code line whole on its own row with its Hebrew under it.
- Timetable "📋 הקורסים: ציון ומבחן" (04/11/2026): per course grade components, exam format, and the formula sheet only
  when allowed - from facts.py's `summary` {grade, exam, formula_sheet} in facts_merged.json (only what the facts say),
  falling back to courses.grade_weights / exam_type. Rebuild all: publish.yml inspect=facts-force.
- His FPGA board (04/11/2026): PuZhi A7-EDU (AliExpress "PUZHI FPGA SDR Store"), Artix-7 **XC7A35T** (listing:
  XC7A35T-2FGG484I -> Vivado part xc7a35tfgg484-2), 8-digit 7-seg, HDMI out, Gigabit Ethernet, UART, onboard JTAG,
  1GB DDR3. Pin file (XDC) / schematic NOT received yet - asked him to get them from the seller; never guess pins.
  APPROVED 04/11/2026 ("if this is what boosts my CV for those companies, I'm in"): the 12-week program builds one CV project - "Mini-TPU" systolic-array int8 NN
  accelerator classifying drone sound clips sent over UART (targets NVIDIA/Google/Amazon/Apple/Intel/Marvell/Elbit/
  Rafael); alternatives on the same accelerator: ECG arrhythmia, keyword spotting, motor faults.
- Board project in the program (04/11/2026): manual received (PA35T-EDU V1.0) -> `fpga/pa35t_edu.xdc` (all pins: 200MHz
  diff clock R4/T4 DIFF_SSTL15 [bank 34 = DDR3 1.5V - verify], rst R14, 6 LEDs active-high, 3 keys active-low, 16 DIP,
  UART P15/P14 via CH340, two 4-digit 7-seg on bank 16 - polarity unknown, found on the board in week 3).
  vlsiProgram.ts: PROJECT, BOARD_PINS, VIVADO install steps (session 1 setup), `board` step on every session (MAC ->
  FSM -> perf counter -> systolic PE/2x2 -> timing/pipeline -> UART/FIFO -> int8 weights in BRAM -> 4x4 array classifies
  drone clips -> reports/GitHub/video -> interview). Shown on the VLSI page, sent to the tutor and the lesson writer
  (VLSI_TASK "## 🔧 על הלוח"); unread session lessons written before this are re-written once (ensureSessionLesson).
  Dataset: DroneAudioDataset (github.com/saraalemadi/DroneAudioDataset), features computed in Python on the PC.
- 05/11/2026 failures: he opened ~20 lessons at once -> all ran in parallel -> free Gemini daily quota gone (annotations:
  "המכסה היומית... נגמרה"; one overload). Fix: lib/queue.ts `startLesson` - at most 2 lessons written at a time, the rest
  "queued" with progress "⏳ בתור" (+ "(פרק מלא)"); `worker/queue_runner.py` (every half hour from site.yml check,
  replacing the parallel retry_after_quota/overload) works ONE at a time: waiting -> quota errors -> overloads (25 min)
  -> fill-ins, and stops until 10:30 Israel when the quota runs out (state in storage system/queue_state.json).
- Every lecture/practice gets BOTH a condensed summary (summary_md) and a full chapter (chapter_md) (his request
  05/11/2026): queue_runner fills them in - full chapter via hub.cmd_process mode full (QUIET: no pushes; a failed fill
  leaves the lesson ready), summary from the full chapter text (author.summary_from_chapter, one cheap call). Java is
  full by default and gets its summary that way. Lesson page: everything folded by default (summary, full chapter,
  exercises, quiz - fold ids per lesson).
- DATA SAFETY (05/11/2026): re-writing a lesson used to replace its quiz -> attempts cascade-deleted. save_chapter now
  keeps the old quiz when he has answered any of it (hub.answered).
- Self-study sessions are written as ONE full chapter (SYSTEM + VLSI_TASK, schema with exercises): first exercise =
  "🔧 משימת הפרויקט: ..." as homework with full solution for his board, then 2-4 practice exercises, 10-15 MCQ. Page
  order for them: full chapter -> quiz -> project task. VLSI page: per session "1. 📖 פרק 2. ✅ שאלון 3. 🔧 משימה",
  and "📋 אפיון הפרויקט" (PROJECT_SPEC: problem, architecture table, spec, deliverables, CV line, interview pitch).
  Session lessons without "גרסה: פרק מלא" in the transcript are rewritten once when not read.
- Cadence tracks archived 05/11/2026 (not deleted): their labs need licensed Cadence tools he does not have, and the
  program already covers SystemVerilog. Semester-B self-study plan: proposed, waiting for his approval.
- 05/11/2026 (2): failures all day = Gemini free tier OVERLOADED (503), not only quota. He asked why depend on Gemini.
  Added Claude as the fallback writer on HIS Claude Pro subscription: `.github/workflows/claude-chapter.yml`
  (anthropics/claude-code-action@v1, secret CLAUDE_CODE_OAUTH_TOKEN from `claude setup-token` on his PC - he adds it in
  GitHub repo Settings -> Secrets; never pasted in chat). It runs `hub.py fetch`, Claude writes chapter.json (full
  chapter + summary_md + quiz + verification) and `hub.py publish`. queue_runner hands a lesson to Claude when Gemini
  is overloaded / out of quota (CLAUDE_PER_DAY = 4, counted in system/queue_state.json; site.yml passes HAS_CLAUDE),
  and stops the run on an overload instead of grinding through every lesson. Fill-ins stay on Gemini only.
- Home page (05/11/2026): folded by default - "על מה להשקיע", all reminders, "מחכה לקריאה", deadlines, weak topics,
  my courses. Open: today at university (each lecture now shows its course's reminders under it), self-study, daily
  review, week, recordings. New "⚙️ בעיבוד ובתור": processing -> waiting -> failures retried by themselves (quota after
  10:30 / overload), numbered (now split - see below). Course list labels last year's comparison
  transcript "📼 להשוואה - מוכן". `hub.py stuck` (publish.yml inspect=stuck) lists every lesson not ready.
- Why nothing was "processing" (05/11/2026): GitHub's "*/30" schedule of site.yml actually fired every 3-4 hours, so
  the queue barely ran. Now `.github/workflows/queue.yml` runs `queue_runner.py --loop` for up to ~5.5 h in one job:
  Gemini busy -> wait 10 min and retry; quota -> sleep until 10:30 if inside the job; nothing he waits for -> stop;
  out of time with work left -> dispatches the next queue.yml. Started by the app whenever a lesson is put in line
  (lib/queue.ts dispatchQueue) + backup schedule every 2 h. Home: "⚙️ בעיבוד עכשיו" and "⏳ בתור" are separate folds,
  each open by itself only when it has 5 items or fewer (6+ stays closed).
- 05/11/2026 (3): diagnosis by `hub.py ping` + a queue pass: strong models (3.8-flash, flash-latest) 429 daily quota,
  lite models 503 on real lessons. He got "⚠️ העיבוד נכשל" pushes every few minutes while the queue retried - now
  no push for busy / quota failures (retried by themselves), and a mix of busy + quota is reported as busy.
- 05/11/2026 (4): the repeated "⚠️ העיבוד נכשל: מאמר 3" = micro site lesson 52d677c0 (week 3, analog/digital signals,
  with PDFs) failing with Gemini "500 INTERNAL" - not classified as busy, so it pushed each retry. Now 500 INTERNAL =
  busy (retried, next model, no push), and the queue tries one lesson at most 3 times a day (state "tries").
  Note: micro has 4 site lessons numbered web 3 (one per section of week 3 on the Notion site) - by design.
- Digital circuits practices 1-3 (05/11/2026): none took place (elections, engineering festival); written by Claude from
  the uploaded "3-מחברת תרגול 1.pdf" (26 handwritten pages: noise margins + NMOS/R inverter VTC & delays; CMOS, drive
  strength, NAND/NOR/complex-gate sizing; Logical Effort) -> chapters/digital-practice-{1,2,3}.json (full chapter +
  summary_md + exercises + MCQ). Notebook errors flagged: NMH 1.92 (not 1.972), tr = 2.197*tau = 22ns (not 2.197ns),
  b = mu_n/mu_p (written inverted once). `hub.py materials` + fetch.yml "files:<course>:<title regex>" pull course
  files encrypted for a session.
- Claude token: he created CLAUDE_CODE_OAUTH_TOKEN (verified set=true via publish.yml inspect=claude). claude-chapter.yml
  needed `id-token: write` + github_token; the first real run then ended "is_error" - diagnosing with the execution
  file printed as annotations.
- Home "מחכה לקריאה · שבוע לימוד N" (05/11/2026): only this study week's lessons (lecture/practice number == studyWeek,
  ready, unread, not self-study / site) - he settles the week on Saturday night; earlier unread weeks show as one line
  "⏪ N משבועות קודמים" linking to /week.
- His PC already has Vivado (checked 05/11/2026 via reg query / dir): Vivado ML Standard 2024.2 in C:\Xilinx (with the
  Xilinx cable drivers) and 2025.2 in C:\AMDDesignTools\2025.2; both have Artix-7 parts. Use 2025.2; no install needed.
- Courses list: in the order he meets them in the week (first timetable slot), courses without classes last.
- "📖 מה כל שורה עושה" (06/11/2026, his screenshot: red Gemini-quota error under the VLSI code): explanations are now
  kept in storage `<user>/codelines/<hash>.json` (hash = web/src/lib/codeHash.ts = worker/codelines.py code_hash,
  djb2 over the block without trailing whitespace) and written ahead of time every morning by `codelines.py` in
  enrich.yml (newest lessons first, chapters + summaries + exercises). The API route reads storage first and saves what
  Gemini writes; when Gemini is out the fold stays closed with a gray note + "לנסות שוב", never a red error.
- Quiz (06/11/2026, he noticed the right answer was almost always first and the longest): Quiz.tsx shows the options
  in a fixed per-question shuffle (seeded by question id; attempts still store the original index). author.SYSTEM /
  VLSI_TASK / VERIFY: options of similar length and style, explanations refer to options by content, not number.
  (Claude's own vlsi-session-1.json had all 10 correct = index 0 and mostly the longest - follow the rule when writing.)
- Self-study lesson page: the session's job-interview questions (vlsiProgram interview, with source links) close the
  quiz fold. /self has a "🗺️ הכרת הלוח" fold (BOARD_TOUR): what each board part is for, what a pin is, when it's used.
- Wave diagrams (06/11/2026, his 10th complaint about graphs): the tutor asked about "tick 3", which was not drawn;
  he read the yellow mark "3" (the 3rd rising edge) and was told he was wrong. Now every moment is labelled under the
  graph (↑1 ↓1 ↑2 ↓2 ...), yellow marks are letters A, B..., and the chat / author prompts forbid "tick" towards him -
  only ↑n / ↓n / letters. VLSI session 1 (blink) done on the board 06/11: LED blinks; next: reset (Saturday night).
- Self-study by what he did, not the clock (06/11/2026): "✓ סיימתי" on a session lesson marks its vlsi:<key> task done;
  the home slot shows "✓ סיימת את המפגש של היום" instead of "עכשיו" when no open session is due today; reminders for
  sessions say "ללמוד: ..." (היום / מחר / בעוד N ימים) and link to /self - never "להגיש".
- Board checked 07/11/2026 (session 2): reset key = NRST (leftmost of the 4 red keys, R14), low when pressed; LED1..LED6
  in a column at the right edge (LED6 red). Session 2 sync reset works on the board.
- Weekly backup (07/11/2026, he asked for it fully automatic): `.github/workflows/backup.yml` (Sunday ~04:00 Israel +
  dispatch) runs `worker/backup.py dump` (all tables found via the REST root + every storage file), encrypts (AES key
  wrapped with `backup/backup_pub.pem`) and keeps a pre-release `backup-<date>` (last 8). The private key is ONLY in his
  Google Drive: "study-hub - מפתח גיבוי (backup_priv.pem)" (file id 1olpLTc84PShiepcPZy98VQWkNLtGJeXy). Restore: docs/BACKUP.md.
- Formula sheet as PDF (08/11/2026, waves course first): `worker/sheet_pdf.py` renders the sheet (markdown + KaTeX, RTL,
  two columns, math forced LTR and shrunk to fit its column) with Playwright/Chromium -> `formula_sheet.pdf` + a
  materials row "📄 דף נוסחאות (PDF להדפסה)"; `docs.save` calls it on every save, `docs.py <course>` re-makes the PDF
  when the sheet is current. A sheet with the stamp "נכתב ע״י Claude" is only ADDED to by Gemini (FORMULAS_UPDATE: new
  formulas + a row per new exercise type in "🧭 מה שואלים ← מה עושים", source tags ה#/ת#). The app's "לעדכן" for the
  formula sheet now dispatches exercises.yml (no direct Gemini rewrite); the doc page has "⬇️ PDF להדפסה"; the .md
  in the course files opens the rendered page. Waves sheet: chapters/waves-formula-sheet.md (lectures 1-3, practices
  1-3; flags: tilt-angle quadrant in practice 3's answer, TA's skin-depth remark, H=B/μ).
- Exercise fixes (08/11/2026): `hub.py exercises <course> chapters/<fixes>.json` (publish.yml inspect=exercises,
  chapter=<fixes json>) replaces one exercise's text, keeping done_at. Waves lecture 1: Gemini had invented the class
  exercise's field (x̂E0cos(ωt-kz)); the slide's is E0(yx̂-xŷ)cos ωt -> H=(2E0/ωμ)sin ωt ẑ, J=ωεE0(yx̂-xŷ)sin ωt.
- Exercise audit (his request 08/11/2026: "check every exercise in every course", order waves -> linear circuits -> rest;
  solutions written out in full - he learns by reading solutions). `hub.py materials` now also writes exercises.json
  (all exercises of the course with ids); `hub.py exercises` fixes by id / adds. Source scripts: chapters/fixes/*.py.
  DONE: waves practice sheets 1 and 2 (14 exercises; official-answer slips flagged ⚠️ in the solutions).
  TODO waves: sheet 3 (5), lecture PDFs 1-3 sheet exercises (12), lesson exercises (15). Then linear circuits, others.
  Pending his approval: a weekly "core" set of 3-5 exercises, the rest folded as an optional bank.
- His weekly routine (08/11/2026; 09/11: Thursday = half linear + half random signals until 22/12): Sun waves (podcast + video first, then the summary, then practice), Mon micro,
  Tue lab 2 + digital circuits, Wed Java, Thu linear circuits. He reads summaries/chapters and learns by reading full
  solutions; practises 3-5 core exercises a week (not 20). ESP32 for micro arrived.
- Auto studio: hub.auto_studio - every new LECTURE of a course matching AUTO_STUDIO (waves) gets a podcast + video
  (lesson_media rows + media.yml via course_site.dispatch_inputs; only where GITHUB_TOKEN exists: process/queue runs).
- Lab 2 report task: created on the lab day for that experiment, due the Monday after at 20:00 ("write right after
  the lab -> partner -> hand in by Monday evening"); old open tasks are moved to that rule (labTasks.ts).
- MCQ: conceptual only; a question that needs a number carries its formula (author.SYSTEM / VLSI_TASK).
- Past exams: waves 20.03.24 + solution, 25.07.24, solution of 05.09.24 uploaded. Pattern: oblique TE plane wave at
  an interface (both exams, 40-50 pts) + transmission lines (stub/Smith/VSWR or bounce diagram) + line parameters.
  University Drive with all exams: https://drive.google.com/drive/folders/1kIkcJQOKA0k1xCQpC0EcN6qmwJZGWHj6
- Studio TTS fixed (08/11/2026): google-genai 3.0 sent speech_config wrongly ("Unknown name speechConfig") -> studio.tts
  calls REST v1beta directly; 3.x TTS models need one content part per line with speechMetadata.speaker and NO system
  instruction; 2.5-preview-tts takes the whole dialogue. Checks: publish inspect=tts; failed media again: inspect=studio-retry.
- Waves exams from the students' Drive added as course files (drive:<id>, kind past_exam): solutions 19.08.24, 2023,
  "פתרונות שאלות מבחן מפולגות" (hub.py drive, publish inspect=drive).
- Every page (except home) starts with components/BackLink: sticky "→ ..." at the top while scrolling (his request
  08/11/2026). Course page -> all courses; top-level pages -> home. He doesn't use the chats (too slow).
- Core exercises (08/11/2026): storage <user>/materials/<course>/exercise_core.json {weeks:{n:[{id,why}]}, exam_note}
  (chapters/<course>_core.json, publish inspect=core). The exercises page shows "⭐ הליבה של שבוע N" + folded bank.
  Waves core weeks 1-3 set (11 exercises) and all 11 re-solved in full. Micro core weeks 1-3 set (10) from the two
  exam papers (תשפ"ו מועד א/ב: 90 min, no formula sheet, 6 MCQ x10 + 2 code questions x20); 7 of them re-solved.
  Digital circuits core weeks 1-3 set (10; no past exams yet; practices 1-3 were written by Claude, MOSFET/energy/diode
  core solutions checked OK; eca95ac1 NMOS VTC not re-checked). Java core weeks 1-3 set (11; exam is MCQ: output /
  error / fill-in / concepts; every output verified by running javac+java in the session). Linear circuits core weeks 1-3 set (10; exam מועד א' תשפ"ו = 6 MCQ
  solved in the notebook: BJT bias, feedback, Schmitt oscillator, op-amp gain expression, CE Q-point+Amid, CC; cascade
  example restored from the lecture transcript). Homework-1 "שאלת מבחן" items have no circuit (figures) - not used. Communication systems core weeks 1-3 set (11; 09/11; fixed: LNA self-noise 3.22e-12 W not 8.8e-14, Q 200 not 80).
  09/11: his Drive links -> recent exams registered as course files: chapters/{comm,linear,digital}_drive2.json
  (34/34/28 files, 2018+; exercises.py extracts them by Gemini over time). NEXT: read the newest exam of each
  (linear 03.04.24 & 07.05.24, digital 17.07.24 & 10.12.23, comm tashpag reconstruction + 2022) and align weeks 1-3 cores.
  DONE 09/11: read linear 7.5.24, digital 28.9.23 + 17.7.24, comm 2020 B + 2022 A: weeks 1-3 cores already match the
  exam topics; exam_note of each core updated with the real format. Comm 2022 A Q1 (LNA gain) computed 11.6 dB vs
  marked 12.8 dB - not used without the official solution.
  NEXT: every week, a core for the new week in each course (he asked for it in ALL courses); later weeks of linear (same recipe: fetch `files:<course>:<regex>` -> exercises.json,
  pick 3-5/week by the exams, chapters/fixes/<course>_core.py -> publish inspect=exercises + inspect=core);
  then exam characterisation per course; then the bank.
- Explainer video (studio.make_explainer): 12-18 slides, KaTeX formulas (local KaTeX in media.yml), matplotlib diagram
  per slide (model-written code run with no env), worked-example steps revealed one by one, ONE natural Gemini voice
  (narrate(): a few slides per TTS request; no edge fallback - fails on quota and queue retry_studio redoes it).
  Free Gemini image models are limit 0. Waves lectures 1-3 videos made 08/11 with this engine.
  His feedback 08/11 ("narrator great, text not in sync, slides cropped, wants subtitles, watches at 1.5x"): fixed -
  group audio is cut at real pauses (split_points, ffmpeg silencedetect) not by text share; one frame per narration
  sentence with a burned subtitle bar, cut at the pauses too; fixed 500px image column (no overflow); ONE image track
  (concat list with exact durations) + ONE continuous audio track muxed once (gluing ~100 AAC clips drifted seconds);
  keyframe every 2s; long formulas shrink to fit; pauses = silencedetect -32dB/0.12s (measured). App Player: speed buttons 0.75-2x (remembered, localStorage "study-speed"). Diagram labels: math in $..$.
- AUTO STUDIO ON again (08/11 evening, he loved the new lecture-1 video: "פגז, ככה לכל הרצאה"): hub.AUTO_STUDIO = waves,
  AUTO_KINDS = ("video",) - every new waves lecture gets the explainer video; podcasts manual. He deletes the old
  lecture 2-3 videos himself; new ones were dispatched 08/11 but hit the Gemini TTS daily quota -> queue retry_studio after reset.
- 09/11: "everything in processing never ends, 2 days" - lessons whose claude-chapter run failed (token 401) stayed
  "processing" and the queue only picks queued/error/ready. queue_runner.unstick() puts processing > 3h back to queued;
  CLAUDE_ON = False (no Claude fallback until he renews CLAUDE_CODE_OAUTH_TOKEN). Self-study (VLSI) sessions get the
  explainer video too (AUTO_STUDIO += VLSI; `code` field on slides = monospace code block); studio-backfill dispatches 2,
  the rest wait as error "ממתין למכסה..." for retry_studio (2 per queue run). unstick() also re-queues errors
  "Claude לא סיים" / DEADLINE_EXCEEDED / 504 older than 12h; 09/11 run wrote all 11 (VLSI 7,14,16,17,18,20,22, micro
  web weeks 3/4/8, micro lecture 3). Weekly scheduled task (Sat 20:47 Israel) builds the next week's core in all courses.
- 🔥 Warm-up (his request 09/11, ALL courses; lib/warmup.ts): FIRST fold in every lesson page ("🔥 חימום לפני השיעור",
  open until the lesson is marked read) = questions on EVERY earlier lesson in study order (lecture N part A/B, then
  practice N; sessions only among sessions): at least one from each, 10 in all (more when there are more earlier
  lessons), extras from the newest, wrong-last-time first. End screen per earlier lesson: >=75% ok, >=50% -> its
  condensed summary (#summary-<id>), else its full chapter (#chapter-<id>). /courses/[id]/warmup (course page button,
  home links) redirects to the warm-up of the next lesson he has not marked read.
- 09/11 batch: (a) lib/rollTasks.ts - an open study task (kind other, not labrep:/labq:) whose date passed moves by whole
  weeks to the future (home + tasks page, after the syncs). (b) timetable: WeekGrid short() and SlotCard show the VLSI
  track as "לימוד עצמי VLSI" (it matched /ספרתי/ and showed as digital circuits). (c) tasks page grouped by week: this
  week open, later weeks folded with counts. (d) communication: 90% exam + 10% assignments (מגן), not uploaded yet
  (hub course-set, chapters/comm_course.json). (e) AUTO_STUDIO = all his courses, AUTO_KINDS = video + podcast, for
  every lecture and every "מפגש" session; studio-backfill queues ALL as waiting (retry_studio 2 per queue run).
  Random signals backfill waits for lectures 1-6 to be re-authored (10/11 check-in). (f) English words: the 1000-word list
  put him off - default view = the 10 newest words + a quiz on them; the full list one tap away (components/Words.tsx).
  (g) 🎯 "מבחן צפוי" per course (/courses/[id]/forecast; storage exam_forecast.json via hub forecast): sections with
  chance %, points, why, taught or not, tip, linked solved exercises (his "פתרתי" status) and a readiness % (chance x
  points over taught sections). Source chapters/fixes/forecasts.py -> chapters/<key>_forecast.json; the Saturday core
  task updates it weekly. Also a PDF mock exam (hub forecast_pdf: one or two linked exercises per section by chance,
  questions first then full solutions; storage exam_forecast.pdf + material "🎯 מבחן צפוי (PDF)", button on the page;
  exercises.py ignores it). Rebuilt on every forecast publish.
  09/11: he wants the PDF in the REAL exam format and count (MCQ stays MCQ with worked solutions, open stays open; rnd 4,
  linear 6 MCQ like moed A 5786, ...). chapters/fixes/mocks.py adds "mock" to <key>_forecast.json (run AFTER
  forecasts.py); hub mock_md renders it (options א-ד, answer + full solution in part B). Done: rnd, linear. Next: comm
  (~14 MCQ), micro (6 MCQ + 2 code), digital (MCQ), java (MCQ), waves (3 open). Recompute every number before publishing.
  (h) 09/11: VLSI/SystemVerilog - "I understand nothing, I repeat like a parrot", and it is the field he wants to work
  in. Needs understanding-first teaching (circuit behind every line, predict-then-simulate, explain-back), proposed to
  him: live guided sessions with Claude on Fri/Sat + a "הבנה" layer per session. Waiting for his answer.
- 09/11 his screenshot: the bottom nav and the floating back button jumped to the middle of a long page on the iPhone
  (backdrop-filter on position:fixed, the same tiling bug as the cards). No backdrop-blur anywhere now; Nav, BackLink
  and the sticky top bar are opaque, fixed ones on their own layer (translateZ(0), will-change).
- Lab 2 (10/11): "✍️ או לכתוב מה המרצה אמרה" in LabUploads -> addLecturerText: a 🎙️ lesson (kind other) whose
  transcript is the typed text, processed like a recording. Lab page button "✍️ להכניס את השאלות שהיו בבוחן הכניסה"
  -> /courses/[id]/entry#report (EntryReport, existing: text/photos -> entry_reported questions).
- Cancelled class meetings (10/11, all courses): web/src/lib/cancelled.ts - storage <user>/cancelled_meetings.json =
  ["<slot_id>|<date>"]; classMeetings skips them, so lecture N stays N and moves to the next meeting (study weeks,
  upload reminders, exercise weeks all follow); notify.py evening push skips them too. UI: /schedule fold
  "🚫 שיעור שבוטל" (a week back to a week ahead, MeetingsToggle). The make-up is just uploaded as usual.
- Exercise layout (11/11, "the equations jump, I can't tell what each line says"): worker/tidy.py - layout only (a
  display formula gets its own line, נוסחה/הצבה/תוצאה labels start lines, glued steps split; text/formulas unchanged,
  idempotent); applied to every new exercise (hub save_exercises, exercises.py, hub exercises) and per course with
  publish inspect=tidy (originals saved to storage tidy_backup_<stamp>.json). Order he asked: digital, Java, micro,
  linear, waves, communication, (random signals).
- Exercise sources (his request 08/11): every exercise shows "מקור: <file | lesson (date)> · 📍 עמ' N" - worker/locate.py
  matches the exercise text to the PDF pages (file, or the lecture's "הרצאה N" slides) + board snapshot numbers;
  storage <user>/materials/<course>/exercise_where.json; runs in exercises.py for new ones, or publish inspect=where
  (title=anything = redo all). A core pick may carry its own "where" (wins). Scanned PDFs have no text -> no page.
- Studio: edge-tts (Microsoft Hila/Avri Hebrew voices) when Gemini TTS quota is gone; video from the lecture's PDF
  ("הרצאה N" in course files, PyMuPDF) when no board snapshots. Linear-circuits media deleted at his request.
- Reminder task: create GitHub repo "projects" by Fri 13/11 (session cannot create repos; files ready in scratchpad -
  regenerate from fpga/ + PROJECT_SPEC if lost). Then add_repo(push) and move fpga/ there.
- fetch/* branches carry web/vercel.json (ignoreCommand exit 0) - Vercel had mailed him "Preview deployment failed" for them.

## Lectures vs practices (his question 11/11/2026)
`fetch.sh outline` (hub outline) dumps every lesson's topics + chapter. Findings:
- **Digital circuits (final, his wish "lecture N -> practice N, no bridge"):** practice 1 = TA notebook 1 (fits
  lecture 1); practices 2/3/4 written by Claude for lectures 2/3/4 (chapters/fixes/dig_track.py, numbers verified
  numerically; hub `reorder` + chapters/digital-reorder.json). The TA notebooks of CMOS sizing and logical effort are
  now kind other 2 / other 3 ("📦 מחברת המתרגל ...") until those lectures - then make them the matching practice N.
  A real practice recording that arrives as practice 2-4 would collide: renumber it to its lecture.
- **Linear (done 11/11):** practices 1-2 written by Claude for lectures 1-2 (chapters/fixes/lin_track.py: sources and
  loading, two-ports, H from the pi model, amplifier models; dB, efficiency, bias, cascades - Sedra ch. 1); the class
  op-amp practice -> practice 3 (fits lecture 3); class practices 2 (slew rate, rectifier, regulator) and 3 (oscillator)
  -> other 2 / other 3 ("📦 ...") until those lectures. chapters/linear-reorder.json.
- **Communication (done 11/11):** practices 1-2 written for lectures 1-2 (chapters/fixes/comm_track.py, exam is open);
  class practices 3-4 already fit lectures 3-4.
- **Waves, Java, micro:** aligned, left as they are (waves P3 = polarization of lecture 3; micro P1-P2 bitwise ~ lecture 2).

## Always both chapters (11/11/2026)
No "write the full chapter" button any more: the lesson page says the full chapter is written automatically; the queue
fills it (lecture / practice with only a summary) and writes the cheap summary for any lesson with only a full chapter
(sessions too). Claude-written practices (transcript "<!-- written by Claude") are never re-written by Gemini;
chapters/fixes/track.py builds them: full = recap + every exercise worked out, condensed = recap.

## Exercises tab: week N = lecture N (11/11/2026)
He studies lecture N + practice N, then opens the course's "תרגילים" tab and picks week N. `lib/exercises.ts`:
lessonWeek = the lesson's number for lectures / practices / "מפגש N" sessions (calendar week only for other kinds;
"📦" notebooks in no week). The tab lists weeks 1..last and opens on the first week with unsolved exercises
("כאן אני"). Core picks (exercise_core.json, still keyed by calendar week) are shown in the week of their own lesson.
Lecture / practice pages no longer show the exercises - only a link to that week. Weekly "✍️ לפתור" task = the course's
latest week.

## Formula display fixes (12-13/11/2026)
- Chapters: a long formula inside a list item becomes its own line indented to the item (lib/math.ts, width counted
  as seen); FitMath (app layout) shrinks display formulas to the phone width. Scan of all chapters: 6 of 5,434 broken.
- Video slides: the text column shrinks until it fits above the subtitles (studio.render_slides).
- `hub studio-redo <course>` (inspect=studio-redo) queues a new video per lecture / session; retry_studio makes 2 per
  queue run (cron every 2 h); the app shows only the newest ready video of a lesson. Random signals: 21 queued 13/11.
  Other courses after it, when he asks / the quota allows.

## Lab experiments as lessons (11/11/2026)
`hub lab-lessons "מעבדה 2"` (inspect=lab-lessons): one lesson kind lab number N per experiment, transcript = booklet docx
(+ partner's / his .docx summary reports) marked LAB_NOTE; the queue writes the lab chapter (KIND_TASK lab: goal,
theory, prelab answers, procedure, 3-5 min board explanation, examiner questions) and auto_studio now also makes the
video + podcast for kind lab (AUTO_STUDIO includes מעבדה). Lab page: "🔬 הניסויים" fold. Experiment 9 has no booklet
(partner's report only). Run it again when a new booklet is uploaded (existing experiments are skipped).

## Self-study redesign (approved 13/11/2026)
- He reads code but can't write it; Vivado steps were unclear. Approved 4 phases: A foundations (weeks 1-2), B the
  language step by step (3.1 module/assign, 3.2 always_comb/case, 4.1 always_ff/register/counter, 4.2 parameter +
  hierarchy/ALU, 5.1 testbench, 5.2 self-checking), C Vivado in depth (6.1 simulation/errors, 6.2 to the board/reports/
  ILA), D core + Mini-TPU project (7.1 FSM, 7.2 counters/shift, 8.1 timing, 8.2 pipelining/metastability, 9.1 MAC,
  9.2 systolic array, 10.1 UART, 10.2 FIFO, 11.1 integration, 11.2 synthesis/STA, 12.1 interview Qs, 12.2 mock).
- Session format: warm-up -> VIDEO only (no podcast for self-study) -> "grammar of the day" -> components line by
  line -> exercises predict/fill/modify/write (hint ladder) + HDLBits / EDA Playground / ChipDev links -> FULL
  simulation guide in every session up to 6.2 (Vivado + EDA Playground) -> "🔧 תרגול על הלוח" (weeks 1-6; project task
  from week 7) -> quiz + interview Qs. Lesson page order matches (self: warm-up, video, chapter, exercises, quiz).
- 2.2 done in this format (chapters/fixes/vlsi_w2s2.py, code checked with iverilog). 3.1 done 17/11 (vlsi_w3s1.py +
  vlsi_w3s1_sv/: mux two ways + exhaustive tb, hex 7-segment, board top with SW8/SW7 polarity switches; video requested).
  Next: 3.2 (always_comb / case per the 4-phase plan; vlsiProgram.ts still has the old title for 3.2). Write each next session before he
  reaches it; vlsiProgram.ts still has the OLD titles from week 3 on - update it with 3.1.
- His Vivado: project C:\fpga\mini_tpu; must "Run as administrator" (else "Spawn failed"); blink.sv disabled (syntax
  error line 19). Stopped 13/11 at: set tb_adder4 as simulation top. Reminder set for Friday 20/11 09:00.

## Weekly core task = week sets (from 14/11/2026)
The Saturday task now checks the week sets (weekset.py) instead of hand-made cores: `fetch.sh weeksets` dumps every
course's sets with the chosen exercises; re-solve the new weeks, fix by id (publish inspect=exercises), drop wrong /
not-taught picks (inspect=weekset-drop, title=id prefixes or "all") and refill (inspect=weekset-fill). 14/11: exercises.py
"reformat" had cut Claude's verified practice solutions -> guarded (keeps length + every number; skips lessons
"written by Claude") and restored (chapters/fixes/weekly_1411.py); fixed waves TM practice + TM exam Q (E_t0=230.9),
comm exam Q1 (NF 23.0 dB), cascade, DSB SNR; dropped digital w4 depletion+body-effect exam Q (no full solution) and
comm w4 FM Q (FM not taught); Java week 4: 4 new exercises (static, pass by value, scope; outputs run).
Forecasts updated 14/11 (forecasts.py): waves TM/Brewster, digital logical effort + pull-down NOT taught, Java static,
comm DSB-SC + superheterodyne taught.

## Lesson page order + tasks (14/11/2026)
- Every lesson page: warm-up -> video (studio) -> full chapter -> condensed -> quiz -> exercises (link to week N, or the
  fold in self-study).
- prep.ts: no "📖 ללמוד את הרצאה N לפני ההרצאה הבאה" for a course with no lecture/practice slot (random signals), and
  its open ones close.
- rollTasks.resumeSelfStudy: when the first open "vlsi:" session's slot has passed, it and every later open session are
  re-dated to the coming self-study slots from tomorrow (he continues from where he stopped); vlsi: tasks no longer roll
  by whole weeks.

## Class exercises "📌 מהכיתה" (14-15/11/2026)
His words: the exams are built from the exercises solved in lectures and practices. `worker/classex.py` (publish
inspect=classex, course regex) has Gemini pull every exercise solved in a lecture/practice chapter into that lesson
(ord -100.., title "📌 מהכיתה: ..."), then weekset.run puts them first in the week. A lesson that already has one is
skipped, so a re-run only does the missing ones. **Claude checks every extracted solution** against the slides:
waves (chapters/fixes/waves_class_1411.py), digital/micro/linear/comm (chapters/fixes/class_1511.py; the digital
one had slide 6's data and V_OL 0.1 - rebuilt from slides 7-12). On 15/11 the Gemini daily quota ran out mid-run:
re-run at 10:20 added comm lecture/practice 4, Java weeks 1-2, digital lecture 2 - checked in chapters/fixes/class_1511b.py (the comm link-design last distance: board -109.24 dBm not reproducible, flagged).

Duplicates (his report 15/11/2026, waves week 2: exercise 1 = exercise 3 - the class version and the chapter version of
one board exercise): `weekset.same()/dedupe()` keep the first (class first) of exercises with the same data, the same
C/Java function, or the same text; the Gemini prompt says so too. The existing sets were cleaned with weekset-drop.

Expected exam = class exercises first (his remark 15/11/2026: "I solved ~10 exercises from the lectures / practices
and none is in the expected exam; the lecturer said they can all appear"): forecasts.py CLASS maps every exercise of the
week lists (ids in chapters/weekset_ids.json) to its forecast section, first in the list, and topics taught in class
that past exams did not show get their own section. **The Saturday update must map the new week's exercises too.**
Exercises tab "כאן אני" = the week of the last lecture/practice he marked read (lessons.read_at), not the first unsolved.

Homework tasks ("📝", external_uid hw:) are only for courses with a lecture/practice slot (16/11/2026: random signals -
a retake, assignments already graded 100% - pushed "solve homework 1-6" on a Monday): save_homework skips, the morning
push skips, syncPrepTasks closes open ones (done, not deleted). Random signals reminders = only the Thursday sessions.

His study flow (16/11/2026), one button at each step: lecture (part A -> part B) -> practice N -> exercises of week N ->
lecture N+1. Lesson page bottom: "✓ סיימתי ⬅️ <next>" marks read and goes on (the last lesson of week N goes to
/courses/<id>/exercises?w=N); the week's exercises page ends with "סיימתי את שבוע N – להרצאה N+1". In each lesson:
video -> full chapter -> condensed -> quiz; his quiz rule: under 80% he redoes it, 80%+ goes on (the result says so).

Week size (16/11/2026, "comm week 1 has 11 exercises"): class exercises + 1-4 others on topics they do not cover + up to
2 exam; applied to ALL existing weeks (weekset-clean) and to new ones (weekset.run). He insists: every rule he gives is
for all courses and for the existing weeks too, not only the course he mentioned or the future.

Predicted questions (16/11/2026, his refinement: "they will not repeat the class exercises - they change the data and add
a catch"): chapters/fixes/predict_<course>.py write "🎯 שאלה צפויה" free exercises (class example + new data + the past
exams' catch; numbers asserted, Java/C compiled and run), PRED in forecasts.py puts them first in their section and in
the PDF mock exam. 28 written (digital 4, Java 5, micro 4, linear 5, rnd 4, comm 3, waves 3). New lectures -> new ones
in the Saturday run.

Comm assignments (16/11/2026; 10% of the grade, "מגן"): he uploaded tasks 1-10 (PDFs, not in the repo). Claude solved all
(numbers asserted, MATLAB run in Octave - apt install octave), page /courses/<id>/assignments (fold per task, copy one /
copy all; link on the course page only when assignments.json exists). The solutions must not be public: they go through
the repo SEALED (worker/sealed.py: X25519 key derived from SUPABASE_SERVICE_KEY; publish inspect=sealed-pub prints the
public key O3hrUN/uOWkXjv/hKr/GtSM9XtTs5dVO/Wmn6CWXXFM=; inspect=assignments opens chapters/*.sealed.json -> storage).
Builder kept in the scratchpad only. Flagged: task 8 Q1 (3 MHz, no option fits), task 5 exam Q (η=0.1 not the marked 0.2).

Zoom recordings (16/11/2026): ariel-ac-il.zoom.us/rec/play pages are now a JS app behind a Cloudflare bot check -
yt-dlp's zoom extractor fails ("Unable to extract data"); do NOT try to get around it. He downloads from Zoom -> Google
Drive (anyone with the link) -> pastes the Drive link in the lesson's edit form (updateLesson relinks + reprocesses).
friendly_error now says so for "[zoom]" errors (before, yt-dlp's "Confirm you are on the latest version" matched the
YouTube-block text). Blocked 16/11: waves lecture 5 + practice 5, comm lecture 5 parts A+B. Even the yt-dlp nightly of 15/11 fails. process.yml now
installs the yt-dlp nightly, and queue_runner retries one Zoom-failed lesson per run once it is 24h old - they process by
themselves when yt-dlp is fixed. Meanwhile: paste Zoom's transcript on the failed lesson page (pasteTranscript), or ONE CLICK: the bookmarklet on /zoom
(lib/zoomBookmarklet.ts) scrolls Zoom's Transcript panel (virtualized list; keyed by position, tested with a fake
virtual list of 400 lines) and posts the text to /zoom (ZoomReceiver -> pasteZoomTranscript finds the lesson by the
recording id in source_url). Chrome extension extension/ (zip at web/public/studyhub-zoom.zip, install steps on /zoom): content script on
*.zoom.us/rec/* collects the transcript when he opens a recording -> background opens /zoom and injects the text ->
ZoomReceiver (accepts its own origin too). Transcript lessons get the lecturer's slides: hub.lecture_slides picks the
course PDF named "הרצאה N"/"תרגול N", else the slide deck (comm: Introduction_to_communication_systems ... .pdf;
waves has הרצאה 1-3 only), sent to Gemini as PDF docs. He may screen-record at x2 himself (his own viewing): a file / lesson title with "x2" / "2x" / "x1.5" is slowed back
to normal speed before transcription (media.slow_down: setpts + atempo, pitch kept). Downloading past Zoom's block is not done.

Quiz top-ups: hub quiz-add (publish inspect=quiz-add, kind/number, chapters/*.json list) appends questions, skips ones
already there. 17/11: random signals sessions 2-4 +9-10 each (chapters/fixes/rnd_quiz_1711.py).

Weekly review (17/11/2026, replaces the daily spaced review): /review = understanding questions only (no $ / no
calculation, lib/review.ts conceptual(), notify.CALC, hub.CALC) from the lessons with read_at in the last 7 days, max 30,
wrong/new first; home card Sat 18:00-Sun; morning push no longer has the daily review line; Saturday 20:00 evening run
sends a separate push "🔁 חזרה שבועית" (he asked ~21:00; pg_cron only reaches 20:00 - 21:00 would need notify_cron.sql
hours + notifySchedule). The Saturday trigger now runs 15:41 and first tops up each lesson read that week to >= 5
understanding questions (course-check prints quiz=N(הבנה M); comm lessons have only 1-5).

TA notebooks (17/11/2026, his request): digital "📦 2" (CMOS inverter + gate sizing) and "📦 3" (logical effort) are
NOT behind - they are ahead of the lectures (taught up to NMOS inverters in lecture 4). Each is merged into practice N of
the week its topic is taught (only what the practice lacks), then retitled "📦 (שולב בתרגול N)"; the Saturday run does
it (step 0b). He thought he had skipped notebook 2 - he has not.

Java + micro exercises = exam format (18/11/2026, his request): every week-list exercise is a multiple-choice question
(question + code + options א-ד + "✍️ choose, then write why in the notebook"); solution = "התשובה: X" + "מה לכתוב
במחברת" + "למה לא האחרות". Weeks 1-4 Java (17) and 1-3 micro (12) converted in chapters/fixes/mcq_1811.py (answers spread
over א-ד; every output run: javac / gcc, files in mcq_1811/). Published with "lock": true (hub exercises marks exp:/code:
read so exercises.py never reformats them). NEW weeks of these two courses: the Saturday run converts them the same way. The Exercises component turns this format
into clickable multiple choice (mcqOf: "**א.** " options + "התשובה: **X**"): pick -> right/wrong -> solution opens;
right on the first try marks it solved; "↺ לנסות שוב". Keep the exact format or it falls back to plain text.

EXAM FORMAT PER COURSE (his decision 19/11/2026) - the week exercises look like each course's exam:
| Course | Exam | Week exercises |
|---|---|---|
| Digital circuits | multiple choice, 4 options | MCQ + full method (chapters/fixes/mcq_digital_1911.py, weeks 1-4, 20) |
| Linear circuits | 6 MCQ; reservists 4 of 6 | MCQ + full method (mcq_linear_1911.py, weeks 1-3, 17) |
| Java | MCQ | MCQ (mcq_1811.py) |
| Micro | 6 MCQ (10 pts) + 2 open code questions (20 pts) | MCQ + ONE open code question a week (micro_open_1911.py, weeks 1-3, run in gcc) |
| Comm | OPEN: 2 questions × 5 parts, 1.5h; alternative assessment 4 parts each | open, full method per part |
| Waves | open | open |
| Random signals | open, 4 questions | open |
Even when he answers right, the solution shows "הדרך המלאה (כמו במחברת)" (formula -> substitution -> result, region
checks) + "למה לא האחרות" - he must show the work in the exam notebook. Every number is asserted in each file's check().
`hub exercises` "add" (kind/number) is now idempotent by title, honours "lock", and with "week": N also appends the
exercise to that week's list (weekset.add). Forecast format strings updated (comm open 2×5, linear 6 MCQ). Predicted
questions (predict_*.py) are still open-style; new ones follow the course format (Saturday run, step 5).
Course-file names ≠ his lecture numbers (19/11/2026, his question): linear week 1 had picks from the files "הרצאה 4 -
הדיודה.pdf" / "הרצאה 6 - הביפולרי באות קטן.pdf" (the lecturer's file numbering). Small-signal (gm=IC/VT) was taught in his
lecture 1 - kept; the diode-models question was not taught yet - dropped (weekset-drop). The label now reads "📄 מקובץ של
הקורס: <file>", and exam-style picks "⭐ בסגנון מבחן". When picking from files, check the topic against HIS lectures.

HAND-BUILT WEEKS (19/11/2026, his request "lecture, practice and the exercises that match them - not exercises from
irrelevant lectures"; linear first, then random signals):
- worker/weekset.py: a week with "manual": true is never rebuilt by run() (classex) nor trimmed by clean().
  `weekset.py set "<course>" <week> <ids>` or `set "<course>" 0 "1=a,b;2=c"` (several weeks, ONE read + write) =
  publish inspect=weekset-set (number, title). week_sets.json is uploaded with cache-control 0: with the default
  (3600) a read served the older file and a write right after lost an exercise. `hub exercises` "add"+"week" now
  writes all week additions once at the end of the run.
- Linear (chapters/fixes/mcq_linear_weeks_1911.py, WEEKS): week 1 = lecture-1 class example + practice 1 ex 1, 2, 4, 6,
  7; week 2 = the lecture-2 examples (dBm, saturation, power/efficiency, transfer characteristic, cascade - the
  lecturer's own, with fixes: gain -200 not 200, dBm working line, P_diss incl. input power, all 4 saturation cases)
  + practice 2 dB; week 3 = lecture 3 (Miller LPF, finite-A numbers, NEW weighted summer d47baffd + log amp 36d4b197)
  + the 4 practice-3 class exercises. Out: file picks (diode 7481fc52, small-signal 02e76b3d, Example 5.8 e936fb16,
  op-amp refresher 76240755) and the practice-2 variants of lecture examples (39a78ac1, b9e4e6c0 - converted to MCQ
  the same morning, now unused). Forecast CLASS remapped; diode section removed.
- Random signals: week N = session N (מפגש N): 1 estimation (3), 2 WSS (3), 3 PSD/filters (4), 4 Poisson (4),
  5 mock 1 (2), 6 his own exam again (his 4 questions, Q1..Q4). The exercises page, for a course with "מפגש" lessons,
  shows only session tabs, "שבוע N: מפגש N", here-I-am = last read session, next button -> session N+1.
  Recorded lectures 1-14 are not his weeks (their exercises stay in the lessons).
- The Saturday task builds each NEW linear week by hand the same way (prompt updated 19/11).

20/11/2026 - his long list of remarks (he hit his weekly limit and asked to do all of it):
- Display (all courses): single line breaks now show as written (remark-breaks in Chapter.tsx) - exam givens no longer
  run together; no scroll bars under inline formulas (globals.css; the bars under "τ = t2 − t1" read like minus signs).
- Exercises: "📐 הנוסחה לשאלה (בלי התשובה)" fold = the formula lines of the solution (Exercises.tsx formulaOf: lines
  with נוסחה/נוסחאות/הקשרים/הכלי up to "למה לא"). 82/194 current exercises have one; new solutions must label formulas.
- Linear weeks 1-3: every solution rewritten (chapters/fixes/linear_explained_2011.py, 18): "📘 מה צריך לדעת קודם"
  (from lectures 1-3, e.g. RMS power of a sine, the 4 amplifier models, op-amp golden rules) -> every step -> why not
  the others. Lecture 2 and 3 chapters were near-empty (2.5k / 7.9k chars) - re-authored from the recordings
  (process.yml keep_exercises=1: the chapter is rewritten, the lesson's fixed exercises stay): 24k / 23k.
- Practice recordings ("📦 תרגול בכיתה 2/3": slew rate, rectifier, 7805, Wien oscillator): NOT moved (his rule 19/11:
  a TA topic goes to the week whose lecture teaches it; if the lecturer has not reached it, to the latest week so he
  misses nothing) -> week 3 holds them for now (648f670e, be58fd65, 30b7e515, e8fdad76; still open format).
- Videos: the voice ran a slide ahead/behind (~90%): several slides are voiced in one request and were cut at a
  guessed pause. Now cut where each slide's first words are actually spoken (studio.align_cuts: Hebrew Whisper word
  times, model cached in media.yml; log "align group N: by words / by pauses (fallback)"); EXPLAINER: narration only
  about its own slide. 73 videos queued again (studio-redo, all courses; old ones stay until the new one is ready).
- Multiple choice = understanding, every course: quiz / practice / warm-up show only no-formula questions when a set
  has 5+ (lib/review.ts understandingOnly); author.SYSTEM + VLSI_TASK: no calculation questions at all.
- Random signals: her level = her 4 Ariel exams (docx in the course files: sem B moed A 12/07, moed B 29/07, summer
  moed A 08/10, his 26/10). Random phase is in none of them -> out. Week 2 = his Q1 + her two process questions
  (chapters/fixes/rnd_ariel_w2_2011.py: A cos + B sin / JWSS, i.i.d + random walk). Session 2 rewritten (words first,
  by her exams). Scheduled 24/11 10:17: session 3 + weeks 3-6 + formula sheet the same way.
- Self-study flow (lesson page, self): video -> chapter -> quiz -> "⬅️ לתרגילים: מה הקוד עושה" (MCQ code questions,
  clickable) -> "⬅️ עכשיו תרגול מעשי" (what to open/know first, the task, "🔧 הפרויקט: חלק N מתוך 24" + the exercises
  whose title starts with 🔧). VLSI_TASK writes sessions that way; 3.1 converted (4 MCQ + 3 practical + board, the
  board task framed as the Mini-TPU's display module). Each next session (3.2 ...) must be written in this flow and
  its board step named as a piece of the Mini-TPU (he wants to build the project from now, not from week 7).
- Self-study page = STAGES (his correction 20/11, components/SelfSteps.tsx): after the chapter, one stage at a time with
  ONE button at its end: 1 quiz (understanding) -> 2 "what does this code do" MCQ -> 3 practical (= today's part of the
  project, written in Vivado) -> "✅ סיימתי את המפגש" (markRead -> session done on /self). The stage he reached is kept
  in localStorage. The earlier anchor buttons jumped to a CLOSED fold, so he saw an empty screen ("לא רשום שם כלום").
- Recording upload from the device (his request 20/11, "not via Drive"): components/RecordingUpload.tsx on "add lesson"
  (lecture/practice) and in the edit form of a lesson that is not ready. Over 48 MB the browser shrinks it with
  ffmpeg.wasm (@ffmpeg/ffmpeg 0.12.15 + core 0.12.10, copied to public/ffmpeg by the postinstall script - same origin
  for the CSP; script-src has 'wasm-unsafe-eval'; proxy matcher skips /ffmpeg/): keyframes only, a frame every 2 s
  (5 s if still > 48 MB), 1280 wide, x264 stillimage crf 32, AAC 24k mono 16 kHz. Tested in Chromium under the app's
  CSP: 3 min / 72 MB -> 2.1 MB in 10 s. Goes to study/<user>/sources/<course>/<time>_<name>.mp4 (name kept: "x2"
  still slows it back); the worker's source_path path processes it like any recording. The uploaded file is NOT
  deleted after processing (his rule: no deletion without approval) - asked him.
- 20/11 later: uploads add + process by themselves when the file is up (no button; the queue also adopts any
  uploaded recording without a lesson - queue_runner.adopt_uploads). Next to the file: "watch_url" = the Zoom link,
  kept as "המקור". "🤷 לא יודע איזה תרגול" (practice, no number) -> hub.match_lecture gives it the number of the
  lecture whose topics/headings share the most words (none -> next lecture number). File-name titles
  (hub.looks_like_file) are replaced by the chapter title. publish inspect=retitle (course, kind, number, title).
- Gemini: 3 free keys now (he added them 20/11; author._keys reads GEMINI_API_KEY with keys split by , / space / new
  line + secrets GEMINI_API_KEY_2.._4). Lessons before videos; video remakes paused until 21/11 09:00 UTC; a publish
  builds only the MISSING week list. ping (publish inspect=ping) showed 3 keys answering.
- Digital: his upload = lecture 5 (Claude wrote it: chapters/fixes/digital_l5.py). TA notebooks "📦 2" (CMOS +
  sizing) and "📦 3" (logical effort) became practice 5 part A / part B (reorder with "part": true) - his rule: no
  separate "חומר N", a TA topic goes to the practice of the lecture that teaches it (or the latest one).
- Saturday run 21/11: weekly review +57 understanding questions in 16 read lessons (chapters/fixes/review_q_2111.py;
  quiz-add now takes [{lesson_id, questions}] - lectures in parts share kind+number). Linear week 2: the lecture-2
  examples deleted by the 19/11 re-author (b27aa2be, 9f29e3c8) came back as 38a70d7f, 4162a96b (week_fix_2111.py).
  Digital week 5: V_OL TA question -> MCQ; d15cf3ba (dynamic CMOS, 9-NMOS stack) dropped - not taught, official
  solution arithmetic wrong (the 3 only comes with the /9 of the stack). His damaged upload (only 19 min readable:
  media.transcribe_local now decodes what it can; save_slides skips damaged snapshots) was the TA practice -> practice
  5 part C; week 6 dropped. Practice 5 also holds NAND/NOR sizing + logical effort (not taught yet - left out of the
  week lists). Comm week 5 = 63280649 (DSB-SC, rewritten 5 parts) + SSB + spectrum (manual). Video sync verified:
  "align group N: by words" in every group. fetch.sh/keys had to be rebuilt (scratchpad cleared with the container).
- ONE lesson per practice N (his screenshot 21/11: "practice 5 three times"): reorder op {"merge": [ids], "into": id,
  "title"} appends chapters + summaries, moves exercises and questions, and hides the parts ("📦 (שולב ב...)" titles are
  filtered out of the course list). save_chapter merges a newly published practice N into an existing practice N by
  itself. Digital practice 5 = parts A+B+C merged (c688ca4a).
- Next.js 16.4.2: the build prints a security-upgrade notice (`next upgrade`); not done - ask him.

Code in quiz questions (18/11/2026, his screenshot: a Java switch written on one line, he got many wrong): codefmt.fix
moves one-line code into a ```java / ```c block, one statement per line, case bodies indented, array initializers kept;
applied to all existing questions (publish inspect=quiz-code, title=apply; Java 8, micro 5 - other courses 0) and to
every new quiz when it is saved (hub, questions insert).

- 21/11 evening: Gemini out of quota + overloaded again (waves lecture 5, 3 h, failed after 55 min). Claude wrote
  waves lecture 5 (chapters/fixes/waves_l5.py: evanescent wave, RLGC, telegrapher, Gamma, SWR, Z_in, stubs, quarter-wave;
  open-exam exercises) and Java lecture 5 (chapters/fixes/java_l5.py: casting, ==, getClass/instanceof, static, J8;
  MCQ outputs verified with javac). Publish input `chapter` must be `chapters/<file>.json`. Dropped the Gemini
  "-latest" aliases from WORK_MODELS (they answer 404). Still waiting: 4 practices (linear x2, digital, Java) being
  transcribed by the queue; Gemini retries them after the 10:30 reset, or Claude writes them.

- 22/11 board-text check (his screenshot: "what is written as the board is not what is on the board"): Claude compared all
  323 "📝 מה כתוב בלוח" blocks with their snapshots (fetch.yml `boards` -> boards.py dump; fixes via publish
  inspect=boardfix, chapters/boardfix-2211.json; the chapter before is kept as chapter_before_boardfix.md). 169 changed:
  blocks describing another snapshot (off-by-one in Java L1, merged parts), lines not on the board (Gemini filled in from
  the transcript), broken $/tables/Arabic letters; dense random-signals whiteboards relabelled "📝 עיקרי הלוח (בתמצית)".
  ROOT BUG fixed: merging parts (cmd_reorder merge / auto-merge of practice N) kept the part's slide:N references while the
  joined lesson's snapshots are different -> carry_slides copies them (N -> count+N); merge-repair fixed digital P5, Java
  P2, linear P2. 18 blocks of micro "web" lessons + VLSI have no snapshot file at all (not checked). author.SLIDES_RULE:
  the block describes ONLY the snapshot after it.
- Open: Java f6e454ca "lecture 6" (created 18:08 21/11) is the TA's תרגול 5 again (same code as practice 6 86de22c3) -
  looks like a duplicate of his upload; digital practice 6 (CMOS VTC) belongs to lecture 5's week. Ask before removing.

- 22/11 coverage check (his question "are the chapters too short / 90 snapshots but 4 shown?"): outline now has
  transcript_chars + transcript_snapshots. Gemini chapters are 3-11% of the transcript (e.g. digital L1/L4 5%, Java L4 4%,
  waves L2-L4 6-8%, micro L2/L3 3-4%), Claude-written ones 16-24% (linear L1-3, waves L1/L5, Java L5). Snapshots are taken
  every ~1 min (many repeats of the same board), but 3-4 images for a 3 h lecture is too few. Plan proposed to him: Claude
  rewrites the thin chapters in full (every topic in order, every distinct board), weeks he already studied first.
  7 chapters are cut mid-sentence (micro L3 + site weeks 2/4/7/9, lab 1) - waiting for his choice.

## NEXT TASK (approved 22/11/2026) - do it in a NEW session, cheaply; he must stay under 52% of his weekly Claude limit until Friday
Goal: Claude only builds; ALL chapter writing by Gemini (free keys). No Claude-written chapters, no image montages.
0. FIRST (approved 22/11): FREEZE new features; trim to the core. KEEP videos (they help him a lot). REMOVE podcasts/audio.
   Stop: weekly-list rebuilds that replace exercises, chapter/exercise reformat passes. Per-lesson self-check (coverage vs
   transcript, not cut, board blocks) with automatic retry; notify him only when he must act. Gemini work is spread over
   days by his timetable and deadlines (never everything in one day). "Stable" = one full week (to Fri 28/11) with no
   intervention from him. He stays in THIS chat (no new sessions): keep instructions here in HANDOFF, read it, don't
   reload big transcripts/images.
1. author.py prompt: full coverage (every topic in order, definitions/derivations/examples/exam hints, no shortening);
   write long lectures in ~40-min transcript parts and join; pick DISTINCT snapshots automatically (image diff, see
   scratchpad distinct.py idea: grayscale 160x90 mean diff > 6) and use all of them; board block = only that snapshot;
   re-ask if chapter < ~15% of transcript or is_cut().
2. queue job "completions", priority by his timetable (next study day first), new uploads must be ready by Friday:
   - unread lesson with thin chapter (<15% of transcript, list in outline transcript_chars) -> rewrite fully (backup old,
     keep exercise done marks);
   - read lesson -> Gemini writes ONLY what is missing vs transcript (+questions/exercises) -> section
     "🔁 השלמות מהשבועות הקודמים" at the top of the NEXT UNREAD lesson of that course.
   - cut chapters (micro L3 + site wk 2/4/7/9, lab 1, VLSI L10) rewritten.
   CHANGED 22/11 evening (his request: "כל השלמה משלה עם שאלון אמריקאי משלה ותרגילים משלה, לא הכל ביחד"):
   every completion is now its OWN lesson (kind other, title "🔁 השלמה להרצאה N[ – חלק א/ב]", number = target-1, so the
   site lists it right before the target; parts cut at ## headings over ~9000 chars). coverage.step() first runs
   explode_all() (old top-of-chapter blocks -> separate lessons, backup chapter_before_split.md; old block questions stay
   on the target), then drill(): 5-6 questions + 2-3 exercises per completion lesson, from a hand-written
   chapters/drills/*.json (course+title match) or else Gemini (exercises marked uncertain). State: coverage.json "drill".
   Comm completion 1 drill written by Claude; the rest by Gemini. Comm 4A: dB+dBm correction (⚠️) added.
   23/11 his working rhythm: he uploads each day's recordings that evening; the system prepares TOMORROW's course(s)
   (schedule_slots) first and pushes "✅ מוכן למחר: <course>" once everything is ready (lessons processed, completions,
   quizzes/exercises, videos of completion lessons + lectures of the last 8 days), or at 21:00 "⚠️ עוד לא הכל מוכן"
   with what is missing (coverage.ready_alert, called at the end of every queue run). Completion lessons get the boards
   of their source lesson copied (fix_slides) and a video each (queue_video -> retry_studio, tomorrow's course first).
   v2 23/11: THIN 15% -> 30% (full chapters measure 40-60% of the transcript); the halves of a lecture ("חלק א/ב")
   shared one completion title, so one half's completion was dropped (comm lecture 3). Every thin lesson is checked
   once more (state "v2"); a read one gets only what is missing vs its chapter AND the existing completion lessons of
   that lecture; new completion titles carry the half ("🔁 השלמה להרצאה 3 חלק א").
   RULE 23/11 "אל תחסיר ממני שום פרט" (all courses, lectures, practices, exercises): author.summary_mode() now always
   False (it was summary+exercises for every course but Java - the root cause of the 10-18% chapters);
   hub.complete_chapter() = full_from_start() + coverage.audit() (each 40-min part vs the chapter, missing details
   appended under "## 🧩 פרטים שהבדיקה מול ההקלטה הוסיפה", backup chapter_before_audit.md) before "ready"; the coverage
   queue also audits every unread lesson once (state "audited"). RULES in coverage.py forbid skipping anything.
   23/11 media project (study-media) went over its 5 GB monthly download (grace to 23/12/2026): videos now encoded with
   mediastore.SMALL (960x540, 5 fps, crf 29, 40k audio); `publish inspect=media-clean number=N` removes files no
   lesson_media row points at (approved) and re-encodes the N biggest ready videos; the queue cleans daily at 03:00.
   Lesson page: no condensed summary, no quiz on practices. Video right after each lesson's text (video_now).
   23/11 noon: he sets the course order - coverage state "focus" (publish inspect=coverage-focus title=<name part>,
   empty = all) limits text, quizzes and videos to one course until he approves the next. Order: comm (done) ->
   digital -> Java -> micro -> linear -> random signals. Waiting comm videos dropped (inspect=drop-videos) at his request.
   Quizzes: wrap_math() wraps LaTeX Gemini wrote without $.
   23/11: completions are trimmed (inspect=coverage-trim title=<course>) - Gemini removes from each "🔁 השלמה" what is
   already in the lessons he marked read and the exercises he marked done; backup chapter_before_trim.md. Comm first.
   FIXED RULES for completions (his words 23/11: "זה דברים שהם קבועים"): ONE completion per week (lecture N +
   practice N -> "🔁 השלמה להרצאה N"); trimmed to what he has not read/solved, retried until a trim passes the guards;
   quiz/exercises only about what the completion holds, never repeating an exercise he marked done (drill_parts sends
   the solved ones); questions not about it removed even if answered (prune_questions). `inspect=coverage-fix
   title=<course>` does all of it (fix_course). Videos only for the focused course.
   Moodle: removed completely 23/11 (settings sync, ics parser, saved link erased) - it caused him problems; never
   connect to the university Moodle again.
   Lab 2 ("מעבדה"): nothing automatic - no completions, quizzes, videos or push (his request 23/11; SKIP_COURSES).
   Repairs waiting for Gemini go to coverage state "pending" (inspect=coverage-pending title=<json>, "first": true
   puts the next study course ahead); the queue loop keeps running until they are done (repairs_left) and the
   "ready for tomorrow" push waits for them. 23/11 night: digital (fix + weeks 4-6) then comm (L5A rewrite + weeks 4-5).
   HIS ORDER BY DAYS (23/11 night): coverage.PLAN = digital -> Java -> micro -> linear -> random signals -> VLSI self
   study -> waves -> comm, starting Tue 24/11. One course in focus (text, repairs, quizzes, videos); at 20:00 Israel
   the next one even if not done, and at once if nothing is missing (plan_focus, state "plan"). Its pending repairs run
   before anything else in the queue (pending_for_next_day).
   Progress pushes: after each repair job on the focus course (progress_push) and when the plan moves on (✅ ready /
   ⏭️ time's up with what is left).
   BOARD CHECK (24/11, his rule): coverage.board_check() sends every "📝 מה כתוב בלוח" block with its snapshot to Gemini
   and rewrites it to match (a projected slide's own text too, nothing unseen); runs after every new chapter
   (hub.complete_chapter) and once for every existing lesson via pending {"course", "boards": true} (state
   "boards_checked"); inspect=board-check title=<course> runs it by hand. Completions drop course goals/syllabus.
   24/11 reliability: notify.yml (pg_cron 08:00/20:00, reliable) also starts queue.yml; the queue loop starts the next
   run itself while repairs are left; coverage.save(keys=[...]) lets lesson processing update only its keys, so the
   queue's "pending" list is never overwritten. Claude must NOT run publish jobs while the queue runs (state race).
   24/11 WEEK SCHEDULE (coverage.SCHEDULE replaces the 20:00 rotation): each course until its deadline or until done:
   digital Tue 20:00, Java Wed 14:00, micro Wed 23:00, linear Thu 14:00, random Thu 23:00, waves Sat 20:00 (studied
   Sun), comm Sun 20:00 (studied Mon); from Tue 01/12 only new lectures. GitHub Models backup (author._github_models,
   gpt-4.1 / 4.1-mini with the workflow GITHUB_TOKEN, permissions models: read) answers text-only tasks when Gemini is
   busy or out of quota; inspect=ghm-test checks it.
   24/11 audit is IN PLACE (his rule): coverage.audit() asks Gemini (PLACE) which topic each missing piece belongs to
   and integrate() puts it at the end of that topic - no "🧩" section any more; inspect=coverage-place title=<course>
   moves old "🧩" sections into their topics (backup chapter_before_place.md).
   24/11 BUG "lecture 7 he never uploaded": adopt_uploads turned a recording file whose lesson he had deleted (the TA
   video uploaded twice on 21/11) into a new lecture again. Now a file is adopted once ever (queue state "adopted")
   and never when a file of the same size is already a lesson.
   24/11 GitHub Models is NOT reachable from the runners: models.github.ai answers a bare "HTTP/2 200 text/plain OK"
   (worker/ghm_probe.py, inspect=ghm-probe) - something in between, not GitHub. The fallback stays in the code and
   simply returns None. Pending jobs now also "place" (old 🧩 sections into their topics) and "verify" (multiple-choice
   answers re-solved; a disagreement gets "⚠️ הפתרון לא אומת"). Zoom link first, uploaded file as fallback.
   24/11 DEFAULTS for every lesson (his rule: every fix he asked for is the default): one quiz per lecture (rewrite /
   audit steps add no questions); a math-fix job (site renderer web/site-check.mjs + Gemini, kept only if it renders
   better; node + npm ci in queue/publish) is queued for the course after each new chapter; exercises with options
   but no stated answer get "התשובה: **X**" from a re-solve (verify) so they are clickable; inline "אפשרויות: א. ..."
   and up to six options (א-ו) are clickable. Focus = every SCHEDULE course due the same day (digital+Java+micro today).
   24/11 15:30 his call: the rest of digital waits until Sunday night (ready Mon 30/11 morning); today Java + micro.
   His final week order (24/11): Tue Java+micro, Wed linear+random, Thu VLSI self-study, Fri-Sat waves, Sun comm,
   Mon digital (coverage.SCHEDULE, deadline 23:59 of each day).
   24/11 exercises in every course follow the exam (pending "convert": lesson exercises not done yet are rewritten
   as clickable multiple choice when exam_type=mcq, open otherwise, each solution with a "**הנוסחה:**" block for the
   📐 hint). Duplicates removed with his approval: Java fake lecture 6 + 35 copies of micro site weeks (import-site
   made a new lesson whenever the lecturer's page anchor moved - fixed: same page + week = same lesson).
   24/11 FREE TEXT BACKUP: GROQ_API_KEY + MISTRAL_API_KEY (GitHub secrets, in every workflow). author._backup_json:
   gpt-oss-120b / qwen3.8-27b on Groq (work, tested Hebrew + LaTeX), Mistral medium/small (free tier rate-limited).
   Text-only Gemini calls fall back to them on busy/quota; the queue keeps running when Gemini's quota is out
   (has_backups); pending steps that need Gemini (boards, rewrite) are skipped until its reset (_skip).
   24/11 evening: each Gemini model has its own free daily quota - WORK_MODELS now also tries gemini-3.7/3.6/3.5-flash,
   3.1-flash-lite and gemma-4-31b-it / gemma-4-26b-a4b-it (Gemma: no system instruction / JSON mode, all in the
   message, JSON taken from the reply). Probe: inspect=ghm-test (worker/backup_test.py).
   Completions are a ONE-TIME catch-up (this week). New chapters must be full from the start: save_chapter ->
   full_from_start() rewrites a thin chapter part by part (coverage.write) before it is marked ready.
   He is at ~80% of his weekly Claude limit (23/11): Claude only checks quizzes of the course he studies next, on request.
   Waves first: practice 4 (b22231ed) done by him except exercises; completions of L2-L4 + P3 go before lecture 5 (7d82bca1).
3. Thursday check -> push notification for anything due Friday not ready.
4. Delete duplicate Java "lecture 6" f6e454ca (= practice 6 86de22c3) - he approved.
GitHub Actions: repo is public = unlimited; his "2,000 minutes used" mail is about private repos, harmless.
Gemini: 3 keys only help if in SEPARATE Google projects (asked him). His Gemini "Plus" student plan gives no API quota.

## Open items
- Syllabus reading: fixed a 400 from Gemini with a plain-JSON fallback (2026-10-22); not yet confirmed with his key.
- Bug found 2026-10-22: `hub.py` passed `docs=` to `author_with_gemini`, which had lost that parameter in a merge, so
  every Gemini chapter failed after transcription (the 3 failed lessons). Fixed; he must press "לנסות שוב" on them.
- Course page "הרצאות + תרגולים" counts meetings held per the timetable (or uploaded lessons if more), per kind.
- Gemini authoring + verification pipeline has never run against the real API from this environment (no key here).

## Working with this repo
- Use **one** Claude session at a time on this repo; two parallel sessions duplicated edits once.
- A new feature: build → `npx eslint src && npx next build` in `web/` → commit → push → tell him what changed
  and what (if any) SQL to run, in Hebrew, without jargon.
- Start a new Claude Code session per bigger task (e.g. each semester) so the conversation context stays small;
  this file and `CLAUDE.md` carry the knowledge between sessions.

25/11/2026: the queue sat idle 21:27-02:52 ("0 done" every 12 min): the focus course still "missed" something no repair
job does (videos waiting for Gemini) while the other courses' jobs were not "mine". Now pending_for_next_day runs the
focus jobs first and then the rest by SCHEDULE deadline. Read-only status: publish inspect=coverage-status (what is
missing per course + the repair jobs left).
Also 25/11: missing_for() counted completions with an empty state (no v2 / audited), so every finished course showed
"N השלמות בכתיבה" for ever - the focus never moved on and no "✅ מוכן" push could come. Now it uses the real state.

## 25/11/2026 morning - HIS DECISION: everything finished today, no completions ever again
- Every course is finished on Wed 25/11 (coverage.SCHEDULE: all 8 courses due 25/11 23:59 -> one focus = all courses).
- Completions were a one-time catch-up. coverage.COMPLETIONS_UNTIL = 26/11 00:00: after it todo() makes no new
  completion; a new upload gets only the normal flow (transcript, full chapter, self-check vs recording, boards,
  video, quiz for lectures, exercises in the exam format). The existing course is only checked (audits, math, boards).
- From Fri 27/11 he uploads every new lecture / practice of all courses (waves etc.) and does not deal with the system.
