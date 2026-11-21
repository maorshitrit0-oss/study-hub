"""Java lecture 5 (21/11/2026: his upload; Gemini out of quota / overloaded, so Claude wrote it from the transcript +
board / NetBeans snapshots). Topics in the order taught (end of J7 + start of J8): type casting (primitives: implicit /
explicit, int division), casting references along a class hierarchy (Car / Toyota / Yaris, a first look at `extends`),
comparing objects (== on references), getClass / Class / getMethods (reflection, only "good to know"), instanceof, the
J7_cars example (instance vs static members, static methods, final static constants, an array of objects), J8: Math,
String, StringBuffer, wrapper classes (Vector), Object at the top (toString, getClass).
The Java exam is multiple choice: exercises = code-understanding MCQ with the full method; the quiz = understanding.
Every code answer was checked by running it with javac/java where a JDK was available (see check()).
  python java_l5.py -> chapters/java-l5.json (publish: course Java, kind lecture, number 5)"""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

L = "אבגד"
_SPOT = iter([2, 0, 3, 1, 1, 3, 0, 2])

PROGRAMS = {
    "Div": ("public class Div { public static void main(String[] a) { int x = 5, y = 4; double d1 = x / y; "
            "double d2 = (double) x / y; double d3 = (double) (x / y); System.out.println(d1 + \" \" + d2 + \" \" + d3); } }",
            "1.0 1.25 1.0"),
    "Cast": ("public class Cast { public static void main(String[] a) { double d = 40.7; int j = (int) d; "
             "int k = (int) -2.9; System.out.println(j + \" \" + k); } }", "40 -2"),
    "Eq": ("public class Eq { public static void main(String[] a) { String s1 = \"Hello\"; String s2 = s1; "
           "String s3 = new String(s1); System.out.println((s1 == s2) + \" \" + (s1 == s3) + \" \" + s1.equals(s3)); } }",
           "true false true"),
    "Hier": ("class Car {} class Toyota extends Car {} public class Hier { public static void main(String[] a) { "
             "Car c = new Toyota(); System.out.println((c instanceof Toyota) + \" \" + (c instanceof Car) + \" \" "
             "+ c.getClass().getSimpleName()); } }", "true true Toyota"),
    "Stat": ("class Car { static String msg; String lic; Car(String l) { lic = l; } static void send(String m) { msg = m; } "
             "String get() { return lic + \":\" + msg; } } public class Stat { public static void main(String[] a) { "
             "Car c1 = new Car(\"A\"); Car c2 = new Car(\"B\"); Car.send(\"go\"); c2.msg = \"stop\"; "
             "System.out.println(c1.get() + \" \" + c2.get()); } }", "A:stop B:stop"),
    "Buf": ("public class Buf { public static void main(String[] a) { StringBuffer sb = new StringBuffer(\"Java\"); "
            "sb.append(\"Fun\"); sb.delete(1, 3); String s = \"Java\"; s.concat(\"Fun\"); "
            "System.out.println(sb + \" \" + s); } }", "JaFun Java"),
}


def check():
    """Runs every program whose printed output an exercise claims (only where a JDK is installed)."""
    if not (shutil.which("javac") and shutil.which("java")):
        print("no JDK here - outputs checked by hand")
        return
    with tempfile.TemporaryDirectory() as d:
        for name, (src, want) in PROGRAMS.items():
            p = Path(d) / name
            p.mkdir()
            (p / f"{name}.java").write_text(src)
            subprocess.run(["javac", f"{name}.java"], cwd=p, check=True)
            got = subprocess.run(["java", name], cwd=p, capture_output=True, text=True, check=True).stdout.strip()
            assert got == want, (name, got, want)
    print("all programs print what the exercises say")


def mcq(title, q, opts, ans, know, steps, why_not, idea, topic):
    want = next(_SPOT)
    order = [i for i in range(4) if i != ans]
    order.insert(want, ans)
    opts = [opts[i] for i in order]
    why_not = {order.index(i): w for i, w in why_not.items()}
    body = (q.strip() + "\n\n" + "\n\n".join(f"**{L[i]}.** {o}" for i, o in enumerate(opts))
            + "\n\n✍️ *לבחור תשובה, לכתוב במחברת את הדרך – ורק אחר כך לבדוק.*")
    sol = (f"### התשובה: **{L[want]}** ✅\n\n### 📘 מה צריך לדעת קודם\n\n{know.strip()}\n\n"
           f"### ✍️ הדרך המלאה (כמו במחברת)\n\n{steps.strip()}\n\n### ❌ למה לא האחרות\n\n"
           + "\n".join(f"- **{L[i]}** – {w}" for i, w in sorted(why_not.items())) + f"\n\n💡 **הרעיון:** {idea}")
    return {"title": title, "question_md": body, "solution_md": sol, "topic": topic, "exam_style": True, "uncertain": False}


