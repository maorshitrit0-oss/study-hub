"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import { dispatchLesson, dispatchNotify } from "@/lib/github";
import { parseIcs } from "@/lib/ics";
import { isoFromNow, israelLocalToIso } from "@/lib/format";
import { extractSyllabus, looksLikeSyllabus } from "@/lib/syllabus";
import { DRIVE_PREFIX, cleanTitle, driveId, materialBlob } from "@/lib/files";
import { fillGlossary } from "@/lib/glossary";
import { closePrepTask } from "@/lib/prep";
import { friendlyGeminiError } from "@/lib/gemini";

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
  const fields = courseFields(f);
  const { data, error } = await sb.from("courses").insert(fields).select("id").single();
  if (error) throw new Error(error.message);
  redirect(fields.kind === "self" ? `/self/${data.id}` : `/courses/${data.id}`);
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
  const sourcePath = str(f, "source_path");
  const kind = str(f, "kind") ?? "lecture";
  if (!url && !sourcePath) return { error: "צריך קישור או קובץ" };
  if (url && kind !== "web" && !/zoom\.us\/|drive\.google\.com|docs\.google\.com/.test(url)) {
    return { error: "צריך קישור להקלטת זום או לקובץ בגוגל דרייב" };
  }
  if (url && /drive\.google\.com\/drive\/folders/.test(url)) {
    return { error: "זה קישור לתיקייה - צריך קישור לקובץ עצמו (פותחים את הקובץ ← שיתוף ← העתקת קישור)" };
  }

  const { data, error } = await sb
    .from("lessons")
    .insert({ course_id: courseId, kind, number: int(f, "number"), title: str(f, "title"), source_url: url, source_path: sourcePath })
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
  // Row-level security limits the update to the user's own lessons; dispatch only if it matched.
  const { data } = await sb.from("lessons").update({ status: "queued", error: null, progress: null }).eq("id", id).select("id");
  if (!data?.length) return;
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

export async function updateLesson(id: string, f: FormData) {
  const { sb } = await requireUser();
  const kind = str(f, "kind");
  const { data } = await sb.from("lessons")
    .update({ number: int(f, "number"), title: str(f, "title"), ...(kind ? { kind } : {}) })
    .eq("id", id).select("course_id").single();
  revalidatePath(`/lessons/${id}`);
  if (data) revalidatePath(`/courses/${data.course_id}`);
}

export async function markRead(id: string, read = true) {
  const { sb } = await requireUser();
  await sb.from("lessons").update({ read_at: read ? new Date().toISOString() : null }).eq("id", id);
  await closePrepTask(sb, id, read);
  revalidatePath(`/lessons/${id}`);
  revalidatePath("/deadlines");
  revalidatePath("/");
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
  const title = cleanTitle(m.title);
  // A file named like a syllabus is treated as one even if another type was picked.
  const kind = (m.kind === "other" || m.kind === "slides") && looksLikeSyllabus(title) ? "syllabus" : m.kind;
  const { data } = await sb.from("materials").insert({
    course_id: courseId, title, kind, storage_path: m.path, mime: m.mime, size_bytes: m.size,
  }).select("id").single();
  revalidatePath(`/courses/${courseId}`);
  return kind === "syllabus" && data ? readSyllabus(data.id) : null;
}

/** Big files: a shared Google Drive link instead of an upload (Supabase free allows 50 MB per file). */
export async function addDriveMaterial(courseId: string, url: string, kind: string, title: string) {
  const id = driveId(url);
  if (!id) return "זה לא קישור לקובץ בדרייב. בדרייב: שיתוף ← 'כל מי שיש לו את הקישור' ← העתקת קישור";
  const name = title.trim() || "קובץ מהדרייב";
  const mime = /\.docx$/i.test(name) ? "application/vnd.openxmlformats-officedocument.wordprocessingml.document" : "application/pdf";
  return (await addMaterial(courseId, { title: name, kind, path: `${DRIVE_PREFIX}${id}`, mime, size: 0 })) ?? "✓ נוסף";
}

export async function setMaterialKind(id: string, kind: string) {
  const { sb } = await requireUser();
  const { data } = await sb.from("materials").update({ kind }).eq("id", id).select("course_id").single();
  if (data) revalidatePath(`/courses/${data.course_id}`);
  return kind === "syllabus" ? readSyllabus(id) : null;
}

/** (Re)reads a syllabus file into the course info. Returns a status line for the user. */
export async function readSyllabus(materialId: string): Promise<string> {
  const { sb } = await requireUser();
  const { data: m } = await sb.from("materials").select("*").eq("id", materialId).single();
  if (!m) return "הקובץ לא נמצא";
  if (m.kind !== "syllabus") await sb.from("materials").update({ kind: "syllabus" }).eq("id", materialId);
  try {
    const file = await materialBlob(sb, m);
    return await extractSyllabus(sb, m.course_id, file, m.mime ?? file.type, m.title);
  } catch (e) {
    return `קריאת הסילבוס נכשלה: ${(e as Error).message}`;
  } finally {
    revalidatePath(`/courses/${m.course_id}`);
  }
}

// ---------- chats ----------

export async function createThread(courseId: string, base: string) {
  const { sb } = await requireUser();
  const { data } = await sb.from("chat_threads").insert({ course_id: courseId, title: "צ'אט חדש" }).select("id").single();
  redirect(data ? `${base}?t=${data.id}` : base);
}

// ---------- grades ----------

export async function setGradeRow(id: string, fields: { credits?: number; grade?: string | null }) {
  const { sb } = await requireUser();
  await sb.from("grades").update(fields).eq("id", id);
  revalidatePath("/grades");
}

