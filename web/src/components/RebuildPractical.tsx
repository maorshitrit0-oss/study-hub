"use client";

import { useState } from "react";
import { rebuildPractical } from "@/app/(app)/actions";

/** The bank rebuilds itself after every upload; this only forces it now. */
export default function RebuildPractical({ courseId }: { courseId: string }) {
  const [msg, setMsg] = useState("");
  return (
    <p className="text-xs text-muted">
      המאגר מתעדכן לבד אחרי כל העלאה (דוח, הקלטה, קובץ, בוחן כניסה).{" "}
      <button type="button" className="text-accent" onClick={async () => setMsg(await rebuildPractical(courseId))}>לבנות מחדש עכשיו</button>
      {msg && <span> · {msg}</span>}
    </p>
  );
}