CHAPTER = r"""
# הרצאה 5: המרת טיפוסים, השוואת אובייקטים, תורשה ראשונית, ומחלקות שימושיות (J7–J8)

> 🎯 **במשפט אחד:** מתי Java ממירה טיפוס לבד ומתי צריך לכתוב `(int)` בעצמך, איך משווים אובייקטים (ולמה `==` מטעה), איך אובייקט "מספר" מה הוא בזמן ריצה, ותרגול מלא של מחלקה `Car` עם איברים סטטיים ואיברי מופע.

## 1. תזכורת: שני סוגי משתנים
| סוג | מה הוא מכיל | דוגמה |
|---|---|---|
| **פרימיטיבי** | את **הערך** עצמו | `int`, `double`, `float`, `boolean` |
| **הפניה (reference)** | **כתובת** של אובייקט בזיכרון | `Car`, `String`, מערך |

כל מה שלא פרימיטיבי הוא הפניה.

## 2. המרת טיפוסים (Casting) – פרימיטיביים
**Casting = המרה מסוג אחד לסוג אחר.**

### 2.1 המרה אוטומטית (implicit) – מקטן לגדול
```java
int j = 10;        // 32 ביט, שלם
double d = 6.2;    // 64 ביט, ממשי
d = j;             // ✓ מותר – אוטומטי
```
**למה מותר:** הסוג בצד **שמאל גדול יותר** (64 ביט). כל ערך של `int` נכנס בו **בלי לאבד מידע**, ולכן הקומפיילר עושה את ההמרה לבד.

### 2.2 המרה מפורשת (explicit) – מגדול לקטן
```java
d = 40.3;
j = d;         // ✗ שגיאת קומפילציה – אפשר לאבד מידע
j = (int) d;   // ✓ מפורש: j = 40 (השבר נחתך)
```
- **בלי ה-cast:** הקומפיילר **מסרב** ("possible lossy conversion"), ולא נוצר קובץ ה-`.class`.
- **עם ה-cast:** אתה אומר לקומפיילר "אני יודע שאני עלול לאבד מידע". השבר `.3` נחתך.

### 2.3 מלכודת: חילוק של שלמים
```java
int x = 5, y = 4;
double d = x / y;           // 1.0  ✗ – החילוק נעשה בשלמים לפני ההשמה
double d = (double) x / y;  // 1.25 ✓ – מספיק להמיר אחד מהם
```
**ההסבר:** `x / y` מחושב **קודם**, ושני הצדדים `int`, ולכן זה חילוק שלמים: `1`. רק אחר כך התוצאה הופכת ל-`1.0`. אם ממירים **לפחות אחד** מהם ל-`double`, החילוק כולו נעשה בדיוק של `double`.

### 2.4 עוד מקרה (מהדוגמה של המכוניות)
```java
car1.engine = 1.6;          // ✗ – engine הוא float, ו-1.6 הוא double כברירת מחדל
car1.engine = (float) 1.6;  // ✓
```
מספר עם נקודה עשרונית הוא `double` כברירת מחדל ב-Java (64 ביט), ו-`float` הוא 32 ביט, ולכן צריך המרה מפורשת. (אפשר גם לכתוב `1.6f`.)

## 3. תורשה – הצצה ראשונה
**שלוש התכונות של כל שפה מונחית עצמים:**
1. **כימוס** (Encapsulation)
2. **תורשה** (Inheritance)
3. **רב-צורתיות** (Polymorphism) – בהמשך הקורס.

**תורשה במילים:**
- מחלקה חדשה יכולה **לרשת** ממחלקה קיימת את כל התכונות (משתנים) וההתנהגויות (מתודות), עם המילה השמורה **`extends`**.
- כותבים רק את מה ש**חדש**.

```java
class Car    { String license; void turn(int angle) {...} }
class Toyota extends Car { void accelerate(...) {...} }   // יש לה גם license ו-turn
class Yaris  extends Toyota { ... }
class BMW    extends Car { ... }
```
**ההיררכיה:**
- `Car` למעלה.
- מתחתיו `Toyota` ו-`BMW`.
- מתחת ל-`Toyota` – `Yaris`.

**כל מחלקה היא גם סוג (type) של משתנה.**

## 4. המרת טיפוסים – הפניות (לאורך ההיררכיה)
**אותו כלל כמו בפרימיטיביים:** "גבוה בהיררכיה" = "גדול".

```java
Car car = new Car();
Toyota toyo = new Toyota();

car = toyo;              // ✓ implicit – Car גבוה יותר: "טויוטה היא סוג של מכונית"
Car car2 = new Toyota(); // ✓ משתנה מסוג Car יכול להצביע לאובייקט Toyota

toyo = car2;             // ✗ שגיאת קומפילציה – Toyota נמוכה יותר מ-Car
toyo = (Toyota) car2;    // ✓ explicit
```
![המרה בין הפניות על הלוח](slide:21)

> 🔜 המרצה אמר שיש עוד "ניואנס" – בדיקה שצריך לעשות לפני המרה מפורשת כזאת (הבדיקה היא `instanceof`, סעיף 7). נרחיב כשנגיע לתורשה ולרב-צורתיות.

## 5. השוואת אובייקטים: `==`
- **על פרימיטיביים:** `==` ו-`!=` משווים **ערכים**.
- **על הפניות:** הם בודקים אם **שני הצדדים מצביעים לאותו אובייקט**, כלומר אם הכתובת שווה. הם **לא** משווים את התוכן.

```java
String str1 = "Hello";
String str2 = str1;            // אותה כתובת
System.out.println(str1 == str2);   // true

str2 = new String(str1);       // new = אובייקט חדש, אותו תוכן
System.out.println(str1 == str2);   // false!
```
![השוואת אובייקטים](slide:28)

**הכלל:** `==` בין הפניות ייתן `true` **רק** אם שתיהן מצביעות **בדיוק לאותו אובייקט**.

> 💡 **כדי להשוות תוכן של מחרוזות** משתמשים ב-`str1.equals(str2)` (הכרנו ב-API של String בהרצאה הקודמת).

## 6. איזה סוג אובייקט זה? `getClass()` (רפלקציה)
- **לכל אובייקט** ב-Java יש מתודה `getClass()`, גם לאובייקטים של מחלקות שלא כתבנו. היא מחזירה אובייקט מסוג **`Class`** (עם C גדולה).
- המתודות של `Class` "מספרות" מה יש באובייקט:
  - `getName()` – שם המחלקה.
  - `getMethods()` – מערך של `Method` עם כל המתודות **הציבוריות** (`public`), כולל אלה שהאובייקט ירש מ-`Object`. מייבאים מ-`java.lang.reflect`.
- היכולת הזאת נקראת **רפלקציה (Reflection)**, והיא קורית **בזמן ריצה**.

**למה זה שימושי:**
- עובדים עם מחלקות שכתבו אחרים, או שכתבת לפני שנים ולא זוכר.
- **אשכול שרתים (cluster):** כמה מחשבים, כל אחד מריץ JVM. מעבירים אובייקטים מ-JVM ל-JVM כדי לחלק עומס (בנק, הרבה לקוחות). ה-JVM שמקבל אובייקט לא בהכרח יודע מה הוא, ו"מתבונן" בו כדי לדעת מה להפעיל.

**הדוגמה מהשיעור:**
```java
class Employee {}
class VicePresident extends Employee {
    public void test1() {}
    public void test2() {}
}
// ב-main:
Employee emp; VicePresident vp = new VicePresident();
emp = vp;                                    // implicit casting
Class cl = emp.getClass();
System.out.println("Type of emp is: " + cl); // class VicePresident  ← הסוג האמיתי של האובייקט!
Method[] m = cl.getMethods();
for (int i = 0; i < m.length; i++)
    System.out.println("Employee has behavior: " + m[i].getName());
```
![getClass ו-getMethods](slide:44)

**מה למדנו מהדוגמה:**
- `getClass()` מחזיר את הסוג של **האובייקט** (`VicePresident`), לא את הסוג של **המשתנה** (`Employee`).
- בהרצה הראשונה `test1` ו-`test2` **לא** הופיעו, כי לא היו `public` (`getMethods` מחזיר רק ציבוריות). אחרי שהוסיף `public` הן הופיעו.

> ℹ️ רפלקציה לא תילמד לעומק בקורס – "טוב לדעת שזה קיים".

## 7. האופרטור `instanceof`
בודק אם **האובייקט** שמשתנה מצביע אליו הוא מסוג מסוים:
```java
if (emp instanceof VicePresident)
    System.out.println("Employee is Vice President");
else
    System.out.println("Employee is not");
```
**בדוגמה:** הודפס `is Vice President`, כי `emp` מצביע לאובייקט שנבנה כ-`new VicePresident()`.

## 8. תרגול מלא: אפליקציה עם שתי מחלקות (J7_cars)
**הרעיון של המרצה:**
- ב-Java **לא** קופצים ל-`main` לכתוב קוד ברצף כמו ב-C.
- **קודם מתארים** מה זו מכונית: תכונות, ואז התנהגויות.
- **מחלקים למתודות קטנות.** זה לא מגדיל את הזיכרון ולא מאט, וזה הופך את הקוד לברור – "לא פחות חשוב מקוד שרץ נכון".

### המחלקה `Car` (בחבילה `cars`)
```java
public class Car {
    String license;                         // מופע (instance)
    public float engine;                    // מופע – נפח מנוע, למשל 1.6
    public String color;
    int speed, temperature;
    static String msg;                      // סטטי – משותף לכל המכוניות

    public void drive(int sp) {
        speed = sp;
        if (speed >= 100) temperature = 120; else temperature = 60;   // נסיעה מהירה מחממת את המנוע
    }
    public boolean checkEngine() { return temperature <= 150; }      // false = המנוע לא בסדר
    public static void sendMessage(String m) { msg = m; }            // "סדרן המוניות" – הודעה לכולם
    public String getMsg() { return msg; }                           // מתודת מופע שקוראת משתנה סטטי – מותר
    public String getLicense() { return license; }
    public void setLicense(String s) { license = s; }
}
```

**משתני מופע לעומת משתנה סטטי:**
- **משתני מופע:** לא בתוך מתודה (לכן לא מקומיים), ובלי `static`. הם נוצרים **רק** כשבונים אובייקט ב-`new Car()`, וכל מכונית מקבלת עותק משלה.
- **`static msg`:** עותק **אחד** בזיכרון, משותף לכל המכוניות. המרצה המשיל אותו לסדרנית של חברת מוניות: היא כותבת הודעה אחת, וכל המוניות רואות אותה מיד.

**מתי מתודה סטטית:**
- **`sendMessage` סטטית:** היא עובדת רק על המשתנה המשותף, ולא על מכונית מסוימת.
- **`checkEngine` לא סטטית:** היא בודקת את המנוע של מכונית **מסוימת**.
- **`getMsg` לא סטטית:** הוא השאיר אותה כמתודת מופע בכוונה, כדי להראות שמתודת מופע יכולה לגשת למשתנה סטטי.

> ⚠️ המרצה נימק את `static` בכך שמתודה רגילה "משוכפלת בזיכרון לכל אובייקט" (אלף מכוניות = אלף עותקים). **בפועל ב-Java הקוד של מתודה נשמר פעם אחת בלבד**, גם למתודות מופע. מה שמשוכפל לכל אובייקט הוא **משתני המופע**. הסיבה האמיתית להגדיר `static`: המתודה לא שייכת לאובייקט מסוים, ולכן קוראים לה דרך שם המחלקה (`Car.sendMessage(...)`) בלי צורך באובייקט.

### כלל הגישה (לזכור בעל פה!)
| מתודה | יכולה לגשת ל... |
|---|---|
| **סטטית** (כמו `main`) | איברים **סטטיים בלבד** |
| **מופע** | איברים **סטטיים וגם** איברי מופע |

**לכן:**
- כשקראו ל-`init()` מתוך `main` בלי `static`, NetBeans נתן: **`non-static method init() cannot be referenced from a static context`**.
- **התיקון:** גם `init`, `run` ו-`reportProgress` סטטיות.
- **גם המשתנים** `car1` ו-`car2` (ואחר כך המערך `cars`) הוגדרו `static`, כי מתודה סטטית צריכה לכתוב אליהם.

### המחלקה `Main`
```java
public class Main {
    final static int NUMB_CARS = 2;          // קבוע: final static, שם באותיות גדולות
    static Car[] cars;

    public static void main(String[] args) { init(); run(); reportProgress(); }

    static void init() {
        cars = new Car[NUMB_CARS];           // קודם בונים את המערך...
        for (int i = 0; i < NUMB_CARS; i++) cars[i] = new Car();   // ...ואז כל אובייקט
        cars[0].setLicense("XYZ 123");  cars[1].setLicense("ABC 999");
        cars[0].engine = (float) 1.6;   cars[1].engine = (float) 2;
        cars[0].color = "RED";          cars[1].color = "BLUE";
    }
    static void run() {
        cars[0].drive(45);
        if (cars[1].checkEngine()) cars[1].drive(90);
        Car.sendMessage("Attention all cars!");   // מתודה סטטית – דרך שם המחלקה
    }
    static void reportProgress() {
        for (int i = 0; i < NUMB_CARS; i++)
            System.out.println("Car: " + cars[i].getLicense() + " received message: " + cars[i].getMsg());
    }
}
```
**הפלט:**
```
Car: XYZ 123 received message: Attention all cars!
Car: ABC 999 received message: Attention all cars!
```
![הפלט של J7_cars](slide:85)

**מה לקחת מהדוגמה:**

**קבועים ומערכים:**
- **`final`** = אי אפשר לשנות את הערך אחרי שנקבע. **קבוע** = `final static` + שם באותיות גדולות.
- **מערך של אובייקטים:** `new Car[2]` בונה רק את **המערך** (שתי הפניות ריקות). כל מכונית צריך לבנות בנפרד ב-`new Car()`.

**קריאה למתודות:**
- **מתודה סטטית** קוראים דרך **שם המחלקה**: `Car.sendMessage(...)`. אפשר גם דרך הפניה לאובייקט, אבל זה פחות ברור.
- **ההוכחה שהמשתנה משותף:** שתי מכוניות שונות (לוחיות שונות) מדפיסות **אותה** הודעה.

**גישה ישירה מול מתודות:**
- מתודה שתפקידה לתת גישה למשתנה (`setLicense`/`getLicense`) מאפשרת להשאיר את המשתנה **לא** `public`.
- `engine` ו-`color` שונו ישירות רק לשם התרגול – "בדרך כלל לא עושים את זה".
- את מילות הגישה (`public` וכו') נלמד בהרצאה נפרדת. בינתיים שמים `public`.

**חבילות ושגיאות:**
- `Main` לא הכיר את `Car` כי הוא בחבילה אחרת (`cars`). NetBeans הוסיף `import cars.Car;`. **חבילה** = תיקייה, ונלמד עליה ב-J10.
- **שגיאת קומפילציה** מצביעה על הקובץ ומספר השורה (`Main.java:61: cannot find symbol` – חסר `s` ב-`cars`). בהמשך נלמד גם על **שגיאות זמן ריצה** (runtime exceptions), שקורות גם אחרי קומפילציה תקינה.

## 9. J8: מחלקות שימושיות שכבר קיימות
**הרעיון:** להשתמש במה שכבר קיים ב-API.

### `Math`
אוסף מתודות **סטטיות** (קוראים ישירות: `Math.abs(x)`):

| מתודה | מה היא עושה |
|---|---|
| `Math.random()` | מספר אקראי בין 0 ל-1 |
| `Math.abs` | ערך מוחלט |
| `Math.max` | הגדול מבין שניים |
| `Math.ceil` | עיגול כלפי מעלה |
| פונקציות טריגונומטריות | `sin`, `cos` וכו' |

המרצה: "כדאי לעשות היכרות עם ה-API כמה שיותר, כדי להתחיל לעבוד על הפרויקט".

### `String`
- **הרבה דרכים ליצור מחרוזת** (בנאים – constructors):
  - ממערך של `char`.
  - ממערך של בתים.
  - מחלק של מערך: מנקודה מסוימת ועד נקודה מסוימת (offset).
- **מתודות שימושיות:**
  - `compareTo` – סדר מילוני (לקסיקוגרפי), שימושי למיון מחרוזות.
  - `concat` – שרשור.
- **`String` אינה ניתנת לשינוי** אחרי שנבנתה.

### `StringBuffer`
מחרוזת **שניתן לשנות** (mutable):
- `append` – מוסיף בסוף.
- `delete(start, end)` – מוחק קטע מהאמצע.

### מחלקות עוטפות (Wrapper classes)
- לכל טיפוס פרימיטיבי יש מחלקה ש"עוטפת" אותו באובייקט: `Boolean`, `Integer`, `Double`...
- **למה צריך אותן:**
  1. **מבני נתונים עובדים על אובייקטים:** למשל `Vector` (כמו מערך שאפשר להגדיל) – `v.add(...)` מקבל אובייקט.
  2. **מתודות סטטיות שימושיות:** למשל `Integer.parseInt("123")` ממיר מחרוזת למספר.

```java
Vector v = new Vector();
Integer a1 = new Integer(10);
v.add(a1);
```

> ⚠️ המרצה אמר "אי אפשר לעשות `add` לערך פרימיטיבי". **מאז Java 5 יש "אריזה אוטומטית" (autoboxing):** `v.add(10)` עובד, והקומפיילר עוטף לבד ב-`Integer`. הרעיון נכון (המבנה מחזיק אובייקטים), רק שהעטיפה קורית אוטומטית. (וגם `new Integer(10)` מסומן היום כמיושן; כותבים `Integer.valueOf(10)`.)

### `Object` – ראש ההיררכיה
- **כל** מחלקה ב-Java יורשת בסוף מ-`Object`, למשל `Integer` ⇐ `Number` ⇐ `Object`.
- לכן **לכל** אובייקט יש `getClass()` ו-**`toString()`**.
- כשמדפיסים אובייקט, Java קוראת ל-`toString()` שלו.

> ⚠️ בהקלטה המרצה אמר פעם "get-string" – הכוונה ל-**`toString()`**.

## 10. בשבוע הבא
- מחלקת `System`.
- **Properties**, עם דוגמה.
"""

