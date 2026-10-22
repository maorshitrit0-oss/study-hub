import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import DeadlineForm from "@/components/DeadlineForm";
import { deleteDeadline, updateDeadline } from "../../actions";
import type { Deadline } from "@/lib/types";

export default async function EditDeadline({ params }: PageProps<"/deadlines/[id]">) {
  const { id } = await params;
  const { sb } = await requireUser();
  const [{ data }, { data: courses }] = await Promise.all([
    sb.from("deadlines").select("*").eq("id", id).maybeSingle(),
    sb.from("courses").select("id, name").eq("archived", false).order("name"),
  ]);
  if (!data) notFound();
  return (
    <div className="space-y-4">
      {data.kind === "exam"
        ? <Link href="/exams" className="text-sm text-accent">→ לוח מבחנים</Link>
        : <Link href="/deadlines" className="text-sm text-accent">→ משימות</Link>}
      <h1 className="text-2xl font-bold">{data.kind === "exam" ? "עריכת מבחן" : "עריכת משימה"}</h1>
      <div className="card">
        <DeadlineForm action={updateDeadline.bind(null, id)} courses={courses ?? []} deadline={data as Deadline} submit="שמירה" />
      </div>
      <form action={deleteDeadline.bind(null, id)}>
        <button className="w-full text-bad text-sm py-2">מחיקה</button>
      </form>
    </div>
  );
}
