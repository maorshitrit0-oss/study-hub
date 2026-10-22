"use client";

import { useActionState, useState } from "react";
import { authenticate, type AuthState } from "./actions";
import Credit from "@/components/Credit";

export default function LoginPage() {
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [state, action, pending] = useActionState<AuthState, FormData>(authenticate, {});

  return (
    <main className="min-h-dvh flex items-center justify-center p-4">
      <p className="fixed top-[max(1rem,env(safe-area-inset-top))] right-4 text-sm font-medium text-accent">בשם ה&apos; נעשה ונצליח</p>
      <div className="card w-full max-w-sm">
        <h1 className="text-2xl font-bold mb-1">Study Hub</h1>
        <p className="text-muted mb-5">לומדים מקריאה, לא מהקלטות.</p>
        <form action={action} className="space-y-3">
          <input type="hidden" name="mode" value={mode} />
          <div>
            <label className="label" htmlFor="email">אימייל</label>
            <input className="input" id="email" name="email" type="email" dir="ltr" required autoComplete="email" />
          </div>
          <div>
            <label className="label" htmlFor="password">סיסמה</label>
            <input className="input" id="password" name="password" type="password" dir="ltr" required minLength={6}
              autoComplete={mode === "signin" ? "current-password" : "new-password"} />
          </div>
          {state.error && <p className="text-bad text-sm">{state.error}</p>}
          {state.message && <p className="text-good text-sm">{state.message}</p>}
          <button className="btn w-full" disabled={pending}>
            {pending ? "רגע..." : mode === "signin" ? "התחברות" : "הרשמה"}
          </button>
        </form>
        <button className="mt-4 text-sm text-accent" onClick={() => setMode(mode === "signin" ? "signup" : "signin")}>
          {mode === "signin" ? "אין לך משתמש? להרשמה" : "יש לך משתמש? להתחברות"}
        </button>
        <Credit className="mt-6" />
      </div>
    </main>
  );
}
