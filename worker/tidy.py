"""Tidy the layout of exercise solutions (his remark 11/11/2026: "the equations jump, two steps in one line, I can't
tell what each line says"). Layout only - the words, formulas and numbers stay exactly as they are:
- a display formula ($$...$$) that shares a line with text gets a line of its own;
- "**נוסחה:** / **הצבה:** / **תוצאה:** / **חישוב:** / **הסבר:**" labels start their own line;
- steps run together in one paragraph ("1. ... 2. ...", " / ") are split one per line;
- the boilerplate "📘 נוסחה מההרצאה ..." stays, on its own line.
"""
import re

DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.S)
LABELS = r"(?:נוסחה|הצבה|תוצאה|חישוב|חישובי ביניים|הסבר|למה|בדיקה|מסקנה|הרעיון|שלב \d+|סעיף [א-ת\d]+|פתרון|תשובה)"
LABEL = re.compile(rf"\s*(\*\*{LABELS}[^*]{{0,20}}\*\*)")


def _split_display(line):
    """'text $$f$$ more' -> ['text', '$$f$$', 'more'] (a lone display formula is left as it is)."""
    if "$$" not in line or DISPLAY.fullmatch(line.strip()):
        return [line]
    out, pos = [], 0
    for m in DISPLAY.finditer(line):
        before = line[pos:m.start()].strip()
        if re.fullmatch(r"[.,;:]+", before):
            before = ""
        if before:
            out.append(before)
        out += ["", f"$${m.group(1).strip()}$$", ""]
        pos = m.end()
    after = line[pos:].strip()
    if re.fullmatch(r"[.,;:]+", after):  # the sentence's period after the formula - not a line of its own
        after = ""
    if after:
        out.append(after)
    return out


def _prose(text):
    """The layout rules, on text outside code (a code line must never be split - 11/11/2026)."""
    # Steps glued with " / " between labels ("**נוסחה:** ... / **הצבה:** ...").
    text = re.sub(rf"\s+/\s+(?=\*\*{LABELS})", "\n", text)
    # A label in the middle of a line starts a new line.
    text = re.sub(rf"(?<=\S)[ \t]+(?=\*\*{LABELS}[^*]{{0,20}}\*\*)", "\n", text)
    # Numbered steps glued in one line: "... ✅. 2. **..." / "... . 3. ..." -> new line before "N."
    text = re.sub(r"(?<=[.✅:)])\s+(?=\d{1,2}\.\s+(?:\*\*|[א-ת]))", "\n", text)
    # 📘 boilerplate on its own line.
    text = re.sub(r"(?<=\S)[ \t]+(?=📘)", "\n", text)
    # "✅" verdict lines and "💡 הרעיון" start a new line.
    text = re.sub(r"(?<=\S)[ \t]+(?=💡)", "\n\n", text)
    return text


def tidy(md):
    if not md:
        return md
    text = md.replace("\r\n", "\n")
    # outside code only: ``` blocks and `inline code` are left exactly as they are
    text = "".join(part if i % 2 else _prose(part) for i, part in enumerate(re.split(r"(```[\s\S]*?```|`[^`\n]*`)", text)))
    lines = []
    in_code = False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
            lines.append(line)
            continue
        if in_code:
            lines.append(line)
            continue
        lines += _split_display(line)
    out = "\n".join(lines)
    # A label line right after text: blank line before it, so it is its own paragraph.
    out = re.sub(rf"(?<=[^\n])\n(?=\*\*{LABELS})", "\n\n", out)
    out = re.sub(r"(?<=[^\n])\n(?=📘|💡|✅)", "\n\n", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    out = re.sub(r"(💡|✅|📘)\s*\n+\s*(?=\*\*)", r"\1 ", out)  # keep "💡 **הרעיון:**" together
    out = re.sub(r"(?m)^(\s*\d{1,2}\.)[ \t]*\n+[ \t]*(?=\*\*)", r"\1 ", out)  # "1. **נוסחה:**" stays one item
    return out.strip()


def redo(sb, course, log=print):
    """Lay out again from the ORIGINAL texts (the first tidy_backup of the course), with the current rules: the first
    version also split code lines and left bare "1." items (his remark 11/11/2026). Only exercises in that backup."""
    import json
    store = sb.storage.from_("study")
    prefix = f"{course['user_id']}/materials/{course['id']}"
    names = sorted(f["name"] for f in store.list(prefix) if f["name"].startswith("tidy_backup_"))
    if not names:
        log(f"::notice title=Tidy::{course['name']}: no backup")
        return 0
    orig = json.loads(store.download(f"{prefix}/{names[0]}").decode())
    n = 0
    for r in orig:
        q, s_ = tidy(r["question_md"] or ""), tidy(r["solution_md"] or "")
        got = sb.table("exercises").update({"question_md": q, "solution_md": s_}).eq("id", r["id"]).execute().data
        n += bool(got)
    log(f"::notice title=Tidy::{course['name']}: {n} exercises laid out again from {names[0]}")
    return n


def run(sb, course, log=print):
    """Tidy every exercise of the course (question and solution); keeps a copy of the originals in storage first."""
    import json
    from datetime import datetime
    rows = sb.table("exercises").select("id, question_md, solution_md").eq("course_id", course["id"]).execute().data
    changed = []
    for r in rows:
        q, s = tidy(r["question_md"] or ""), tidy(r["solution_md"] or "")
        if q != (r["question_md"] or "").strip() or s != (r["solution_md"] or "").strip():
            changed.append((r, q, s))
    if not changed:
        log(f"::notice title=Tidy::{course['name']}: nothing to tidy")
        return 0
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    backup = [{"id": r["id"], "question_md": r["question_md"], "solution_md": r["solution_md"]} for r, _, _ in changed]
    sb.storage.from_("study").upload(f"{course['user_id']}/materials/{course['id']}/tidy_backup_{stamp}.json",
                                     json.dumps(backup, ensure_ascii=False).encode("utf-8"),
                                     {"content-type": "application/json", "upsert": "true"})
    for r, q, s in changed:
        sb.table("exercises").update({"question_md": q, "solution_md": s}).eq("id", r["id"]).execute()
    log(f"::notice title=Tidy::{course['name']}: {len(changed)}/{len(rows)} exercises tidied (originals saved: tidy_backup_{stamp}.json)")
    return len(changed)
