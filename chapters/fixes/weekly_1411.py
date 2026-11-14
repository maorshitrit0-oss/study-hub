"""Weekly check of the exercise sets, 14/11/2026 (the Saturday core task, now on the week sets of weekset.py).
- Restores the verified solutions of the practices Claude wrote (digital 2-4, linear 1-2, comm 1-2): the automatic
  "reformat" pass of exercises.py had rewritten them and cut them after the first steps (now guarded).
- Fixes picked exercises whose numbers were wrong (re-solved in Python): waves TM practice (θi 47.3°, not 31.3°) and
  the TM exam question (E_t0 = 230.9 V/m, not 163.3), comm exam Q1 (NF = 23.0 dB, not 25), comm cascade practice
  (full steps), comm DSB SNR practice (σ² = 2N0B).
- Java week 4 (static, pass by value / reference, scope) had no practice exercise (Java lectures are full chapters):
  4 new ones, each output checked by running the code.
  python weekly_1411.py -> chapters/weekly-1411-<course>.json (publish inspect=exercises)"""
import json
from pathlib import Path

CH = Path(__file__).resolve().parents[1]


def restore(files):
    out = []
    for kind, n, f in files:
        for x in json.loads((CH / f).read_text(encoding="utf-8"))["exercises"]:
            out.append({"kind": kind, "number": n, "find": x["title"], "title": x["title"],
                        "question_md": x["question_md"], "solution_md": x["solution_md"]})
    return out


