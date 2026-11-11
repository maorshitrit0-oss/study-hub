"""Shared builder for practices Claude writes so that practice N follows lecture N (his request 11/11/2026):
full chapter = recap + every exercise worked out; condensed = recap only; exercises + MCQ in the app."""
NOTE = ("> 📌 התרגול הזה נכתב בדיוק לפי מה שנלמד בהרצאה {n}: הנוסחאות והדוגמאות מהלוח, וכל תוצאה נבדקה בחישוב מספרי.\n")


def pack(n, title, topics, ex, qs, intro, recap, uncertain, note=NOTE):
    head = note.format(n=n) + "\n" + intro + "\n\n## תזכורת מהרצאה " + str(n) + "\n" + recap
    summary = head + "\n\n## התרגילים\nהתרגילים והפתרונות המלאים בלשונית התרגילים. כדאי לפתור לבד ורק אז לפתוח את הפתרון.\n"
    full = head + "\n\n" + "\n\n".join(
        f"## {x['title']}\n\n**השאלה:** {x['question_md']}\n\n**👀 הפתרון:**\n\n{x['solution_md']}" for x in ex)
    return {"title": title, "chapter_md": full, "summary_md": summary, "topics": topics, "glossary": [], "course_facts": [],
            "syllabus_covered": [], "exam_type": "mcq", "grade_weights": [], "homework": [],
            "exercises": [dict(x, exam_style=True, uncertain=False) for x in ex],
            "questions": [dict(question=q, options=o, correct=c, explanation=e, topic=t, difficulty=d) for q, o, c, e, t, d in qs],
            "verification": {"fixes": ["נכתב על ידי Claude לפי הרצאה " + str(n) + "; כל מספר חושב מחדש בחישוב מספרי."],
                             "uncertain": uncertain}}
