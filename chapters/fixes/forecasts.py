"""🎯 Expected exam per course (his request 09/11/2026): from the past exams read so far; exercise ids from the cores.
python forecasts.py -> chapters/<course>_forecast.json. Updated weekly (the Saturday core task)."""
import json
from pathlib import Path

CH = Path(__file__).resolve().parents[1]
UPDATED = "15/11/2026"


def ids(core, *prefixes):
    d = json.loads((CH / f"{core}_core.json").read_text(encoding="utf-8"))
    full = {p["id"] for w in d["weeks"].values() for p in w}
    out = []
    for pre in prefixes:
        hit = [x for x in full if x.startswith(pre)]
        assert len(hit) == 1, (core, pre)
        out.append(hit[0])
    return out


def sec(title, chance, why, taught=True, points=None, tip=None, ex=()):
    return {"title": title, "chance": chance, "why": why, "taught": taught, "points": points, "tip": tip, "exercise_ids": list(ex)}


F = {}

F["waves"] = ("גלים ומערכות", {
    "format": "שאלות פתוחות: שאלת גל מישורי בפגיעה אלכסונית (40-50 נק׳) + קווי תמסורת + פרמטרי קו.",
    "basis": "מבחני 20.03.24 ו-25.07.24 מהדרייב, ומה שנלמד עד הרצאה 4 ותרגול 4",
    "sections": [
        sec("גל מישורי בפגיעה אלכסונית (TE / TM) בממשק – זוויות, Γ, T, שדות, ברוסטר וזווית קריטית", 95, "הופיע כשאלה 1 בשני המבחנים האחרונים, 40-50 נקודות. TM, זווית ברוסטר וזווית קריטית נלמדו בתרגול 4.", True, 45,
            "קודם k, η, λ בכל תווך; אחר כך סנל; אחר כך Γ ו-T של TE; ובסוף השדות המלאים עם k̂ אלכסוני.",
            ids("waves", "c5ef4b9c", "0f49ad90", "b2dd7932", "44ec295a")),
        sec("קווי תמסורת – Γ, Zin, VSWR, סטאב / סמית' או דיאגרמת קפיצות", 90, "שאלה 2 בשני המבחנים. התחיל בהרצאה 4 (מודל רכיבים מפולגים); החישובים עצמם – בהרצאות הבאות.", False, 30),
        sec("הספק וצפיפות הספק (פויינטינג) דרך משטח", 70, "סעיף כמעט קבוע בשאלת הגל.", True, 10, None, ids("waves", "2cb89521", "feb73418")),
        sec("פרמטרי קו (L, C) לקו קואקסיאלי / דו-תילי", 60, "סעיף קצר שחוזר.", False, 10),
        sec("תווך מוליך – α, β, עומק חדירה", 50, "מופיע כסעיף בשאלת הגל.", True, 10, None, ids("waves", "c13181f7", "0a6cb812")),
        sec("קיטוב – סוג וזווית אליפסה", 40, "המבחן מגדיר קיטוב TE; שאלת קיטוב מלאה פחות נפוצה.", True, 10, None, ids("waves", "a26af07a", "3875244a")),
    ]})

F["micro"] = ("מיקרו", {
    "format": "90 דקות, בלי דף נוסחאות: 6 שאלות אמריקאיות (10 נק׳) + 2 שאלות הבנת קוד (20 נק׳).",
    "basis": "מועד א׳ ומועד ב׳ תשפ״ו",
    "sections": [
        sec("פעולות ביטים ומסכות (XOR, ניקוי/הדלקה, שדות)", 95, "בשני המבחנים – שאלות 1-2.", True, 20,
            "לכתוב כל ערך בבינארי (8 ביט) לפני שמחשבים.", ids("micro", "e161f6d5", "1590cbbc", "57b69b82", "c0f71e7d")),
        sec("הבנת קוד: פסיקות ו-volatile", 90, "שאלת קוד של 20 נקודות בשני המבחנים.", True, 20, None, ids("micro", "cf42a626", "19ec7fa7")),
        sec("GPIO ו-INPUT_PULLUP (לחוץ = LOW)", 90, "שאלה 2 במועד ב׳.", True, 10, None, ids("micro", "7e1126a3", "2d31f517")),
        sec("ADC – רזולוציה והנחתה", 85, "שאלה 4 במועד א׳ ושאלה 5 במועד ב׳.", True, 10, None, ids("micro", "7a12cfef", "70f90662")),
        sec("PWM – תדר, רזולוציה, duty", 80, "שאלה אמריקאית קבועה.", False, 10),
        sec("UART – באוד, מסגרת", 70, "הופיע במבחנים.", False, 10),
        sec("הבנת קוד: I2C", 70, "שאלת קוד של 20 נק׳ במבחן.", False, 20),
        sec("Watchdog (WDT)", 60, "שאלה אמריקאית.", False, 10),
    ]})

