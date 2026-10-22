import { notFound } from "next/navigation";
import CourseForm from "@/components/CourseForm";
import { requireUser } from "@/lib/supabase/server";
import { deleteCourse, setArchived, updateCourse } from "../../../actions";
import type { Course } from "@/lib/types";

export default async function EditCourse({ params }: PageProps<"/courses/[id]/edit">) {
  const { id } = await params;
  const { sb } = await requireUser();
  const { data } = await sb.from("courses").select("*").eq("id", id).maybeSingle();
  if (!data) notFound();
  const course = data as Course;
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">עריכת {course.name}</h1>
      <div className="card"><CourseForm action={updateCourse.bind(null, id)} course={course} submit="שמירה" /></div>
      <div className="card space-y-3">
        <form action={setArchived.bind(null, id, !course.archived)}>
          <button className="btn-ghost w-full">{course.archived ? "החזרה מהארכיון" : "העברה לארכיון (הקורס הסתיים)"}</button>
        </form>
        <form action={deleteCourse.bind(null, id)}>
          <button className="w-full text-bad text-sm py-2">מחיקת הקורס וכל התוכן שלו</button>
        </form>
      </div>
    </div>
  );
}
