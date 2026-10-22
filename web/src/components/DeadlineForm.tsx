import { isoToIsraelLocal } from "@/lib/format";
import type { Deadline } from "@/lib/types";

export default function DeadlineForm({ action, courses, deadline, presetCourse, submit }: {
  action: (f: FormData) => Promise<void>;
  courses: { id: string; name: string }[];
  deadline?: Deadline;
  presetCourse?: string;
  submit: string;
}) {
  return (
    <form action={action} className="space-y-3">
      <input className="input" name="title" required defaultValue={deadline?.title}
        placeholder="מטלה 3 / מבחן מועד א / דוח מכין ניסוי 2" />
      <div className="grid grid-cols-2 gap-3">
        <select className="input" name="kind" defaultValue={deadline?.kind ?? "assignment"}>
          <option value="assignment">מטלה</option>
          <option value="exam">מבחן</option>
          <option value="quiz">בוחן</option>
          <option value="lab_report">דוח מעבדה</option>
          <option value="other">אחר</option>
        </select>
        <select className="input" name="course_id" defaultValue={deadline?.course_id ?? presetCourse ?? ""}>
          <option value="">ללא קורס</option>
          {courses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>
      <input className="input" name="due_at" type="datetime-local" required
        defaultValue={deadline ? isoToIsraelLocal(deadline.due_at) : undefined} />
      <textarea className="input min-h-20" name="notes" defaultValue={deadline?.notes ?? ""} placeholder="הערות (לא חובה)" />
      <button className="btn w-full">{submit}</button>
    </form>
  );
}