F["digital"] = ("^מעגלים ספרתיים", {
    "format": "שעתיים, רב-ברירה עם הנמקה במחברת, חומר פתוח מודפס.",
    "basis": "מבחני קיץ תשפ״ג (28.9.23) ויולי 2024, ומה שנלמד עד הרצאה 4 (מהפכי NMOS)",
    "sections": [
        sec("שולי רעש ומתחים של מהפך (VOH, VOL, VIH, VIL, VM)", 95, "שאלה ראשונה בשני המבחנים.", True, None,
            "לזהות את סוג המהפך (נגד / NMOS / CMOS) ואז את התחום של כל טרנזיסטור בכל נקודה.", ids("digital", "73492580", "eca95ac1")),
        sec("מאמץ לוגי – F, G, H, h אופטימלי", 85, "שאלה בשני המבחנים. עוד לא נלמד בהרצאה (רק במחברת המתרגל, שמחכה להרצאה על מידוד).", False, None, None, ids("digital", "3ae49d34", "7367dda3", "0f6df12f")),
        sec("NMOS כנגד (Ron) ותחומי עבודה", 70, "שאלה 1 ביולי 2024. נלמד בהרצאות 3-4 (תחומי עבודה, מהפכי NMOS).", True, None, None, ids("digital", "aea4429f")),
        sec("הספק סטטי ודינמי", 70, "שאלות 3-4 בתשפ״ג.", True, None, None, ids("digital", "42ead578")),
        sec("השהיות (tPLH, tPHL)", 60, "חוזר בשאלות המהפך.", True, None, None, ids("digital", "e9a1f688")),
        sec("לוגיקת מעבר (PTL) ואפקט המצע", 60, "שאלה 2 בתשפ״ג.", False),
        sec("שער דינמי / NP-CMOS – איזו פונקציה", 50, "שאלה 4 ביולי 2024.", False),
        sec("רשת Pull-Down לפונקציה", 50, "נדרש לשאלת השער הדינמי. עוד לא נלמד (CMOS בהרצאות הבאות).", False, None, None, ids("digital", "ae63e497")),
        sec("ממיר ספרתי-אנלוגי (DAC)", 40, "שאלה 3 ביולי 2024.", False),
    ]})

F["java"] = ("Java", {
    "format": "אמריקאי: ״מה יודפס״, ״מה השגיאה בקוד״, השלמת קוד ושאלות מושגים. מותר דף נוסחאות אחד.",
    "basis": "קובץ שאלות הדוגמה למבחן, ומה שנלמד עד הרצאה 4",
    "sections": [
        sec("״מה יודפס״ – מעקב אחרי קוד", 95, "רוב השאלות במבחן מהסוג הזה.", True, None, "טבלה: עמודה לכל משתנה, שורה לכל סיבוב.",
            ids("java", "67319c08", "1719a9c8", "56de9517", "22f606b0", "cb65f6df")),
        sec("ממשקים – הוספת מתודה לממשק קיים", 85, "שאלה 1 בקובץ הדוגמה.", False),
        sec("מחלקות אבסטרקטיות וירושה – השלמת קוד", 85, "שאלה 4 בקובץ הדוגמה.", False),
        sec("״מה השגיאה בקוד״", 85, "שאלה 3 בקובץ הדוגמה.", True, None, None, ids("java", "f69303fa", "f0440317")),
        sec("== מול equals במחרוזות", 80, "שאלה 2 בקובץ הדוגמה.", True, None, None, ids("java", "308ebd98")),
        sec("חריגות – סדר catch וקוד בלתי ישיג", 80, "שאלה 3 בקובץ הדוגמה.", False, None, None, ids("java", "482b5658")),
        sec("static, העברת פרמטרים (ערך מול הפניה) וטווח הכרה", 70, "נלמד בהרצאה 4. הערכה: שאלות ״מה יודפס״ על שינוי מערך או אובייקט בתוך מתודה נפוצות במבחני Java.", True),
        sec("הזזות ביטים", 30, "נלמד בהרצאה 2.", True, None, None, ids("java", "3dc66bdf")),
    ]})

