import Link from "next/link";

/**
 * The way back, always in reach (his requests, 08/11/2026): a bar at the top that stays while scrolling, and the same
 * link as a floating button just above the bottom menu - so at the end of a long page he never scrolls back up.
 */
export default function BackLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <>
      <div className="sticky top-0 z-10 -mx-4 px-4 py-2 bg-[#06142a] border-b border-line print:hidden">
        <Link href={href} className="text-sm text-accent font-medium">{children}</Link>
      </div>
      <Link href={href} aria-label="חזרה"
        className="fixed z-30 left-3 bottom-[calc(4.75rem+env(safe-area-inset-bottom))] grid h-10 w-10 place-items-center rounded-full border border-accent/60 bg-[#06142a]/90 text-lg text-accent shadow-lg [transform:translateZ(0)] [will-change:transform] print:hidden">
        {/* a small round button: the long pill covered the text it floated over (his screenshot 11/11/2026) */}
        →
      </Link>
    </>
  );
}
