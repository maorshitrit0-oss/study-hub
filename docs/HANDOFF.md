# Handoff: everything a new Claude session needs

Read this first in every new session. Keep it up to date: when something is decided, built or changed,
add it here in the same commit. The conversation that built the app will not be available.

## The user
- Maor Shitrit, 3rd-year electrical engineering student, Ariel University. Writes Hebrew; always answer in Hebrew.
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
- אותות אקראיים ורעש – exam מועד ג 22/12/2026.
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
- Formula sheets build themselves (`worker/docs.py`, daily + after exercises.yml) for courses whose facts/notes mention
  "דף נוסחאות"; rebuilt when lessons are newer than the sheet. The app page still has "🔄 לעדכן".
- Home: reminders are about submissions/exams/entry quizzes, not reading; the deadlines card hides automatic
  prep/ex/site-week/upload tasks; "🎯 היום מעבדה" card on lab days; "חזרה יומית" explains itself (spaced repetition of
  quiz questions he answered: 1/3/7/14/30/60 days, wrong -> tomorrow). He hardly uses the course chat (only admin info).
- Timetable: `WeekGrid` - days across (Sunday on the right), hours down, short course names - for the phone; the full
  list + editing is folded below.
- Later (end of semester): exam variations per course as files, from past exams and each lecturer's style.

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
