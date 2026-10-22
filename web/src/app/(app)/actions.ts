"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import { dispatchLesson, dispatchNotify } from "@/lib/github";
import { parseIcs } from "@/lib/ics";
import { israelLocalToIso } from "@/lib/format";
import { extractSyllabus } from "@/lib/syllabus";

const str = (f: FormData, k: string) => {
  const v = String(f.get(k) ?? "").trim();
  return v || null;
};
const int = (f: FormData, k: string) => {
  const v = parseInt(String(f.get(k) ?? ""), 10);
  return Number.isFinite(v) ? v : null;
};

function courseFields(f: FormData) {
  const weights = String(f.get("grade_weights") ?? "")
    .split(/[,\n]/)
    .map((p) => p.match(/^\s*(.+?)\s*[:\-]?\s*(\d+)\s*%?\s*$/))
    .filter(Boolean)
    .map((m) => ({ name: m![1], weight: Number(m![2]) }));
  return {
    name: str(f, "name") ?? "קורס",
    code: str(f, "code"),
    kind: str(f, "kind") ?? "course",
    year: int(f, "year"),
    semester: str(f, "semester"),
    lecturer: str(f, "lecturer"),
    ta: str(f, "ta"),
    exam_type: str(f, "exam_type"),
    grade_weights: weights,
    notes: str(f, "notes"),
  };
}

// ---------- courses ----------

export async function createCourse(f: FormData) {
  const { sb } = await requireUser();
  const { data, error } = await sb.from("courses").insert(courseFields(f)).select("id").single();
  if (error) throw new Error(error.message);
  redirect(`/courses/${data.id}`);
}

export async function updateCourse(id: string, f: FormData) {
  const { sb } = await requireUser();
  const { error } = await sb.from("courses").update(courseFields(f)).eq("id", id);
  if (error) throw new Error(error.message);
  revalidatePath(`/courses/${id}`);
}

export async function setArchived(id: string, archived: boolean) {
  const { sb } = await requireUser();
  await sb.from("courses").update({ archived }).eq("id", id);
  revalidatePath("/courses");
  revalidatePath(`/courses/${id}`);
}

export async function deleteCourse(id: string) {
  const { sb } = await requireUser();
  await sb.from("courses").delete().eq("id", id);
  redirect("/courses");
}

// ---------- lessons ----------

export type AddLessonState = { error?: string; ok?: boolean };

