// Shown instantly on every navigation while the server renders the next page.
export default function Loading() {
  return (
    <div className="space-y-4 animate-pulse" aria-busy="true" aria-label="טוען">
      <div className="h-8 w-48 rounded-lg bg-line" />
      <div className="card h-28" />
      <div className="card h-40" />
      <div className="card h-24" />
    </div>
  );
}
