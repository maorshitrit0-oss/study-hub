import Link from "next/link";

/** Switch between self-study tracks, staying on the same kind of page (map or tutor). */
export default function TrackTabs({ tracks, current, suffix = "" }: { tracks: { id: string; name: string }[]; current: string; suffix?: string }) {
  if (tracks.length < 2) return null;
  return (
    <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
      {tracks.map((t) => (
        <Link key={t.id} href={`/self/${t.id}${suffix}`}
          className={`chip whitespace-nowrap py-1.5 px-3 ${t.id === current ? "!bg-accent !text-white" : ""}`}>
          {t.name.replace(/^Cadence · /, "Cadence: ")}
        </Link>
      ))}
    </div>
  );
}
