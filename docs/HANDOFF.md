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
- Exams: waves 12/1 & 10/2/2027, Java 17/1 & 25/2, linear 19/1 & 14/2, digital 25/1 & 18/2 (times unknown, 09:00 placeholders).
- Still unknown: מבוא לבקרה exam date (semester ב; deferred until semester ב).

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

## Open items
- Syllabus reading: fixed a 400 from Gemini with a plain-JSON fallback (2026-10-22); not yet confirmed with his key.
- The first Java lecture (processed on GitHub Actions) – not yet confirmed whether Gemini wrote the chapter.
- Gemini authoring + verification pipeline has never run against the real API from this environment (no key here).

## Working with this repo
- Use **one** Claude session at a time on this repo; two parallel sessions duplicated edits once.
- A new feature: build → `npx eslint src && npx next build` in `web/` → commit → push → tell him what changed
  and what (if any) SQL to run, in Hebrew, without jargon.
- Start a new Claude Code session per bigger task (e.g. each semester) so the conversation context stays small;
  this file and `CLAUDE.md` carry the knowledge between sessions.
