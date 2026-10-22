import Link from "next/link";
import { requireUser } from "@/lib/supabase/server";
import Chat from "@/components/Chat";

export default async function ChatPage({ params }: PageProps<"/courses/[id]/chat">) {
  const { id } = await params;
  const { sb, userId } = await requireUser();
  const [{ data: course }, { data: history }] = await Promise.all([
    sb.from("courses").select("name, kind").eq("id", id).single(),
    sb.from("chat_messages").select("role, content").eq("course_id", id).order("created_at", { ascending: false }).limit(40),
  ]);
  return (
    <div className="space-y-3">
      <Link href={course?.kind === "self" ? `/self/${id}` : `/courses/${id}`} className="text-sm text-accent">→ {course?.name}</Link>
      <h1 className="text-xl font-bold">{course?.kind === "self" ? "מפגש" : "צ'אט"} · {course?.name}</h1>
      <Chat courseId={id} userId={userId} initial={(history ?? []).reverse()} isLab={course?.kind === "lab"} isSelf={course?.kind === "self"} />
    </div>
  );
}
