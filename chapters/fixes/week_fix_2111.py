"""Saturday 21/11/2026: (1) linear week 2 - the two lecture-2 examples deleted when lecture 2 was re-authored (before
keep_exercises) come back, written the explained way; (2) digital week 5 - the TA notebook's V_OL question as multiple
choice. -> chapters/week-fix-2111-{linear,digital}.json (publish inspect=exercises)."""
import json
from pathlib import Path

from linear_explained_2011 import W2, mcq

lin = []
for e in W2:
    if e["id"].startswith(("b27aa2be", "9f29e3c8")):
        x = {k: v for k, v in e.items() if k != "id"}
        x.update(add=True, kind="lecture", number=2, week=2,
                 title="חקירת אופיין תמסורת לא ליניארי של טרנזיסטור" if e["id"].startswith("b27") else "ניתוח שרשור מגברים (Cascade)")
        lin.append(x)

dig = mcq("7aa11f21-c5ed-4aee-a6cc-cbdd12c78ec1",
          "מהפך CMOS עם $V_{DD}=5V$ ובלי עומס במוצא. מה $V_{OL}$ כש-$V_{in}=5V$, ולמה?",
          ["$V_{OL}=0V$ – ה-PMOS בקטעון וה-NMOS מחבר את המוצא לאדמה, ואין זרם", "$V_{OL}=V_t$ – נשאר מפל של מתח סף",
           "$V_{OL}=2.5V$ – שני הטרנזיסטורים פתוחים", "$V_{OL}$ תלוי ביחס בין רוחבי הטרנזיסטורים, כמו במהפך עם נגד"], 0,
          r"""- **מהפך CMOS** (הרצאה 5): כניסה גבוהה ⇐ ה-PMOS ($V_{GS,p}=0$) **בקטעון**, ה-NMOS פתוח.
- אין זרם במצב יציב ⇐ אין מפל מתח על ה-NMOS.""",
          r"""**1. ה-PMOS:** $V_{GS,p}=V_{in}-V_{DD}=5-5=0$ ⇐ קטעון ⇐ לא מספק זרם.

**2. ה-NMOS:** $V_{GS,n}=V_{in}=5V>V_t$ ⇐ פתוח (טריודה).

**3. זרם:** אין מקור זרם מלמעלה ⇐ $I_D=0$ ⇐ המפל על ה-NMOS אפס.

**4. תוצאה:** $V_{OL}=0\,V$ – נדנוד מלא, בלי תלות ביחס הרוחבים (בניגוד למהפך עם נגד או עם עומס).""",
          {1: "מפל של $V_t$ יש במוצא הגבוה של עומס בחיבור דיודה, לא כאן.", 2: "שניהם פתוחים רק במעבר, סביב $V_{DD}/2$.", 3: "ב-CMOS אין זרם סטטי, ולכן $V_{OL}$ לא תלוי ביחס."},
          "ב-CMOS הנמוך הוא אדמה והגבוה הוא $V_{DD}$ – כי במצב יציב אין זרם.")
dig["topic"] = "מהפך CMOS"

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    (root / "week-fix-2111-linear.json").write_text(json.dumps(lin, ensure_ascii=False, indent=1), encoding="utf-8")
    (root / "week-fix-2111-digital.json").write_text(json.dumps([dig], ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(lin), 1)
