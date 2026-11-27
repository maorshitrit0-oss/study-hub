import { redirect } from "next/navigation";

/** The course chat was removed (his request 27/11/2026: he hardly used it) - an old link goes to the course. */
export default async function ChatPage({ params }: PageProps<"/courses/[id]/chat">) {
  const { id } = await params;
  redirect(`/courses/${id}`);
}
