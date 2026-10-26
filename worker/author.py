"""Turn a transcript + board snapshots into a reading chapter and a multiple-choice quiz."""
import json
import os
from pathlib import Path

CHAPTER_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "chapter_md": {"type": "string"},
        "topics": {"type": "array", "items": {"type": "string"}},
        "course_facts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["exam", "exam_hint", "grading", "reservist",
                                                            "assignments", "attendance", "materials", "industry",
                                                            "other"]},
                    "text": {"type": "string"},
                },
                "required": ["category", "text"],
            },
        },
        "syllabus_covered": {"type": "array", "items": {"type": "integer"}},
        "glossary": {
            "type": "array",
            "items": {"type": "object", "properties": {"en": {"type": "string"}, "he": {"type": "string"},
                                                       "explanation": {"type": "string"}},
                      "required": ["en", "he", "explanation"]},
        },
        "exam_type": {"type": "string", "enum": ["mcq", "open", "mixed", "none", "unknown"]},
        "grade_weights": {
            "type": "array",
            "items": {"type": "object", "properties": {"name": {"type": "string"}, "weight": {"type": "integer"}},
                      "required": ["name", "weight"]},
        },
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "question": {"type": "string"},
                    "options": {"type": "array", "items": {"type": "string"}},
                    "correct": {"type": "integer"},
                    "explanation": {"type": "string"},
                    "difficulty": {"type": "integer"},
                },
                "required": ["topic", "question", "options", "correct", "explanation", "difficulty"],
            },
        },
    },
    "required": ["title", "chapter_md", "topics", "course_facts", "exam_type", "grade_weights", "questions"],
}

FACT_LABEL = {"exam": "המבחן", "exam_hint": "מה יהיה במבחן", "grading": "ציון ומשקלים", "reservist": "מילואים",
              "assignments": "מטלות והגשות", "attendance": "נוכחות", "materials": "חומרים מותרים וספרות",
              "industry": "מהתעשייה ולראיונות עבודה", "other": "כללי"}

