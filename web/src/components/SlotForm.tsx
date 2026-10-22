import { DAYS, hhmm, type Slot } from "@/lib/types";

export default function SlotForm({ action, courses, slot, submit }: {
  action: (f: FormData) => Promise<void>;
  courses: { id: string; name: string }[];
  slot?: Slot;
  submit: string;
}) {
  return (
    <form action={action} className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <select className="input" name="course_id" defaultValue={slot?.course_id ?? ""}>
          <option value="">ללא קורס</option>
          {courses.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select className="input" name="kind" defaultValue={slot?.kind ?? "lecture"}>
          <option value="lecture">הרצאה</option>
          <option value="practice">תרגול</option>
          <option value="lab">מעבדה</option>
          <option value="other">אחר</option>
        </select>
      </div>
      <input className="input" name="title" defaultValue={slot?.title} placeholder="שם (אם אין קורס)" />
      <div className="grid grid-cols-3 gap-3">
        <select className="input" name="weekday" defaultValue={slot?.weekday ?? 0} aria-label="יום">
          {DAYS.map((d, i) => <option key={d} value={i}>{d}</option>)}
        </select>
        <input className="input" name="start_time" type="time" required defaultValue={slot ? hhmm(slot.start_time) : "09:00"} aria-label="התחלה" />
        <input className="input" name="end_time" type="time" required defaultValue={slot ? hhmm(slot.end_time) : "12:00"} aria-label="סיום" />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <input className="input" name="room" defaultValue={slot?.room ?? ""} placeholder="חדר" />
        <input className="input" name="instructor" defaultValue={slot?.instructor ?? ""} placeholder="מרצה / מתרגל" />
      </div>
      <button className="btn w-full">{submit}</button>
    </form>
  );
}
