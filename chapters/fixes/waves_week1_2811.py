"""Waves week 1 (28/11/2026, his order: waves first, in study order).
- L1 class exercise 93c7e01d: solution stored with literal "\\n" (shown as text) - newlines restored, content checked.
- Sheet 1 Q3 (chiral medium, d6580bc6): resolved. The sheet itself uses e^{-jwt} (its Q1 writes e^{j(-wt+...)});
  with that convention and D = eps E + j xi B the derivation gives exactly the sheet's +2 w mu xi curl E.
- Sheet 1 Q4 (af6d8cbf): boundary conditions re-derived; the sheet's printed key contradicts them (z-current cannot
  change H_z) - the correct result stays, the note stays, flag cleared (the physics is certain).
Writes chapters/fix_2811_waves_w1.json."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SP = Path("/tmp/claude-0/-home-user-study-hub/07493fa9-fb63-5beb-830d-81523c08fa4e/scratchpad")
OLD = "\n\n> 🔎 נבדק מחדש (28/11): כל שלב והתוצאה נבדקו ונמצאו נכונים."
OK = "\n\n> 🔎 נבדק מחדש (28/11): כל שלב והתוצאה נבדקו ונמצאו נכונים."

SIGN = r"""### הסימן של האיבר האחרון – המוסכמה של הדף
בדף העבודה הזה הגלים כתובים כ-$e^{j(-\omega t+\dots)}$ (ראו שאלה 1 באותו דף) – כלומר המוסכמה $e^{-j\omega t}$. אז:
$$\nabla\times\tilde E=j\omega\tilde B,\qquad\nabla\times\tilde H=-j\omega\tilde D$$
חוזרים על אותם שלבים:
- $\tilde B=-\frac{j}{\omega}\nabla\times\tilde E$ ⇐ $\tilde H=-\frac{j}{\omega\mu}\nabla\times\tilde E+j\xi\tilde E$, $\tilde D=\varepsilon\tilde E+\frac{\xi}{\omega}\nabla\times\tilde E$.
- מציבים באמפר ומכפילים ב-$j\omega\mu$:
$$\nabla\times\nabla\times\tilde E-\omega\mu\xi\nabla\times\tilde E=k^2\tilde E+\omega\mu\xi\nabla\times\tilde E$$
- עם $\nabla\times\nabla\times\tilde E=-\nabla^2\tilde E$:
$$\boxed{\nabla^2\tilde E+k^2\tilde E+2\omega\mu\xi\,\nabla\times\tilde E=0}$$
✅ בדיוק הביטוי שבדף. (במוסכמה ההנדסית $e^{j\omega t}$ יוצא אותו דבר עם מינוס – זה רק סימן הזמן.)

> ⚠️ מה שנשאר מהנוסח: בדף כתוב $j\xi\tilde H$ בקשר של $\tilde D$; כך היחידות לא מסתדרות והתוצאה לא יוצאת. עם $j\xi\tilde B$ (הצורה המקובלת לתווך כירלי) – יוצאת בדיוק."""


def main():
    xs = {x["id"][:8]: x for x in json.loads((SP / "w_all.json").read_text(encoding="utf-8"))}
    out = []
    x = xs["93c7e01d"]
    sol = re.sub(r"\n{3,}", "\n\n", x["solution_md"].replace("\\n", "\n")).strip()
    out.append({"id": x["id"], "title": x["title"], "solution_md": sol + OK, "uncertain": False})
    x = xs["d6580bc6"]
    sol = x["solution_md"].replace(OLD, "")
    i, j = sol.index("### על הסימן של האיבר האחרון"), sol.index("💡 **הרעיון:**")
    sol = sol[:i] + SIGN + "\n\n" + sol[j:]
    out.append({"id": x["id"], "title": x["title"], "solution_md": sol.rstrip() + OK, "uncertain": False})
    x = xs["af6d8cbf"]
    sol = x["solution_md"].replace(OLD, "").replace("**לשאול את המתרגל לפני המבחן.**",
          "במבחן כותבים את מה שיוצא מתנאי השפה (כמו כאן) – אפשר לציין שזה לא תואם את הדף.")
    out.append({"id": x["id"], "title": x["title"], "solution_md": sol.rstrip() + OK, "uncertain": False})
    (HERE.parent / "fix_2811_waves_w1.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(len(out), "exercises")


if __name__ == "__main__":
    main()