SYSTEM = """אתה מרצה ומתרגל מעולה בהנדסת חשמל. הסטודנט לא צפה בהקלטה ולומד רק מקריאה ומשאלונים.
כתוב הכל בעברית - גם כשהשקפים, הקוד או הקובץ באנגלית: תרגם את התוכן לעברית (בקוד - ההערות וההסברים בעברית, הקוד עצמו כמו שהוא).
מונחים טכניים - בעברית, ובפעם הראשונה גם המונח באנגלית בסוגריים. השאלון וההסברים - בעברית.

כללי הכתיבה של chapter_md (Markdown):
- כותרות ## לכל נושא (ו-### לתת-נושא), לפי סדר ההרצאה. הסטודנט מבין רק דרך דוגמאות, ולכן כל נושא וכל תת-נושא בנוי בדיוק כך:
  1. **רקע:** למה הנושא קיים ואיזו בעיה הוא פותר - 2-3 משפטים פשוטים, בלי מונחים שעוד לא הוסברו.
  2. ההסבר של המרצה: ההגדרות, הנוסחאות והשרטוטים מההרצאה.
  3. > 🏠 **מהחיים:** מכשיר או מצב אמיתי שבו הנושא הזה פועל בפועל (מזגן, טלפון, מטען, מחשב, רכב, רמזור, וויי-פיי...), ואיך בדיוק - כאן, בסוף הנושא ולפני הנושא הבא. נכון הנדסית; אם אינך בטוח - דוגמה אחרת.
  4. אם המרצה פתר תרגיל או דוגמה על הנושא - כאן, אחרי הדוגמה מהחיים. אם לא - ממשיכים לנושא הבא.
- גרף זמנים של דלגלג (שעון, D, reset, Q) - לא בתווים אלא בלוק ```wave``` (האפליקציה מציירת ומחשבת את Q):
  {"cycles": 5, "signals": {"D": "0111111111", "rst": "0000011100"}, "ff": {"type": "sync", "init": "0"}}
  תו לכל חצי מחזור (מקום זוגי = עליית שעון), כניסות משתנות רק במקומות אי-זוגיים; type: none / sync / async.
- נוסחאות ב-LaTeX. בתוך משפט ($...$) רק סמל או ביטוי קצר (כמו $\vec{E}$ או $f=1/T$); כל משוואה מלאה - בשורה נפרדת עם $$...$$, כי טקסט עברי מימין לשמאל שובר נוסחאות ארוכות בתוך שורה.
- גם בשאלות, בתשובות ובהסברים של השאלון - נוסחאות ב-$...$ (לא טקסט קוד), קצרות. קוד בבלוקים עם שם השפה.
- שלב צילומי לוח/שקפים רלוונטיים בדיוק במקום שבו הם מוסברים, בתחביר: ![תיאור קצר](slide:N) כאשר N הוא מספר השקף. בחר את הצילומים שבאמת מוסיפים (בדרך כלל 5-20).
- כל מה שהמרצה הדגיש כחשוב / "יופיע במבחן" - בשורה: > ⭐ **חשוב למבחן:** ...
- אם המרצה טעה או שהתמלול סותר את השקפים - ציין: > ⚠️ ... ותן את הנכון.
- השמט פטפוט, ענייני זום וניהול כיתה. שמור כל מידע מנהלי חשוב (משקל ציונים, סוג מבחן, מטלות, תאריכים) בסעיף "מידע על הקורס" בתחילת הפרק.
- התמלול אוטומטי ויש בו שגיאות במונחים - תקן לפי ההקשר והשקפים, אל תעתיק שגיאות.
- אל תמציא תוכן שלא היה בהרצאה. מותר להוסיף הסבר קצר כשמשהו לא ברור, ולסמן אותו "(הרחבה)".
- בסוף הפרק (בהרצאה ובתרגול) סעיף "## מהעולם האמיתי: תעשייה וראיונות עבודה" - הסטודנט בשנה ג' ומתכונן לעבודה בתעשייה:
  - קודם כל מה שהמרצה אמר על העולם שמחוץ לאקדמיה: שימושים בתעשייה, חברות ומוצרים, סיפורים מהניסיון שלו, מה מהנדסים עושים בפועל, כלים וטכנולוגיות, טיפים לקריירה ולראיונות. סמן "🎙️ המרצה:".
  - ואחר כך (הרחבה) קצרה ומדויקת: איפה הנושאים של השיעור משמשים בתעשייה, ו-2-4 שאלות שנפוצות בראיונות עבודה על הנושאים האלה עם תשובה קצרה ונכונה. רק דברים מבוססים ומקובלים - לא שמות חברות או נתונים שאינך בטוח בהם.

questions: 10-15 שאלות אמריקאיות, 4 תשובות בכל אחת, correct הוא האינדקס (0-3) של התשובה הנכונה.
- שאלות הבנה ויישום, לא רק שינון. מסיחים סבירים. פזר את מיקום התשובה הנכונה.
- explanation: למה הנכונה נכונה ולמה כל אחת מהאחרות שגויה.
- topic: אחד מהערכים ב-topics. difficulty: 1 קל, 2 בינוני, 3 קשה.
topics: 3-8 נושאים קצרים שהפרק מכסה (ישמשו למעקב אחרי חוזקות וחולשות).

course_facts: כל מידע מנהלי חשוב שנאמר (גם בפטפוט בתחילת השיעור!), משפט ברור אחד לכל פריט, עם מספרים ותאריכים מדויקים:
- exam: מבנה המבחן (אמריקאי/פתוח, מקוון/בכתב, משך, חומר עזר מותר, מועדים).
- exam_hint: כל אמירה של המרצה על מה יהיה או לא יהיה במבחן ("זה יופיע במבחן", "את זה לא צריך לדעת", "שאלה כזו תהיה").
- grading: משקלים, ציון עובר, בונוסים, ציון מגן.
- reservist: הקלות ונהלים למשרתי מילואים - פרט את כל האפשרויות ואת מה צריך לעשות ועד מתי (למשל לשלוח מייל עד תאריך).
- assignments: מטלות, תדירות, אופן ההגשה, דדליינים, חובת הגשה.
- attendance: חובת נוכחות. materials: סביבת עבודה, ספרים, דף נוסחאות.
- industry: כל מה שהמרצה אמר על התעשייה, עבודה, ראיונות עבודה, חברות, שימושים מעשיים וקריירה (רק מה שנאמר בשיעור).
- other: כל דבר מנהלי חשוב אחר.
אם לא נאמר שום דבר מנהלי - רשימה ריקה. אל תמציא.
exam_type ו-grade_weights: רק אם נאמרו במפורש בחומר הזה, אחרת "unknown" ורשימה ריקה.
glossary: 10-30 מונחים באנגלית מהחומר (מהשקפים, מהקוד ומהדיבור) - הסטודנט לא חזק באנגלית ונבחן על חומר שכתוב באנגלית.
en - המונח כמו שהוא מופיע באנגלית; he - התרגום/המונח המקובל בעברית; explanation - משפט קצר בעברית מה זה אומר בקורס הזה.
כלול גם מילים באנגלית שאינן מונחים טכניים אבל מופיעות בשקפים/בשאלות (למשל assume, derive, respectively).
syllabus_covered: אם צורפה רשימת נושאי הסילבוס - המספרים של הנושאים שהשיעור הזה לימד (גם חלקית). אחרת רשימה ריקה."""

