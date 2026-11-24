"""Checks the free backup providers (Groq, Mistral) from the runner: reachable, key works, Hebrew + LaTeX + JSON."""
import json

from google.genai import types

import author

text = """מהפך CMOS: כאשר הכניסה נמוכה, טרנזיסטור ה-PMOS מוליך וה-NMOS בקיטעון, ולכן המוצא שווה ל-$V_{DD}$.
מתח המעבר $V_M$ הוא הנקודה שבה $V_{in} = V_{out}$; במהפך סימטרי $V_M = V_{DD}/2$.
שולי הרעש: $NM_L = V_{IL} - V_{OL}$ ו-$NM_H = V_{OH} - V_{IH}$."""
schema = {"type": "object", "properties": {"questions": {"type": "array", "items": {"type": "object", "properties": {
    "question": {"type": "string"}, "options": {"type": "array", "items": {"type": "string"}}, "correct": {"type": "integer"},
    "explanation": {"type": "string"}}}}}}
for env, url, model in author.BACKUPS:
    author.BACKUPS_ONE = [(env, url, model)]
    saved = author.BACKUPS
    author.BACKUPS = [(env, url, model)]
    out = author._backup_json([types.Part.from_text(text=text)],
                              "כתוב 2 שאלות אמריקאיות של הבנה על הפרק, 4 תשובות, correct = אינדקס, נוסחאות ב-$...$.", schema)
    author.BACKUPS = saved
    print("RESULT", model, json.dumps(out, ensure_ascii=False)[:900] if out else None, flush=True)
