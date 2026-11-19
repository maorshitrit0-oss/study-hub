"""Java + micro week exercises in the EXAM FORMAT (his request 18/11/2026: "the exam is multiple choice - a question and
4 answers; I choose, then write the explanation in my notebook"). Every exercise of the week lists (weeks 1-4 Java,
1-3 micro) becomes: the question (with its code) + options א-ד; the solution = the answer + what to write in the
notebook + why the others are wrong. Every output was run: Java in javac 21 (mcq_1811/*.java), C in gcc (mcq_1811/m.c).
  python mcq_1811.py -> chapters/mcq-1811-java.json, mcq-1811-micro.json (publish inspect=exercises; "lock" keeps them)"""
import json
from pathlib import Path

L = "אבגד"
J = lambda c: "```java\n" + c.strip() + "\n```"  # noqa: E731
C = lambda c: "```c\n" + c.strip() + "\n```"  # noqa: E731


_SPOT = iter([0, 2, 1, 3, 2, 0, 3, 1] * 10)  # where the right answer lands, spread over א-ד


def mcq(id_, q, opts, ans, note, why_not):
    """opts: 4 strings; ans: index of the right one. The options are reordered so the answers spread over א-ד."""
    want = next(_SPOT)
    order = [i for i in range(4) if i != ans]
    order.insert(want, ans)                       # order[new position] = old index
    opts = [opts[i] for i in order]
    why_not = {order.index(i): w for i, w in why_not.items()}
    ans = want
    body = (q.strip() + "\n\n" + "\n\n".join(f"**{L[i]}.** {o}" for i, o in enumerate(opts))
            + "\n\n✍️ *לבחור תשובה, ואז לכתוב במחברת למה – ורק אחר כך לפתוח את הפתרון.*")
    sol = (f"### התשובה: **{L[ans]}** ✅\n\n**הדרך המלאה (כמו במחברת):**\n\n{note.strip()}\n\n**למה לא האחרות:**\n"
           + "\n".join(f"- **{L[i]}** – {w}" for i, w in why_not.items()))
    return {"id": id_, "question_md": body, "solution_md": sol, "exam_style": True, "lock": True}


