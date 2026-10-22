"use client";

/** Last resort when even the main layout fails: plain page with the error text and a way back. */
export default function GlobalError({ error }: { error: Error & { digest?: string } }) {
  return (
    <html lang="he" dir="rtl">
      <body style={{ background: "#071a33", color: "#e6e9f2", fontFamily: "system-ui", padding: 24 }}>
        <p style={{ color: "#7cc4ff" }}>בשם ה&apos; נעשה ונצליח</p>
        <h1>משהו השתבש</h1>
        <p>טעינה מחדש בדרך כלל מסדרת את זה. אם זה חוזר - צלם את המסך ושלח ל-Claude.</p>
        <p dir="ltr" style={{ fontSize: 12, opacity: 0.7 }}>{error.message}{error.digest ? ` · ${error.digest}` : ""}</p>
        {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
        <a href="/" style={{ color: "#7cc4ff" }}>טעינה מחדש</a>
        <p style={{ fontSize: 12, opacity: 0.6 }}>Study Hub · פותח על ידי Maor Shitrit</p>
      </body>
    </html>
  );
}