WAVES = [
    {"id": "8c561610-3ea8-43a2-b76e-26c3bc9366e0", "solution_md": r"""**שלב 1 – זווית ההעברה מהכיוון של הגל העובר:** $\hat k_t=\sin\theta_t\,\hat x+\cos\theta_t\,\hat z$.

**נוסחה:** $$\sin\theta_t=0.6,\quad \cos\theta_t=0.8$$

**תוצאה:** $$\theta_t=36.87^\circ$$

**שלב 2 – זווית הפגיעה (סנל):**

**נוסחה:** $$\sqrt{\varepsilon_{r1}}\sin\theta_i=\sqrt{\varepsilon_{r2}}\sin\theta_t$$

**הצבה:** $$\sin\theta_i=\frac{\sqrt3\cdot0.6}{\sqrt2}=0.735$$

**תוצאה:** $$\theta_i=\theta_r\approx47.3^\circ$$

> ⚠️ תוקן: בפתרון הקודם יצא $31.3^\circ$ – טעות בהצבה. $\sin\theta_i$ חייב להיות גדול מ-$\sin\theta_t$ כי עוברים לתווך צפוף יותר.

**שלב 3 – עכבות:** $$\eta_1=\frac{120\pi}{\sqrt2}\approx266.6\,\Omega,\qquad \eta_2=\frac{120\pi}{\sqrt3}\approx217.7\,\Omega$$

**שלב 4 – משרעת הגל העובר מההספק:**

**נוסחה:** $$P_t=\frac{|E_{t0}|^2}{2\eta_2}$$

**תוצאה:** $$E_{t0}=\sqrt{2\cdot217.7\cdot100}\approx208.6\,V/m$$

**שלב 5 – מקדמי TM:**

**נוסחה:** $$\Gamma_\parallel=\frac{\eta_2\cos\theta_t-\eta_1\cos\theta_i}{\eta_2\cos\theta_t+\eta_1\cos\theta_i},\qquad T_\parallel=(1+\Gamma_\parallel)\frac{\cos\theta_i}{\cos\theta_t}$$

**הצבה:** $$\eta_2\cos\theta_t=174.1,\quad \eta_1\cos\theta_i=180.7$$

**תוצאה:** $$\Gamma_\parallel\approx-0.019,\qquad T_\parallel\approx0.832$$

**שלב 6 – משרעות:** $$E_{i0}=\frac{E_{t0}}{T_\parallel}\approx250.8\,V/m,\qquad E_{r0}=\Gamma_\parallel E_{i0}\approx-4.7\,V/m$$ ✅

**בדיקה (שימור אנרגיה בניצב לממשק):** $P_i\cos\theta_i=118\cdot0.678=80.0$, ו-$P_r\cos\theta_i+P_t\cos\theta_t\approx0.03+80=80.0$ ✅

💡 **הרעיון:** $\Gamma$ כמעט אפס כי $47.3^\circ$ קרובה לזווית ברוסטר ($\arctan\sqrt{3/2}=50.8^\circ$) – שם בקיטוב TM אין החזרה בכלל."""},
    {"id": "b751881a-baba-451b-b113-0128ac1fc128", "solution_md": r"""### 5.1 – זוויות
$\hat k_t=0.6\hat x+0.8\hat z$ ⇐ $\sin\theta_t=0.6$, $\cos\theta_t=0.8$ ⇐ $$\theta_t=36.87^\circ$$

**סנל:** $$\sqrt4\sin\theta_i=\sqrt2\cdot0.6\;\Rightarrow\;\sin\theta_i=0.424\;\Rightarrow\;\theta_i=\theta_r\approx25.1^\circ$$ ✅

### 5.2 – משרעות
**עכבות:** $$\eta_1=\frac{120\pi}{2}=188.5\,\Omega,\qquad \eta_2=\frac{120\pi}{\sqrt2}=266.6\,\Omega$$

**הגל העובר:** $$E_{t0}=\sqrt{2\eta_2P_t}=\sqrt{2\cdot266.6\cdot100}=\sqrt{53314}\approx230.9\,V/m$$

> ⚠️ תוקן: בפתרון הקודם $\sqrt{53314}$ חושב כ-163.3 – טעות. $\sqrt{53314}\approx230.9$, וכל המשרעות שאחריו תוקנו.

**מקדמי TM:** $$\Gamma_\parallel=\frac{\eta_2\cos\theta_t-\eta_1\cos\theta_i}{\eta_2\cos\theta_t+\eta_1\cos\theta_i}=\frac{213.3-170.7}{213.3+170.7}\approx0.111$$

$$T_\parallel=(1+\Gamma_\parallel)\frac{\cos\theta_i}{\cos\theta_t}=1.111\cdot\frac{0.9055}{0.8}\approx1.257$$

**תוצאה:** $$E_{i0}=\frac{230.9}{1.257}\approx183.6\,V/m,\qquad E_{r0}=0.111\cdot183.6\approx20.4\,V/m,\qquad E_{t0}\approx230.9\,V/m$$ ✅

### 5.3 – השדה המגנטי המועבר
ב-TM השדה המגנטי בכיוון $\hat y$: $$H_{t0}=\frac{E_{t0}}{\eta_2}=\frac{230.9}{266.6}\approx0.866\,A/m$$

$$k_2=\frac{2\pi f\sqrt{\varepsilon_{r2}}}{c}=\frac{2\pi\cdot10^9\cdot\sqrt2}{3\cdot10^8}\approx29.62\,rad/m$$

$$\vec h_t=0.866\cos\left(2\pi\cdot10^9t-29.62(0.6x+0.8z)\right)\hat y\;[A/m]$$

**בנקודה $x=1,\ z=10$ ו-$t=1\,ns$:** הפאזה $2\pi-29.62\cdot8.6\approx-248.45\,rad$ ⇐ $\cos\approx-0.967$ ⇐ $$\vec h_t\approx-0.84\,\hat y\;A/m$$ ✅

### 5.4 – הספק הגל החוזר
$$P_i=\frac{E_{i0}^2}{2\eta_1}=\frac{183.6^2}{377}\approx89.4\,W/m^2,\qquad P_r=|\Gamma_\parallel|^2P_i\approx1.10\,W/m^2$$ ✅

**בדיקה:** $P_i\cos\theta_i=80.9$ ו-$P_r\cos\theta_i+P_t\cos\theta_t=1.0+80=81.0$ ✅

💡 **הרעיון:** בפגיעה אלכסונית האנרגיה נשמרת ברכיב הניצב לממשק – זו בדיקה מהירה לכל התשובות."""},
]