JAVA = [
    mcq("6fee50e7-4dee-44bc-a7b3-60831b953487", "המשתמש מקליד `0`. מה ידפיס הקוד?\n\n" + J('''
int num = input.nextInt();
if (num >= 0) {
    System.out.println("Positive !");
} else if (num == 0) {
    System.out.println("Zero.");
} else {
    System.out.println("Negative !");
}'''), ["`Zero.`", "`Positive !`", "`Positive !` ואז `Zero.`", "שגיאת קומפילציה"], 1,
        "התנאים נבדקים **מלמעלה למטה**, ונכנסים רק לענף הראשון שמתקיים. $0\\ge0$ אמת ⇐ `Positive !`, ושאר הענפים מדולגים. "
        "הבאג: `>=` במקום `>` – הענף של `== 0` לעולם לא יגיע. (נבדק בהרצה.)",
        {0: "היה נכון רק אם התנאי הראשון היה `num > 0`.", 2: "`else if` לא רץ אחרי ענף שכבר התקיים.", 3: "הקוד תקין תחבירית."}),
    mcq("45496a5e-40c6-44b2-8207-4ea982812c4f", "הקלט: `-2`, אחריו `3`, ואז `1.5 2.5 4`. מה יודפס?\n\n" + J('''
int count;
do {
    count = input.nextInt();
    if (count <= 0) {
        System.out.println("Please enter a positive number.");
    }
} while (count <= 0);
double sum = 0;
for (int i = 1; i <= count; i++) {
    sum += input.nextDouble();
}
System.out.println("Sum = " + sum);
System.out.println("Average = " + sum / count);'''),
        ["`Sum = 8.0` ו-`Average = 2.6666666666666665`", "`Please enter a positive number.` ואז `Sum = 8.0` ו-`Average = 2.6666666666666665`",
         "`Please enter a positive number.` ואז `Sum = 8.0` ו-`Average = 2`", "`Sum = 6.0` ו-`Average = 2.0`"], 1,
        "`do-while` רץ פעם אחת לפחות: `-2` ⇐ הודעה וחוזר; `3` ⇐ יוצא. הלולאה קוראת 3 מספרים: $1.5+2.5+4=8.0$. "
        "`sum` הוא `double` ⇐ החילוק ממשי: $8/3=2.6666666666666665$. (נבדק בהרצה.)",
        {0: "שכח את ההודעה על `-2`.", 2: "החילוק לא בשלמים – `sum` הוא `double`.", 3: "קרא את `-2` כאחד המספרים."}),
    mcq("0293c40e-7d79-4a98-8156-834b0fa839ad", "בתוכנית הסכום והממוצע כתבו בטעות את תנאי החזרה כך. המשתמש עונה `y` בפעם הראשונה. "
        "כמה פעמים ירוץ החישוב?\n\n" + J('''
char again;
do {
    // ... the calculation ...
    again = input.next().charAt(0);
} while (again == 'y' && again == 'Y');'''), ["פעמיים", "עד שעונים `n`", "פעם אחת בלבד", "לולאה אינסופית"], 2,
        "תו אחד לא יכול להיות גם `'y'` **וגם** `'Y'` ⇐ התנאי תמיד שקר ⇐ `do-while` רץ פעם אחת ויוצא. "
        "הנכון: `||` (או). (נבדק בהרצה: סיבוב אחד.)",
        {0: "היה נכון עם `||`.", 1: "עם `&&` אין חזרה בכלל.", 3: "התנאי תמיד שקר, לא תמיד אמת."}),
    mcq("308ebd98-f41c-46d1-88ea-ccbe4ecc7eb7", "מה יהיה הפלט?\n\n" + J('''
String s1 = "Hello";
String s2 = new String("Hello");
System.out.print(s1 == s2);
System.out.print(" " + s1.equals(s2));'''), ["`true true`", "`false false`", "`false true`", "`true false`"], 2,
        "`==` משווה **הפניות**: `new` יוצר אובייקט חדש ⇐ `false`. `equals` משווה **תוכן** ⇐ `true`.",
        {0: "היה נכון בלי `new` (שני ליטרלים מאותו מאגר).", 1: "התוכן זהה.", 3: "הפוך."}),
    mcq("38d9cc8c-d0a3-45b8-bddf-107e4ffb07bf", "מה ידפיס הקוד?\n\n" + J('''
int b1 = -128;
int c1 = (b1 >>> 1);
int d1 = (b1 >> 1);
System.out.println(c1 + " " + d1);'''), ["`-64 -64`", "`64 -64`", "`2147483584 -64`", "`2147483584 2147483584`"], 2,
        "$-128$ = `0xFFFFFF80`. `>>>` מכניס **0** משמאל ⇐ `0x7FFFFFC0` $=2^{31}-64=2147483584$. "
        "`>>` מכניס את **סיבית הסימן** ⇐ $-64$. (נבדק בהרצה.)",
        {0: "`>>>` לא שומר סימן.", 1: "`>>>` על 32 סיביות, לא על 8.", 3: "`>>` כן שומר סימן."}),
    mcq("ffdb3a40-02ca-4f8e-823d-7cec4ad96378", "`int i = 10, j = 3, k = 0;` ואחריו `k = ++j + i;` – מה הערכים של `i, j, k`?",
        ["`10, 3, 13`", "`10, 4, 14`", "`11, 4, 15`", "`10, 4, 13`"], 1,
        "`++j` מגדיל **לפני** השימוש: $j=4$, ואז $k=4+10=14$. `i` לא משתנה. (נבדק בהרצה.)",
        {0: "`++j` כן משנה את `j`.", 2: "`i` לא קודם.", 3: "קדם-קידום משתמש בערך **החדש** (4)."}),
    mcq("65da62fc-f2b1-4290-affb-ea899265e4ef", "`int x = 5;` ואחריו `System.out.println(x++ + ++x);` – מה מודפס, ומה ערך `x` בסוף?",
        ["`11`, `x=7`", "`12`, `x=7`", "`12`, `x=6`", "`10`, `x=5`"], 1,
        "משמאל לימין: `x++` נותן **5** ואז $x=6$; `++x` מגדיל ל-7 ונותן **7** ⇐ $5+7=12$, $x=7$. (נבדק בהרצה.)",
        {0: "`++x` נותן את הערך החדש, 7.", 2: "גם `++x` מגדיל.", 3: "שני האופרטורים משנים את `x`."}),
    mcq("1719a9c8-588a-4006-a9f5-c0c524b84fb7", "`int sum = 7, count = 2;` – מה מדפיסות שלוש השורות?\n\n" + J('''
System.out.println(sum / count);
System.out.println((double) sum / count);
System.out.println((double) (sum / count));'''), ["`3.5` `3.5` `3.5`", "`3` `3.5` `3.5`", "`3` `3.5` `3.0`", "`3.0` `3.5` `3.0`"], 2,
        "(1) שלם/שלם ⇐ חילוק שלמים: `3`. (2) ההמרה על `sum` **לפני** החילוק ⇐ `3.5`. (3) הסוגריים מחשבים קודם `7/2=3` ורק אז "
        "ממירים ⇐ `3.0`. (נבדק בהרצה.)",
        {0: "השורה הראשונה בשלמים.", 1: "בשלישית ההמרה **אחרי** החילוק.", 3: "בראשונה אין `double` – מודפס `3`."}),
    mcq("58304176-2823-4313-8dcd-b3aceb420c68", "מה ידפיס הקוד?\n\n" + J('''
static boolean isPrime(int num) {
    if (num <= 1) {
        return false;
    }
    for (int i = 2; i < Math.sqrt(num); i++) {
        if (num % i == 0) {
            return false;
        }
    }
    return true;
}
// main:
System.out.println(9 + (isPrime(9) ? " is prime." : " is not prime."));
System.out.println(7 + (isPrime(7) ? " is prime." : " is not prime."));'''),
        ["`9 is not prime.` / `7 is prime.`", "`9 is prime.` / `7 is prime.`", "`9 is not prime.` / `7 is not prime.`", "`9 is prime.` / `7 is not prime.`"], 1,
        "ל-9: $\\sqrt9=3$, והלולאה רצה רק כל עוד $i<3$ ⇐ בודקת רק $i=2$; $9\\%2\\ne0$ ⇐ מחזירה `true` – **באג**. "
        "התיקון: `i <= Math.sqrt(num)`. ל-7 התשובה נכונה. (נבדק בהרצה.)",
        {0: "זו התשובה של הקוד **המתוקן** (`<=`).", 2: "7 ראשוני, ואין לו מחלק בבדיקה.", 3: "הפוך."}),
    mcq("9379c0e8-b0ee-48de-910b-190e6347cf74", "הקלט: `2.5` ואז `-1.2`. מה ידפיס הקוד?\n\n" + J('''
int start = (int) Math.ceil(Math.min(a, b));
int end = (int) Math.floor(Math.max(a, b));
for (int i = start; i <= end; i++) {
    System.out.print(i + " ");
}'''), ["`-1 0 1 2`", "`-2 -1 0 1 2`", "`-1 0 1 2 3`", "לא מודפס כלום, כי `a > b`"], 0,
        "`min` ו-`max` מסדרים את הקצוות: $[-1.2,\\,2.5]$. `ceil(-1.2)=-1` (עיגול **למעלה** = לכיוון 0 במספר שלילי), "
        "`floor(2.5)=2` ⇐ `-1 0 1 2`. (נבדק בהרצה.)",
        {1: "`ceil(-1.2)` הוא $-1$, לא $-2$.", 2: "`floor(2.5)` הוא 2.", 3: "`min/max` מטפלים בסדר."}),
    mcq("262a6118-3c9a-41cd-8f84-ae4796a377ec", "מה יקרה כשמריצים את הקוד?\n\n" + J('''
int[] numbers = new int[22];
for (int i = 0; i <= numbers.length; i++) {
    numbers[i] = i;
}
System.out.println(numbers[21]);'''), ["מודפס `21`", "מודפס `22`", "שגיאת קומפילציה", "חריגה בזמן ריצה: `ArrayIndexOutOfBoundsException`"], 3,
        "האינדקסים הם $0..21$ (`length` = 22). בגלל `<=` הלולאה מגיעה ל-`i = 22` ⇐ `numbers[22]` לא קיים ⇐ חריגה, "
        "עוד לפני ההדפסה. התיקון: `i < numbers.length`. (נבדק בהרצה.)",
        {0: "ההדפסה לא מגיעה – החריגה קודמת.", 1: "אין תא 22.", 2: "המהדר לא בודק גבולות מערך."}),
    mcq("482b5658-f339-436f-928e-12dd955ca82b", "מריצים `java SumArgs 1.1 2.2 3`. מה יודפס?\n\n" + J('''
double sum = 0;
for (int i = 0; i < args.length; i++) {
    sum += Double.parseDouble(args[i]);
}
System.out.println("Sum = " + sum);'''), ["`Sum = 6.3`", "`Sum = 6.300000000000001`", "`Sum = 1.12.23`", "`NumberFormatException`"], 1,
        "`args` = מחרוזות, ו-`parseDouble` ממיר למספרים. 1.1 ו-2.2 לא נשמרים בבינארי בדיוק ⇐ שגיאת עיגול קטנה: "
        "`6.300000000000001`. (נבדק בהרצה.)",
        {0: "`double` לא מדפיס 6.3 כאן בגלל העיגול.", 2: "זה היה קורה בלי `parseDouble` (שרשור).", 3: "כל הארגומנטים מספרים חוקיים."}),
    mcq("89c8155c-e683-4904-9514-a6d8cacea7e8", "במחלקה `Circle` (רדיוס, צבע, מונה סטטי שעולה בבנאי, `setRadius`, `area`, `getCount`). מה יודפס?\n\n" + J('''
Circle a = new Circle(1, "red");
Circle b = new Circle(2, "blue");
Circle c = b;
c.setRadius(3);
System.out.println(Circle.getCount() + " " + (int) b.area());'''), ["`3 12`", "`2 28`", "`3 28`", "`2 12`"], 1,
        "`Circle c = b;` **לא** יוצר אובייקט – רק הפניה נוספת לאותו מעגל ⇐ הבנאי רץ פעמיים ⇐ `count = 2`. "
        "`c.setRadius(3)` משנה את **אותו** אובייקט של `b` ⇐ $\\pi\\cdot3^2=28.27$ ⇐ `(int)` חותך ל-28. (נבדק בהרצה.)",
        {0: "אין `new` שלישי, והרדיוס של `b` השתנה.", 2: "אין `new` שלישי.", 3: "`c` ו-`b` הם אותו אובייקט."}),
    mcq("3da55b01-5a08-4553-99c6-75b4ac069a0f", "מה יודפס?\n\n" + J('''
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
}'''), ["`2 1 3`", "`3 3 3`", "`2 1 1`", "`1 1 3`"], 0,
        "`static` = עותק **אחד** משותף ⇐ סופר את כל 3 הקריאות. `mine` = עותק בכל אובייקט ⇐ `a`: 2, `b`: 1. (נבדק בהרצה.)",
        {1: "`mine` לא משותף.", 2: "`total` משותף לכל האובייקטים.", 3: "`a.add()` נקרא פעמיים."}),
    mcq("d2a1a459-baac-431d-98c8-5693d0178dfd", "מה יודפס?\n\n" + J('''
static void change(int x, int[] arr) {
    x = 100;
    arr[0] = 100;
}
// main:
int n = 5;
int[] a = {5, 6};
change(n, a);
System.out.println(n + " " + a[0]);'''), ["`100 100`", "`5 5`", "`5 100`", "`100 5`"], 2,
        "Java מעבירה **ערך**: ל-`int` מועתק המספר ⇐ `n` נשאר 5. למערך מועתקת **ההפניה** ⇐ `arr[0]` משנה את אותו מערך ⇐ 100. (נבדק בהרצה.)",
        {0: "`x` הוא עותק.", 1: "שינוי תוכן המערך כן נראה בחוץ.", 3: "הפוך."}),
    mcq("d52984f9-2732-4514-82ce-da5bf64c0ef2", "מה יודפס?\n\n" + J('''
static void swap(int[] a) { int t = a[0]; a[0] = a[1]; a[1] = t; }
static void swapNew(int[] a) { a = new int[]{9, 9}; }
// main:
int[] p = {1, 2};
swap(p);
swapNew(p);
System.out.println(p[0] + "," + p[1]);'''), ["`1,2`", "`2,1`", "`9,9`", "`2,2`"], 1,
        "`swap` משנה **תאים** של המערך עצמו ⇐ `{2,1}`. `swapNew` מכוון את ה**עותק** המקומי `a` למערך חדש – `p` לא זז. (נבדק בהרצה.)",
        {0: "`swap` כן הצליח.", 2: "`a = new ...` לא משנה את `p`.", 3: "יש משתנה עזר `t`."}),
    mcq("e31b24f2-804f-4c30-98a4-1e111aec8c0e", "מה יודפס?\n\n" + J('''
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
}'''), ["`3 3 13`", "`3 1 11`", "`2 1 11`", "`3 1 10`"], 1,
        "ב-`f` ה-`x` המקומי **מסתיר** את השדה ⇐ מודפס 3, והשדה נשאר 1. הלולאה מוסיפה $0+10$ ⇐ 11. (נבדק בהרצה.)",
        {0: "המקומי לא משנה את השדה.", 2: "`x++` רץ לפני ההדפסה.", 3: "השדה התחיל מ-1: $1+0+10=11$."}),
]

