import Link from "next/link";
import TrackTabs from "@/components/TrackTabs";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import Chat from "@/components/Chat";
import ChatThreads from "@/components/ChatThreads";
import { listThreads, threadMessages, validThread } from "@/lib/threads";

/** The tutor of a self-study track; lives under /self so the "לימוד עצמי" tab stays selected. */
export default async function TutorPage({ params, searchParams }: PageProps<"/self/[id]/chat">) {
  const { id } = await params;
  const threadId = validThread((await searchParams).t);
  const { sb, userId } = await requireUser();
  const [{ data: course }, { data: history }, threads, { data: tracks }] = await Promise.all([
    sb.from("courses").select("name, kind").eq("id", id).maybeSingle(),
    threadMessages(sb, id, threadId, 40),
    listThreads(sb, id),
    sb.from("courses").select("id, name").eq("kind", "self").eq("archived", false).order("created_at"),
  ]);
  if (!course) notFound();
  return (
    <div className="space-y-3">
      <Link href={`/self/${id}`} className="text-sm text-accent">→ {course.name}</Link>
      <TrackTabs tracks={tracks ?? []} current={id} suffix="/chat" />
      <h1 className="text-xl font-bold">מפגש · {course.name}</h1>
      <ChatThreads courseId={id} base={`/self/${id}/chat`} threads={threads} current={threadId} />
      <Chat key={threadId ?? "main"} courseId={id} userId={userId} threadId={threadId} initial={(history ?? []).reverse()} isSelf />
    </div>
  );
}