export async function addLesson(courseId: string, _: AddLessonState, f: FormData): Promise<AddLessonState> {
  const { sb } = await requireUser();
  const url = str(f, "url");
  const kind = str(f, "kind") ?? "lecture";
  if (!url) return { error: "צריך קישור" };
  if (kind !== "web" && !/zoom\.us\//.test(url)) return { error: "זה לא נראה כמו קישור להקלטת זום" };

  const { data, error } = await sb
    .from("lessons")
    .insert({ course_id: courseId, kind, number: int(f, "number"), title: str(f, "title"), source_url: url })
    .select("id")
    .single();
  if (error) return { error: error.message };

  const author = f.get("author") === "claude" ? "none" : "gemini";
  const dispatchError = await dispatchLesson(data.id, author);
  if (dispatchError) {
    await sb.from("lessons").update({ status: "error", error: dispatchError }).eq("id", data.id);
  }
  revalidatePath(`/courses/${courseId}`);
  return { ok: true };
}

export async function retryLesson(id: string) {
  const { sb } = await requireUser();
  await sb.from("lessons").update({ status: "queued", error: null, progress: null }).eq("id", id);
  const err = await dispatchLesson(id);
  if (err) await sb.from("lessons").update({ status: "error", error: err }).eq("id", id);
  revalidatePath(`/lessons/${id}`);
}

export async function deleteLesson(id: string, courseId: string) {
  const { sb, userId } = await requireUser();
  const { data: files } = await sb.storage.from("study").list(`${userId}/lessons/${id}`, { limit: 1000 });
  if (files?.length) await sb.storage.from("study").remove(files.map((x) => `${userId}/lessons/${id}/${x.name}`));
  await sb.from("lessons").delete().eq("id", id);
  redirect(`/courses/${courseId}`);
}

export async function markRead(id: string) {
  const { sb } = await requireUser();
  await sb.from("lessons").update({ read_at: new Date().toISOString() }).eq("id", id);
  revalidatePath(`/lessons/${id}`);
}

// ---------- quiz ----------

/** Records an answer and returns the correct option (checked on the server). */
export async function answerQuestion(questionId: string, chosen: number) {
  const { sb } = await requireUser();
  const { data: q } = await sb.from("questions").select("course_id, correct").eq("id", questionId).single();
  if (!q) throw new Error("question not found");
  await sb.from("attempts").insert({
    question_id: questionId,
    course_id: q.course_id,
    chosen,
    is_correct: chosen === q.correct,
  });
  return q.correct as number;
}

// ---------- materials ----------

export async function addMaterial(courseId: string, m: { title: string; kind: string; path: string; mime: string; size: number }) {
  const { sb } = await requireUser();
  await sb.from("materials").insert({
    course_id: courseId, title: m.title, kind: m.kind, storage_path: m.path, mime: m.mime, size_bytes: m.size,
  });
  let note: string | null = null;
  const readable = m.mime === "application/pdf" || m.mime.startsWith("image/") || m.mime.startsWith("text/");
  if (m.kind === "syllabus" && readable) {
    const { data: file } = await sb.storage.from("study").download(m.path);
    note = file ? await extractSyllabus(sb, courseId, file, m.mime).catch((e) => `קריאת הסילבוס נכשלה: ${(e as Error).message}`) : null;
  }
  revalidatePath(`/courses/${courseId}`);
  return note;
}

export async function deleteMaterial(id: string, courseId: string) {
  const { sb } = await requireUser();
  const { data } = await sb.from("materials").select("storage_path").eq("id", id).single();
  if (data) await sb.storage.from("study").remove([data.storage_path]);
  await sb.from("materials").delete().eq("id", id);
  revalidatePath(`/courses/${courseId}`);
}

// ---------- deadlines ----------

function deadlineFields(f: FormData) {
  return {
    title: str(f, "title") ?? "משימה",
    kind: str(f, "kind") ?? "assignment",
    course_id: str(f, "course_id"),
    due_at: israelLocalToIso(str(f, "due_at")!),
    notes: str(f, "notes"),
  };
}

export async function addDeadline(f: FormData) {
  const { sb } = await requireUser();
  if (!str(f, "due_at")) return;
  await sb.from("deadlines").insert(deadlineFields(f));
  revalidatePath("/deadlines");
  revalidatePath("/");
}

export async function updateDeadline(id: string, f: FormData) {
  const { sb } = await requireUser();
  if (!str(f, "due_at")) return;
  await sb.from("deadlines").update(deadlineFields(f)).eq("id", id);
  revalidatePath("/deadlines");
  revalidatePath("/");
  redirect("/deadlines");
}

export async function toggleDeadline(id: string, done: boolean) {
  const { sb } = await requireUser();
  await sb.from("deadlines").update({ done }).eq("id", id);
  revalidatePath("/deadlines");
  revalidatePath("/");
}

export async function deleteDeadline(id: string) {
  const { sb } = await requireUser();
  await sb.from("deadlines").delete().eq("id", id);
  revalidatePath("/");
  redirect("/deadlines");
}

// ---------- settings / Moodle sync ----------

export async function saveSettings(f: FormData) {
  const { sb, userId } = await requireUser();
  await sb.from("settings").upsert({ user_id: userId, moodle_ics_url: str(f, "moodle_ics_url"), updated_at: new Date().toISOString() });
  revalidatePath("/settings");
}

export async function setReservist(on: boolean) {
  const { sb, userId } = await requireUser();
  await sb.from("settings").upsert({ user_id: userId, is_reservist: on, updated_at: new Date().toISOString() });
  revalidatePath("/settings");
  revalidatePath("/courses", "layout");
}

export async function syncMoodle(): Promise<string> {
  const { sb, userId } = await requireUser();
  const { data: s } = await sb.from("settings").select("moodle_ics_url").eq("user_id", userId).maybeSingle();
  if (!s?.moodle_ics_url) return "לא הוגדר קישור ללוח השנה של המודל (בהגדרות)";
  const res = await fetch(s.moodle_ics_url, { cache: "no-store" });
  if (!res.ok) return `המודל החזיר שגיאה ${res.status}`;
  const events = parseIcs(await res.text()).filter((e) => e.start.getTime() > Date.now() - 7 * 864e5);

  const { data: courses } = await sb.from("courses").select("id, name").eq("archived", false);
  const rows = events.map((e) => {
    const text = `${e.categories} ${e.summary}`;
    const course = courses?.find((c) => text.includes(c.name));
    const kind = /מבחן|בחינה|exam/i.test(text) ? "exam" : /בוחן|quiz/i.test(text) ? "quiz" : /דוח|report/i.test(text) ? "lab_report" : "assignment";
    return {
      user_id: userId,
      external_uid: e.uid,
      title: e.summary,
      kind,
      course_id: course?.id ?? null,
      due_at: e.start.toISOString(),
      notes: e.categories || null,
    };
  });
  if (rows.length) {
    const { error } = await sb.from("deadlines").upsert(rows, { onConflict: "user_id,external_uid", ignoreDuplicates: false });
    if (error) return error.message;
  }
  revalidatePath("/deadlines");
  revalidatePath("/");
  return `סונכרנו ${rows.length} אירועים מהמודל`;
}

// ---------- push notifications ----------

export async function pushPublicKey(): Promise<string | null> {
  const { sb } = await requireUser();
  const { data } = await sb.rpc("push_public_key");
  if (data) return data as string;
  // First use: ask the notification worker to create the signing keys (takes ~1 minute).
  await dispatchNotify("setup");
  return null;
}

export async function savePushSubscription(sub: { endpoint: string; keys: { p256dh: string; auth: string } }) {
  const { sb, userId } = await requireUser();
  await sb.from("push_subscriptions").delete().eq("endpoint", sub.endpoint);
  const { error } = await sb.from("push_subscriptions").insert({
    user_id: userId, endpoint: sub.endpoint, p256dh: sub.keys.p256dh, auth: sub.keys.auth,
  });
  if (error) throw new Error(error.message);
}

export async function removePushSubscription(endpoint: string) {
  const { sb } = await requireUser();
  await sb.from("push_subscriptions").delete().eq("endpoint", endpoint);
}

export async function sendTestPush() {
  const { userId } = await requireUser();
  return dispatchNotify("test", userId);
}

// ---------- timetable ----------

function slotFields(f: FormData) {
  return {
    title: str(f, "title") ?? "שיעור",
    kind: str(f, "kind") ?? "lecture",
    course_id: str(f, "course_id"),
    weekday: int(f, "weekday") ?? 0,
    start_time: str(f, "start_time") ?? "09:00",
    end_time: str(f, "end_time") ?? "10:00",
    room: str(f, "room"),
    instructor: str(f, "instructor"),
  };
}

export async function addSlot(f: FormData) {
  const { sb } = await requireUser();
  await sb.from("schedule_slots").insert(slotFields(f));
  revalidatePath("/schedule");
  revalidatePath("/");
}

export async function updateSlot(id: string, f: FormData) {
  const { sb } = await requireUser();
  await sb.from("schedule_slots").update(slotFields(f)).eq("id", id);
  revalidatePath("/");
  redirect("/schedule");
}

export async function deleteSlot(id: string) {
  const { sb } = await requireUser();
  await sb.from("schedule_slots").delete().eq("id", id);
  revalidatePath("/");
  redirect("/schedule");
}
