import Link from "next/link";
import { redirect } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import Chat from "@/components/Chat";
import ChatThreads from "@/components/ChatThreads";
import { listThreads, threadMessages, validThread } from "@/lib/threads";

export default async function ChatPage({ params, searchParams }: PageProps<"/courses/[id]/chat">) {
  const { id } = await params;
  const threadId = validThread((await searchParams).t);
  const { sb, userId } = await requireUser();
  const [{ data: course }, { data: history }, threads] = await Promise.all([
    sb.from("courses").select("name, kind").eq("id", id).single(),
    threadMessages(sb, id, threadId, 40),
    listThreads(sb, id),
  ]);
  if (course?.kind === "self") redirect(`/self/${id}/chat${threadId ? `?t=${threadId}` : ""}`);
  return (
    <div className="space-y-3">
      <Link href={`/courses/${id}`} className="text-sm text-accent">→ {course?.name}</Link>
      <h1 className="text-xl font-bold">צ&apos;אט · {course?.name}</h1>
      <ChatThreads courseId={id} base={`/courses/${id}/chat`} threads={threads} current={threadId} />
      <Chat key={threadId ?? "main"} courseId={id} userId={userId} threadId={threadId} initial={(history ?? []).reverse()} isLab={course?.kind === "lab"} />
    </div>
  );
}