F["linear"] = ("ליניאר|לינאר", {
    "format": "שעתיים, בלי חומר עזר: 3 שאלות פתוחות (או 6 אמריקאיות שפותרים במחברת).",
    "basis": "מועד ב׳ תשפ״ד (7.5.24) ומועד א׳ תשפ״ו",
    "sections": [
        sec("ביטוי להגבר של מעגל מגברי שרת", 95, "שאלה 1 בתשפ״ד (12 נק׳) ושאלה 4 בתשפ״ו.", True, 12,
            "אדמה וירטואלית ← KCL בכל הדק מינוס ← לבטא את Vo.", ids("linear", "869840af", "0444281f", "40f38d24", "bbac9c6f", "012f6f63")),
        sec("נקודת עבודה של BJT ויציבותה (β משתנה, נגד אמיטר)", 90, "48 נק׳ בתשפ״ד; שאלת VBB בתשפ״ו.", False, 48),
        sec("משוב בשלוש דרגות – סוג, β, הגבר בחוג סגור", 85, "40 נק׳ בתשפ״ד; שאלה 2 בתשפ״ו – אותו מעגל.", False, 40),
        sec("אות קטן – CE / CC (הגבר, Rin, Rout)", 70, "שאלות 5-6 בתשפ״ו.", True, None, None, ids("linear", "610c8ed2")),
        sec("מתנד עם שמיט-טריגר", 50, "שאלה 3 בתשפ״ו.", False),
        sec("שרשור מגברים והספקים", 30, "נלמד בהרצאה 2.", True, None, None, ids("linear", "9f29e3c8", "320d8cba")),
    ]})

F["comm"] = ("תקשורת", {
    "format": "14-17 שאלות רב-ברירה, שעתיים עד שעתיים וחצי, חומר פתוח, פתרון במחברת חובה. מטלות 10% מגן.",
    "basis": "מבחני תש״ף ותשפ״ב (אריאל), ומה שנלמד עד הרצאה 4",
    "sections": [
        sec("שרשרת כבלים ומגברים – פריס, ספרת רעש, LNA", 95, "שאלה 1 כמעט בכל מבחן.", True, None,
            "הכל לליניארי; מנחת: F = L; כל דרגה מתחלקת בהגבר של כל מה שלפניה.",
            ids("comm", "9333a666", "71f4c8e8", "73099eff", "78e7b850")),
        sec("הספק כניסה נדרש ל-SNR / סף רגישות", 90, "שאלה 2 כמעט בכל מבחן.", True, None, None, ids("comm", "3e538d23", "7056519a", "9eece440")),
        sec("AM – נצילות הספק, גילוי סינכרוני", 90, "שאלות 1 ו-3 במבחנים. DSB-SC וגילוי קוהרנטי נלמדו בהרצאה 4; AM עם נשא ונצילות – בהמשך.", True),
        sec("FM / NBFM – רוחב סרט, בסל", 80, "חוזר בכל מבחן.", False),
        sec("SSB וסופרהטרודין – תדר בבואה", 80, "חוזר בכל מבחן. מקלט סופרהטרודין נלמד בהרצאה 4; SSB – בהמשך.", True),
        sec("dB/dBm ומאזן קישור", 70, "כלי בכל שאלה.", True, None, None, ids("comm", "3eaf7c29", "e3309cba", "f4693d86", "9991573f")),
    ]})

