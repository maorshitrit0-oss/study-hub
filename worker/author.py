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
                                                            "assignments", "attendance", "materials", "other"]},
                    "text": {"type": "string"},
                },
                "required": ["category", "text"],
            },
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
              "assignments": "מטלות והגשות", "attendance": "נוכחות", "materials": "חומרים מותרים וספרות", "other": "כללי"}

SYSTEM = """אתה מרצה ומתרגל מעולה בהנדסת חשמל. הסטודנט לא צפה בהקלטה ולומד רק מקריאה ומשאלונים.
כתוב בעברית. מונחים טכניים - גם באנגלית בסוגריים בפעם הראשונה.

כללי הכתיבה של chapter_md (Markdown):
- כותרות ## לכל נושא, לפי סדר ההרצאה. הסבר אינטואיטיבי קודם, אחר כך הגדרות ונוסחאות, ואז דוגמה.
- נוסחאות ב-LaTeX: $...$ בתוך שורה, $$...$$ בשורה נפרדת. קוד בבלוקים עם שם השפה.
- שלב צילומי לוח/שקפים רלוונטיים בדיוק במקום שבו הם מוסברים, בתחביר: ![תיאור קצר](slide:N) כאשר N הוא מספר השקף. בחר את הצילומים שבאמת מוסיפים (בדרך כלל 5-20).
- כל מה שהמרצה הדגיש כחשוב / "יופיע במבחן" - בשורה: > ⭐ **חשוב למבחן:** ...
- אם המרצה טעה או שהתמלול סותר את השקפים - ציין: > ⚠️ ... ותן את הנכון.
- השמט פטפוט, ענייני זום וניהול כיתה. שמור כל מידע מנהלי חשוב (משקל ציונים, סוג מבחן, מטלות, תאריכים) בסעיף "מידע על הקורס" בתחילת הפרק.
- התמלול אוטומטי ויש בו שגיאות במונחים - תקן לפי ההקשר והשקפים, אל תעתיק שגיאות.
- אל תמציא תוכן שלא היה בהרצאה. מותר להוסיף הסבר קצר כשמשהו לא ברור, ולסמן אותו "(הרחבה)".

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
- attendance: חובת נוכחות. materials: סביבת עבודה, ספרים, דף נוסחאות. other: כל דבר מנהלי חשוב אחר.
אם לא נאמר שום דבר מנהלי - רשימה ריקה. אל תמציא.
exam_type ו-grade_weights: רק אם נאמרו במפורש בחומר הזה, אחרת "unknown" ורשימה ריקה."""

KIND_TASK = {
    "lecture": "זו הרצאה. כתוב פרק קריאה מלא שמחליף צפייה בהרצאה.",
    "practice": "זה תרגול. בפרק: רשימת התרגילים שנפתרו, ולכל תרגיל - השאלה, ופתרון מלא שלב אחרי שלב עם הסבר למה עושים כל צעד, טריקים וטעויות נפוצות. השאלות האמריקאיות יבדקו הבנת שיטות הפתרון.",
    "lab": "זה מפגש מעבדה. כתוב: מטרת הניסוי, רקע תיאורטי, מהלך, מה מודדים ולמה, תוצאות צפויות, וטעויות נפוצות. השאלות - בסגנון בוחן כניסה.",
    "web": "זה חומר מאתר אינטרנט שהסטודנט רוצה ללמוד בעצמו. כתוב פרק קריאה מסודר ומלמד על בסיס התוכן.",
    "other": "כתוב פרק קריאה מסודר על בסיס החומר.",
}


KIND_NAME = {"lecture": "הרצאה", "practice": "תרגול", "lab": "מעבדה", "web": "מאמר מהאינטרנט", "other": "חומר"}
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
    lines += [
        f"פריט: {KIND_NAME.get(lesson['kind'], '')} {lesson.get('number') or ''} {lesson.get('title') or ''}".strip(),
        KIND_TASK.get(lesson["kind"], KIND_TASK["other"]),
    ]
    if slide_count:
        lines.append(f"מצורפים {slide_count} צילומי לוח/שקפים, ממוספרים 1..{slide_count} לפי הסדר. בתמלול מסומן מתי כל אחד הופיע.")
    lines += ["", "=== התמלול / התוכן ===", transcript]
    return "\n".join(lines)


def author_with_gemini(course, lesson, transcript, slides, previous_topics, log=print):
    """slides: list of (number, Path). Returns the parsed chapter dict."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    model = os.environ.get("GEMINI_MODEL") or "gemini-flash-latest"
    parts = [types.Part.from_text(text=build_prompt(course, lesson, transcript, len(slides), previous_topics))]
    for n, path in slides:
        parts.append(types.Part.from_text(text=f"שקף {n}:"))
        parts.append(types.Part.from_bytes(data=Path(path).read_bytes(), mime_type="image/webp"))

    log(f"כותב פרק קריאה ושאלון ({model})...")
    resp = client.models.generate_content(
        model=model,
        contents=[types.Content(role="user", parts=parts)],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM,
            response_mime_type="application/json",
            response_json_schema=CHAPTER_SCHEMA,
            max_output_tokens=65536,
        ),
    )
    return validate(json.loads(resp.text))


def validate(ch):
    """Drop malformed questions instead of failing the whole lesson."""
    good = []
    for q in ch.get("questions", []):
        opts = q.get("options") or []
        if len(opts) >= 2 and isinstance(q.get("correct"), int) and 0 <= q["correct"] < len(opts):
            good.append(q)
    ch["questions"] = good
    ch.setdefault("topics", [])
    return ch