KIND_TASK = {
    "lecture": "זו הרצאה. כתוב פרק קריאה מלא שמחליף צפייה בהרצאה.",
    "practice": "זה תרגול. בפרק: רשימת התרגילים שנפתרו, ולכל תרגיל - השאלה, ופתרון מלא שלב אחרי שלב עם הסבר למה עושים כל צעד, טריקים וטעויות נפוצות. השאלות האמריקאיות יבדקו הבנת שיטות הפתרון.",
    "lab": """זה ניסוי במעבדה (חוברת ניסוי / דוח מכין). הסטודנט צריך: להבין את הניסוי, להכין את הדוח המכין, לעבור בוחן כניסה,
ולהיות מוכן שיעלו אותו ללוח להסביר את הניסוי לכיתה. **הישאר רק בגבולות החומר של הדוח המכין וחוברת הניסוי - לא מעבר.**
מבנה הפרק:
## מטרת הניסוי - בשתיים-שלוש שורות.
## הרקע התיאורטי הנדרש - רק מה שצריך לניסוי הזה, עם נוסחאות; שרטוטים מהחוברת - תאר במילים.
## שאלות הדוח המכין - כל שאלה, ופתרון מלא שלב אחרי שלב עם הסבר למה. אם יש חישוב - כל הצבה.
## מהלך הניסוי - מה מחברים, מה מודדים בכל שלב ולמה, ומה התוצאה הצפויה.
## הסבר ללוח (3-5 דקות) - תסריט של מה להגיד לכיתה, בנקודות, בסדר הגיוני: מטרה ← עיקרון פעולה ← המעגל ← מה מודדים ← מה מצפים לראות.
## שאלות שהמדריך עלול לשאול - 8-12 שאלות עם תשובה קצרה וברורה לכל אחת.
## טעויות נפוצות במעבדה.
השאלות האמריקאיות - בסגנון בוחן כניסה, רק על החומר של הניסוי.""",
    "web": "זה חומר מאתר אינטרנט שהסטודנט רוצה ללמוד בעצמו. כתוב פרק קריאה מסודר ומלמד על בסיס התוכן.",
    "other": "כתוב פרק קריאה מסודר על בסיס החומר.",
}


KIND_NAME = {"lecture": "הרצאה", "practice": "תרגול", "lab": "ניסוי", "web": "מאמר מהאינטרנט", "other": "חומר"}
EXAM_NAME = {"mcq": "אמריקאי", "open": "פתוח", "mixed": "משולב", "none": "ללא מבחן"}


