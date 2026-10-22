"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { supabaseBrowser } from "@/lib/supabase/client";
import Credit from "@/components/Credit";

/** Second sign-in step for accounts with an authenticator app. */
export default function MfaPage() {
  const [code, setCode] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const router = useRouter();
  const go = (to: string) => { router.replace(to); router.refresh(); };

  async function verify(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    const sb = supabaseBrowser();
    const { data } = await sb.auth.mfa.listFactors();
    const factor = data?.totp?.find((f) => f.status === "verified");
    if (!factor) return go("/");
    const { error } = await sb.auth.mfa.challengeAndVerify({ factorId: factor.id, code: code.trim() });
    setBusy(false);
    if (error) { setMsg("הקוד לא נכון או שפג תוקפו - נסה את הקוד הנוכחי"); setCode(""); return; }
    go("/");
  }

  return (
    <main className="min-h-dvh flex items-center justify-center p-4">
      <p className="fixed top-[max(1rem,env(safe-area-inset-top))] right-4 text-sm font-medium text-accent">בשם ה&apos; נעשה ונצליח</p>
      <form onSubmit={verify} className="card w-full max-w-sm space-y-4">
        <h1 className="text-xl font-bold">אימות דו-שלבי</h1>
        <p className="text-sm text-muted">הקלד את 6 הספרות מאפליקציית האימות (Google Authenticator).</p>
        <input className="input text-center text-2xl tracking-[0.4em]" dir="ltr" inputMode="numeric" autoComplete="one-time-code"
          autoFocus maxLength={6} placeholder="000000" value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))} />
        {msg && <p className="text-sm text-bad">{msg}</p>}
        <button className="btn w-full" disabled={busy || code.length !== 6}>{busy ? "בודק..." : "כניסה"}</button>
        <button type="button" className="text-sm text-muted w-full"
          onClick={async () => { await supabaseBrowser().auth.signOut(); go("/login"); }}>
          התנתקות
        </button>
        <Credit className="mt-2" />
      </form>
    </main>
  );
}
