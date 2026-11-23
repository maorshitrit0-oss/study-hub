import BackLink from "@/components/BackLink";
import { requireUser } from "@/lib/supabase/server";
import PushToggle from "@/components/PushToggle";
import TwoFactor from "@/components/TwoFactor";
import { UsagePanel, type Snapshot } from "@/components/Usage";
import { setReservist } from "../actions";
import { signOut } from "@/app/login/actions";

export default async function Settings() {
  const { sb, userId } = await requireUser();
  const [{ data: s }, { data: user }, { data: usage }] = await Promise.all([
    sb.from("settings").select("is_reservist").eq("user_id", userId).maybeSingle(),
    sb.auth.getUser(),
    sb.from("usage_snapshot").select("data").eq("id", 1).maybeSingle(),
  ]);
  return (
    <div className="space-y-5">
      <BackLink href={"/"}>→ דף הבית</BackLink>
      <h1 className="text-2xl font-bold">הגדרות</h1>

      <section className="card space-y-3">
        <h2 className="font-semibold">אבטחה: אימות דו-שלבי</h2>
        <TwoFactor />
      </section>

      <section className="card space-y-3 scroll-mt-4" id="usage">
        <h2 className="font-semibold">שימוש במשאבים החינמיים</h2>
        <UsagePanel snap={(usage?.data as Snapshot) ?? null} />
      </section>

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
        <h2 className="font-semibold">התקנה באייפון</h2>
        <p className="text-sm text-muted">ב-Safari: כפתור השיתוף ← &quot;הוסף למסך הבית&quot;. האפליקציה תיפתח כמו אפליקציה רגילה.</p>
      </section>

      <section className="card space-y-3">
        <p className="text-sm text-muted" dir="ltr">{user.user?.email}</p>
        <form action={signOut}><button className="btn-ghost w-full">התנתקות</button></form>
      </section>
    </div>
  );
}
