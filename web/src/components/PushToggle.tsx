"use client";

import { useEffect, useState } from "react";
import { pushPublicKey, removePushSubscription, savePushSubscription, sendTestPush } from "@/app/(app)/actions";

type State = "loading" | "unsupported" | "install" | "denied" | "off" | "on";

function keyBytes(b64: string) {
  const s = atob((b64 + "=".repeat((4 - (b64.length % 4)) % 4)).replace(/-/g, "+").replace(/_/g, "/"));
  return Uint8Array.from(s, (c) => c.charCodeAt(0));
}

export default function PushToggle() {
  const [state, setState] = useState<State>("loading");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    (async () => {
      const ios = /iphone|ipad|ipod/i.test(navigator.userAgent);
      const standalone = window.matchMedia("(display-mode: standalone)").matches;
      if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
        setState(ios && !standalone ? "install" : "unsupported");
        return;
      }
      if (ios && !standalone) return setState("install");
      if (Notification.permission === "denied") return setState("denied");
      const reg = await navigator.serviceWorker.register("/sw.js");
      setState((await reg.pushManager.getSubscription()) ? "on" : "off");
    })();
  }, []);

  async function enable() {
    setBusy(true);
    setMsg("");
    try {
      if ((await Notification.requestPermission()) !== "granted") {
        setState("denied");
        return;
      }
      const key = await pushPublicKey();
      if (!key) {
        setMsg("מכין את ההתראות בפעם הראשונה... נסה שוב בעוד דקה.");
        return;
      }
      const reg = await navigator.serviceWorker.register("/sw.js");
      await navigator.serviceWorker.ready;
      const sub = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: keyBytes(key) });
      await savePushSubscription(sub.toJSON() as { endpoint: string; keys: { p256dh: string; auth: string } });
      setState("on");
      setMsg("ההתראות הופעלו ✓");
    } catch (e) {
      setMsg(`לא הצלחתי להפעיל: ${(e as Error).message}`);
    } finally {
      setBusy(false);
    }
  }

  async function disable() {
    setBusy(true);
    const reg = await navigator.serviceWorker.getRegistration();
    const sub = await reg?.pushManager.getSubscription();
    if (sub) {
      await removePushSubscription(sub.endpoint);
      await sub.unsubscribe();
    }
    setState("off");
    setBusy(false);
  }

  async function test() {
    setBusy(true);
    const err = await sendTestPush();
    setMsg(err ?? "נשלחה התראת בדיקה - תגיע תוך דקה בערך.");
    setBusy(false);
  }

  if (state === "loading") return <p className="text-sm text-muted">בודק...</p>;
  if (state === "install") {
    return (
      <p className="text-sm">
        באייפון ההתראות עובדות רק מהאפליקציה שעל מסך הבית: ב-Safari לוחצים על כפתור השיתוף ← &quot;הוסף למסך הבית&quot;,
        פותחים את Study Hub מהאייקון, וחוזרים לכאן.
      </p>
    );
  }
  if (state === "unsupported") return <p className="text-sm text-muted">הדפדפן הזה לא תומך בהתראות.</p>;
  if (state === "denied") {
    return <p className="text-sm">ההתראות חסומות. באייפון: הגדרות ← התראות ← Study Hub ← לאפשר התראות.</p>;
  }
  return (
    <div className="space-y-2">
      {state === "on" ? (
        <>
          <p className="text-sm text-good">ההתראות פעילות במכשיר הזה ✓</p>
          <div className="grid grid-cols-2 gap-2">
            <button className="btn-ghost" disabled={busy} onClick={test}>שליחת התראת בדיקה</button>
            <button className="btn-ghost" disabled={busy} onClick={disable}>כיבוי</button>
          </div>
        </>
      ) : (
        <button className="btn w-full" disabled={busy} onClick={enable}>{busy ? "רגע..." : "הפעלת התראות"}</button>
      )}
      {msg && <p className="text-sm text-muted">{msg}</p>}
    </div>
  );
}
