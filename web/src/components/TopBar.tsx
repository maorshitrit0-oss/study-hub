"use client";

import { usePathname, useRouter } from "next/navigation";

/** Top of every screen: the blessing on the right, a back button on the left (except on home). */
export default function TopBar() {
  const path = usePathname();
  const router = useRouter();
  const tabRoot = ["/", "/schedule", "/exams", "/courses", "/deadlines"].includes(path);
  return (
    <div className="flex items-center justify-between min-h-9 mb-2">
      <span className="text-sm font-medium text-accent">בשם ה&apos; נעשה ונצליח</span>
      {!tabRoot && (
        <button onClick={() => (window.history.length > 1 ? router.back() : router.push("/"))}
          className="flex items-center gap-1 text-sm text-accent px-2 py-1 -mx-2 rounded-lg active:bg-accent-soft" aria-label="חזרה">
          <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 18l6-6-6-6" />
          </svg>
          חזרה
        </button>
      )}
    </div>
  );
}