COMM = [
    {"id": "e862c8ca-2127-49fc-ba74-53b634768643", "solution_md": r"""**שלב 1 – כל רכיב בליניארי** (למנחת: $G=1/L$ ו-$F=L$):

| רכיב | ב-dB | $G$ | $F$ |
|---|---|---|---|
| מנחת 1: $0.2\cdot50$ | 10 dB | 0.1 | 10 |
| מגבר 1 | 30 dB, F=10 dB | 1000 | 10 |
| מנחת 2: $0.2\cdot100$ | 20 dB | 0.01 | 100 |
| מגבר 2 | 33 dB, F=20 dB | 1995 | 100 |

**שלב 2 – הגבר כולל (ב-dB מחברים):** $$G=-10+30-20+33=33\,dB\approx2\cdot10^3$$ ✅

**שלב 3 – פריס:**

**נוסחה:** $$F=F_1+\frac{F_2-1}{G_1}+\frac{F_3-1}{G_1G_2}+\frac{F_4-1}{G_1G_2G_3}$$

**הצבה:** $$F=10+\frac{9}{0.1}+\frac{99}{0.1\cdot1000}+\frac{99}{0.1\cdot1000\cdot0.01}=10+90+0.99+99=200$$

**תוצאה:** $$NF=10\log_{10}200\approx23.0\,dB$$ ✅

> ⚠️ תוקן: בפתרון הקודם נכתב 25 dB. החישוב נותן $200$ ⇐ $23.0\,dB$. (המנחת האחרון שבאיור – אם יש לו הפסד, הוא מתווסף כאיבר חמישי ומתחלק ב-$G_1G_2G_3G_4=200$, כלומר כמעט לא משנה.)

💡 **הרעיון:** המנחת שלפני המגבר הראשון "מכפיל" את הרעש של המגבר פי 10 (90 מתוך 200!) – לכן שמים LNA ליד האנטנה."""},
    {"id": "ba6e02b7-639d-4f6f-a6bc-5c1a8b531e60", "solution_md": r"""**שלב 1 – הפסדי הכבלים:** $$L_1=0.2\cdot50=10\,dB,\qquad L_2=0.2\cdot95=19\,dB$$

**שלב 2 – הגבר כולל:** $$G=-10+30-19+42=43\,dB$$ ✅

**שלב 3 – הכל לליניארי:**

| רכיב | $G$ | $F$ |
|---|---|---|
| כבל 10 dB | 0.1 | 10 |
| מגבר (30 dB, F=3 dB) | 1000 | 2 |
| כבל 19 dB | 0.0126 | 79.4 |
| מגבר (42 dB, F=20 dB) | 15849 | 100 |

**שלב 4 – פריס:**
$$F=10+\frac{2-1}{0.1}+\frac{79.4-1}{0.1\cdot1000}+\frac{100-1}{0.1\cdot1000\cdot0.0126}$$
$$F=10+10+0.78+78.6\approx99.4$$

**תוצאה:** $$NF=10\log_{10}99.4\approx20.0\,dB$$ ✅

💡 **הרעיון:** שני "מזיקים" גדולים: הכבל הראשון (10) והמגבר האחרון שבא אחרי כבל של 19 dB (78.6) – כי ההגבר המצטבר לפניו הוא רק $1.26$."""},
    {"id": "a9d7f454-d68e-448f-84f7-12fadec297c3", "solution_md": r"""### סעיף 1 – הספק האות במוצא
אחרי המכפל וה-LPF: $s_o(t)=\tfrac12x(t)\cos\theta$, ולכן
$$S_o=\tfrac14\overline{x^2}\cos^2\theta=\tfrac12P_{in}\cos^2\theta\qquad\left(P_{in}=\tfrac12\overline{x^2}\right)$$ ✅

### סעיף 2 – הספק הרעש במוצא
**רוחב הסרט של אות DSB הוא $2B$** (פס צד עליון ותחתון). רעש עם צפיפות חד-צדדית $N_0$ ברוחב $2B$ ⇐ הספק רעש כולל $2N_0B$,
ולכל אחד מהרכיבים $n_I, n_Q$ אותו הספק: $$\sigma_n^2=\overline{n_I^2}=\overline{n_Q^2}=2N_0B$$

> ⚠️ תוקן: בניסוח הקודם נכתב $\sigma_n^2=N_0B$ – זה לא מתאים לרוחב סרט $2B$, ובסוף החישוב "תוקן" עם גורם $\tfrac12$ בלי הסבר.

אחרי המכפל וה-LPF: $n_o(t)=\tfrac12n_I\cos\theta+\tfrac12n_Q\sin\theta$ (הרכיבים בלתי תלויים):
$$N_o=\tfrac14\sigma_n^2(\cos^2\theta+\sin^2\theta)=\tfrac14\sigma_n^2=\tfrac12N_0B$$ ✅ (לא תלוי ב-$\theta$)

### סעיף 3 – SNR במוצא
$$SNR_{out}=\frac{S_o}{N_o}=\frac{\tfrac12P_{in}\cos^2\theta}{\tfrac12N_0B}=\frac{P_{in}}{N_0B}\cos^2\theta$$

בסנכרון מלא ($\theta=0$): $$SNR_{out}=\frac{P_{in}}{N_0B}$$ ✅

💡 **הרעיון:** הרעש במוצא לא תלוי בפאזה (n_I ו-n_Q שווים בהספק), אבל האות קטן פי $\cos^2\theta$ – לכן גילוי קוהרנטי דורש סנכרון פאזה."""},
]

