"""Java: exercises whose stored solution was hollow / flagged (28/11/2026), solved by Claude. Every program below was
compiled with javac and run in the session (Field/Dog, Car/Door/Doorside, EX1, EX2, Company); MCQ outputs checked
by running them. Writes chapters/fix_2811_java_hollow.json for publish.yml inspect=exercises (course Java)."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SP = Path("/tmp/claude-0/-home-user-study-hub/07493fa9-fb63-5beb-830d-81523c08fa4e/scratchpad")
J = SP / "j"
OK = "\n\n> 🔎 נבדק מחדש (28/11): הקוד הורץ והתשובה נבדקה."
DONE = "\n\n> 🔎 נבדק מחדש (28/11): נכתב מחדש במלואו; הקוד הודר והורץ."


def code(p):
    return "```java\n" + (J / p).read_text(encoding="utf-8").rstrip() + "\n```"


S = {}
S["96d273a3"] = r"""### 📘 מה צריך לדעת קודם
- **משתנה מופע** (בלי `static`): לכל כלב עותק משלו – שם, צבע, גובה, משקל.
- **משתנה `static`**: עותק **אחד** למחלקה כולה – מתאים למונה הכלבים. הבנאי מגדיל אותו בכל `new`.
- **מתודה `static`** נקראת דרך שם המחלקה: `Dog.printCount()`.
- בקובץ אחד – רק מחלקה `public` אחת, ושם הקובץ כשמה (`Field.java`).

### ✍️ הדרך המלאה (כמו במחברת)
1. שדות פרטיים (`private`) + מונה `static`.
2. בנאי שמקבל שם ומגדיל את המונה.
3. Setters לשם, לצבע, ולגובה+משקל יחד.
4. `bark`, `printDetails`, ו-`printCount` הסטטית.
5. ב-`Field.main` – יוצרים שני כלבים ומפעילים את המתודות.

""" + code("dog/Field.java") + r"""

**פלט (הורץ):**
```
Rex: Bark!
Name: Rex, color: brown, height: 60, weight: 25.5
Name: Luna, color: white, height: 45, weight: 18.2
Dogs created: 2
```

💡 **הרעיון:** מה ששייך לכל כלב – משתנה מופע; מה ששייך לכל הכלבים יחד – `static`."""

S["95a7a6f2"] = r"""### 📘 מה צריך לדעת קודם
- `enum` – טיפוס עם רשימה סגורה של ערכים; `Doorside.values()` מחזיר אותם לפי הסדר.
- מערך של אובייקטים: `new Door[4]` יוצר 4 **הפניות ריקות** (`null`) – צריך `new Door()` לכל תא.
- שדה `static boolean lock` – אחד לכל הדלתות; `lockOn`/`lockOff` הסטטיות משנות אותו לכולן בבת אחת.

### ✍️ הדרך המלאה (כמו במחברת)
1. `enum Doorside` עם ארבעת הצדדים.
2. `Door`: שדות מופע (`name`, `color`), שדות `static` (`lock`, מונה דלתות), `setName`/`getName`, `lockOn`/`lockOff`.
3. `Car`: שדות מופע (`model`, מערך `doors`), שדה `static` (`wheels`), וב-`main`: בונים 4 דלתות, נותנים לכל אחת צד, מדפיסים, נועלים ופותחים.

""" + code("car/Car.java") + r"""

**פלט (הורץ):**
```
Door: LeftFront
Door: RightFront
Door: LeftBack
Door: RightBack
Locked: true
Locked: false
Corolla has 4 wheels and 4 doors
```
(בפרויקט אמיתי כל מחלקה בקובץ משלה באותה חבילה – `Car.java`, `Door.java`, `Doorside.java`; כאן הכול בקובץ אחד כדי שאפשר להריץ.)

💡 **הרעיון:** `lock` סטטי ⇐ נעילה של דלת אחת = נעילה של כולן."""

S["e2148400"] = r"""### 📘 מה צריך לדעת קודם
- `Scanner` לקלט: `nextInt()`, `nextDouble()`.
- לולאת `do-while` רצה **לפחות פעם אחת** – מתאים לתפריט שמוצג עד שבוחרים "יציאה".
- ממוצע: סכום חלקי מספר. אם הסכום `double`, החילוק עשרוני.

### ✍️ הדרך המלאה (כמו במחברת)
1. תפריט: 1 = חישוב ממוצע, 2 = יציאה.
2. בבחירה 1: קולטים מספר תלמידים, ואז ציון לכל אחד בלולאה, ומחשבים ממוצע.
3. הלולאה חוזרת עד שבוחרים 2.

""" + code("ex/EX2.java") + r"""

**הרצה (הורץ עם 3 ציונים: 90, 80, 75):** `Average: 81.66666666666667`, ואז בחירה 2 ⇐ `Bye`.

💡 **הרעיון:** תפריט = `do-while` עם תנאי יציאה; `sum` מסוג `double` כדי שהחילוק לא יקוצץ."""

S["5af1538f"] = r"""### 📘 מה צריך לדעת קודם
- `Scanner in = new Scanner(System.in); int num = in.nextInt();` – קליטת מספר שלם.
- שרשרת `if / else if / else` – בודקת תנאים לפי הסדר ומבצעת רק את הראשון שמתקיים.

