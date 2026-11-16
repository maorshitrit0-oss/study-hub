import ZoomReceiver from "@/components/ZoomReceiver";
import { headers } from "next/headers";
import { zoomBookmarklet } from "@/lib/zoomBookmarklet";

/**
 * Zoom transcript -> lesson (16/11/2026). Opened by the bookmarklet with ?src=<recording link>; without it, the page
 * explains how to install the bookmarklet.
 */
export default async function ZoomPage({ searchParams }: { searchParams: Promise<{ src?: string }> }) {
  const { src } = await searchParams;
  const h = await headers();
  const app = `https://${h.get("host")}`;
  if (src) return <div className="space-y-4"><h1 className="text-2xl font-bold">📋 תמלול מזום</h1><ZoomReceiver /></div>;
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">📋 תמלול זום לאפליקציה</h1>
      <section className="card space-y-2 text-sm">
        <p className="font-semibold">🧩 הכי פשוט: התוסף לכרום (התמלול נשלח לבד כשפותחים הקלטה)</p>
        <ol className="list-decimal ps-5 space-y-1">
          <li><a href="/studyhub-zoom.zip" className="text-accent underline">להוריד את התוסף</a> ולחלץ את הקובץ (קליק ימני ← חלץ הכל).</li>
          <li>בכרום לפתוח את <b dir="ltr">chrome://extensions</b> ולהדליק למעלה מימין <b>Developer mode</b> (מצב מפתח).</li>
          <li>ללחוץ <b>Load unpacked</b> ולבחור את התיקייה שחולצה.</li>
        </ol>
        <p>מעכשיו: להדביק את קישור הזום בשיעור כרגיל, ואחרי שהעיבוד נכשל – פשוט לפתוח את ההקלטה מהמודל. אחרי כחצי דקה נפתחת
          לשונית של האפליקציה והשיעור נכתב. (צריך להיות מחובר לאפליקציה בכרום.)</p>
      </section>
      <section className="card space-y-2 text-sm">
        <p className="font-semibold">או: סימנייה (בלי להתקין כלום)</p>
        <p><b>פעם אחת (במחשב):</b> לגרור את הכפתור הכחול לסרגל הסימניות של הדפדפן (אם הסרגל מוסתר: Ctrl+Shift+B).</p>
        {/* React blocks javascript: hrefs, so the bookmark link is written as raw HTML */}
        <div dangerouslySetInnerHTML={{ __html: `<a href="${zoomBookmarklet(app).replace(/"/g, "%22")}" class="btn inline-block">📋 תמלול זום לאפליקציה</a>` }} />
        <p><b>בכל הקלטה:</b> להדביק את קישור הזום בשיעור כרגיל. כשהעיבוד נכשל – לפתוח את ההקלטה בזום, לפתוח את חלונית Transcript
          מימין, וללחוץ על הסימנייה. היא גוללת את כל התמלול לבד (חצי דקה), פותחת את האפליקציה ושולחת אותו לשיעור הנכון.
          הפרק, המתומצת, השאלון והתרגילים נכתבים ממנו.</p>
        <p className="text-muted">צריך להיות מחובר לאפליקציה באותו דפדפן.</p>
      </section>
    </div>
  );
}