SUMMARY = r"""## 🎯 המסר של השיעור
המרה מקטן לגדול אוטומטית, מגדול לקטן רק עם `(type)`. זה נכון גם לאובייקטים: "גבוה בהיררכיה" = גדול. `==` על אובייקטים בודק **כתובת**, לא תוכן. ומתודה סטטית רואה רק איברים סטטיים.

## 📌 חייבים לזכור
- **פרימיטיביים:**
  - `double d = intVar;` ✓
  - `int j = doubleVar;` ✗ ⇐ `(int) doubleVar` חותך את השבר.
- **חילוק שלמים:** `5/4` = `1`. `(double)5/4` = `1.25`.
- **`float`:** `float f = 1.6;` ✗ ⇐ `(float)1.6` או `1.6f`.
- **הפניות:**
  - `Car c = new Toyota();` ✓
  - `Toyota t = c;` ✗ ⇐ `(Toyota) c`
- **השוואה:**
  - `==` בין הפניות = **אותו אובייקט**.
  - `new String(s)` = אובייקט חדש ⇐ `==` נותן `false`.
  - תוכן משווים עם `equals`.
- **בזמן ריצה:**
  - `obj.getClass()` = הסוג **האמיתי** של האובייקט.
  - `getMethods()` = המתודות ה-`public` (רפלקציה).
  - `obj instanceof X` = האם האובייקט מסוג `X`.
- **כלל הגישה:**
  - סטטי ⇐ רק סטטי.
  - מופע ⇐ גם וגם.
  - ("non-static method cannot be referenced from a static context")
- **איברים סטטיים:**
  - משתנה סטטי = עותק אחד לכל האובייקטים.
  - מתודה סטטית קוראים דרך שם המחלקה.
  - קבוע = `final static` באותיות גדולות.
- **מערך אובייקטים:** `new Car[n]` ואז `new Car()` לכל איבר.
- **J8:**
  - `Math` (סטטיות).
  - `String` (לא משתנה) / `StringBuffer` (משתנה: `append`, `delete`).
  - מחלקות עוטפות (`Integer.parseInt`).
  - `Object` בראש – `toString`, `getClass`.

## ⚠️ טעויות נפוצות
- לחשוב ש-`double d = 5/4;` נותן 1.25.
- להשוות מחרוזות ב-`==`.
- לקרוא למתודת מופע מתוך `main` בלי אובייקט.
- לשכוח לבנות כל אובייקט במערך אחרי `new Car[n]` (אחרת – הפניה ריקה).
"""

