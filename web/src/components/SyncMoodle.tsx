"use client";

import { useState, useTransition } from "react";
import { syncMoodle } from "@/app/(app)/actions";

export default function SyncMoodle() {
  const [msg, setMsg] = useState("");
  const [pending, start] = useTransition();
  return (
    <div className="space-y-2">
      <button className="btn-ghost w-full" disabled={pending} onClick={() => start(async () => setMsg(await syncMoodle()))}>
        {pending ? "מסנכרן..." : "סנכרון משימות מהמודל עכשיו"}
      </button>
      {msg && <p className="text-sm text-muted">{msg}</p>}
    </div>
  );
}