F["rnd"] = ("אקראיים", {
    "format": "4 שאלות, 90 דקות (כשעתיים עם תוספת). עונים על כל השאלות; במילואים בוחרים בין 3 ל-4 – ואם עונים על שתיהן, ניקוד כפול על שני הסעיפים הטובים. 6 עמודים + דף נוסחאות רשמי בטופס.",
    "basis": "המבחן שלך (מועד ב׳ קיץ תשפ״ו) ומבחני בר-אילן תשפ״ד-תשפ״ו",
    "sections": [
        sec("שאלה 1: תהליך עם מקדמים אקראיים – סמ״ר, ותהליך נגזר (הפרש/סכום)", 95, "במבחן שלך: X[n]=A+nB וההפרש שלו; גם בבר-אילן.", True, 30,
            "לבדוק אם R תלוי רק בהפרש; ולפשט את התהליך הנגזר לפני החישוב (A+nB ⇐ ההפרש = B).", ids("rnd", "fe403441", "7888a5c6", "80bc90e2")),
        sec("שאלה 2: אות דרך מסנן – S_Y, שרטוט, הספק, H₂ עם מוצא 0", 95, "במבחן שלך (30 נק׳) ובבר-אילן.", True, 30,
            "|H|² עם תחום ← S_Y ← שרטוט עם ערכים ← הספק = שטח; מוצא 0 ⇐ H מתאפס איפה ש-S_X≠0.", ids("rnd", "3e70590d", "8ac02e43", "890a8285", "5de8e4b9")),
        sec("שאלה 3: תהליך פואסון", 80, "שאלה 3 במבחן שלך (העבר לא משנה; λ מזמן ממוצע); 44 נק׳ בבר-אילן תשפ״ו.", True, 20, "קטעים זרים בלתי תלויים; אירוע כל T בממוצע ⇐ λ=1/T.",
            ids("rnd", "8975b84c", "e7f7e0ce", "990a0df6", "f554d180")),
        sec("שאלה 4: משערך לינארי עם משתנים רציפים", 80, "שאלה 4 במבחן שלך.", True, 20, None, ids("rnd", "fb317617", "597ce441", "6ddd33ef")),
    ]})

# ---------------------------------------------------------------------------------------------------------------------
# 15/11/2026, his remark: "the lecturer said every exercise of the lectures and practices can be in the exam - I solved
# ~10 and not one of them is in the expected exam". So every expected question now lists FIRST the exercises of his
# weekly lists (week N = lecture N + practice N; "📌 מהכיתה" = solved in class) that train it, then the past-exam ones;
# topics taught in class that the past exams did not show get a section of their own. Ids: chapters/weekset_ids.json.
WS_IDS = json.loads((CH / "weekset_ids.json").read_text(encoding="utf-8"))


def w(*prefixes):
    out = []
    for pre in prefixes:
        hit = [x for x in WS_IDS if x.startswith(pre)]
        assert len(hit) == 1, pre
        out.append(hit[0])
    return out


