import Link from "next/link";
import { requireUser } from "@/lib/supabase/server";
import { dueReviews } from "@/lib/review";
import { attachOrphanTasks, syncPrepTasks } from "@/lib/prep";
import { syncExerciseTasks } from "@/lib/exercises";
import { syncLabTasks } from "@/lib/labTasks";
import { catchUps, ensureSelfSlots, mainTrack } from "@/lib/selfPlan";
import { isSiteLesson, studyWeek, syncWeekTasks, todayWeek } from "@/lib/week";
import DeadlineRow from "@/components/DeadlineRow";
import Fold from "@/components/Fold";
import { isWeak, pct, topicStats } from "@/lib/progress";
import { isoFromNow, isoToIsraelLocal, israelNow } from "@/lib/format";
import SlotCard from "@/components/SlotCard";
import MissingRecordings from "@/components/MissingRecordings";
import { missingRecordings } from "@/lib/recordings";
import { LEVEL_LABEL, LEVEL_TONE, weeklyPlan } from "@/lib/plan";
import { UsageAlerts, type Snapshot } from "@/components/Usage";
import { DAYS, lessonName, type Course, type Deadline, type Lesson, type Slot } from "@/lib/types";

export default async function Home() {
  const { sb } = await requireUser();
  await Promise.all([syncPrepTasks(sb).catch(() => {}), attachOrphanTasks(sb).catch(() => {}), syncWeekTasks(sb).catch(() => {}), syncExerciseTasks(sb).catch(() => {}), syncLabTasks(sb).catch(() => {})]);
  const in14 = isoFromNow(14);
  const now = israelNow();
  const [{ data: courses }, { data: deadlines }, stats, { data: today }, missing] = await Promise.all([
    sb.from("courses").select("*").eq("archived", false).order("year").order("name"),
    sb.from("deadlines").select("*").eq("done", false).lte("due_at", in14).order("due_at").limit(40),
    topicStats(sb),
    sb.from("schedule_slots").select("*").eq("weekday", now.weekday).order("start_time"),
    missingRecordings(sb).catch(() => []),
  ]);
  const [plan, { data: usage }, review] = await Promise.all([
    weeklyPlan(sb),
    sb.from("usage_snapshot").select("data").eq("id", 1).maybeSingle(),
    dueReviews(sb).catch(() => ({ total: 0 })),
  ]);
  // Home lists submissions, exams and quizzes; the automatic reading / exercise / upload tasks live in their own places
  // (the week page, the exercises page, "להעלות").
  const AUTO = /^(prep|ex|site-week|upload|vlsi):/; // lab reports / entry-quiz notes (labrep, labq) do show
  const dueSoon = ((deadlines ?? []) as (Deadline & { external_uid?: string | null })[])
    .filter((d) => !AUTO.test(d.external_uid ?? "")).slice(0, 8);
  // Friday / Saturday night: today's self-study topic - or the catch-ups that come first.
  const track = await mainTrack(sb).catch(() => null);
  if (track) await ensureSelfSlots(sb, track.id).catch(() => {});
  // The VLSI session due next (the first one not done), on Friday / Saturday night.
  const selfToday = track && (now.weekday === 5 || now.weekday === 6)
    ? await Promise.all([
      sb.from("deadlines").select("title, due_at").like("external_uid", "vlsi:%").eq("done", false).order("due_at").limit(1),
      catchUps(sb),
    ]).then(([{ data }, c]) => ({
      session: data?.[0] ? { title: (data[0].title as string).replace(/^🎓 VLSI /, "") } : null, pending: c,
      // Today's session already done (he marked it): the next open one is due another day.
      doneToday: !data?.[0] || isoToIsraelLocal(data[0].due_at as string).slice(0, 10) !== isoToIsraelLocal(new Date().toISOString()).slice(0, 10),
    }))
    : null;
  const usageAlerts = (usage?.data as Snapshot | undefined)?.alerts ?? [];
  const focus = plan.filter((p) => p.score > 0).slice(0, 3);
  const reminders = plan.flatMap((p) => p.reminders).slice(0, 6);
  const todaySlots = ((today ?? []) as Slot[]).filter((s) => s.end_time.slice(0, 5) > now.time);
  const courseName = new Map((courses as Course[] | null)?.map((c) => [c.id, c.name]));
  // The line: being written now, then waiting (oldest first), then failures that are retried by themselves.
  const { data: pendingRows } = await sb.from("lessons").select("id, course_id, kind, number, title, status, progress, error, updated_at")
    .in("status", ["processing", "queued", "error"]).order("updated_at").limit(80);
  const pendingList = ((pendingRows ?? []) as (Lesson & { error: string | null; updated_at: string })[]);
  const retried = (l: { error: string | null }) => /מכסה|עמוסים/.test(l.error ?? "");
  const line = [
    ...pendingList.filter((l) => l.status === "processing").map((l) => ({ l, where: "now", why: l.progress ?? "מעבד" })),
    ...pendingList.filter((l) => l.status === "queued").map((l) => ({ l, where: "line", why: "ממתין בתור" })),
    ...pendingList.filter((l) => l.status === "error" && retried(l))
      .map((l) => ({ l, where: "retry", why: /מכסה/.test(l.error ?? "") ? "ינסה שוב אחרי 10:30 (מכסה)" : "ינסה שוב (Gemini עמוס)" })),
  ];
  const now_ = line.filter((x) => x.where === "now");
  const waitingLine = line.filter((x) => x.where !== "now");
  // Last year's material from a lecturer's site is reference only, not "waiting to be read".
  // "מחכה לקריאה" = this study week only (he is one week behind; 05/11/2026): the course's lecture / practice N of
  // study week N, not read yet. Earlier weeks he left undone are counted apart - he settles them on Saturday night.
  const sw = studyWeek();
  const selfIds = new Set((courses as Course[] | null)?.filter((c) => c.kind === "self").map((c) => c.id));
  const { data: weekRows } = await sb.from("lessons").select("id, course_id, kind, number, title, status, read_at, source_url")
    .in("kind", ["lecture", "practice"]).eq("status", "ready").is("read_at", null).lte("number", sw);
  const mine = ((weekRows ?? []) as Lesson[]).filter((l) => courseName.has(l.course_id) && !selfIds.has(l.course_id) && !isSiteLesson(l));
  const unread = mine.filter((l) => l.number === sw);
  const behind = mine.filter((l) => (l.number ?? 0) < sw);
  const weak = stats.filter(isWeak).sort((a, b) => (pct(a) ?? 0) - (pct(b) ?? 0)).slice(0, 5);

  return (
    <div className="space-y-5">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">מה לומדים היום?</h1>
        <Link href="/settings" aria-label="הגדרות" className="text-muted p-2 -m-2">
          <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" />
          </svg>
        </Link>
      </div>

      {todaySlots.length > 0 && (
        <section className="card">
          <div className="flex justify-between items-center mb-2">
            <h2 className="font-semibold">היום באוניברסיטה · יום {DAYS[now.weekday]}</h2>
            <Link href="/schedule" className="text-sm text-accent">המערכת</Link>
          </div>
          <div className="space-y-2">
            {todaySlots.map((s) => {
              // Reminders before each lecture (05/11/2026: "rather before each lecture than a shopping list").
              const before = plan.find((p) => p.course.id === s.course_id)?.reminders ?? [];
              return (
                <div key={s.id}>
                  <SlotCard s={s} courseName={s.course_id ? courseName.get(s.course_id) : undefined}
                    done={!!selfToday?.doneToday && s.course_id === track?.id}
                    now={s.start_time.slice(0, 5) <= now.time} />
                  {s.course_id && (s.kind === "lecture" || s.kind === "practice") && (
                    <Link href={`/courses/${s.course_id}/warmup`} className="text-xs text-accent block mt-1 ps-2">🔥 חימום לפני השיעור – כמה שאלות על השיעורים האחרונים</Link>
                  )}
                  {before.length > 0 && (
                    <ul className="text-xs space-y-1 mt-1 ps-2">
                      {before.slice(0, 3).map((r) => <li key={r.text}><Link href={r.href}>📌 {r.text}</Link></li>)}
                    </ul>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}

      {selfToday?.session && track && (
        <Link href={selfToday.pending.length ? "/week" : "/self"} className="card block">
          <span className="font-semibold">🎓 היום לימוד VLSI</span>
          <span className="block text-sm text-muted mt-1">
            {selfToday.pending.length ? `קודם השלמות (${selfToday.pending.length}) ←` : `${selfToday.session.title} ←`}
          </span>
        </Link>
      )}

      {/* Lab later today: practise the entry quiz. */}
      {todaySlots.filter((s) => s.kind === "lab").map((s) => (
        <Link key={s.id} href={`/courses/${s.course_id}/entry`} className="card flex justify-between items-center">
          <span className="font-semibold">🎯 היום מעבדה - בוחן כניסה</span>
          <span className="text-sm text-accent">לתרגל ←</span>
        </Link>
      ))}

      {review.total > 0 && (
        <Link href="/review" className="card block">
          <span className="flex justify-between items-center">
            <span className="font-semibold">🔁 חזרה יומית</span>
            <span className="text-sm text-accent">{review.total} שאלות מחכות ←</span>
          </span>
          <span className="block text-xs text-muted mt-1">
            שאלות מהשאלונים שכבר ענית עליהם, שחוזרות במרווחים הולכים וגדלים (אחרי 1, 3, 7, 14, 30 ו-60 יום) כדי שלא תשכח;
            שאלה שטעית בה חוזרת למחרת.
          </span>
        </Link>
      )}

      <Link href="/week" className="card flex justify-between items-center">
        <span className="font-semibold">📅 השבוע שלי · שבוע לימוד {studyWeek()}</span>
        <span className="text-sm text-muted">בסמסטר: שבוע {todayWeek()} ←</span>
      </Link>

      <MissingRecordings items={missing} courseName={courseName} />

      {usageAlerts.length > 0 && (
        <section className="card">
          <h2 className="font-semibold mb-2">⚠️ צריך לטפל</h2>
          <UsageAlerts snap={usage!.data as Snapshot} />
        </section>
      )}

      {focus.length > 0 && (
        <Fold id="home-focus" title="על מה להשקיע השבוע" hint={`${focus.length}`}>
          <ul className="space-y-3">
            {focus.map((p) => (
              <li key={p.course.id}>
                <Link href={`/courses/${p.course.id}`} className="block">
                  <div className="flex justify-between items-center gap-2">
                    <span className="font-medium">{p.course.name}</span>
                    <span className={`text-xs rounded-full px-2 py-0.5 shrink-0 ${LEVEL_TONE[p.level]}`}>{LEVEL_LABEL[p.level]}</span>
                  </div>
                  <div className="text-xs text-muted mt-0.5">{p.reasons.join(" · ")}</div>
                </Link>
              </li>
            ))}
          </ul>
        </Fold>
      )}

      {reminders.length > 0 && (
        <Fold id="home-reminders" title="📌 כל התזכורות" hint={`${reminders.length}`}>
          <ul className="space-y-2 text-sm">
            {reminders.map((r) => (
              <li key={r.text}><Link href={r.href} className="flex gap-2"><span>📌</span><span>{r.text}</span></Link></li>
            ))}
          </ul>
        </Fold>
      )}

      {/* Being written now, and the line - separate (05/11/2026); each opens by itself only with 5 or fewer. */}
      {/* Always shown (05/11/2026): also when nothing is being written right now, with why. */}
      {(now_.length > 0 || waitingLine.length > 0) && (
        <Fold id="home-now" defaultOpen={now_.length <= 5} title="⚙️ בעיבוד עכשיו" hint={`${now_.length}`}>
          {now_.length === 0 && (
            <p className="text-sm text-muted">
              כרגע אף שיעור לא נכתב. {waitingLine.some((x) => x.where === "retry")
                ? "השיעורים בתור מחכים ל-Gemini (עמוס או שנגמרה המכסה) - התור מנסה שוב לבד כל 10 דקות, ואחרי 10:30 כשהמכסה מתאפסת."
                : "השיעור הבא בתור יתחיל תוך דקות."}
            </p>
          )}
          <ul className="space-y-2 text-sm">
            {now_.map((x) => (
              <li key={x.l.id}>
                <Link href={`/lessons/${x.l.id}`} className="flex justify-between gap-2">
                  <span className="min-w-0">▶️ {courseName.get(x.l.course_id) ?? ""} · {lessonName(x.l)}{x.l.title && x.l.kind !== "web" ? ` · ${x.l.title}` : ""}</span>
                  <span className="text-xs text-muted shrink-0">{x.why}</span>
                </Link>
              </li>
            ))}
          </ul>
        </Fold>
      )}
      {waitingLine.length > 0 && (
        <Fold id="home-line" defaultOpen={waitingLine.length <= 5} title="⏳ בתור" hint={`${waitingLine.length}`}>
          <p className="text-xs text-muted mb-2">נכתבים לפי הסדר, אחד-אחד. כש-Gemini עמוס - מחכים 10 דקות ומנסים שוב; כשהמכסה נגמרה - ממשיכים אחרי 10:30.</p>
          <ol className="space-y-2 text-sm">
            {waitingLine.map((x, i) => (
              <li key={x.l.id}>
                <Link href={`/lessons/${x.l.id}`} className="flex justify-between gap-2">
                  <span className="min-w-0">{i + 1}. {courseName.get(x.l.course_id) ?? ""} · {lessonName(x.l)}{x.l.title && x.l.kind !== "web" ? ` · ${x.l.title}` : ""}</span>
                  <span className="text-xs text-muted shrink-0">{x.why}</span>
                </Link>
              </li>
            ))}
          </ol>
        </Fold>
      )}

      {(unread.length > 0 || behind.length > 0) && (
        <Fold id="home-unread" title={`מחכה לקריאה · שבוע לימוד ${sw}`} hint={`${unread.length}`}>
          {unread.length === 0 && <p className="text-sm text-muted py-1">✅ קראת את כל מה ששייך לשבוע הזה.</p>}
          {behind.length > 0 && (
            <Link href="/week" className="block text-xs text-warn mb-2">
              ⏪ {behind.length} משבועות קודמים לא נקראו - לסיכום של מוצ״ש ←
            </Link>
          )}
          <ul className="divide-y divide-line">
            {unread.map((l) => (
              <li key={l.id}>
                <Link href={`/lessons/${l.id}`} className="flex justify-between py-2.5">
                  <span>{lessonName(l)}</span>
                  <span className="text-sm text-muted">{courseName.get(l.course_id)}</span>
                </Link>
              </li>
            ))}
          </ul>
        </Fold>
      )}

      <Fold id="home-deadlines" title="דדליינים קרובים" hint={`${dueSoon.length}`}>
        <div className="flex justify-end mb-1"><Link href="/deadlines" className="text-sm text-accent">הכל</Link></div>
        {dueSoon.length ? (
          <ul className="divide-y divide-line">
            {dueSoon.map((d) => (
              <DeadlineRow key={d.id} d={d} courseName={d.course_id ? courseName.get(d.course_id) : undefined} />
            ))}
          </ul>
        ) : (
          <p className="text-muted text-sm py-2">אין משימות בשבועיים הקרובים.</p>
        )}
      </Fold>

      {weak.length > 0 && (
        <Fold id="home-weak" title="נושאים לחיזוק" hint={`${weak.length}`}>
          <ul className="space-y-2">
            {weak.map((s) => (
              <li key={`${s.course_id}${s.topic}`}>
                <Link href={`/courses/${s.course_id}/practice?topic=${encodeURIComponent(s.topic)}`} className="flex justify-between">
                  <span>{s.topic} <span className="text-xs text-muted">· {courseName.get(s.course_id)}</span></span>
                  <span className="text-bad font-medium">{pct(s)}%</span>
                </Link>
              </li>
            ))}
          </ul>
        </Fold>
      )}

      <Fold id="home-courses" title="הקורסים שלי" hint={`${courses?.length ?? 0}`}>
        <div className="flex justify-end mb-2">
          <Link href="/courses/new" className="btn-ghost text-sm">+ קורס</Link>
        </div>
        {courses?.length ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {(courses as Course[]).map((c) => {
              const cs = stats.filter((s) => s.course_id === c.id);
              const answered = cs.reduce((a, s) => a + s.answered, 0);
              const correct = cs.reduce((a, s) => a + s.correct, 0);
              const total = cs.reduce((a, s) => a + s.total, 0);
              return (
                <Link key={c.id} href={`/courses/${c.id}`} className="card block">
                  <div className="font-semibold">{c.name}</div>
                  <div className="text-xs text-muted mt-0.5">
                    {c.year ? `שנה ${c.year}` : ""} {c.semester ? `· סמסטר ${c.semester}` : ""}
                  </div>
                  <div className="mt-3 h-2 rounded-full bg-bg overflow-hidden">
                    <div className="h-full bg-good" style={{ width: `${total ? (100 * correct) / total : 0}%` }} />
                  </div>
                  <div className="text-xs text-muted mt-1">
                    {total ? `${correct}/${total} שאלות נשלטות · ${answered ? Math.round((100 * correct) / answered) : 0}% הצלחה` : "עוד אין שאלות"}
                  </div>
                </Link>
              );
            })}
          </div>
        ) : (
          <div className="card text-center py-8">
            <p className="mb-3">עוד אין קורסים. מתחילים מהוספת קורס ראשון.</p>
            <Link href="/courses/new" className="btn">הוספת קורס</Link>
          </div>
        )}
      </Fold>
    </div>
  );
}