### ✍️ הדרך המלאה (כמו במחברת)
1. קולטים מספר.
2. אם גדול מ-0 – חיובי; אחרת, אם קטן מ-0 – שלילי; אחרת – אפס.

""" + code("ex/EX1.java") + r"""

**הרצה (הורץ):** קלט `-5` ⇐ `-5 is negative`.

💡 **הרעיון:** שלושה מקרים זרים ⇐ `if / else if / else`."""

S["7ee300bf"] = r"""### 📘 מה צריך לדעת קודם
- מחלקה `abstract`: אי אפשר ליצור ממנה אובייקט; מתודה `abstract` – בלי גוף, וכל מחלקת בת חייבת לממש אותה.
- `this.name` – השדה של האובייקט (להבדיל מהפרמטר `name`).
- `super(name)` – קריאה לבנאי של מחלקת האב; חייבת להיות השורה הראשונה בבנאי.
- בקובץ אחד – רק מחלקה `public` אחת, ושם הקובץ כשמה. כאן `Company` היא ה-`public`.

### ✍️ הדרך המלאה (כמו במחברת)
| תיבה | השלמה | למה |
|---|---|---|
| [1] | **שום מילה** | המילה `abstract` כבר כתובה, ו-`public` (שגם לא ברשימה) אסור: `Company` כבר `public` באותו קובץ. אם בנוסח המקורי התיבה באה **במקום** `abstract` – התשובה `abstract`. |
| [2] | `this` | `this.name = name;` – השדה מקבל את הפרמטר. |
| [3] | `abstract` | מתודה בלי גוף (נגמרת ב-`;`) חייבת להיות `abstract`. |
| [4] | `super` | `super(name);` – בנאי האב מאתחל את `name`. |
| [5] | `new` | יצירת אובייקט: `new FullTimeEmployee("Yossi", 12000)`. |

הקוד המלא הודר והורץ ⇐ הפלט: `12000.0`.
> ⚠️ בפתרון הקודם נכתב `public` בתיבה [1] – זה לא מתקמפל ("class Employee is public, should be declared in a file named Employee.java").

💡 **הרעיון:** מחלקה אבסטרקטית מגדירה "מה", מחלקת הבת מממשת "איך", ו-`super` מעביר לאב את החלק שלו."""

Q_9ca = r"""בהינתן שלושה מספרים, מה יהיה הפלט המדויק של התוכנית?

```java
int num1 = 10;
int num2 = 23;
int num3 = 5;
int min = (num1 < num2) ? num1 : num2;
min = (min < num3) ? min : num3;
System.out.println("The smallest number is = " + min);
if (min < 10)
    System.out.println("The smallest number is less than 10!");
else
    System.out.println("The smallest number is greater than or equal to 10!");
```

**א.** `The smallest number is = 5` ואז `The smallest number is less than 10!`

**ב.** `The smallest number is = 10` ואז `The smallest number is greater than or equal to 10!`

**ג.** `The smallest number is = 5` ואז `The smallest number is greater than or equal to 10!`

**ד.** `The smallest number is = 23` ואז `The smallest number is less than 10!`"""

FINE = ["52cefe98", "8cf0d7ab", "5a63cd96", "67319c08", "722b2741", "262a6118", "9ca48615", "3da55b01", "bf8dbde1",
        "308ebd98", "9c3787c5", "c9d1c55d", "8daa4cb7", "d52984f9", "de9a6abc", "e413fa9e", "c1a83618", "cba4421e",
        "191c7c9e", "c5947670"]
NOTE_52 = ("\n\n> הערה: התשובה נכונה כש-`Book` **לא** דורסת את `equals` – אז `equals` של `Object` משווה הפניות, כמו `==`. "
           "אם במחלקה מהשיעור `equals` נדרסה להשוואת שדות, `b1.equals(b3)` היה `true`.")


def main():
    xs = {x["id"][:8]: x for x in json.loads((SP / "java_todo.json").read_text(encoding="utf-8"))}
    out = []
    for k, sol in S.items():
        x = xs[k]
        out.append({"id": x["id"], "title": x["title"], "solution_md": sol + DONE, "uncertain": False, "lock": True})
    for k in FINE:
        x = xs[k]
        sol = x["solution_md"].rstrip()
        fx = {"id": x["id"], "title": x["title"], "uncertain": False, "lock": True}
        if k == "52cefe98":
            sol += NOTE_52
        if k == "9ca48615":
            fx["question_md"] = Q_9ca
        if k == "8daa4cb7":
            fx["question_md"] = x["question_md"].replace("**ب.**", "**ב.**")
            sol = re.sub(r"\*\*הנוסחה:\*\*\s*\$\$\s*\\text\{Reference Assignment & Casting Rules\}\s*\$\$",
                         "**הכלל:** משתנה מסוג אב יכול להצביע על אובייקט בן; השמה מאב לבן דורשת המרה מפורשת.", sol)
            sol = sol.replace("להשديר", "להשים").replace("**ب**", "**ב**").replace("שורה (5 מנסה", "שורה (5) מנסה")
        fx["solution_md"] = sol + OK
        out.append(fx)
    (HERE.parent / "fix_2811_java_hollow.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(len(out), "exercises")


if __name__ == "__main__":
    main()