EX = [
    mcq("מה מודפס? חילוק שלמים והמרה",
        r"""```java
int x = 5, y = 4;
double d1 = x / y;
double d2 = (double) x / y;
double d3 = (double) (x / y);
System.out.println(d1 + " " + d2 + " " + d3);
```
מה הפלט?""",
        ["`1.0 1.25 1.0`", "`1.25 1.25 1.25`", "`1.0 1.25 1.25`", "`1 1.25 1`"], 0,
        r"""- ביטוי מחושב **לפני** ההשמה. אם שני הצדדים של `/` הם `int` – חילוק **שלמים** (השבר נזרק).
- `(double)` חל על מה שמיד אחריו: `(double) x` ממיר רק את `x`; `(double)(x / y)` ממיר את **התוצאה** של חילוק השלמים.
- `double` מודפס תמיד עם נקודה: `1.0`.""",
        r"""**1.** `d1`: `x / y` = `5 / 4` בשלמים = `1` ⇐ נשמר ב-double ⇐ `1.0`.

**2.** `d2`: `(double) x` = `5.0`, ואז `5.0 / 4` = חילוק ממשי ⇐ `1.25`.

**3.** `d3`: קודם הסוגריים: `x / y` = `1` (שלמים), ואז ההמרה ⇐ `1.0`.

**הפלט:** `1.0 1.25 1.0`.""",
        {1: "רק d2 עושה חילוק ממשי; ב-d1 וב-d3 החילוק נעשה בשלמים.",
         2: "ב-d3 ההמרה מגיעה **אחרי** שהחילוק כבר חתך את השבר.",
         3: "משתנה double מודפס עם נקודה עשרונית – `1.0`, לא `1`."},
        "חשוב **מתי** קורית ההמרה: לפני החילוק (נשמר השבר) או אחריו (השבר כבר אבד).", "המרת טיפוסים"),
    mcq("איזו שורה לא מתקמפלת?",
        r"""```java
class Car {}
class Toyota extends Car {}
...
Car car = new Car();          // (1)
Toyota toyo = new Toyota();   // (2)
car = toyo;                   // (3)
Car car2 = new Toyota();      // (4)
toyo = car2;                  // (5)
```
איזו שורה גורמת לשגיאת קומפילציה?""",
        ["שורה (5)", "שורה (3)", "שורה (4)", "כל השורות תקינות"], 0,
        r"""- כמו בפרימיטיביים: מותר **אוטומטית** להעביר מ"קטן" ל"גדול".
- בהיררכיית מחלקות: **גבוה = גדול**. `Car` גבוה מ-`Toyota` (טויוטה היא סוג של מכונית).
- הקומפיילר מסתכל על **סוג המשתנה**, לא על האובייקט שהוא מצביע אליו בפועל.""",
        r"""**1.** שורות (1), (2) – בונים אובייקט מהסוג של המשתנה ✓.

**2.** שורה (3): `Car ← Toyota` – מנמוך לגבוה ⇐ implicit ✓.

**3.** שורה (4): משתנה `Car` מצביע לאובייקט `Toyota` ✓ (אותו כלל).

**4.** שורה (5): `Toyota ← Car` – מגבוה לנמוך. הסוג של `car2` הוא `Car`, והקומפיילר לא "יודע" שבפועל יש שם טויוטה ⇐ **שגיאה**.

**התיקון:** `toyo = (Toyota) car2;` – המרה מפורשת.""",
        {1: "Car גבוה מ-Toyota – זו המרה אוטומטית תקינה.",
         2: "משתנה מסוג Car יכול להצביע לאובייקט Toyota.",
         3: "שורה (5) דורשת `(Toyota)` מפורש."},
        "הקומפיילר בודק את **סוג המשתנה**: מטה בהיררכיה ⇐ צריך cast מפורש.", "המרת טיפוסים"),
    mcq("== על מחרוזות",
        r"""```java
String s1 = "Hello";
String s2 = s1;
String s3 = new String(s1);
System.out.println((s1 == s2) + " " + (s1 == s3) + " " + s1.equals(s3));
```
מה הפלט?""",
        ["`true false true`", "`true true true`", "`false false true`", "`true false false`"], 0,
        r"""- `==` בין הפניות בודק **אותה כתובת** (אותו אובייקט), לא תוכן.
- `new` יוצר **תמיד** אובייקט חדש בכתובת חדשה.
- `equals` של String משווה **תוכן** (תו אחר תו).""",
        r"""**1.** `s2 = s1` – מעתיקים את **הכתובת** ⇐ שניהם מצביעים לאותו אובייקט ⇐ `s1 == s2` הוא `true`.

**2.** `s3 = new String(s1)` – אובייקט **חדש** עם אותו תוכן ⇐ כתובת אחרת ⇐ `s1 == s3` הוא `false`.

**3.** `s1.equals(s3)` – התוכן זהה ("Hello") ⇐ `true`.

**הפלט:** `true false true`.""",
        {1: "s3 נבנה ב-new – אובייקט אחר, ולכן == נותן false.",
         2: "s2 מקבל את אותה כתובת כמו s1 – == נותן true.",
         3: "equals משווה תוכן, והתוכן זהה."},
        "`==` = אותו אובייקט; `equals` = אותו תוכן.", "השוואת אובייקטים"),
    mcq("getClass ו-instanceof",
        r"""```java
class Car {}
class Toyota extends Car {}
...
Car c = new Toyota();
System.out.println((c instanceof Toyota) + " " + (c instanceof Car) + " "
                   + c.getClass().getSimpleName());
```
מה הפלט?""",
        ["`true true Toyota`", "`false true Car`", "`true false Toyota`", "`false true Toyota`"], 0,
        r"""- `instanceof` ו-`getClass()` בודקים את **האובייקט** בזמן ריצה – לא את סוג המשתנה.
- אובייקט של מחלקה יורשת הוא **גם** מסוג המחלקה שמעליה (טויוטה **היא** מכונית).""",
        r"""**1.** `c` מצביע לאובייקט שנבנה ב-`new Toyota()`.

**2.** `c instanceof Toyota` – האובייקט הוא טויוטה ⇐ `true`.

**3.** `c instanceof Car` – טויוטה יורשת מ-Car, ולכן היא גם Car ⇐ `true`.

**4.** `c.getClass()` – המחלקה **האמיתית** של האובייקט ⇐ `Toyota` (כמו בדוגמה מהשיעור: `emp` מסוג Employee הדפיס `VicePresident`).

**הפלט:** `true true Toyota`.""",
        {1: "getClass ו-instanceof לא מסתכלים על סוג המשתנה (Car) אלא על האובייקט.",
         2: "אובייקט Toyota הוא גם Car – instanceof Car נותן true.",
         3: "האובייקט נבנה כ-Toyota – instanceof Toyota נותן true."},
        "בזמן ריצה Java יודעת מה **האובייקט** באמת – גם אם המשתנה מסוג כללי יותר.", "getClass ו-instanceof"),
    mcq("משתנה סטטי משותף",
        r"""```java
class Car {
    static String msg;
    String lic;
    Car(String l) { lic = l; }
    static void send(String m) { msg = m; }
    String get() { return lic + ":" + msg; }
}
...
Car c1 = new Car("A");
Car c2 = new Car("B");
Car.send("go");
c2.msg = "stop";
System.out.println(c1.get() + " " + c2.get());
```
מה הפלט? (`Car(String l)` הוא "בנאי" – מתודה שרצה כשבונים את האובייקט; נלמד עליו בהמשך.)""",
        ["`A:stop B:stop`", "`A:go B:stop`", "`A:go B:go`", "`A:null B:stop`"], 0,
        r"""- משתנה **סטטי** קיים **פעם אחת** בזיכרון ומשותף לכל האובייקטים (כמו ההודעה של הסדרנית).
- אפשר לגשת אליו דרך שם המחלקה או דרך כל הפניה – זה תמיד **אותו** משתנה.
- `lic` הוא משתנה מופע – לכל מכונית עותק משלה.""",
        r"""**1.** `c1.lic = "A"`, `c2.lic = "B"` – לכל אחת משלה.

**2.** `Car.send("go")` ⇐ המשתנה המשותף `msg = "go"`.

**3.** `c2.msg = "stop"` – זה **אותו** `msg` (אין עותק נפרד ל-c2) ⇐ `msg = "stop"`.

**4.** `c1.get()` ⇐ `"A:stop"`; `c2.get()` ⇐ `"B:stop"`.

**הפלט:** `A:stop B:stop`.""",
        {1: "c2.msg לא יוצר עותק פרטי – הוא דורס את המשתנה המשותף, ולכן גם c1 רואה stop.",
         2: "השינוי האחרון ל-msg היה stop, והוא משותף לשתיהן.",
         3: "msg קיבל ערך לפני ההדפסה (go ואז stop)."},
        "סטטי = עותק אחד לכולם: שינוי דרך אובייקט אחד נראה בכולם.", "איברים סטטיים"),
    mcq("StringBuffer מול String",
        r"""```java
StringBuffer sb = new StringBuffer("Java");
sb.append("Fun");
sb.delete(1, 3);
String s = "Java";
s.concat("Fun");
System.out.println(sb + " " + s);
```
מה הפלט? (`delete(start, end)` מוחק מהאינדקס `start` ועד לפני `end`.)""",
        ["`JaFun Java`", "`JavaFun JavaFun`", "`JaFun JavaFun`", "`Jun Java`"], 0,
        r"""- **StringBuffer** ניתן לשינוי: `append` ו-`delete` משנים את האובייקט עצמו.
- **String** לא ניתנת לשינוי: `concat` **מחזירה מחרוזת חדשה** ולא משנה את `s`. אם לא שומרים את התוצאה – היא הולכת לאיבוד.
- אינדקסים מתחילים מ-0.""",
        r"""**1.** `sb = "Java"` ⇐ `append("Fun")` ⇐ `"JavaFun"`.

**2.** `delete(1, 3)` מוחק את האינדקסים 1 ו-2: `J[a][v]aFun` ⇐ נשאר `"JaFun"`.

**3.** `s.concat("Fun")` מחזירה `"JavaFun"` חדשה, אבל לא שמרנו אותה ⇐ `s` נשארת `"Java"`.

**הפלט:** `JaFun Java`.""",
        {1: "s לא השתנתה – concat מחזירה מחרוזת חדשה ולא שמרנו אותה; וגם ה-delete מחק תווים מ-sb.",
         2: "ה-StringBuffer נכון, אבל s לא השתנתה.",
         3: "delete(1,3) מוחק את a ו-v (אינדקסים 1-2), לא שלושה תווים."},
        "StringBuffer משתנה במקום; String לעולם לא – מתודות שלה מחזירות מחרוזת **חדשה**.", "String ו-StringBuffer"),
]