CLASS_NOTE = "התרגילים מהשבועות שלך (הרצאה + תרגול; 📌 = נפתר בכיתה – המרצה אמר שהם יכולים להופיע במבחן) + שאלות ממבחני עבר"
CLASS = {  # course -> {section index: week-list exercises}, plus new sections
    "waves": ({0: w("8c561610", "b751881a"),
               4: w("30c4dbdd", "19307f4d", "fb766438", "fdf477e9"),
               5: w("a26af07a", "54addb9c")},
              [sec("משוואות מקסוול ופרמטרי גל: בדיקת שדה, H מתוך E, k, λ, η, תנאי שפה", 80,
                   "כל התרגילים מהכיתה של הרצאה 1 ותרגול 1. בשאלת הגל במבחן הסעיפים הראשונים הם בדיוק זה: מתוך E נתון למצוא k, λ, η, את H ולבדוק את משוואות מקסוול.",
                   True, 15, "רוטור של E ← פאראדיי ← אינטגרל בזמן = B. תמיד לבדוק את ארבע המשוואות: שתי דיברגנץ ושני רוטורים.",
                   w("e170a79a", "93c7e01d", "768dc496", "b075adf5", "44ec295a", "b56401e0", "ed05ef04"))]),
    "linear": ({0: w("dc984255", "258f4f74", "8539b42d", "c580b9a6", "b8898460", "40f38d24", "76240755"),
                3: w("02e76b3d", "e936fb16"),
                5: w("c1439767", "70038c31", "1261c5ba", "39a78ac1", "b9e4e6c0")},
               [sec("רשתות שני-זוגיים: פרמטרי h ו-z (גם מתוך מודל π)", 60,
                    "נפתר בכיתה בהרצאה 1 ובתרגול 1 (מודל π ← פרמטרי h).", True, 15,
                    "קצר במוצא ← h11, h21; נתק בכניסה ← h12, h22.", w("94a5949d", "8c3880bb", "09c12485")),
                sec("דיודה – פתרון בשני מודלים", 40, "שאלת מבחן ששייכת לשבוע 1.", True, 10, None, w("7481fc52"))]),
    "micro": ({0: w("e24e192e", "9df26f09", "553159a3", "912bcbdb", "0c2c2376", "f61b71ba", "5fc67982"),
               2: w("968bbeb5", "19ec7fa7"),
               3: w("1b38eb7a")}, []),
    "comm": ({0: w("6dad52f1", "9333a666", "2d7a8080", "73099eff", "71f4c8e8"),
              1: w("cbf1a8ce", "e79529cb", "f498bfee", "7056519a", "2420dd4f", "94900492", "e4f0e2e7", "f32f3f8b"),
              2: w("98fc3b21", "1fce2fb5", "ed625cad", "c4d0ee40"),
              5: w("c9afaad5", "ff8590cc", "c60c0f64", "f1eb8f9c", "ef88bbdd", "035fdbb6", "c497b4f4", "eacdedd6", "a2058312", "9d07e927", "758c7080")},
             [sec("מסננים, תהודה והספק של אותות (RC / RL / RLC)", 40, "נפתר בכיתה בהרצאה 1 ובתרגולים 1-2.", True, 10, None,
                  w("77c57235", "8e534070", "3198b801"))]),
    "digital": ({0: w("ce0d3288", "73492580", "58d4d12e", "f09fbb0e", "5ffaecdf", "d542fec2", "dd17dfe3", "9a62d056"),
                 2: w("769434a9", "876fa9fd", "a333d682", "98d9a092"),
                 3: w("3a95dd1c"),
                 4: w("ae6f28f5", "e9a1f688", "a4aae128")},
                [sec("דיודה וטרנזיסטור ביפולרי – מצב עבודה, שערי דיודות", 40, "תרגולים 2-3.", True, None, None,
                     w("4a92f6c9", "772067ea", "ed75de2a", "1875f5c3"))]),
    "java": ({0: w("ffdb3a40", "65da62fc", "1719a9c8", "22f606b0"),
              3: w("f0440317"),
              6: w("3da55b01", "d2a1a459", "d52984f9", "e31b24f2"),
              7: w("38d9cc8c")},
             [sec("כתיבת קוד קצר: תנאים, לולאות, מערכים ומחלקה פשוטה", 70,
                  "התרגילים מהכיתה של שבועות 1-3 (תרגול 1, הרצאה 2) – ושאלות השלמת קוד במבחן בנויות מהם.", True, None,
                  "קודם לכתוב בעברית את השלבים, אחר כך קוד; לבדוק ידנית על קלט אחד.",
                  w("6fee50e7", "45496a5e", "0293c40e", "58304176", "9379c0e8", "262a6118", "482b5658", "89c8155c"))]),
    "rnd": ({0: w("fe403441", "7888a5c6", "5c348062", "210da1b0", "3661feaf", "e1727d78", "130332dd", "32de7adc"),
             1: w("3e70590d", "890a8285", "5de8e4b9", "4acf12fb", "699891e8", "92264487", "176bcf82"),
             2: w("e7f7e0ce", "990a0df6", "f554d180", "11e7e6aa", "f9005ad3", "9a4d8704"),
             3: w("fb317617", "597ce441", "19cb3529", "bc391d30", "73916e62", "c336bbe3", "8fff574f", "dae0357b", "513ce83e",
                  "d1f7153a", "462599c1", "5e96963d", "443fa09b", "3a245f8d")},
            [sec("וקטורים גאוסיים – קווריאנס של Ax, צפיפות מותנית, פונקציה אופיינית", 50, "סעיף בשאלות המשערך והתהליכים.", True, 10, None,
                 w("d165bb9e", "ac3f2987", "6dc493c5", "4d2c8853"))]),
}


