# ☕ דף עזר Java - תבניות ותחביר

> דף אחד דו-צדדי למבחן. כל תבנית = "איך כותבים", עם הסבר קצר. מתעדכן לבד כשנוספים שיעורים.

### 1. שלד של תוכנית, הידור והרצה
```java
public class Main {                        // שם הקובץ חייב להיות Main.java
    public static void main(String[] args) {   // כאן התוכנית מתחילה
        System.out.println("שלום");           // הדפסה + ירידת שורה
    }
}
```
`javac Main.java` ← נוצר `Main.class` (bytecode) ← `java Main` (ה-JVM מריץ). `print` = בלי ירידת שורה. `//` הערה לשורה, `/* ... */` הערה לכמה שורות. כל פקודה נגמרת ב-`;`.

### 2. טיפוסים ומשתנים
| טיפוס | מה | דוגמה |
|---|---|---|
| `int` / `long` | שלם (32 / 64 ביט) | `int n = 10;` |
| `double` | עשרוני | `double d = 2.5;` |
| `char` | תו אחד, `' '` | `char c = 'A';` |
| `boolean` | `true` / `false` | `boolean ok = n > 5;` |
| `String` | טקסט, `" "` (מחלקה, לא פרימיטיבי) | `String s = "Hi";` |

קבוע: `final int MAX = 100;` · המרה: `(int) 3.9` ← 3 (חיתוך) · `Integer.parseInt("42")` ← 42 · `String.valueOf(42)` ← "42"

### 3. אופרטורים
- חשבון: `+ - * / %` · ⭐ `int/int` = חילוק שלמים: `7/2`←3, `7/2.0`←3.5 · `%` שארית: `7%2`←1 (זוגי: `n%2==0`)
- השוואה: `== != < > <= >=` · לוגי: `&&` (וגם) `||` (או) `!` (לא)
- קיצורים: `x++` (x=x+1), `x += 3` (x=x+3) · מותנה: `max = (a>b) ? a : b;`
- ⭐ `"x=" + 5 + 3` ← "x=53" (שרשור משמאל לימין); `"x=" + (5+3)` ← "x=8"

### 4. מחרוזות (String)
`s.length()` אורך · `s.charAt(i)` התו במקום i (מ-0) · `s.substring(a,b)` מ-a עד b-1 · `s.indexOf("x")` מיקום (או -1) · `s.toUpperCase()` · ⭐ השוואת תוכן: `s.equals(t)` (לא `==`, שמשווה כתובות)

### 5. קלט מהמקלדת
```java
import java.util.Scanner;                  // בראש הקובץ, לפני class
Scanner in = new Scanner(System.in);       // אובייקט שקורא מהמקלדת
int n = in.nextInt();                      // שלם · nextDouble() עשרוני · next() מילה · nextLine() שורה
```

### 6. תנאים
```java
if (grade >= 90) {              // אם
    System.out.println("A");
} else if (grade >= 60) {       // אחרת אם
    System.out.println("Pass");
} else {                        // אחרת
    System.out.println("Fail");
}
switch (day) {                  // בחירה לפי ערך
    case 1:  System.out.println("Sun"); break;   // break - לצאת, אחרת ממשיך ל-case הבא
    default: System.out.println("?");            // אם אף case לא התאים
}
```

### 7. לולאות
```java
for (int i = 0; i < n; i++) { ... }     // התחלה; תנאי להמשך; צעד - מספר פעמים ידוע
while (x > 0) { ... }                   // כל עוד התנאי נכון (אולי 0 פעמים)
do { ... } while (x > 0);               // לפחות פעם אחת
for (int v : arr) { ... }               // for-each: כל איבר במערך
```
`break` יציאה מהלולאה · `continue` דילוג לסיבוב הבא