# understanding only (his rule 19/11): no "compute this" questions in the lesson quiz
Q = [
    ("למה `double d = j;` (כש-j הוא int) עובר קומפילציה בלי cast?",
     ["כי double גדול יותר ויכול להכיל כל ערך int בלי לאבד מידע", "כי Java תמיד ממירה לבד בכל כיוון",
      "כי int ו-double הם אותו סוג", "כי j מאותחל לאפס"],
     0, "המרה מקטן לגדול היא implicit – אין סכנה לאבד מידע.", "המרת טיפוסים"),
    ("מה בעצם אומר המתכנת לקומפיילר כשהוא כותב `(int) d`?",
     ["\"אני יודע שאני עלול לאבד מידע (את השבר), ואני לוקח אחריות\"", "\"תעגל את d למספר השלם הקרוב\"",
      "\"תבדוק בזמן ריצה שאין שבר\"", "\"תשנה את הסוג של d ל-int לתמיד\""],
     0, "cast מפורש = הסכמה לאבד דיוק; השבר נחתך (לא מעוגל), ו-d עצמו לא משתנה.", "המרת טיפוסים"),
    ("למה `Car c = new Toyota();` תקין, אבל `Toyota t = c;` לא?",
     ["Car גבוה יותר בהיררכיה; מעבר מגבוה לנמוך דורש cast מפורש", "כי c ריק",
      "כי Toyota לא יורשת מ-Car", "כי אסור שני משתנים לאותו אובייקט"],
     0, "כמו בפרימיטיביים: מטה בהיררכיה = מגדול לקטן ⇐ `(Toyota) c`.", "המרת טיפוסים"),
    ("מה בודק `==` כששני הצדדים הם הפניות לאובייקטים?",
     ["אם שניהם מצביעים לאותו אובייקט בזיכרון", "אם התוכן של האובייקטים זהה",
      "אם שני האובייקטים מאותה מחלקה", "אם האובייקטים לא ריקים"],
     0, "השוואת כתובות; לתוכן משתמשים ב-equals.", "השוואת אובייקטים"),
    ("משתנה מסוג Employee מצביע לאובייקט שנבנה ב-`new VicePresident()`. מה יחזיר `getClass()`?",
     ["VicePresident – הסוג האמיתי של האובייקט", "Employee – הסוג של המשתנה", "Object", "Class"],
     0, "getClass מסתכל על האובייקט בזמן ריצה, כמו בדוגמה מהשיעור.", "getClass ו-instanceof"),
    ("למה נקבל \"non-static method init() cannot be referenced from a static context\" כשקוראים ל-init() מתוך main?",
     ["main סטטית, ומתודה סטטית יכולה לגשת רק לאיברים סטטיים", "כי init לא מחזירה ערך",
      "כי צריך לקרוא ל-init לפני main", "כי init מוגדרת אחרי main בקובץ"],
     0, "סטטי ⇐ רק סטטי; מופע ⇐ גם וגם.", "איברים סטטיים"),
    ("למה המרצה הגדיר את `sendMessage` כסטטית?",
     ["היא עובדת רק על המשתנה המשותף msg ולא על מכונית מסוימת", "כי היא מחזירה ערך",
      "כי רק מתודות סטטיות יכולות לקבל String", "כי סטטי רץ מהר יותר"],
     0, "מתודה שלא שייכת לאובייקט מסוים – קוראים לה דרך המחלקה: `Car.sendMessage(...)`.", "איברים סטטיים"),
    ("אחרי `cars = new Car[2];` – מה יש במערך?",
     ["שתי הפניות ריקות; כל מכונית צריך עוד לבנות ב-new Car()", "שתי מכוניות מוכנות",
      "שני אפסים", "מכונית אחת"],
     0, "בניית מערך של אובייקטים לא בונה את האובייקטים עצמם.", "מערך אובייקטים"),
    ("מה ההבדל בין String ל-StringBuffer?",
     ["StringBuffer ניתן לשינוי (append, delete); String לא משתנה אחרי שנבנתה", "אין הבדל",
      "String ניתנת לשינוי ו-StringBuffer לא", "StringBuffer מחזיק רק מספרים"],
     0, "String אינה ניתנת לשינוי; StringBuffer הוא mutable.", "String ו-StringBuffer"),
    ("למה יש לכל אובייקט ב-Java את toString() ו-getClass()?",
     ["כי כל מחלקה יורשת בסוף מ-Object, שמגדירה אותן", "כי צריך לכתוב אותן בכל מחלקה",
      "כי הן מתודות של String", "רק לאובייקטים של מחלקות עוטפות יש אותן"],
     0, "Object בראש ההיררכיה; כל מחלקה יורשת ממנה.", "Object"),
]

