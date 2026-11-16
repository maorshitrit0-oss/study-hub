"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { pasteZoomTranscript } from "@/app/(app)/actions";

/** Receives the transcript from the Zoom bookmarklet (lib/zoomBookmarklet.ts) and sends it to its lesson. */
export default function ZoomReceiver() {
  const [state, setState] = useState("מחכה לתמלול מדף הזום...");
  const router = useRouter();
  useEffect(() => {
    let done = false;
    const on = async (e: MessageEvent) => {
      if (done || !/^https:\/\/([a-z0-9-]+\.)*zoom\.us$/.test(e.origin)) return;
      const d = e.data as { type?: string; src?: string; text?: string };
      if (d?.type !== "zoom-transcript" || !d.src || !d.text) return;
      done = true;
      (e.source as Window | null)?.postMessage("zoom-ok", e.origin);
      setState(`התקבלו ${d.text.split("\n").length} שורות. שומר...`);
      const r = await pasteZoomTranscript(d.src, d.text);
      if (r.lessonId) router.push(`/lessons/${r.lessonId}`);
      else setState(r.error ?? "משהו השתבש");
    };
    window.addEventListener("message", on);
    return () => window.removeEventListener("message", on);
  }, [router]);
  return <p className="card">{state}</p>;
}
