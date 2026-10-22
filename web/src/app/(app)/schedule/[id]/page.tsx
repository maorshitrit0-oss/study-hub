import Link from "next/link";
import { notFound } from "next/navigation";
import { requireUser } from "@/lib/supabase/server";
import SlotForm from "@/components/SlotForm";
import { deleteSlot, updateSlot } from "../../actions";
import type { Slot } from "@/lib/types";

export default async function EditSlot({ params }: PageProps<"/schedule/[id]">) {
  const { id } = await params;
  const { sb } = await requireUser();
  const [{ data }, { data: courses }] = await Promise.all([
    sb.from("schedule_slots").select("*").eq("id", id).maybeSingle(),
    sb.from("courses").select("id, name").eq("archived", false).order("name"),
  ]);
  if (!data) notFound();
  return (
    <div className="space-y-4">
      <Link href="/schedule" className="text-sm text-accent">→ מערכת שעות</Link>
      <h1 className="text-2xl font-bold">עריכת שיעור</h1>
      <div className="card"><SlotForm action={updateSlot.bind(null, id)} courses={courses ?? []} slot={data as Slot} submit="שמירה" /></div>
      <form action={deleteSlot.bind(null, id)}><button className="w-full text-bad text-sm py-2">מחיקה מהמערכת</button></form>
    </div>
  );
}
