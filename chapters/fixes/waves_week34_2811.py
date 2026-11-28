"""Waves weeks 3-4 (28/11/2026, study order).
- c5ef4b9c (lecture-3 summary, slab): wording and final answer compared with the summary pages 42-49 - identical.
- 812f92a7 (sheet 4 Q7): sheet's key compared. 7.1-7.5 agree. 7.6 key 0.229 W/m^2 = |E_t|^2/eta_2 without the 1/2
  of the time average (7.44^2/238.4 = 0.232); the average is 0.116. E_i0 = 3.46x - 3z on the sheet is a typo
  (k.E != 0; the key itself uses E_r0 = 4 = |3.46x - 2z|). Writes chapters/fix_2811_waves_w34.json."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SP = Path("/tmp/claude-0/-home-user-study-hub/07493fa9-fb63-5beb-830d-81523c08fa4e/scratchpad")
OLD1 = "\n\n> 🔎 נבדק מחדש (28/11): כל שלב והתוצאה נבדקו ונמצאו נכונים."
OLD2 = "\n\n> 🔎 נבדק מחדש (28/11): נפתר מחדש במלואו; כל המספרים חושבו מחדש."
OK = "\n\n> 🔎 נבדק מחדש (28/11): הושווה למקור ולתשובה הסופית שבו."


def main():
    xs = {x["id"][:8]: x for x in json.loads((SP / "w_all.json").read_text(encoding="utf-8"))}
    out = []
    x = xs["c5ef4b9c"]
    sol = x["solution_md"].replace(OLD1, "").replace(
        "> ⚠️ נוסח השאלה נלקח מקובץ הרצאה 3 (מצגת סרוקה) ועוד לא הושווה מילה במילה לשקף. הפתרון נבדק מאפס.",
        "> ✔ הנוסח והתשובה הסופית $\\Gamma=\\frac{1-\\varepsilon_r}{1+\\varepsilon_r}$ זהים לסיכום של הרצאה 3 (\"החזרה ומעבר בלוח דיאלקטרי – גישת עכבת כניסה\").")
    out.append({"id": x["id"], "title": x["title"], "solution_md": sol.rstrip() + OK, "uncertain": False})
    x = xs["812f92a7"]
    sol = x["solution_md"].replace(OLD2, "").replace(
        "> ⚠️ בפתרון הקודם נכתב $0.229$ – לא מתקבל מאף גרסה של הנתונים (גם לא עם $E_{i0}=4.58$ או קיטוב TE). לבדוק מול הפתרון הרשמי.",
        "> ⚠️ בתשובות הסופיות של הדף: $P_t'=0.229\\ \\frac{\\text{W}}{\\text{m}^2}$. זה בערך $\\frac{E_{t0}^2}{\\eta_2}=\\frac{7.44^2}{238.4}=0.232$ – **בלי** ה-$\\frac12$ של ההספק הממוצע. "
        "צפיפות ההספק הממוצעת היא $\\frac{E_{t0}^2}{2\\eta_2}=0.116$, ורק היא מקיימת את בדיקת השימור למעלה. שאר התשובות (7.1–7.5: $\\theta_r=30^\\circ$, $f=106\\text{ MHz}$, $\\lambda_1=1\\text{ m}$, $\\vec k_r=\\pi(\\hat x-1.73\\hat z)$, $E_{r0}=4$, $P_t=0$) זהות לדף.")
    out.append({"id": x["id"], "title": x["title"], "solution_md": sol.rstrip() + OK, "uncertain": False})
    (HERE.parent / "fix_2811_waves_w34.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(len(out), "exercises", [("✔" in o["solution_md"], "0.232" in o["solution_md"]) for o in out])


if __name__ == "__main__":
    main()