J_INTRO = "**איך לפתור:** קודם על דף – טבלה עם עמודה לכל משתנה – ורק אז לפתוח את הפתרון. הפלט נבדק בהרצה."
JAVA = [
    {"add": True, "kind": "lecture", "number": 4, "title": "תרגיל 1 · static מול משתנה של אובייקט – מה יודפס?", "exam_style": True,
     "question_md": J_INTRO + """

```java
public class Counter {
    static int total = 0;
    int mine = 0;

    void add() {
        total++;
        mine++;
    }

    public static void main(String[] args) {
        Counter a = new Counter();
        Counter b = new Counter();
        a.add();
        a.add();
        b.add();
        System.out.println(a.mine + " " + b.mine + " " + Counter.total);
    }
}
```""",
     "solution_md": """**הכלל:** `static` = עותק **אחד** למחלקה, משותף לכל האובייקטים. בלי `static` = עותק נפרד **בכל אובייקט**.

| פעולה | a.mine | b.mine | total |
|---|---|---|---|
| התחלה | 0 | 0 | 0 |
| `a.add()` | 1 | 0 | 1 |
| `a.add()` | 2 | 0 | 2 |
| `b.add()` | 2 | 1 | 3 |

**הפלט:** `2 1 3` ✅ (נבדק בהרצה)

💡 **הרעיון:** `total` סופר את כל הקריאות מכל האובייקטים; `mine` סופר רק את של האובייקט עצמו. ניגשים ל-static דרך שם המחלקה: `Counter.total`."""},
    {"add": True, "kind": "lecture", "number": 4, "title": "תרגיל 2 · העברה לפי ערך: int מול מערך", "exam_style": True,
     "question_md": J_INTRO + """

```java
public class Pass {
    static void change(int x, int[] arr) {
        x = 100;
        arr[0] = 100;
    }

    public static void main(String[] args) {
        int n = 5;
        int[] a = {5, 6};
        change(n, a);
        System.out.println(n + " " + a[0]);
    }
}
```""",
     "solution_md": """**הכלל:** ב-Java **הכול** מועבר לפי ערך (by value). אבל הערך של משתנה מערך / אובייקט הוא **הפניה** (כתובת).

- `x` מקבל **עותק** של 5. `x = 100` משנה רק את העותק ⇐ `n` נשאר **5**.
- `arr` מקבל עותק של **ההפניה** – מצביע על אותו מערך כמו `a`. `arr[0] = 100` משנה את המערך עצמו ⇐ `a[0]` הופך ל-**100**.

**הפלט:** `5 100` ✅ (נבדק בהרצה)

💡 **הרעיון:** משנים **תוכן** של מערך/אובייקט – רואים את זה בחוץ. משנים משתנה פרימיטיבי – לא."""},
    {"add": True, "kind": "lecture", "number": 4, "title": "תרגיל 3 · החלפה בתוך מערך מול מערך חדש", "exam_style": True,
     "question_md": J_INTRO + """

```java
public class Swap {
    static void swap(int[] a) { int t = a[0]; a[0] = a[1]; a[1] = t; }
    static void swapNew(int[] a) { a = new int[]{9, 9}; }

    public static void main(String[] args) {
        int[] p = {1, 2};
        swap(p);
        swapNew(p);
        System.out.println(p[0] + "," + p[1]);
    }
}
```""",
     "solution_md": """- `swap(p)`: `a` מצביע על אותו מערך כמו `p` ⇐ ההחלפה קורית במערך עצמו ⇐ `p = {2, 1}`.
- `swapNew(p)`: `a = new int[]{9, 9}` משנה **רק את ההפניה המקומית** `a` – עכשיו היא מצביעה על מערך חדש. `p` עדיין מצביע על הישן.

**הפלט:** `2,1` ✅ (נבדק בהרצה)

💡 **הרעיון:** `a[0] = ...` משנה את המערך; `a = new ...` משנה רק לאן `a` מצביע – והחוץ לא רואה את זה. זו שאלת מבחן קלאסית."""},
    {"add": True, "kind": "lecture", "number": 4, "title": "תרגיל 4 · טווח הכרה: משתנה מקומי שמסתיר שדה", "exam_style": True,
     "question_md": J_INTRO + """

```java
public class Scope {
    static int x = 1;

    static void f() {
        int x = 2;
        x++;
        System.out.print(x + " ");
    }

    public static void main(String[] args) {
        f();
        System.out.print(x + " ");
        for (int i = 0; i < 2; i++) {
            int y = i * 10;
            x += y;
        }
        System.out.println(x);
    }
}
```""",
     "solution_md": """- בתוך `f()`: `int x = 2;` הוא משתנה **מקומי חדש** שמסתיר את השדה `x`. `x++` ⇐ 3 ⇐ מודפס **`3 `**.
- ב-`main`: `x` הוא השדה הסטטי – לא השתנה ⇐ מודפס **`1 `**.
- הלולאה: `i=0` ⇐ `y=0`, `x=1`; `i=1` ⇐ `y=10`, `x=11`. (`y` ו-`i` קיימים רק בתוך הלולאה.)
- מודפס **`11`**.

**הפלט:** `3 1 11` ✅ (נבדק בהרצה)

💡 **הרעיון:** משתנה חי רק בתוך הסוגריים `{}` שבהם הוגדר; מקומי באותו שם "מסתיר" את השדה עד סוף הבלוק."""},
]

if __name__ == "__main__":
    out = {
        "digital": restore([("practice", 2, "digital-practice-2-new.json"), ("practice", 3, "digital-practice-3-new.json"),
                            ("practice", 4, "digital-practice-4-new.json")]),
        "linear": restore([("practice", 1, "linear-practice-1-new.json"), ("practice", 2, "linear-practice-2-new.json")]),
        "comm": restore([("practice", 1, "comm-practice-1-new.json"), ("practice", 2, "comm-practice-2-new.json")]) + COMM,
        "waves": WAVES,
        "java": JAVA,
    }
    for k, v in out.items():
        (CH / f"weekly-1411-{k}.json").write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
        print(k, len(v))