MICRO = [
    mcq("912bcbdb-5a64-4493-bbfc-a2616cad6fe3", "`uint8_t reg = 0x5A;` – איזו שורה **מדליקה את ביט 0 ומכבה את ביט 3** בלי לגעת בשאר, ומה התוצאה?",
        ["`reg = (reg | 0x08) & ~0x01;` ⇐ `0x5A`", "`reg = (reg | 0x01) & ~0x08;` ⇐ `0x53`", "`reg = reg & 0x01 | ~0x08;` ⇐ `0xF7`", "`reg = (reg & 0x01) | 0x08;` ⇐ `0x08`"], 1,
        "הדלקה: `| 0x01` (מסכה עם 1 בביט 0). כיבוי: `& ~0x08` (שלילת המסכה: 0 רק בביט 3). "
        "`0x5A`=`0101 1010` ⇐ `0101 1011` ⇐ `0101 0011` = `0x53`. (נבדק ב-gcc.)",
        {0: "הפוך: מדליק 3 ומכבה 0.", 2: "קדימות: `&` לפני `|`, והשלילה מדליקה כמעט הכל.", 3: "`& 0x01` מוחק את כל שאר הביטים."}),
    mcq("0c2c2376-10f2-486c-87db-3de51528e952", "בית הכלב: ביט 7 מין, ביטים 6–2 גיל, ביט 1 שמח, ביט 0 רעב. `dog = 0xB6`. מה מחזיר ה-getter של הגיל `(dog >> 2) & 0x1F`?",
        ["45", "22", "13", "54"], 2,
        "`0xB6` = `1011 0110`. הזזה ב-2: `0010 1101`; `& 0x1F` (5 ביטים) מוריד את ביט המין ⇐ `01101` = **13**. "
        "(ובאותו בית: מין 1, שמח 1, רעב 0.) (נבדק ב-gcc.)",
        {0: "בלי `& 0x1F` – כולל את ביט המין.", 1: "הזזה ב-3 במקום 2.", 3: "בלי הזזה ובלי מסכה נכונה."}),
    mcq("57b69b82-02d2-4b92-af55-6d02cb24642a", "מה ערכי `reg` אחרי ה-XOR הראשון ואחרי השני?\n\n" + C('''
uint8_t reg = 0x05;               /* 00000101 */
uint8_t mask = (uint8_t)(1U << 2);
reg = reg ^ mask;
reg = reg ^ mask;'''), ["`0x01` ואז `0x05`", "`0x01` ואז `0x01`", "`0x09` ואז `0x05`", "`0x04` ואז `0x00`"], 0,
        "המסכה `0000 0100`. XOR **הופך** את ביט 2: `0101`⇐`0001` (0x01). XOR שני הופך בחזרה ⇐ `0x05`. "
        "$A\\oplus B\\oplus B=A$ – XOR כפול מחזיר את המקור. (נבדק ב-gcc.)",
        {1: "XOR לא \"נדבק\" – הוא הופך שוב.", 2: "ביט 2 היה דולק, לכן נכבה.", 3: "זה AND, לא XOR."}),
    mcq("e24e192e-1721-496a-99da-b2e7128ddde9", "`#define AGE_BITS 5` ו-`#define MAX_AGE 1 << AGE_BITS - 1` (בלי סוגריים). מה הערך של `MAX_AGE`?",
        ["31", "16", "32", "4"], 1,
        "בקדם-מעבד זו החלפת טקסט: `1 << 5 - 1`. החיסור **קודם** להזזה ⇐ `1 << 4` = **16**. "
        "הנכון: `#define MAX_AGE ((1 << AGE_BITS) - 1)` = 31. (gcc גם מזהיר על זה.)",
        {0: "זה עם הסוגריים.", 2: "החיסור כן מתבצע – לפני ההזזה.", 3: "`1<<4` הוא 16."}),
    mcq("9df26f09-e09c-48b3-a2ca-26a2e76765fc", "`unsigned char dog = 0x83;` ואחריו `dog_set_is_happy(&dog, 0);` (ביט 1, מכבה עם `&= ~HAPPY_MASK`). מה `dog`?",
        ["`0x83`", "`0x02`", "`0x81`", "`0x7D`"], 2,
        "`0x83` = `1000 0011`. `~HAPPY_MASK` = `1111 1101` ⇐ רק ביט 1 נכבה ⇐ `1000 0001` = `0x81`. (נבדק ב-gcc.)",
        {0: "ביט 1 היה דולק ונכבה.", 1: "זו המסכה עצמה.", 3: "זה `~0x82` – מחק ביטים אחרים."}),
    mcq("553159a3-4484-466f-a0e1-0cc3cbc6224a", "`unsigned char dog = 0xFF;` ואחריו `dog_set_age(&dog, 5);` (גיל בביטים 2–6). מה `dog` **עם** האיפוס `&= ~AGE_MASK`, ומה **בלי** האיפוס?",
        ["`0x97` / `0xFF`", "`0x97` / `0x97`", "`0x14` / `0xFF`", "`0xFF` / `0x97`"], 0,
        "עם איפוס: `0xFF & ~0x7C` = `0x83`, ואז `| (5<<2)` = `| 0x14` ⇐ `0x97`. בלי איפוס: `0xFF | 0x14` = `0xFF` – "
        "הגיל הישן (31) נשאר. לכן **קודם לאפס, אחר כך להציב**. (נבדק ב-gcc.)",
        {1: "בלי איפוס הביטים הישנים נשארים.", 2: "האיפוס מוחק רק את שדה הגיל, לא את כל הבית.", 3: "הפוך."}),
    mcq("f61b71ba-9a84-4cc1-bf79-21bc747b0263", "בית הכלב (ביט 0 רעב, 1 שמח, 2–6 גיל, 7 מין). איזו שורת מסכות נכונה?",
        ["`HUNGRY=0x01, HAPPY=0x02, AGE=0x7C, SEX=0x80`", "`HUNGRY=0x01, HAPPY=0x02, AGE=0x1F, SEX=0x80`", "`HUNGRY=0x00, HAPPY=0x01, AGE=0x7C, SEX=0x07`", "`HUNGRY=0x01, HAPPY=0x04, AGE=0x3E, SEX=0x80`"], 0,
        "מסכה = `1 << ביט`. גיל: 5 אחדות (`0x1F`) **מוזזות** לביט 2 ⇐ `0x1F << 2 = 0x7C` (`0111 1100`). מין: `1 << 7 = 0x80`. (נבדק ב-gcc.)",
        {1: "`0x1F` לא מוזז למקום של השדה.", 2: "מסכה היא `1<<n`, לא מספר הביט.", 3: "שמח הוא ביט 1 ⇐ `0x02`; הגיל מתחיל בביט 2."}),
    mcq("1590cbbc-bc83-423d-af75-0f4e88feb3bd", "מה הערך הבינארי הסופי של `x`?\n\n" + C('''
uint8_t x = 0b01101101;
x = (x & ~(1U << 2)) | (1U << 7);'''), ["`11101001`", "`11101101`", "`01101001`", "`10101101`"], 0,
        "`& ~(1<<2)` מכבה את ביט 2: `0110 1001`. `| (1<<7)` מדליק את ביט 7: `1110 1001`. (נבדק ב-gcc: `0xE9`.)",
        {1: "ביט 2 לא כובה.", 2: "ביט 7 לא הודלק.", 3: "נכבה ביט אחר."}),
    mcq("968bbeb5-fd52-4068-be7c-1afe2fdfbceb", "כפתור בין GPIO 14 לאדמה, `pinMode(14, INPUT_PULLUP);`. הקוד:\n\n" + C('''
if (digitalRead(14) == HIGH) {
    digitalWrite(25, HIGH);
    digitalWrite(2, HIGH);
} else {
    digitalWrite(25, LOW);
    digitalWrite(2, LOW);
}''') + "\n\nמתי הלדים דולקים?", ["כשהכפתור לחוץ", "כשהכפתור **משוחרר**", "תמיד", "אף פעם"], 1,
        "עם `INPUT_PULLUP`: משוחרר = HIGH (הנגד הפנימי מושך למעלה), לחוץ = LOW (חיבור לאדמה). הקוד בודק `HIGH` ⇐ "
        "הלדים דולקים כש**לא** לוחצים. כדי שיידלקו בלחיצה: `== LOW`.",
        {0: "בלחיצה נקרא LOW.", 2: "הקריאה משתנה עם הכפתור.", 3: "במצב משוחרר התנאי מתקיים."}),
    mcq("19ec7fa7-7a62-4c11-a460-fa719aa13331", "Debounce של 20 ms עם `millis()`: הקריאה משתנה ל-LOW ב-1000 ms, קופצת ל-HIGH ב-1003, חוזרת ל-LOW ב-1005 ונשארת LOW. "
        "מתי יודפס `pressed`?", ["ב-1000 ms", "ב-1005 ms", "ב-1020 ms", "ב-1025 ms"], 3,
        "כל שינוי בקריאה **מאפס** את הטיימר (`lastChange`). השינוי האחרון ב-1005 ⇐ המצב מתקבל רק כשעברו 20 ms יציבים: $1005+20=1025$.",
        {0: "זה עוד לפני היציבות – בדיוק מה ש-debounce מונע.", 1: "רק מתחיל לספור.", 2: "הטיימר אופס ב-1003 וב-1005."}),
    mcq("1b38eb7a-1d80-4f7c-8bf7-7f18b7b31e93", "ממיר ADC של 12 ביט עם מתח ייחוס 3.3 V (ESP32). מה מספר הרמות וגודל המדרגה?",
        ["4096 רמות, 0.806 mV", "4096 רמות, 0.806 V", "1024 רמות, 3.22 mV", "12 רמות, 0.275 V"], 0,
        "רמות $=2^{12}=4096$. מדרגה $=3.3/4096=0.000806\\,V=0.806\\,mV$. (3.22 mV הוא של ממיר 10 ביט.)",
        {1: "טעות ביחידות – פי 1000.", 2: "זה ממיר של 10 ביט.", 3: "מספר הרמות הוא $2^n$, לא $n$."}),
    mcq("7e1126a3-dbe3-4a88-bb3f-1ebc50ad4e79", "כפתור מחובר בין GPIO 4 ל-GND, `pinMode(4, INPUT_PULLUP);`. מה ייקרא מרגל 4?",
        ["משוחרר HIGH, לחוץ LOW – הנגד הפנימי מושך למתח כשאין חיבור לאדמה",
         "משוחרר LOW, לחוץ HIGH – `INPUT_PULLUP` הופך את הערך בתוכנה",
         "תמיד HIGH – הנגד הפנימי חזק מהאדמה", "לא מוגדר בשני המצבים – צריך נגד חיצוני"], 0,
        "הנגד הפנימי (עשרות קילו-אוהם) מחבר את הפין ל-3.3V. משוחרר ⇐ אין זרם ⇐ HIGH. לחוץ ⇐ חיבור ישיר לאדמה \"מנצח\" ⇐ LOW.",
        {1: "אין היפוך בתוכנה – ההיפוך מהחיווט.", 2: "הנגד חלש בכוונה.", 3: "בדיוק בשביל זה יש pull-up."}),
]

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for name, qs in (("java", JAVA), ("micro", MICRO)):
        (root / f"mcq-1811-{name}.json").write_text(json.dumps(qs, ensure_ascii=False, indent=1), encoding="utf-8")
        print(name, len(qs), "answers:", "".join(L[int(q['solution_md'].split('**')[1] == 'x')] if False else q['solution_md'][15] for q in qs))