def build_prompt(course, lesson, transcript, slide_count, previous_topics):
    lines = [
        f"קורס: {course['name']}",
        f"סוג המבחן בקורס: {EXAM_NAME.get(course.get('exam_type'), 'לא ידוע')}",
    ]
    if course.get("notes"):
        lines.append(f"הערות על הקורס: {course['notes']}")
    if previous_topics:
        lines.append("נושאים שכבר נלמדו בקורס: " + ", ".join(previous_topics[-40:]))
    if course.get("syllabus_topics"):
        lines.append("נושאי הסילבוס (למילוי syllabus_covered): " +
                     "; ".join(f"{i + 1}. {t}" for i, t in enumerate(course["syllabus_topics"])))
    lines += [
        f"פריט: {KIND_NAME.get(lesson['kind'], '')} {lesson.get('number') or ''} {lesson.get('title') or ''}".strip(),
        KIND_TASK.get(lesson["kind"], KIND_TASK["other"]),
    ]
    if slide_count:
        lines.append(f"מצורפים {slide_count} צילומי לוח/שקפים, ממוספרים 1..{slide_count} לפי הסדר. בתמלול מסומן מתי כל אחד הופיע.")
    if transcript:
        lines += ["", "=== התמלול / התוכן ===", transcript]
    else:
        lines += ["", "המקור לפרק הוא הקובץ המצורף. קרא אותו כולו."]
    return "\n".join(lines)


# Free-tier quotas are per project AND per model (e.g. 20 requests/day on the newest Flash): fall back
# across models, and across keys when GEMINI_API_KEY holds several comma-separated keys.
WORK_MODELS = ["gemini-flash-latest", "gemini-3.8-flash", "gemini-2.5-flash", "gemini-flash-lite-latest", "gemini-2.5-flash-lite"]


def _list(v):
    return [x.strip() for x in (v or "").split(",") if x.strip()]


def _keys():
    return _list(os.environ.get("GEMINI_API_KEY"))


def _models():
    own = _list(os.environ.get("GEMINI_MODELS") or os.environ.get("GEMINI_MODEL"))
    return list(dict.fromkeys(own + WORK_MODELS))


def _is(e, *words):
    t = str(e)
    return any(w.lower() in t.lower() for w in words)


def friendly_error(e):
    if _is(e, "RESOURCE_EXHAUSTED", "429", "quota"):
        return "המכסה היומית החינמית של Gemini נגמרה בכל המודלים. היא מתאפסת כל יום בסביבות 10:00 בבוקר - אז ללחוץ 'לנסות שוב'."
    if _is(e, "UNAVAILABLE", "503", "overloaded", "high demand"):
        return "השרתים של Gemini היו עמוסים. ללחוץ 'לנסות שוב' בעוד כמה דקות."
    if _is(e, "confirm you", "not a bot"):
        return ("יוטיוב חוסם את השרת שמעבד את ההקלטות, אז אי אפשר להוריד ממנו. "
                "ללחוץ 'לנסות שוב' - הקלטות יוטיוב נקראות עכשיו דרך Gemini.")
    return str(e)[:1500]


def _with_gemini(call):
    """Runs call(client, model) with retries on overload and fallback across models and keys on quota."""
    import time
    from google import genai

    keys = _keys()
    if not keys:
        raise RuntimeError("לא הוגדר GEMINI_API_KEY")
    last = None
    for key in keys:
        client = genai.Client(api_key=key)
        for model in _models():
            for attempt in range(3):
                try:
                    return call(client, model)
                except Exception as e:  # noqa: BLE001
                    last = e
                    # Overload, or a dropped connection ("Server disconnected without sending a response"): retry.
                    busy = _is(e, "UNAVAILABLE", "503", "overloaded", "high demand", "disconnected", "timed out",
                               "Connection reset", "RemoteProtocolError")
                    if busy and attempt < 2:
                        time.sleep(5 * (attempt + 1) ** 2)
                        continue
                    if busy or _is(e, "RESOURCE_EXHAUSTED", "429", "quota", "NOT_FOUND", "404", "not supported"):
                        print(f"gemini {model}: {str(e)[:120]} -> next model", flush=True)
                        break
                    raise
    raise RuntimeError(friendly_error(last))


