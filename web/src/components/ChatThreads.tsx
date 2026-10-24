import Link from "next/link";
import { createThread } from "@/app/(app)/actions";
import type { Thread } from "@/lib/threads";

/** Tabs for the course's chats: the main one, every chat he opened, and "new chat". */
export default function ChatThreads({ courseId, base, threads, current }: {
  courseId: string; base: string; threads: Thread[] | null; current: string | null;
}) {
  if (threads === null) return null; // chat_threads.sql not run yet: one chat only
  const tab = (active: boolean) => `chip whitespace-nowrap py-1.5 px-3 ${active ? "!bg-accent !text-white" : ""}`;
  return (
    <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
      <form action={createThread.bind(null, courseId, base)}>
        <button className={tab(false)}>＋ צ&apos;אט חדש</button>
      </form>
      <Link href={base} className={tab(!current)}>ראשי</Link>
      {[...threads].reverse().map((t) => (
        <Link key={t.id} href={`${base}?t=${t.id}`} className={tab(current === t.id)}>{t.title}</Link>
      ))}
    </div>
  );
}