### 8. מערכים
```java
int[] a = new int[5];          // 5 תאים, כולם 0; אינדקסים 0..4
int[] b = {3, 7, 1};           // יצירה עם ערכים
a.length                       // אורך (בלי סוגריים!)  ·  a[a.length] ← שגיאה ArrayIndexOutOfBounds
int[][] m = new int[3][4];     // דו-ממדי: 3 שורות, 4 עמודות; m[i][j]
```

### 9. מתודה (פונקציה)
```java
public static int sum(int a, int b) {   // מחזירה int, מקבלת שני int
    return a + b;                       // return - מחזירה ערך ויוצאת
}
int s = sum(3, 4);                      // קריאה ← 7
```
`void` = לא מחזירה ערך · אותו שם עם פרמטרים שונים = **overloading** · פרמטרים פרימיטיביים מועברים כעותק (שינוי בפנים לא משנה בחוץ)

### 10. ⭐ תבנית מחלקה (class)
```java
public class Student {
    private String name;               // שדות (fields): המידע של כל אובייקט; private = רק בתוך המחלקה
    private int grade;
    private static int count = 0;      // static: משותף לכל האובייקטים

    public Student(String name, int grade) {   // בנאי (constructor): אותו שם כמו המחלקה, בלי טיפוס החזרה
        this.name = name;              // this.name = השדה; name = הפרמטר
        this.grade = grade;
        count++;
    }
    public Student() { this("none", 0); }     // בנאי ברירת מחדל שקורא לבנאי השני

    public String getName() { return name; }  // getter - קריאת שדה
    public void setGrade(int g) {             // setter - שינוי שדה עם בדיקה
        if (g >= 0 && g <= 100) grade = g;
    }
    @Override
    public String toString() {                // מה יודפס ב-println(obj)
        return name + ": " + grade;
    }
}
Student s = new Student("Maor", 90);          // יצירת אובייקט: new + קריאה לבנאי
System.out.println(s);                        // ← Maor: 90 (בזכות toString)
```
**אנקפסולציה:** שדות `private` + גישה דרך get/set. `public` כולם · `protected` מחלקה, יורשים ו-package · בלי מילה = package · `private` רק המחלקה.

### 11. ירושה ופולימורפיזם
```java
public class GradStudent extends Student {    // יורשת את כל מה ש-Student
    private String thesis;
    public GradStudent(String n, int g, String t) {
        super(n, g);                           // קריאה לבנאי של האב - חייבת להיות שורה ראשונה
        thesis = t;
    }
    @Override
    public String toString() { return super.toString() + " (" + thesis + ")"; }  // דריסה + שימוש בגרסת האב
}
Student p = new GradStudent("Dana", 95, "AI");   // משתנה מסוג אב, אובייקט מסוג בן
p.toString();                                     // ⭐ רצה הגרסה של GradStudent (dynamic binding)
```
`abstract class` - אי אפשר `new`; מתודה `abstract` בלי גוף, הבן חייב לממש · `interface` - רק "מה" (חתימות); `class A implements I` · `instanceof` - בדיקת סוג: `if (p instanceof GradStudent)`

### 12. חריגות (exceptions)
```java
try {
    int x = 10 / 0;                    // זורק ArithmeticException
} catch (ArithmeticException e) {      // תופס ומטפל
    System.out.println("Error: " + e.getMessage());
} finally { ... }                      // רץ תמיד
throw new IllegalArgumentException("bad");   // לזרוק בעצמנו
```

### טעויות נפוצות
- `=` (השמה) במקום `==` (השוואה) בתוך `if`.
- `s1 == s2` במקום `s1.equals(s2)` למחרוזות.
- `i <= a.length` בלולאה ← חריגה; נכון: `i < a.length`.
- חילוק שלמים: `(a+b)/2` כש-a,b הם `int` זורק את החצי.
- `;` אחרי `if (...)` או `for (...)` - הגוף לא שייך לתנאי.
- שם הקובץ ≠ שם המחלקה ה-`public`.
