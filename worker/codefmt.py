"""Code written on ONE line inside a quiz question (his screenshot 18/11/2026: a Java switch flowed across the line and he
got many questions wrong). Finds the code in the question text and puts it in a ```java / ```c block, one statement per
line with indentation. Only the layout changes - every character of the code stays.
  python hub.py quiz-code "<course>" [--apply]   (without --apply: prints what would change)"""
import re

START = re.compile(r"(?<![\w.])(?:int|long|double|float|char|boolean|String|byte|short|for|while|if|switch|do|System\.|public|"
                   r"class|static|void|final|uint8_t|uint16_t|uint32_t|unsigned|#define|volatile|const|Scanner|Integer|"
                   r"pinMode|digitalWrite|digitalRead|x\s*=|[a-z]\w*\s*(?:\[\])?\s*=\s)(?=[\s(\[.])")
HEB = re.compile(r"[֐-׿]")
C_HINT = re.compile(r"uint\d+_t|#define|unsigned|printf|digitalRead|digitalWrite|pinMode|volatile|->|\bISR\b")


def fmt(code):
    """One statement per line: split after ; { } (outside strings and parentheses) and after case X: / default:."""
    out, line, depth, ind, i, n = [], "", 0, 0, 0, len(code)
    case_at = set()  # brace levels that are inside a case label: their statements get one more indent

    def push(label=False):
        nonlocal line
        t = re.sub(r"\s{2,}", " ", line.strip()) if '"' not in line and "'" not in line else line.strip()
        if t:
            extra = 1 if (ind in case_at and not label) else 0
            out.append("    " * max(ind + extra, 0) + t)
        line = ""
    while i < n:
        ch = code[i]
        if ch in "\"'":  # a string / char literal: copy as is
            j = i + 1
            while j < n and code[j] != ch:
                j += 2 if code[j] == "\\" else 1
            line += code[i:j + 1]
            i = j + 1
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth == 0 and ch == ";":
            line += ch
            push()
        elif depth == 0 and ch == "{" and line.rstrip().endswith(("=", "]", ",")):
            # an array initializer {10, 20, 30}: stays on its line
            j, d = i, 0
            while j < n:
                d += (code[j] == "{") - (code[j] == "}")
                if d == 0:
                    break
                j += 1
            line += " " + code[i:j + 1].strip() if not line.endswith(" ") else code[i:j + 1].strip()
            i = j + 1
            continue
        elif depth == 0 and ch == "{":
            line += " {" if line.strip() else "{"
            push()
            ind += 1
        elif depth == 0 and ch == "}":
            push()
            case_at.discard(ind)
            ind -= 1
            line = "}"
            # "} else" / "} while (...)" stay on the closing brace's line
            rest = code[i + 1:].lstrip()
            if not re.match(r"(else|while|catch|finally)\b", rest):
                push()
        elif depth == 0 and ch == ":" and re.match(r"\s*(case\b.*|default)\s*$", line):
            line += ch
            case_at.discard(ind)
            push(label=True)
            case_at.add(ind)
        else:
            line += ch
        i += 1
    push()
    return "\n".join(out)


def fix(text, lang=None):
    """The question with its one-line code in a block, or None when there is nothing to fix."""
    if "```" in text or "\n" in text.strip() and text.count(";") < 2:
        return None
    m = START.search(text)
    if not m:
        return None
    s = m.start()
    # the code ends at the last ; or } before Hebrew text resumes
    tail = text[s:]
    heb = HEB.search(tail)
    seg = tail[:heb.start()] if heb else tail
    end = max(seg.rfind(";"), seg.rfind("}"))
    if end < 0:
        return None
    code = seg[:end + 1]
    if code.count(";") + code.count("{") < 2 or len(code) < 25:
        return None  # a single short expression reads fine inline
    lang = lang or ("c" if C_HINT.search(code) else "java")
    before = text[:s].rstrip()
    if before.endswith("`") and tail[end + 1:].lstrip().startswith("`"):  # it was in inline backticks: drop them
        before, tail = before[:-1], tail[:end + 1] + tail[end + 1:].lstrip()[1:]
    before, after = before.rstrip(), tail[end + 1:].strip()
    out = f"{before}\n\n```{lang}\n{fmt(code)}\n```\n\n{after}".strip()
    # Arabic letters that slipped into the Hebrew text ("`b` و-`x`", "ب-Java")
    return re.sub(r"(?<=[\s`])و(?=-)", "ו", re.sub(r"(?<=[\s`])ب(?=-)", "ב", out))
