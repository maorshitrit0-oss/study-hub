import Link from "next/link";

/**
 * "→ the course" that stays at the top of the screen while scrolling (08/11/2026: at the end of a long lesson he had
 * to scroll all the way up to get back to the course).
 */
export default function BackLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <div className="sticky top-0 z-10 -mx-4 px-4 py-2 bg-[#06142a]/90 backdrop-blur-md border-b border-line print:hidden">
      <Link href={href} className="text-sm text-accent font-medium">{children}</Link>
    </div>
  );
}