def _generate_json(parts, system, schema, thinking="MEDIUM"):
    """One structured-output call (with model/key fallback); adapts to models without thinking levels or schemas."""
    from google.genai import types

    def call(client, model):
        def run(with_thinking, with_schema):
            cfg = dict(system_instruction=system, response_mime_type="application/json", max_output_tokens=65536)
            contents = list(parts)
            if with_schema:
                cfg["response_json_schema"] = schema
            else:
                contents.append(types.Part.from_text(
                    text="החזר אך ורק JSON תקין לפי ה-JSON Schema הזה:\n" + json.dumps(schema, ensure_ascii=False)))
            if with_thinking:
                cfg["thinking_config"] = types.ThinkingConfig(thinking_level=thinking)
            return client.models.generate_content(model=model, contents=[types.Content(role="user", parts=contents)],
                                                  config=types.GenerateContentConfig(**cfg))
        try:
            return run(True, True)
        except Exception as e:  # noqa: BLE001
            if _is(e, "thinking"):
                return run(False, True)
            if _is(e, "INVALID_ARGUMENT"):
                return run(False, False)
            raise

    resp = _with_gemini(call)
    text = (resp.text or "").strip()
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()
    return json.loads(text)


def _source_parts(course, lesson, transcript, slides, previous_topics, docs=()):
    from google.genai import types
    parts = [types.Part.from_text(text=build_prompt(course, lesson, transcript, len(slides), previous_topics))]
    for data, mime in docs:
        parts.append(types.Part.from_text(text="הקובץ המצורף (המקור לפרק):"))
        parts.append(types.Part.from_bytes(data=data, mime_type=mime))
    for n, path in slides:
        parts.append(types.Part.from_text(text=f"שקף {n}:"))
        parts.append(types.Part.from_bytes(data=Path(path).read_bytes(), mime_type="image/webp"))
    return parts


def author_with_gemini(course, lesson, transcript, slides, previous_topics, log=print, docs=()):
    """slides: list of (number, Path); docs: list of (bytes, mime) files to read.
    Writes the chapter, then has it fact-checked. Returns the chapter dict."""
    log("כותב פרק קריאה ושאלון...")
    sources = _source_parts(course, lesson, transcript, slides, previous_topics, docs)
    draft = validate(_generate_json(sources, SYSTEM, CHAPTER_SCHEMA, "MEDIUM"))
    log("בודק את הפרק והשאלון מול ההקלטה, השקפים והידע המקצועי...")
    return verify_with_gemini(sources, draft, log)


VERIFY_SYSTEM = """אתה בודק עובדות קפדן בהנדסת חשמל. הסטודנט ייבחן על החומר, ולכן אסור שתישאר בפרק או בשאלון אף טעות.
קיבלת את המקור (תמלול + צילומי לוח/שקפים) וטיוטה של פרק קריאה ושאלון. עבור על הכל, פריט אחרי פריט:

1. כל הגדרה, נוסחה, יחידה, סימן, מספר, קוד ודוגמה בפרק:
   - בדוק שהם תואמים למה שנאמר/נכתב במקור, ושהם נכונים מבחינה מקצועית.
   - שגיאת תמלול או העתקה - תקן.
   - המרצה עצמו טעה - השאר את מה שהמרצה אמר רק אם זה מה שייבדק, והוסף > ⚠️ עם הגרסה הנכונה וההסבר. אם זו פליטת פה ברורה - תקן ישירות וציין ב-fixes.
   - טענה שאי אפשר לאמת מהמקור ואינך בטוח בה ב-100% - נסח בזהירות או הסר, ורשום ב-uncertain.
   - נוסחאות: בדוק ממדים/יחידות ומקרי קצה. חישובים בדוגמאות: חשב מחדש.
2. כל שאלה בשאלון: פתור אותה בעצמך מאפס, בלי להסתכל על correct. ודא ש:
   - התשובה המסומנת היא הנכונה, ושהיא היחידה הנכונה (אין שתי תשובות שאפשר להגן עליהן).
   - השאלה מבוססת על החומר, חד-משמעית, ובלי מלכודות ניסוח.
   - ההסבר נכון.
   תקן מה שצריך. שאלה שאי אפשר לתקן בוודאות - הסר.
3. course_facts / exam_type / grade_weights: השאר רק מה שנאמר במפורש במקור, מדויק.
4. דוגמאות "🏠 מהחיים": ודא שכל דוגמה נכונה הנדסית ושהנושא באמת פועל בה כפי שנכתב; תקן או החלף דוגמה שגויה.
   הסעיף "מהעולם האמיתי": מה שמסומן "🎙️ המרצה" - רק מה שנאמר במקור. ההרחבה ושאלות הראיון - ודא שהן נכונות מקצועית; הסר שמות חברות, מספרים או טענות שאינך בטוח בהם.
5. glossary: ודא שכל תרגום נכון ומקובל בהנדסת חשמל ושההסבר נכון. תקן או הסר.
6. ודא שהפרק והשאלון כתובים בעברית (מונחים באנגלית רק בסוגריים).

החזר את הפרק המתוקן המלא באותו מבנה, ובנוסף verification:
- fixes: רשימה קצרה של כל מה שתיקנת (משפט לכל תיקון).
- uncertain: טענות שנשארו ושכדאי לוודא מול המרצה/הספר.
אל תקצר את הפרק ואל תשמיט תוכן נכון."""

