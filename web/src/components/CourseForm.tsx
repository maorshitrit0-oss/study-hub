import type { Course } from "@/lib/types";

export default function CourseForm({ action, course, submit }: {
  action: (f: FormData) => Promise<void>;
  course?: Course;
  submit: string;
}) {
  const weights = course?.grade_weights?.map((w) => `${w.name} ${w.weight}%`).join(", ") ?? "";
  return (
    <form action={action} className="space-y-4">
      <div>
        <label className="label" htmlFor="name">שם הקורס</label>
        <input className="input" id="name" name="name" required defaultValue={course?.name} placeholder="מעגלים ליניאריים" />
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className="label" htmlFor="kind">סוג</label>
          <select className="input" id="kind" name="kind" defaultValue={course?.kind ?? "course"}>
            <option value="course">קורס</option>
            <option value="lab">מעבדה</option>
            <option value="project">פרויקט</option>
            <option value="self">לימוד עצמי</option>
          </select>
        </div>
        <div>
          <label className="label" htmlFor="year">שנה</label>
          <select className="input" id="year" name="year" defaultValue={course?.year ?? 3}>
            <option value="">—</option>
            {[1, 2, 3, 4].map((y) => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
        <div>
          <label className="label" htmlFor="semester">סמסטר</label>
          <select className="input" id="semester" name="semester" defaultValue={course?.semester ?? "א"}>
            <option value="">—</option>
            <option value="א">א</option>
            <option value="ב">ב</option>
            <option value="קיץ">קיץ</option>
          </select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label" htmlFor="lecturer">מרצה</label>
          <input className="input" id="lecturer" name="lecturer" defaultValue={course?.lecturer ?? ""} />
        </div>
        <div>
          <label className="label" htmlFor="ta">מתרגל/ת</label>
          <input className="input" id="ta" name="ta" defaultValue={course?.ta ?? ""} />
        </div>
      </div>
      <div>
        <label className="label" htmlFor="exam_type">סוג המבחן</label>
        <select className="input" id="exam_type" name="exam_type" defaultValue={course?.exam_type ?? ""}>
          <option value="">לא ידוע</option>
          <option value="mcq">אמריקאי</option>
          <option value="open">פתוח</option>
          <option value="mixed">משולב</option>
          <option value="none">ללא מבחן</option>
        </select>
      </div>
      <div>
        <label className="label" htmlFor="grade_weights">משקל בציון</label>
        <input className="input" id="grade_weights" name="grade_weights" defaultValue={weights} placeholder="בחינה 80%, מטלות 20%" />
      </div>
      <div>
        <label className="label" htmlFor="notes">הערות (חוקי מבחן, דף נוסחאות, דרישות...)</label>
        <textarea className="input min-h-24" id="notes" name="notes" defaultValue={course?.notes ?? ""} />
      </div>
      <button className="btn w-full">{submit}</button>
    </form>
  );
}
