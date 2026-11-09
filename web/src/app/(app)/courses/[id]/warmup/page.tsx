import { notFound, redirect } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import { nextLesson } from "@/lib/warmup";
import type { Lesson } from "@/lib/types";

/** "🔥 Warm-up before the next class" (course page, home): the warm-up inside the next lesson he has not read yet. */
export default async function WarmupPage({ params }: PageProps<"/courses/[id]/warmup">) {
  const { id } = await params;
  const { sb } = await requireUser();
  const { data: lessons } = await sb.from("lessons").select("id, kind, number, title, status, created_at, source_url, transcript, read_at").eq("course_id", id);
  const next = nextLesson((lessons ?? []) as unknown as Lesson[]);
  if (!next) notFound();
  redirect(`/lessons/${next.id}#warmup-${next.id}`);
}
