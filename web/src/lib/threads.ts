import type { SupabaseClient } from "@supabase/supabase-js";

// Several chats per course. Messages with no thread_id belong to the course's main chat. Everything here
// still works before supabase/chat_threads.sql was run (then there is just the one chat).

export type Thread = { id: string; title: string; created_at: string };
export const NEW_THREAD_TITLE = "צ'אט חדש";
const UUID = /^[0-9a-f-]{36}$/;
export const validThread = (t: unknown) => (typeof t === "string" && UUID.test(t) ? t : null);

/** The latest messages of one chat, newest first. */
export async function threadMessages(sb: SupabaseClient, courseId: string, threadId: string | null, limit: number) {
  const base = () => sb.from("chat_messages").select("role, content").eq("course_id", courseId)
    .order("created_at", { ascending: false }).limit(limit);
  const res = await (threadId ? base().eq("thread_id", threadId) : base().is("thread_id", null));
  return res.error ? base() : res;
}

export async function saveMessage(sb: SupabaseClient, row: Record<string, unknown>, threadId: string | null) {
  if (!threadId) return sb.from("chat_messages").insert(row);
  const res = await sb.from("chat_messages").insert({ ...row, thread_id: threadId });
  return res.error ? sb.from("chat_messages").insert(row) : res;
}

export async function listThreads(sb: SupabaseClient, courseId: string) {
  const { data, error } = await sb.from("chat_threads").select("id, title, created_at").eq("course_id", courseId).order("created_at");
  return error ? null : ((data ?? []) as Thread[]); // null: not migrated yet
}

/** A new chat is named after its first question. */
export async function nameThread(sb: SupabaseClient, threadId: string | null, firstMessage: string) {
  if (!threadId) return;
  const title = firstMessage.replace(/\s+/g, " ").trim().slice(0, 40) || NEW_THREAD_TITLE;
  await sb.from("chat_threads").update({ title }).eq("id", threadId).eq("title", NEW_THREAD_TITLE);
}
