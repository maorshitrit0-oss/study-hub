import CourseForm from "@/components/CourseForm";
import { createCourse } from "../../actions";

export default async function NewCourse({ searchParams }: PageProps<"/courses/new">) {
  const kind = (await searchParams).kind === "self" ? "self" : undefined;
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">קורס חדש</h1>
      <div className="card"><CourseForm action={createCourse} submit="יצירת קורס" defaultKind={kind} /></div>
    </div>
  );
}
