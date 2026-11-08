"""The formula sheet as a PDF to print (his request, 08/11/2026: "I want it as a PDF, updated all the time").
Markdown + LaTeX -> an A4 page (RTL, two columns, small print) rendered by Chromium with KaTeX -> PDF, saved next to the
markdown (formula_sheet.pdf) and listed in the course files. docs.save calls it after every change of the sheet.

  python sheet_pdf.py <sheet.md> <out.pdf> [course name]     (local: SHEET_ASSETS=<dir with katex files>)
"""
import html
import os
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import markdown

KATEX = os.environ.get("SHEET_ASSETS") or "https://cdn.jsdelivr.net/npm/katex@0.16.47/dist"
MATH = re.compile(r"\$\$(.+?)\$\$|\$(?!\s)([^$\n]+?)(?<!\s)\$", re.S)

CSS = """
@page { size: A4; margin: 8mm 7mm; }
* { box-sizing: border-box; }
html, body { width: 100%; overflow: hidden; }
body { font-family: Heebo, 'DejaVu Sans', Arial, sans-serif; font-size: 9.6pt; line-height: 1.22; color: #000;
       direction: rtl; margin: 0; }
header { display: flex; justify-content: space-between; border-bottom: 1.2px solid #000; padding-bottom: 1mm;
         margin-bottom: 1.5mm; font-size: 8.5pt; }
header b { font-size: 11.5pt; }
main { columns: 2; column-gap: 5mm; column-rule: 0.5px solid #999; width: 100%; }
main > * { max-width: 100%; }
main > table:first-of-type th:nth-child(1) { width: 45%; }
main > table:first-of-type th:nth-child(2) { width: 45%; }
main > table:first-of-type th:nth-child(3) { width: 10%; }
h1 { display: none; }
h2 { font-size: 10.8pt; margin: 2mm 0 0.8mm; padding: 0.4mm 1.5mm; background: #e6e6e6; border-right: 2.5px solid #000;
     break-after: avoid; }
h3 { font-size: 10pt; margin: 1.6mm 0 0.5mm; border-bottom: 0.6px solid #888; break-after: avoid; }
h4 { font-size: 8.4pt; margin: 1mm 0 0.3mm; break-after: avoid; }
p, li { margin: 0.4mm 0; }
ul, ol { margin: 0.3mm 0; padding-right: 4mm; }
table { border-collapse: collapse; width: 100%; table-layout: fixed; margin: 0.8mm 0; break-inside: avoid; font-size: 8.8pt; }
td, th { border: 0.5px solid #777; padding: 0.4mm 0.9mm; vertical-align: top; }
th { background: #eee; }
blockquote { margin: 0.8mm 0; padding: 0.4mm 1.5mm; border-right: 2px solid #555; background: #f5f5f5; }
code { font-size: 8.6pt; }
.katex { font-size: 1.0em; direction: ltr; unicode-bidi: isolate; }
.katex-display { margin: 0.6mm 0; break-inside: avoid; direction: ltr; text-align: center; }
.box { break-inside: avoid; }
"""


def to_html(md, course=""):
    """Math is kept out of the markdown converter (it would eat backslashes and underscores) and rendered by KaTeX."""
    md = re.sub(r"^> נבנה .*\n\n", "", md)
    keep = []

    def hide(m):
        keep.append(m.group(0))
        return f"⁣M{len(keep) - 1}⁣"
    body = markdown.markdown(MATH.sub(hide, md), extensions=["tables", "sane_lists"])
    body = re.sub("⁣M(\\d+)⁣", lambda m: html.escape(keep[int(m.group(1))]), body)
    today = datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%d/%m/%Y")
    return f"""<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;700&display=swap">
<link rel="stylesheet" href="{KATEX}/katex.min.css">
<script src="{KATEX}/katex.min.js"></script><script src="{KATEX}/contrib/auto-render.min.js"></script>
<style>{CSS}</style></head><body>
<header><span><b>📄 דף נוסחאות · {html.escape(course)}</b></span><span>בשם ה' נעשה ונצליח · עודכן {today}</span></header>
<main>{body}</main>
<script>
renderMathInElement(document.body, {{delimiters: [{{left: "$$", right: "$$", display: true}},
  {{left: "$", right: "$", display: false}}], throwOnError: false}});
// A formula wider than its column is scaled down to fit (never cut off) - after the fonts are in.
document.fonts.ready.then(() => {{
for (const k of document.querySelectorAll(".katex")) {{
  const box = k.closest(".katex-display") || k.closest("td, th, li, p, blockquote") || k.parentElement;
  const cs = getComputedStyle(box);
  const room = box.getBoundingClientRect().width - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight) - 2;
  const w = Math.max(k.getBoundingClientRect().width, k.scrollWidth);
  if (w > room && room > 0) k.style.fontSize = (0.97 * room / w) + "em";
}}
document.body.dataset.ready = "1"; }});
</script></body></html>"""


def render(md, course=""):
    """PDF bytes (Chromium through Playwright)."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Laid out at the printed width (A4 minus the margins), so the fit-to-column step measures the real columns.
        page = browser.new_page(viewport={"width": 740, "height": 1050})
        page.emulate_media(media="print")
        page.set_content(to_html(md, course), wait_until="networkidle")
        page.wait_for_selector("body[data-ready='1']", timeout=60000)
        pdf = page.pdf(format="A4", print_background=True, prefer_css_page_size=True)
        browser.close()
    return pdf


def publish(sb, course, md, bucket="study"):
    """formula_sheet.pdf next to the markdown + a row in the course files (once). Failing here never loses the sheet."""
    path = f"{course['user_id']}/materials/{course['id']}/formula_sheet.pdf"
    sb.storage.from_(bucket).upload(path, render(md, course.get("name") or ""),
                                    {"content-type": "application/pdf", "upsert": "true"})
    if not sb.table("materials").select("id").eq("storage_path", path).execute().data:
        sb.table("materials").insert({"user_id": course["user_id"], "course_id": course["id"], "title": "📄 דף נוסחאות (PDF להדפסה)",
                                      "kind": "other", "storage_path": path, "mime": "application/pdf"}).execute()
    print(f"::notice title=Formula sheet PDF::{course.get('name')}", flush=True)


if __name__ == "__main__":
    src = open(sys.argv[1], encoding="utf-8").read()
    if sys.argv[2].endswith(".html"):
        open(sys.argv[2], "w", encoding="utf-8").write(to_html(src, sys.argv[3] if len(sys.argv) > 3 else ""))
    else:
        open(sys.argv[2], "wb").write(render(src, sys.argv[3] if len(sys.argv) > 3 else ""))
