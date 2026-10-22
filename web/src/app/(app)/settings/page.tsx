import { requireUser } from "@/lib/supabase/server";
import SyncMoodle from "@/components/SyncMoodle";
import PushToggle from "@/components/PushToggle";
import { saveSettings, setReservist } from "../actions";
import { signOut } from "@/app/login/actions";

export default async function Settings() {
  const { sb, userId } = await requireUser();
  const [{ data: s }, { data: user }] = await Promise.all([
    sb.from("settings").select("moodle_ics_url, is_reservist").eq("user_id", userId).maybeSingle(),
    sb.auth.getUser(),
  ]);
  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold">הגדרות</h1>

      <section className="card space-y-3">
        <h2 className="font-semibold">מילואים</h2>
        <p className="text-sm text-muted">
          {s?.is_reservist
            ? "מסומן שאתה משרת מילואים: ההקלות של כל קורס מודגשות בראש דף הקורס, והצ'אט מתחשב בזה."
            : "ההקלות למילואימניקים שהמרצים מזכירים נשמרות בכל מקרה בדף הקורס."}
        </p>
        <form action={setReservist.bind(null, !s?.is_reservist)}>
          <button className={s?.is_reservist ? "btn-ghost w-full" : "btn w-full"}>
            {s?.is_reservist ? "אני כבר לא במילואים" : "אני משרת מילואים בסמסטר הזה"}
          </button>
        </form>
      </section>

      <section className="card space-y-3">
        <h2 className="font-semibold">התראות</h2>
        <p className="text-sm text-muted">כל בוקר: מה מגישים היום ומחר ומבחנים בשבוע הקרוב. וגם כשפרק חדש מוכן לקריאה.</p>
        <PushToggle />
      </section>

      <section className="card space-y-3">
        <h2 className="font-semibold">סנכרון עם המודל</h2>
        <ol className="text-sm text-muted list-decimal ps-5 space-y-1">
          <li>במודל: לוח שנה ← ייצוא לוח שנה (Export calendar)</li>
          <li>בוחרים &quot;כל האירועים&quot; ו&quot;60 הימים הקרובים&quot; ← &quot;קבלת כתובת לוח השנה&quot;</li>
          <li>מעתיקים את הכתובת ומדביקים כאן</li>
        </ol>
        <form action={saveSettings} className="space-y-2">
          <input className="input" name="moodle_ics_url" dir="ltr" defaultValue={s?.moodle_ics_url ?? ""}
            placeholder="https://moodle.ariel.ac.il/calendar/export_execute.php?..." />
          <button className="btn w-full">שמירה</button>
        </form>
        <SyncMoodle />
        <p className="text-xs text-muted">משימות שמשויכות לקורס לפי השם שלו במודל. כדאי לתת לקורסים כאן אותו שם כמו במודל.</p>
      </section>

      <section className="card space-y-3">
        <h2 className="font-semibold">התקנה באייפון</h2>
        <p className="text-sm text-muted">ב-Safari: כפתור השיתוף ← &quot;הוסף למסך הבית&quot;. האפליקציה תיפתח כמו אפליקציה רגילה.</p>
      </section>

      <section className="card space-y-3">
        <p className="text-sm text-muted" dir="ltr">{user.user?.email}</p>
        <form action={signOut}><button className="btn-ghost w-full">התנתקות</button></form>
      </section>

      <p className="text-center text-xs text-muted">Study Hub · פותח על ידי Maor Shitrit</p>

      <p className="text-center text-xs text-muted">
        Study Hub · פותח על ידי <span dir="ltr">Maor Shitrit</span>
      </p>
    </div>
  );
}