VERIFY_SCHEMA = {
    **CHAPTER_SCHEMA,
    "properties": {
        **CHAPTER_SCHEMA["properties"],
        "verification": {
            "type": "object",
            "properties": {
                "fixes": {"type": "array", "items": {"type": "string"}},
                "uncertain": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["fixes", "uncertain"],
        },
    },
    "required": CHAPTER_SCHEMA["required"] + ["verification"],
}


def verify_with_gemini(sources, draft, log=print):
    """Second, independent pass: fact-check the chapter and re-solve every quiz question."""
    from google.genai import types
    parts = list(sources) + [types.Part.from_text(text="=== הטיוטה לבדיקה (JSON) ===\n" + json.dumps(draft, ensure_ascii=False))]
    try:
        checked = validate(_generate_json(parts, VERIFY_SYSTEM, VERIFY_SCHEMA, "HIGH"))
    except Exception as e:  # noqa: BLE001 - keep the draft rather than lose the lesson, but say so
        log(f"הבדיקה נכשלה ({e}); נשמרת הטיוטה עם סימון")
        draft["verification"] = {"fixes": [], "uncertain": ["הבדיקה האוטומטית לא רצה על הפרק הזה - כדאי לבדוק אותו בזהירות."]}
        return draft
    v = checked.get("verification") or {}
    if v.get("uncertain"):
        v["uncertain"] = _search_check(v["uncertain"])
    log(f"נבדק: {len(v.get('fixes', []))} תיקונים, {len(v.get('uncertain', []))} נקודות לבדיקה")
    return checked


def _search_check(claims):
    """Best effort: check the remaining doubtful claims against Google Search."""
    try:
        from google.genai import types
        listing = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(claims[:8]))
        resp = _with_gemini(lambda client, model: client.models.generate_content(
            model=model,
            contents=f"בדוק בחיפוש כל טענה, וענה לכל אחת בשורה אחת בעברית בפורמט: <הטענה> - נכון / לא נכון / לא חד-משמעי: <הסבר קצר>\n{listing}",
            config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())]),
        ))
        lines = [l.strip(" -*") for l in (resp.text or "").splitlines() if l.strip()]
        return lines or claims
    except Exception:  # noqa: BLE001
        return claims


def verification_md(ch):
    v = ch.get("verification") or {}
    fixes, unsure = v.get("fixes") or [], v.get("uncertain") or []
    out = ["", "---", "### ✅ בדיקת עובדות",
           "הפרק והשאלון נבדקו בבדיקה נפרדת מול ההקלטה, צילומי הלוח והידע המקצועי, וכל שאלה נפתרה מחדש."]
    if fixes:
        out += ["", "**תוקן בבדיקה:**"] + [f"- {f}" for f in fixes]
    if unsure:
        out += ["", "**כדאי לוודא מול המרצה / הספר:**"] + [f"- {u}" for u in unsure]
    if not fixes and not unsure:
        out.append("לא נמצאו טעויות.")
    return "\n".join(out)


def validate(ch):
    """Drop malformed questions instead of failing the whole lesson."""
    good = []
    for q in ch.get("questions", []):
        opts = q.get("options") or []
        if len(opts) >= 2 and isinstance(q.get("correct"), int) and 0 <= q["correct"] < len(opts):
            good.append(q)
    ch["questions"] = good
    ch.setdefault("topics", [])
    ch["glossary"] = [g for g in ch.get("glossary") or [] if isinstance(g, dict) and g.get("en") and g.get("he")]
    return ch