# 16/11/2026, his refinement: the exam will NOT repeat the class exercises - the lecturers change the data and add a catch.
# So each likely question gets "🎯 שאלה צפויה" exercises: a class example with new data + the catch the past exams use,
# solved and checked (chapters/fixes/predict_<course>.py). Shown first in their section. Key: section index, or the
# title start of a CLASS section.
PRED = {
    "digital": {0: ["dd2ae1a2-a428-4d9f-8c27-aa618fc4b037"], 2: ["dfecb57d-7b54-41e3-bdb3-499b06495b47"],
                3: ["1a377a5b-8288-4eeb-8be7-7ec751f04c7b"], 4: ["1a377a5b-8288-4eeb-8be7-7ec751f04c7b", "dd2ae1a2-a428-4d9f-8c27-aa618fc4b037"],
                "דיודה וטרנזיסטור": ["b88208e9-bda3-43b9-beac-210bef71e32d"]},
    "java": {0: ["6ebe8f83-32d4-43f1-8d43-43cf757eb347", "849c9dc7-9388-483d-9b16-cb6f07b0851c"],
             3: ["85eec43d-343d-41cb-a0a8-80121ed73316"], 4: ["ebbf1cdf-9457-4008-b5e5-7c03df35c14b"],
             6: ["849c9dc7-9388-483d-9b16-cb6f07b0851c"], 7: ["6ebe8f83-32d4-43f1-8d43-43cf757eb347"],
             "כתיבת קוד קצר": ["0255fed3-1b60-48a7-ba14-7088c3930c3a"]},
    "micro": {0: ["e159f56f-e1c2-4c68-ac3a-2c6d637ef12f", "484bc01f-66fb-4ea4-b52f-fd897e69aa6b"],
              2: ["8829a6c5-69de-4d3e-9b30-dd7b0f1c6cfa"], 3: ["f88840c7-f46d-4fab-946e-48c6009dea22"]},
}
PRED_NOTE = "🎯 = שאלה צפויה: דוגמה מההרצאה / מהתרגול עם נתונים אחרים והקאץ' שמבחני העבר מוסיפים – כך המרצים בונים את המבחן"


def with_class(key, data):
    per, new = CLASS.get(key, ({}, []))
    secs = []
    for i, s0 in enumerate(data["sections"]):
        s1 = dict(s0)
        mine = per.get(i, [])
        if mine:
            s1["exercise_ids"] = mine + [x for x in s1["exercise_ids"] if x not in mine]
            s1["taught"] = True
        secs.append(s1)
    secs = secs + [dict(x) for x in new]
    pred = PRED.get(key, {})
    for i, s1 in enumerate(secs):
        mine = pred.get(i, []) + [x for k, v in pred.items() if isinstance(k, str) and s1["title"].startswith(k) for x in v]
        if mine:
            s1["exercise_ids"] = mine + [x for x in s1["exercise_ids"] if x not in mine]
    basis = data["basis"] + " · " + CLASS_NOTE + (" · " + PRED_NOTE if pred else "")
    return dict(data, sections=secs, basis=basis)


if __name__ == "__main__":
    for key, (_, data) in F.items():
        data = with_class(key, dict(data, updated=UPDATED))
        (CH / f"{key}_forecast.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print(key, len(data["sections"]))
