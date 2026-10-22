/** Developer credit, shown at the bottom of every screen. */
export default function Credit({ className = "" }: { className?: string }) {
  return (
    <p className={`text-center text-xs text-muted ${className}`}>
      Study Hub · פותח על ידי <span dir="ltr">Maor Shitrit</span>
    </p>
  );
}
