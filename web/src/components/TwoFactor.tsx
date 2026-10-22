"use client";

import { useEffect, useState } from "react";
import { supabaseBrowser } from "@/lib/supabase/client";

type Enroll = { id: string; qr: string; secret: string };

/** Two-step sign-in with an authenticator app (TOTP): enable, verify, disable. */
export default function TwoFactor() {
  const [factorId, setFactorId] = useState<string | null | undefined>(undefined);
  const [enroll, setEnroll] = useState<Enroll | null>(null);
  const [code, setCode] = useState("");
  const [msg, setMsg] = useState("");

  const refresh = () => supabaseBrowser().auth.mfa.listFactors()
    .then(({ data }) => setFactorId(data?.totp?.find((f) => f.status === "verified")?.id ?? null));
  useEffect(() => { refresh(); }, []);

  async function start() {
    setMsg("");
    const sb = supabaseBrowser();
    // Drop half-finished enrollments first; Supabase allows only one pending TOTP factor.
    const { data: list } = await sb.auth.mfa.listFactors();
    for (const f of list?.all ?? []) if (f.status !== "verified") await sb.auth.mfa.unenroll({ factorId: f.id });
    const { data, error } = await sb.auth.mfa.enroll({ factorType: "totp", friendlyName: `Study Hub ${Date.now()}` });
    if (error || !data) return setMsg(error?.message ?? "שגיאה");
    setEnroll({ id: data.id, qr: data.totp.qr_code, secret: data.totp.secret });
  }

  async function confirm() {
    if (!enroll) return;
    const { error } = await supabaseBrowser().auth.mfa.challengeAndVerify({ factorId: enroll.id, code: code.trim() });
    if (error) return setMsg("הקוד לא נכון - נסה את הקוד הנוכחי מהאפליקציה");
    setEnroll(null);
    setCode("");
    setMsg("✓ האימות הדו-שלבי פעיל. מעכשיו כל התחברות תבקש קוד מהאפליקציה.");
    refresh();
  }

  async function disable() {
    if (!factorId || !confirm_("לכבות את האימות הדו-שלבי?")) return;
    const { error } = await supabaseBrowser().auth.mfa.unenroll({ factorId });
    setMsg(error ? error.message : "האימות הדו-שלבי כובה.");
    refresh();
  }

  if (factorId === undefined) return <p className="text-sm text-muted">בודק...</p>;
  if (factorId) {
    return (
      <div className="space-y-2">
        <p className="text-sm text-good">✓ פעיל: כל התחברות דורשת גם קוד מאפליקציית האימות.</p>
        <button className="btn-ghost w-full" onClick={disable}>כיבוי</button>
        {msg && <p className="text-sm text-muted">{msg}</p>}
      </div>
    );
  }
  if (enroll) {
    return (
      <div className="space-y-3">
        <ol className="text-sm list-decimal ps-5 space-y-1">
          <li>מתקינים באייפון את <b>Google Authenticator</b> (או Microsoft Authenticator) מה-App Store.</li>
          <li>באפליקציה: <b>+</b> ← סריקת קוד QR, וסורקים את הקוד. מהאייפון עצמו: מעתיקים את המפתח ובוחרים &quot;הזנת מפתח&quot;.</li>
          <li>מקלידים כאן את 6 הספרות שמופיעות שם.</li>
        </ol>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={enroll.qr} alt="קוד QR לאפליקציית האימות" className="w-44 h-44 bg-white rounded-xl p-2 mx-auto" />
        <p className="text-xs text-muted text-center break-all" dir="ltr">{enroll.secret}</p>
        <input className="input text-center tracking-[0.4em]" dir="ltr" inputMode="numeric" autoComplete="one-time-code"
          maxLength={6} placeholder="000000" value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))} />
        <button className="btn w-full" disabled={code.length !== 6} onClick={confirm}>אישור</button>
        {msg && <p className="text-sm text-bad">{msg}</p>}
      </div>
    );
  }
  return (
    <div className="space-y-2">
      <p className="text-sm text-muted">מגן גם אם מישהו יגלה את הסיסמה: בכל התחברות צריך גם קוד מהטלפון שלך.</p>
      <button className="btn w-full" onClick={start}>הפעלת אימות דו-שלבי</button>
      {msg && <p className="text-sm text-muted">{msg}</p>}
    </div>
  );
}

const confirm_ = (q: string) => typeof window !== "undefined" && window.confirm(q);