/** Only rows without a grade (planned / current courses) can be removed; real grades stay. */
export async function deleteGradeRow(id: string) {
  const { sb } = await requireUser();
  await sb.from("grades").delete().eq("id", id).is("grade", null);
  revalidatePath("/grades");
}

// ---------- self-study roadmap ----------

export async function setSkillLevel(id: string, level: number) {
  const { sb } = await requireUser();
  const { data } = await sb.from("skills").update({ level: Math.max(0, Math.min(4, level)), updated_at: new Date().toISOString() })
    .eq("id", id).select("course_id").single();
  if (data) revalidatePath(`/self/${data.course_id}`);
}

export async function addSkill(courseId: string, f: FormData) {
  const { sb } = await requireUser();
  const kind = str(f, "kind") === "project" ? "project" : "topic";
  const { data: last } = await sb.from("skills").select("ord").eq("course_id", courseId).eq("kind", kind)
    .order("ord", { ascending: false }).limit(1).maybeSingle();
  await sb.from("skills").insert({ course_id: courseId, kind, title: str(f, "title") ?? "נושא", ord: (last?.ord ?? 0) + 1 });
  revalidatePath(`/self/${courseId}`);
}

// ---------- English words ----------

export async function buildGlossary(courseId: string): Promise<string> {
  const { sb } = await requireUser();
  try {
    const n = await fillGlossary(sb, courseId);
    return n ? `✓ נוספו ${n} מילים` : "לכל הפרקים בקורס כבר יש מילים";
  } catch (e) {
    return `⚠️ ${friendlyGeminiError(e)}`;
  } finally {
    revalidatePath("/words");
  }
}

export async function deleteTerm(id: string) {
  const { sb } = await requireUser();
  await sb.from("glossary").delete().eq("id", id);
  revalidatePath("/words");
}

export async function deleteMaterial(id: string, courseId: string) {
  const { sb } = await requireUser();
  const { data } = await sb.from("materials").select("storage_path").eq("id", id).single();
  if (data && !data.storage_path.startsWith(DRIVE_PREFIX)) await sb.storage.from("study").remove([data.storage_path]);
  await sb.from("materials").delete().eq("id", id);
  revalidatePath(`/courses/${courseId}`);
}

// ---------- deadlines ----------

const UNKNOWN_DUE_DAYS = 120;

function deadlineFields(f: FormData) {
  const checkDue = f.get("check_due") === "on";
  const due = str(f, "due_at");
  return {
    title: str(f, "title") ?? "משימה",
    kind: str(f, "kind") ?? "assignment",
    course_id: str(f, "course_id"),
    // No date yet: park it far ahead so it never looks urgent; the app and the push remind to check instead.
    due_at: due && !checkDue ? israelLocalToIso(due) : isoFromNow(UNKNOWN_DUE_DAYS),
    check_due: checkDue || !due,
    notes: str(f, "notes"),
  };
}

/** Writes a deadline; before the check_due column exists, falls back to a plain dated one. */
async function saveDeadline(sb: Awaited<ReturnType<typeof requireUser>>["sb"], fields: ReturnType<typeof deadlineFields>, id?: string) {
  const run = (row: Partial<typeof fields>) => (id ? sb.from("deadlines").update(row).eq("id", id) : sb.from("deadlines").insert(row));
  const { error } = await run(fields);
  if (error && /check_due/.test(error.message)) {
    const { check_due: _, ...rest } = fields;
    void _;
    await run(rest);
  }
}

export async function addDeadline(f: FormData) {
  const { sb } = await requireUser();
  await saveDeadline(sb, deadlineFields(f));
  revalidatePath("/deadlines");
  revalidatePath("/exams");
  revalidatePath("/");
}

export async function updateDeadline(id: string, f: FormData) {
  const { sb } = await requireUser();
  const fields = deadlineFields(f);
  await saveDeadline(sb, fields, id);
  revalidatePath("/");
  redirect(fields.kind === "exam" ? "/exams" : "/deadlines");
}

export async function toggleDeadline(id: string, done: boolean) {
  const { sb } = await requireUser();
  await sb.from("deadlines").update({ done }).eq("id", id);
  revalidatePath("/deadlines");
  revalidatePath("/");
}

export async function deleteDeadline(id: string) {
  const { sb } = await requireUser();
  const { data } = await sb.from("deadlines").delete().eq("id", id).select("kind").maybeSingle();
  revalidatePath("/");
  redirect(data?.kind === "exam" ? "/exams" : "/deadlines");
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

// ---------- recording reminders ----------

export async function markRecording(slotId: string, classDate: string, status: "uploaded" | "none") {
  const { sb } = await requireUser();
  await sb.from("recording_marks").upsert({ slot_id: slotId, class_date: classDate, status }, { onConflict: "slot_id,class_date" });
  revalidatePath("/");
}

// ---------- course info (facts) ----------

export async function addFact(courseId: string, f: FormData) {
  const { sb } = await requireUser();
  const text = str(f, "text");
  if (!text) return;
  const row = { course_id: courseId, category: str(f, "category") ?? "other", text };
  const { error } = await sb.from("course_facts").insert({ ...row, source: "manual" });
  if (error) await sb.from("course_facts").insert(row); // database without the source column yet
  revalidatePath(`/courses/${courseId}`);
}

export async function deleteFact(id: string, courseId: string) {
  const { sb } = await requireUser();
  await sb.from("course_facts").delete().eq("id", id);
  revalidatePath(`/courses/${courseId}`);
}
