"use client";

import { useState } from "react";
import { readExerciseFiles } from "@/app/(app)/actions";

/** Starts reading the course's homework / past-exam files for exercises (also runs every morning by itself). */
export default function ReadExerciseFiles({ courseId }: { courseId: string }) {
  const [msg, setMsg] = useState("");
  return (
    <div className="text-sm">
      <button className="btn-ghost" onClick={async () => setMsg(await readExerciseFiles(courseId))}>
        📂 לקרוא עכשיו תרגילים מהקבצים של הקורס
      </button>
      {msg && <p className="mt-1">{msg}</p>}
      <p className="text-xs text-muted mt-1">קורה גם לבד כל בוקר, לכל קובץ חדש (מטלה, מבחן, דף תרגילים).</p>
    </div>
  );
}
