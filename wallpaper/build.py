"""iPad wallpaper of his week: the timetable with each course's grade, exam and formula sheet (04/11/2026)."""
import json, sys
W, H = int(sys.argv[2]), int(sys.argv[3])
d = json.load(open(sys.argv[1], encoding="utf-8"))
names = {c["id"]: c["name"] for c in d["courses"]}
# What each lecture box says (from the course info in the app; Java grade corrected from practice 2:
# assignments are practice only, 20% is the mini-project).
INFO = {
 "גלים ומערכות מפולגות": ["100% מבחן · פתוח", "דף נוסחאות: 2 עמודים (דף דו-צדדי)", "מבחן: 12/1/27"],
 "מבוא למערכות תקשורת": ["100% מבחן · פתוח, בכתב יד", "90 דק׳ · 2 שאלות", "דף נוסחאות: 2 דפים + טבלאות שיינתנו", "מבחן: 2/2/27"],
 "מעבדה 2": ["45% מעשי סוף · 10% מעשי אמצע", "20% בוחני כניסה · 10% דוח מסכם", "10% עלייה ללוח · 5% התרשמות"],
 "מעגלים ספרתיים": ["100% מבחן", "אמריקאי במחשב · ~11 שאלות · באנגלית", "מבחן: 25/1/27"],
 "מונחה עצמים בשפת Java": ["80% מבחן · 20% מיני-פרויקט", "מבחן אמריקאי", "דף עזר: דף אחד", "מבחן: 17/1/27"],
 "מיקרו מעבדים": ["100% מבחן", "פתוח · תיאורטי", "מבחן: 18/1/27"],
 "מעגלים לינאריים": ["90% מבחן · 10% תרגילי בית", "אמריקאי · 90 דק׳ · בכיתה", "דף נוסחאות: מותר", "מבחן: 19/1/27", "נוכחות חובה בהרצאות"],
}
SHORT = {"מונחה עצמים בשפת Java": "Java · מונחה עצמים", "גלים ומערכות מפולגות": "גלים ומערכות מפולגות"}
COLORS = {"גלים ומערכות מפולגות": "#3db4ff", "מבוא למערכות תקשורת": "#b48cff", "מעבדה 2": "#f5b94a",
          "מעגלים ספרתיים": "#3ddc97", "מונחה עצמים בשפת Java": "#ff8a5c", "מיקרו מעבדים": "#ff6b9a",
          "מעגלים לינאריים": "#5ce1e6"}
KIND = {"lecture": "הרצאה", "practice": "תרגול", "lab": "מעבדה", "other": ""}
DAYS = ["ראשון", "שני", "שלישי", "רביעי", "חמישי"]
START, END = 8, 22
top, bottom = 200, 120
hour = (H - top - bottom) / (END - START)
left_pad, time_w, right_pad = 40, 90, 40
col = (W - left_pad - right_pad - time_w) / 5

def hm(t):
    h, m = t.split(":")[:2]
    return int(h) + int(m) / 60

boxes = []
for s in d["slots"]:
    if s["weekday"] > 4:
        continue
    name = names.get(s["course_id"], s.get("title") or "")
    a, b = hm(s["start_time"]), hm(s["end_time"])
    y = top + (a - START) * hour
    h = (b - a) * hour
    # RTL: Sunday on the right, the time column on the far right.
    x = W - right_pad - time_w - (s["weekday"] + 1) * col
    color = COLORS.get(name, "#8fa6c0")
    info = INFO.get(name, []) if s["kind"] in ("lecture", "lab") else []
    lines = "".join(f"<div class='i'>{t}</div>" for t in info)
    boxes.append(f"""<div class='box' style='left:{x+6:.0f}px;top:{y+3:.0f}px;width:{col-12:.0f}px;height:{h-6:.0f}px;border-color:{color};background:{color}22'>
<div class='n' style='color:{color}'>{SHORT.get(name, name)}</div><div class='k'>{KIND.get(s['kind'],'')} · <span dir='ltr'>{s['start_time'][:5]}–{s['end_time'][:5]}</span></div>{lines}</div>""")

grid = []
for hr in range(START, END + 1):
    y = top + (hr - START) * hour
    grid.append(f"<div class='hl' style='top:{y:.0f}px;left:{left_pad}px;width:{W-left_pad-right_pad}px'></div>")
    if hr < END:
        grid.append(f"<div class='t' style='top:{y+4:.0f}px;right:{right_pad}px;width:{time_w-10}px'>{hr:02d}:00</div>")
for i, day in enumerate(DAYS):
    x = W - right_pad - time_w - (i + 1) * col
    grid.append(f"<div class='dh' style='left:{x:.0f}px;width:{col:.0f}px;top:{top-52}px'>{day}</div>")
    grid.append(f"<div class='vl' style='left:{x:.0f}px;top:{top-10}px;height:{H-top-bottom+10:.0f}px'></div>")

html = f"""<!doctype html><html dir='rtl'><head><meta charset='utf-8'>
<link href='https://fonts.googleapis.com/css2?family=Heebo:wght@400;600;800&display=block' rel='stylesheet'>
<style>
*{{margin:0;box-sizing:border-box}}
body{{width:{W}px;height:{H}px;overflow:hidden;font-family:Heebo,'Liberation Sans',sans-serif;color:#e4eef9;
background:radial-gradient(ellipse at 20% 0%,#0d2a4d 0%,#050e1c 55%) ,#050e1c;position:relative}}
.top{{position:absolute;top:28px;width:100%;text-align:center;font-size:30px;color:#8fa6c0;letter-spacing:1px}}
h1{{position:absolute;top:66px;width:100%;text-align:center;font-size:56px;font-weight:800}}
.hl{{position:absolute;height:1px;background:rgba(80,150,220,.18)}}
.vl{{position:absolute;width:1px;background:rgba(80,150,220,.18)}}
.t{{position:absolute;font-size:22px;color:#8fa6c0;text-align:left}}
.dh{{position:absolute;text-align:center;font-size:34px;font-weight:600}}
.box{{position:absolute;border:3px solid;border-radius:18px;padding:10px 14px;overflow:hidden}}
.n{{font-size:28px;font-weight:800;line-height:1.15}}
.k{{font-size:20px;color:#b9cbe0;margin:2px 0 6px}}
.i{{font-size:21px;line-height:1.35}}
.foot{{position:absolute;bottom:34px;width:100%;text-align:center;font-size:24px;color:#8fa6c0}}
</style></head><body>
<div class='top'>בשם ה' נעשה ונצליח</div>
<h1>מערכת שעות · סמסטר א׳ תשפ״ז</h1>
{''.join(grid)}{''.join(boxes)}
<div class='foot'>🎓 לימוד VLSI: שישי <span dir='ltr'>10:00–12:00</span> · מוצ״ש <span dir='ltr'>20:30–22:00</span> &nbsp;&nbsp;|&nbsp;&nbsp; פותח על ידי Maor Shitrit</div>
</body></html>"""
open(sys.argv[4], "w", encoding="utf-8").write(html)
