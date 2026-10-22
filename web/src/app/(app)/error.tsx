"use client";

import { useEffect } from "react";

// After a new version is deployed, a page opened before it can't load the new code; one reload fixes it.
const STALE = /ChunkLoadError|Loading chunk|dynamically imported module|Failed to fetch|Failed to find Server Action|deployment/i;
const KEY = "reloaded-after-error";

export default function AppError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error(error);
    try {
      if (STALE.test(error.message) && !sessionStorage.getItem(KEY)) {
        sessionStorage.setItem(KEY, "1");
        window.location.reload();
        return;
      }
      sessionStorage.removeItem(KEY);
    } catch { /* storage blocked */ }
  }, [error]);

  return (
    <div className="card space-y-3 mt-6">
      <h1 className="text-lg font-bold">משהו השתבש בדף הזה</h1>
      <p className="text-sm text-muted">בדרך כלל טעינה מחדש מסדרת את זה (למשל אחרי שהאפליקציה התעדכנה). אם זה חוזר - צלם את המסך הזה ושלח ל-Claude.</p>
      <p className="text-xs text-muted break-all" dir="ltr">{error.message || "error"}{error.digest ? ` · ${error.digest}` : ""}</p>
      <div className="flex gap-2">
        <button className="btn" onClick={() => window.location.reload()}>טעינה מחדש</button>
        <button className="btn-ghost" onClick={() => reset()}>לנסות שוב</button>
      </div>
    </div>
  );
}
