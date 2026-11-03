"use client";

/** Print / save as PDF (iPhone: Share -> Print -> pinch out -> Share -> Save to Files). */
export default function PrintButton() {
  return (
    <div className="flex items-center gap-3 flex-wrap">
      <button type="button" className="btn" onClick={() => window.print()}>🖨️ הדפסה / שמירה כ-PDF</button>
      <span className="text-xs text-muted">באייפון: שיתוף ← הדפסה ← לפתוח את התצוגה בשתי אצבעות ← שיתוף ← שמירה בקבצים</span>
    </div>
  );
}