if __name__ == "__main__":
    check()
    data = {"title": "הרצאה 5: המרת טיפוסים, השוואת אובייקטים, getClass ו-instanceof, איברים סטטיים, Math/StringBuffer/מחלקות עוטפות",
            "chapter_md": CHAPTER.strip(), "summary_md": SUMMARY.strip(),
            "topics": ["המרת טיפוסים", "השוואת אובייקטים", "getClass ו-instanceof", "איברים סטטיים", "מערך אובייקטים",
                       "String ו-StringBuffer", "מחלקות עוטפות", "Object"],
            "glossary": [], "course_facts": [], "syllabus_covered": [], "exam_type": "mcq", "grade_weights": [],
            "homework": [], "exercises": EX,
            "questions": [{"question": q, "options": o, "correct": c, "explanation": e, "topic": t, "difficulty": 1}
                          for q, o, c, e, t in Q],
            "verification": {
                "fixes": ["נכתב על ידי Claude מהתמלול ומצילומי המסך (Gemini היה עמוס ובלי מכסה). הקוד של J7_cars הועתק מצילומי NetBeans.",
                          "המרצה אמר שמתודת מופע משוכפלת בזיכרון לכל אובייקט – תוקן: קוד של מתודה נשמר פעם אחת; משוכפלים רק משתני המופע.",
                          "המרצה אמר שאי אפשר להוסיף ערך פרימיטיבי ל-Vector – הוסף: מאז Java 5 יש autoboxing (v.add(10) עובד).",
                          "המרצה אמר 'get-string' – הכוונה ל-toString(). המרצה אמר 5/4=1.2 ותיקן ל-1.25.",
                          "הפלט של כל שאלה אמריקאית חושב ידנית; כשיש JDK, check() מריץ את התוכניות ומשווה."],
                "uncertain": ["גוף המתודה drive (הטמפרטורה 120 מעל מהירות 100) ו-checkEngine (גבול 150) לפי מה שנאמר בהקלטה – הערכים המדויקים לא נראו בצילום."]}}
    out = Path(__file__).resolve().parents[1] / "java-l5.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out, len(data["chapter_md"]))
