import Link from "next/link";

/**
 * The way back, always in reach (his requests, 08/11/2026): a bar at the top that stays while scrolling, and the same
 * link as a floating button just above the bottom menu - so at the end of a long page he never scrolls back up.
 */
export default function BackLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <>
      <div className="sticky top-0 z-10 -mx-4 px-4 py-2 bg-[#06142a]/90 backdrop-blur-md border-b border-line print:hidden">
        <Link href={href} className="text-sm text-accent font-medium">{children}</Link>
      </div>
      <Link href={href} aria-label="חזרה"
        className="fixed z-30 left-3 bottom-[calc(4.75rem+env(safe-area-inset-bottom))] max-w-[60vw] truncate rounded-full border border-accent/60 bg-[#06142a]/95 px-4 py-2 text-sm font-medium text-accent shadow-lg backdrop-blur-md print:hidden">
        {children}
      </Link>
    </>
  );
}
