import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import Chat from "@/components/Chat";

/** The tutor of a self-study track; lives under /self so the "לימוד עצמי" tab stays selected. */
export default async function TutorPage({ params }: PageProps<"/self/[id]/chat">) {
  const { id } = await params;
  const { sb, userId } = await requireUser();
  const [{ data: course }, { data: history }] = await Promise.all([
    sb.from("courses").select("name, kind").eq("id", id).maybeSingle(),
    sb.from("chat_messages").select("role, content").eq("course_id", id).order("created_at", { ascending: false }).limit(40),
  ]);
  if (!course) notFound();
  return (
    <div className="space-y-3">
      <Link href={`/self/${id}`} className="text-sm text-accent">→ {course.name}</Link>
      <h1 className="text-xl font-bold">מפגש · {course.name}</h1>
      <Chat courseId={id} userId={userId} initial={(history ?? []).reverse()} isSelf />
    </div>
  );
}
