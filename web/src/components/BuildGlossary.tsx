"use client";

import { useState, useTransition } from "react";
import { buildGlossary } from "@/app/(app)/actions";

export default function BuildGlossary({ courseId }: { courseId: string }) {
  const [msg, setMsg] = useState("");
  const [pending, start] = useTransition();
  return (
    <>
      <button className="btn w-full" disabled={pending} onClick={() => start(async () => setMsg(await buildGlossary(courseId)))}>
        {pending ? "מוציא מילים מהפרקים..." : "להוציא מילים מהפרקים הקיימים"}
      </button>
      {msg && <p className="text-sm text-muted">{msg}</p>}
    </>
  );
}
