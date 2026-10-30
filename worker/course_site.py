"""Import a lecturer's course website (a public Notion page, with its sub-pages and attached files) into a course.

  python course_site.py show <url>                  print what would be imported (pages as Markdown, files, links)
  python course_site.py import <course_id> <url>    files -> course files (materials), all text -> one course file,
                                             each week / extra page (review questions) / past exam -> a lesson + chapter
  python course_site.py pending                     daily: re-read imported sites and continue writing chapters
  python course_site.py check                       every half hour: re-read only (new recordings start at once)

Notion renders in the browser, so its public pages are read through the same JSON endpoints its own page uses
(loadPageChunk / syncRecordValues / getSignedFileUrls). Nothing is deleted; running it again adds only what is new.
"""
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

import requests

BUCKET = "study"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140 Safari/537.36"}
MAX_FILE = 50 * 1024 * 1024  # Supabase free tier, per file
MAX_PAGES = 60


def dashed(i):
    i = i.replace("-", "")
    return f"{i[:8]}-{i[8:12]}-{i[12:16]}-{i[16:20]}-{i[20:]}"


def page_id(url):
    # The id is the last 32 hex digits of the last path part ("...-2027-327e0f37...": the year is not part of it).
    tail = urlparse(url).path.rstrip("/").split("/")[-1].replace("-", "")[-32:]
    if not re.fullmatch(r"[0-9a-f]{32}", tail):
        raise SystemExit("זה לא קישור לדף Notion (חסר מזהה הדף בסוף הכתובת)")
    return dashed(tail)


def unwrap(url):
    """Google calendar/search redirect -> the real link."""
    u = urlparse(url)
    if u.netloc.endswith("google.com") and u.path == "/url":
        return parse_qs(u.query).get("q", [url])[0]
    return url


class Notion:
    def __init__(self, url):
        u = urlparse(url)
        # app.notion.com/p/<space>/... links are the same page; the public site answers the API.
        host = u.netloc if u.netloc.endswith("notion.site") else "www.notion.so"
        if u.netloc == "app.notion.com":
            space = u.path.split("/")[2] if u.path.startswith("/p/") else ""
            host = f"{space}.notion.site" if space else "www.notion.so"
        self.base = f"https://{host}"
        self.root = page_id(url)
        self.blocks = {}
        self.http = requests.Session()
        self.http.headers.update(UA)

    def api(self, name, body):
        for attempt in range(4):
            r = self.http.post(f"{self.base}/api/v3/{name}", json=body, timeout=60)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            return r.json()
        r.raise_for_status()

    def _add(self, record_map):
        for bid, rec in (record_map.get("block") or {}).items():
            v = rec.get("value") or {}
            if "value" in v and isinstance(v["value"], dict):  # newer responses wrap value + role
                v = v["value"]
            if v.get("alive", True) is not False and v:
                self.blocks[bid] = v

    def load_page(self, pid):
        cursor, chunk = {"stack": []}, 0
        while True:
            data = self.api("loadPageChunk", {"pageId": pid, "limit": 100, "cursor": cursor,
                                              "chunkNumber": chunk, "verticalColumns": False})
            self._add(data.get("recordMap") or {})
            cursor = data.get("cursor") or {"stack": []}
            chunk += 1
            if not cursor.get("stack") or chunk > 30:
                break
        self.fill_missing(pid)

    def fill_missing(self, pid):
        """Children that the page chunk did not include (closed toggles, long pages)."""
        tried = set()
        for _ in range(10):
            parents = {}
            for bid in self.tree_ids(pid):
                for c in self.blocks.get(bid, {}).get("content", []):
                    if c not in self.blocks:
                        parents.setdefault(bid, []).append(c)
            missing = [c for cs in parents.values() for c in cs]
            if not missing or all(p in tried for p in parents):
                return
            before = len(self.blocks)
            space = self.blocks.get(pid, {}).get("space_id")
            try:
                for i in range(0, len(missing), 100):
                    reqs = [{"pointer": {"table": "block", "id": b, **({"spaceId": space} if space else {})}, "version": -1}
                            for b in missing[i:i + 100]]
                    self._add((self.api("syncRecordValues", {"requests": reqs}) or {}).get("recordMap") or {})
            except requests.RequestException:
                pass  # public sites refuse it; load each parent block as its own chunk instead
            if len(self.blocks) == before:
                for parent in parents:
                    if parent not in tried:
                        tried.add(parent)
                        try:
                            self._add(self.api("loadPageChunk", {"pageId": parent, "limit": 100, "cursor": {"stack": []},
                                                                 "chunkNumber": 0, "verticalColumns": False}).get("recordMap") or {})
                        except requests.RequestException:
                            pass

    def tree_ids(self, pid):
        """Blocks of one page (not descending into sub-pages)."""
        out, stack = [], [pid]
        while stack:
            bid = stack.pop()
            out.append(bid)
            b = self.blocks.get(bid)
            if b and (bid == pid or b.get("type") != "page"):
                stack += list(reversed(b.get("content", [])))
        return out

    def title(self, bid):
        return plain(self.blocks.get(bid, {}).get("properties", {}).get("title")) or "ללא כותרת"

    def page_url(self, pid):
        return f"{self.base}/{pid.replace('-', '')}"

    def file_url(self, bid, src):
        """A downloadable link for an attachment of a public page."""
        if not (src.startswith("attachment:") or "secure.notion-static.com" in src or "prod-files-secure" in src):
            return src
        space = self.blocks.get(bid, {}).get("space_id")
        try:
            data = self.api("getSignedFileUrls", {"urls": [{"url": src, "permissionRecord": {
                "table": "block", "id": bid, **({"spaceId": space} if space else {})}}]})
            signed = (data or {}).get("signedUrls") or []
            if signed and signed[0]:
                return signed[0]
        except requests.RequestException:
            pass
        return f"{self.base}/signed/{quote(src, safe='')}?table=block&id={bid}" + (f"&spaceId={space}" if space else "")


def plain(rich):
    return "".join(seg[0] for seg in rich or [] if seg and isinstance(seg[0], str)).strip()


FILE_TYPES = {"file", "pdf", "image", "video", "audio"}


def walk(n, max_pages=MAX_PAGES):
    """All pages from the root: [(page_id, title, lines)], files [{page_id, line, name, block, src}], links [...].
    A file's `line` is its index in its page's lines, so files can be grouped by the section they appear in."""
    pages, files, links, seen = [], [], [], set()
    queue = [(n.root, 0)]
    while queue and len(pages) < max_pages:
        pid, depth = queue.pop(0)
        if pid in seen:
            continue
        seen.add(pid)
        try:
            n.load_page(pid)
        except requests.RequestException as e:
            print(f"::warning title=Site::page {pid} not readable: {e}", flush=True)
            continue
        title = n.title(pid)
        lines = []

        def rich(r, bid=None):
            out = []
            for seg in r or []:
                text, ann = seg[0], (seg[1] if len(seg) > 1 else [])
                for a in ann:
                    if a[0] == "a" and len(a) > 1:
                        href = unwrap(a[1])
                        if href.startswith("/"):
                            href = n.base + href
                        if href.startswith("attachment:") and bid:  # a file attached as a link (e.g. a .pptx)
                            files.append({"page_id": pid, "page": title, "line": len(lines), "name": text.strip() or
                                          href.rsplit(":", 1)[-1], "block": bid, "src": href})
                            text = f"📎 {text}"
                        else:
                            links.append({"page_id": pid, "page": title, "line": len(lines), "text": text, "url": href})
                            text = f"[{text}]({href})"
                    elif a[0] == "p" and len(a) > 1:
                        sub = dashed(a[1])
                        queue.append((sub, depth + 1))
                        links.append({"page_id": pid, "page": title, "line": len(lines), "text": "", "url": n.page_url(sub), "sub": sub})
                        text = f"[{n.title(sub) if sub in n.blocks else 'דף'}]({n.page_url(sub)})"
                    elif a[0] == "e" and len(a) > 1:
                        text = f"${a[1]}$"
                    elif a[0] == "b":
                        text = f"**{text}**" if text.strip() else text
                    elif a[0] == "c":
                        text = f"`{text}`"
                out.append(text)
            return "".join(out)

        def block(bid, indent):
            b = n.blocks.get(bid)
            if not b:
                return
            t, props, pad = b.get("type"), b.get("properties", {}), "  " * indent
            text = rich(props.get("title"), bid)
            children = b.get("content", [])
            if t == "page" and bid != pid:
                queue.append((bid, depth + 1))
                links.append({"page_id": pid, "page": title, "line": len(lines), "text": "", "url": n.page_url(bid), "sub": bid})
                lines.append(f"{pad}- 📄 [{plain(props.get('title')) or 'דף'}]({n.page_url(bid)})")
                return
            if t in FILE_TYPES or t in ("bookmark", "embed"):
                src = (props.get("source") or props.get("link") or [[""]])[0][0]
                src = unwrap(src or b.get("format", {}).get("display_source", ""))
                name = plain(props.get("title")) or unquote(Path(urlparse(src).path).name) or t
                if t in ("bookmark", "embed") or (t == "video" and not src.startswith("attachment:")):
                    links.append({"page_id": pid, "page": title, "line": len(lines), "text": name, "url": src})
                    lines.append(f"{pad}- 🔗 [{name}]({src})")
                elif t == "image":
                    lines.append(f"{pad}- 🖼️ {name}")
                else:
                    files.append({"page_id": pid, "page": title, "line": len(lines), "name": name, "block": bid, "src": src})
                    lines.append(f"{pad}- 📎 {name}")
                return
            prefix = {"header": "# ", "sub_header": "## ", "sub_sub_header": "### ", "bulleted_list": "- ",
                      "numbered_list": "1. ", "to_do": "- [ ] ", "toggle": "- ", "quote": "> ", "callout": "> "}.get(t, "")
            if t == "code":
                lang = plain(props.get("language")).lower()
                lines.append(f"{pad}```{lang}\n{plain(props.get('title'))}\n{pad}```")
            elif t == "equation":
                lines.append(f"{pad}$$\n{plain(props.get('title'))}\n$$")
            elif t == "divider":
                lines.append("---")
            elif t == "table_row":
                cols = n.blocks.get(b.get("parent_id"), {}).get("format", {}).get("table_block_column_order") or list(props)
                lines.append(pad + "| " + " | ".join(rich(props.get(c), bid) for c in cols) + " |")
            elif text:
                lines.append(f"{pad}{prefix}{text}")
            nested = indent + 1 if t in ("bulleted_list", "numbered_list", "toggle", "to_do") else indent
            for c in children:
                block(c, nested)

        for c in n.blocks.get(pid, {}).get("content", []):
            block(c, 0)
        pages.append((pid, title, lines))
    return pages, files, links


# ---------- show ----------

def annotate(text):
    """The run's text as annotations (readable through the checks API when the log is not)."""
    chunks = [text[i:i + 3500] for i in range(0, len(text), 3500)][:30]
    for i, c in enumerate(chunks):
        kind = ("notice", "warning", "error")[i // 10]
        print(f"::{kind} title=part {i + 1}/{len(chunks)}::" + c.replace("%", "%25").replace("\r", "").replace("\n", "%0A"), flush=True)


def cmd_show(url):
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            show(url)
        except Exception as e:  # noqa: BLE001 - report it where it can be read
            print(f"FAILED: {type(e).__name__}: {e}")
    print(buf.getvalue())
    annotate(buf.getvalue())


def show(url):
    if re.search(r"youtube\.com/|youtu\.be/", url):  # can Gemini read this YouTube video directly (official API)?
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"].split(",")[0].strip())
        for model in ["gemini-2.5-flash", "gemini-flash-latest"]:
            try:
                r = client.models.generate_content(model=model, contents=types.Content(parts=[
                    types.Part(file_data=types.FileData(file_uri=url),
                               video_metadata=types.VideoMetadata(start_offset="600s", end_offset="660s")),
                    types.Part(text="תמלל מילה במילה את מה שנאמר בקטע הזה (עברית), ותאר בשורה מה רואים על המסך.")]),
                    config=types.GenerateContentConfig(media_resolution="MEDIA_RESOLUTION_LOW"))
                print(f"{model}: OK tokens={r.usage_metadata.prompt_token_count}\n{(r.text or '')[:1500]}")
                break
            except Exception as e:  # noqa: BLE001
                print(f"{model}: FAILED {str(e)[:300]}")
        return
    n = Notion(url)
    pages, files, links = walk(n)
    print(f"\n===== {len(files)} FILES =====")
    for f in files:
        u = n.file_url(f["block"], f["src"])
        try:
            with n.http.get(u, stream=True, timeout=30) as r:  # signed links answer GET only
                info = f"{r.status_code} {r.headers.get('content-type', '')} {r.headers.get('content-length', '?')}"
        except requests.RequestException as e:
            info = f"ERR {e}"
        print(f"- [{f['page']}] {f['name']} :: {info}")
    print(f"\n===== {len(links)} LINKS =====")
    for l in [l for l in links if not l.get("sub")]:
        print(f"- [{l['page']}] {l['text']} -> {l['url']}")
    print("\n===== WEEK SECTIONS =====")
    for pid, title, lines in pages:
        for name, start, end in sections(lines):
            print(f"- [{title}] {name} ({end - start} lines)")
    for pid, title, lines in pages:
        print(f"\n===== PAGE {title} ({pid}) =====\n" + "\n".join(lines))


# ---------- import ----------

SITE_MD = "site.md"            # <user>/materials/<course>/site.md - all the site's text; its first line holds the URL
SITE_NOTE = "<!-- course-site -->"  # first line of a lesson made from the site (its transcript is the site's text)
FILE_REF = re.compile(r"^\[\[file:(.+?)\]\]$", re.M)
VIDEO = re.compile(r"\.(mov|mp4|m4v|avi|mkv|webm)$", re.I)
EXAM = re.compile(r"מועד|מבחן|בחינה|exam", re.I)
WEEK = re.compile(r"^#{1,3} .*?(week|שבוע)\s*\d+", re.I)
HEAD = re.compile(r"^(#{1,3}) ")


def db():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def safe_name(name):
    return re.sub(r"[^\w.\-]+", "_", name, flags=re.A).strip("_")[-80:] or "file"


def sections(lines):
    """Week sections of a page: [(title, start, end)] by its "Week N" / "שבוע N" headings (code blocks skipped)."""
    heads, fence = [], False
    for i, line in enumerate(lines):
        if not fence and HEAD.match(line):
            heads.append((i, len(HEAD.match(line)[1]), line))
        # A code block is one entry holding both of its fences.
        if sum(x.lstrip().startswith("```") for x in line.split("\n")) % 2:
            fence = not fence
    out = []
    for k, (i, level, line) in enumerate(heads):
        if not WEEK.match(line):
            continue
        end = next((j for j, lv, _ in heads[k + 1:] if lv <= level), len(lines))
        out.append((re.sub(r"[#*]", "", line).strip(), i, end))
    return out


def week_number(title):
    """"Week 3 - ADC" -> 3 (the semester week of last year's material; matched to this year's lecture 3)."""
    m = re.search(r"(?:week|שבוע)\s*(\d+)", title or "", re.I)
    return int(m[1]) if m else None


def kind_of(name):
    if EXAM.search(name):
        return "past_exam"
    return "slides" if re.search(r"\.(pdf|pptx?)$", name, re.I) else "other"


def cmd_import(course_id, url, write=True):
    sb, n = db(), Notion(url)
    course = sb.table("courses").select("*").eq("id", course_id).single().execute().data
    uid, store = course["user_id"], sb.storage.from_(BUCKET)
    pages, files, links = walk(n)
    print(f"::notice title=Site::{len(pages)} pages, {len(files)} files, {len(links)} links", flush=True)

    # 1. Files -> course files (each once; videos and files over 50 MB stay as links in the site text).
    have = {m["storage_path"] for m in sb.table("materials").select("storage_path").eq("course_id", course_id).execute().data}
    paths, skipped, names = {}, [], set()
    for f in files:
        key = (f["name"], f["page_id"])
        if VIDEO.search(f["name"]) or f["name"] in names:
            if f["name"] not in names:
                skipped.append(f"{f['name']} (סרטון - נשאר באתר)")
            continue
        names.add(f["name"])
        path = f"{uid}/materials/{course_id}/site_{f['block'][:8]}_{safe_name(f['name'])}"
        if path in have:
            paths[key] = path
            continue
        try:
            r = n.http.get(n.file_url(f["block"], f["src"]), timeout=300)
            r.raise_for_status()
            data = r.content
            if len(data) > MAX_FILE:
                skipped.append(f"{f['name']} (גדול מ-50MB)")
                continue
            mime = r.headers.get("content-type", "application/octet-stream").split(";")[0]
            if f["name"].lower().endswith(".pdf"):
                mime = "application/pdf"
            store.upload(path, data, {"content-type": mime, "upsert": "true"})
            sb.table("materials").insert({"user_id": uid, "course_id": course_id, "title": f["name"], "kind": kind_of(f["name"]),
                                          "storage_path": path, "mime": mime, "size_bytes": len(data)}).execute()
            paths[key] = path
            print(f"file: {f['name']} ({len(data) // 1024} KB)", flush=True)
        except Exception as e:  # noqa: BLE001 - one file must not stop the import
            skipped.append(f"{f['name']} ({str(e)[:80]})")
            print(f"::warning title=Site file::{f['name']}: {str(e)[:300]}", flush=True)

    # 2. All the text -> one course file (also what the course chat reads with "עם קבצי הקורס").
    md = [f"מקור: {url}", f"# אתר הקורס - {course['name']}"]
    for pid, title, lines in pages:
        md += ["", f"# 📄 {title}", f"({n.page_url(pid)})", "", *lines]
    if skipped:
        md += ["", "## קבצים שלא הועתקו", *[f"- {x}" for x in skipped]]
    site_path = f"{uid}/materials/{course_id}/{SITE_MD}"
    store.upload(site_path, "\n".join(md).encode("utf-8"), {"content-type": "text/markdown; charset=utf-8", "upsert": "true"})
    if site_path not in have:
        sb.table("materials").insert({"user_id": uid, "course_id": course_id, "title": "🌐 אתר הקורס (כל הטקסט)",
                                      "kind": "other", "storage_path": site_path, "mime": "text/plain"}).execute()

    # 3. Lessons: a chapter + quiz per week, per extra page (review questions...), per past exam.
    by_page = {pid: (title, lines) for pid, title, lines in pages}
    subs_in = {}  # sub-page -> (parent page, line)
    for l in links:
        if l.get("sub") and l["sub"] in by_page and l["sub"] not in subs_in:
            subs_in[l["sub"]] = (l["page_id"], l["line"])
    planned, used_pages = [], {n.root}

    def doc_paths(pid, start, end):
        return [paths[(f["name"], f["page_id"])] for f in files
                if f["page_id"] == pid and start <= f["line"] < end and (f["name"], f["page_id"]) in paths
                and f["name"].lower().endswith(".pdf") and not EXAM.search(f["name"])]

    for pid, title, lines in pages:
        for name, start, end in sections(lines):
            body, docs = lines[start:end], doc_paths(pid, start, end)
            for sub, (parent, line) in subs_in.items():  # a week's own sub-page ("Week 9 Material") belongs to it
                if parent == pid and start <= line < end:
                    used_pages.add(sub)
                    body += ["", f"## {by_page[sub][0]}", *by_page[sub][1]]
                    docs += doc_paths(sub, 0, len(by_page[sub][1]))
            # A week the lecturer has not filled yet is left for a later day's run (lessons are never updated).
            if docs or sum(len(x) for x in body) >= 600:
                planned.append((f"{n.page_url(pid)}#w{start}", name, body, docs, ""))
            used_pages.add(pid)
    for pid, title, lines in pages:
        if pid in used_pages or sum(len(x) for x in lines) < 1500:
            continue
        hint = "זה דף שאלות חזרה של המרצה: פתור כל שאלה בפירוט, כדוגמה פתורה, עם קוד מלא ומוסבר." if EXAM.search(title) or "שאלות" in title else ""
        planned.append((n.page_url(pid), title, lines, doc_paths(pid, 0, len(lines)), hint))
    for f in files:
        key = (f["name"], f["page_id"])
        if EXAM.search(f["name"]) and f["name"].lower().endswith(".pdf") and key in paths:
            planned.append((f"{n.page_url(f['page_id'])}#{f['block']}", f"מבחן קודם: {Path(f['name']).stem}", [],
                            [paths[key]], "זה מבחן קודם של המרצה (קובץ מצורף): פתור כל שאלה במלואה, שלב אחרי שלב, כדוגמה פתורה."))

    existing = {l["source_url"]: l for l in sb.table("lessons").select("id, source_url, number").eq("course_id", course_id).execute().data}
    new = [p for p in planned if p[0] not in existing]
    for src, title, *_ in planned:  # week number on lessons imported before numbers were kept (the chapter renames them)
        week = week_number(title)
        if src in existing and week and not existing[src].get("number"):
            sb.table("lessons").update({"number": week}).eq("id", existing[src]["id"]).execute()
    for src, title, body, docs, hint in new:
        transcript = "\n".join([SITE_NOTE, f"מתוך אתר הקורס של המרצה ({src}).", hint,
                                *[f"[[file:{d}]]" for d in dict.fromkeys(docs)], "", *body]).strip()
        sb.table("lessons").insert({"user_id": uid, "course_id": course_id, "kind": "web", "title": title[:200],
                                    "number": week_number(title), "source_url": src, "transcript": transcript,
                                    "status": "queued", "progress": "מאתר הקורס - ממתין לכתיבת הפרק"}).execute()
    print(f"::notice title=Site::{len(paths)} files, {len(new)} new lessons ({len(planned) - len(new)} already there)", flush=True)
    recordings(sb, course, pages, links)
    if write:
        process_pending(sb)


# ---------- recordings: this semester's lectures, each compared with the same lecture of last year ----------

PAIRS = "site_recordings.json"   # <user>/materials/<course>/site_recordings.json: {"current": [...], "previous": [...]}
RECORDING = re.compile(r"(youtube\.com/watch|youtu\.be/|zoom\.us/rec/)")
NOT_LECTURE = re.compile(r"\bex\b|exercise|תרגול|recitation|תרגיל", re.I)
MY_GROUP = re.compile(r"\bEE\b|חשמל", re.I)  # he studies electrical engineering (the site also has a CE group)


def recording_lists(pages, links):
    """{year: [(text, url)]} from headings like "2027 Zoom Recordings (EE Group)" - his group's list per year."""
    by_year = {}
    for pid, _title, lines in pages:
        heads = [(i, line) for i, line in enumerate(lines) if HEAD.match(line)]
        for k, (i, line) in enumerate(heads):
            year = re.search(r"20\d\d", line)
            if not year or not re.search(r"record|הקלט", line, re.I):
                continue
            level = len(HEAD.match(line)[1])
            end = next((j for j, l in heads[k + 1:] if len(HEAD.match(l)[1]) <= level), len(lines))
            items = [(l["text"], l["url"]) for l in links
                     if l["page_id"] == pid and i < l["line"] < end and RECORDING.search(l["url"] or "")]
            group = bool(MY_GROUP.search(line)) or not re.search(r"\b(CE|EE)\b", line)
            prev = by_year.get(year[0])
            if items and (prev is None or (group and not prev[0])):
                by_year[year[0]] = (group, items)
    return {y: items for y, (_, items) in by_year.items()}


def recordings(sb, course, pages, links):
    """This semester's recordings -> lecture lessons (numbered in order); last year's list is kept for comparison:
    when lecture N is processed, last year's lecture N is transcribed too and the chapter compares the two."""
    years = recording_lists(pages, links)
    if not years:
        return
    cur = max(years)
    current = [u for _, u in years[cur]]
    previous = [u for t, u in years.get(str(int(cur) - 1), []) if not NOT_LECTURE.search(t or "")]
    store = sb.storage.from_(BUCKET)
    pairs_path = f"{course['user_id']}/materials/{course['id']}/{PAIRS}"
    try:
        notified = set(json.loads(store.download(pairs_path).decode()).get("notified") or [])
    except Exception:  # noqa: BLE001 - first run
        notified = set()
    lessons = sb.table("lessons").select("number, source_url").eq("course_id", course["id"]).eq("kind", "lecture").execute().data
    have_url, have_num = {l["source_url"] for l in lessons}, {l["number"] for l in lessons}
    for i, url in enumerate(current, 1):
        if url in have_url or i in have_num:  # he may have uploaded this lecture's Zoom himself
            continue
        row = sb.table("lessons").insert({"user_id": course["user_id"], "course_id": course["id"], "kind": "lecture",
                                          "number": i, "source_url": url, "status": "queued",
                                          "progress": "הקלטה מאתר הקורס - בתור"}).execute().data[0]
        print(f"::notice title=Site::lecture {i} from the site's recordings -> {dispatch(row['id'])}", flush=True)
    store.upload(pairs_path, json.dumps({"current": current, "previous": previous, "notified": sorted(notified)}).encode(),
                 {"content-type": "application/json", "upsert": "true"})


def dispatch(lesson_id, author="gemini"):
    """Starts process.yml for a lesson (GitHub Actions; GITHUB_TOKEN with actions: write)."""
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    if not repo or not token:
        return "no GITHUB_TOKEN - not started"
    r = requests.post(f"https://api.github.com/repos/{repo}/actions/workflows/process.yml/dispatches",
                      headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
                      json={"ref": "main", "inputs": {"lesson_id": lesson_id, "author": author}}, timeout=30)
    return "started" if r.ok else f"GitHub {r.status_code}: {r.text[:200]}"


def previous_lecture(sb, lesson):
    """Last year's lecture with the same number (transcribed for comparison; started here if it is not yet)."""
    if lesson["kind"] != "lecture" or not lesson.get("number"):
        return None
    try:
        pairs = json.loads(sb.storage.from_(BUCKET).download(
            f"{lesson['user_id']}/materials/{lesson['course_id']}/{PAIRS}").decode())
    except Exception:  # noqa: BLE001 - not a course with an imported site
        return None
    prev = pairs.get("previous") or []
    if lesson["number"] > len(prev):
        return None
    url = prev[lesson["number"] - 1]
    rows = sb.table("lessons").select("*").eq("course_id", lesson["course_id"]).eq("source_url", url).execute().data
    if rows:
        return rows[0]
    row = sb.table("lessons").insert({"user_id": lesson["user_id"], "course_id": lesson["course_id"], "kind": "other",
                                      "number": lesson["number"], "title": f"שנה שעברה · הרצאה {lesson['number']} (להשוואה)",
                                      "source_url": url, "status": "queued",
                                      "progress": "הקלטה משנה שעברה - מתומללת להשוואה עם ההרצאה של השנה"}).execute().data[0]
    print(f"previous year's lecture {lesson['number']}: {dispatch(row['id'], 'none')}", flush=True)
    return row


def process_pending(sb, budget=100 * 60):
    """Writes the chapters of lessons made from course sites, oldest first; stops when Gemini's daily quota is
    used up - the next morning's run continues (worker/course_site.py pending, from the daily cron)."""
    import author
    import hub
    start = time.time()
    rows = (sb.table("lessons").select("id, transcript, status, error").eq("kind", "web").in_("status", ["queued", "error"])
            .order("created_at").execute().data)
    # Failed only for the quota -> retry; any other failure waits for him to press "retry".
    rows = [r for r in rows if (r.get("transcript") or "").startswith(SITE_NOTE)
            and (r["status"] == "queued" or "מכסה" in (r.get("error") or ""))]

    for r in rows:
        if time.time() - start > budget:
            print("::notice title=Site::time budget used - the rest continue tomorrow", flush=True)
            return
        try:
            hub.cmd_process(r["id"])
        except Exception as e:  # noqa: BLE001
            if author._is(e, "RESOURCE_EXHAUSTED", "429", "quota", "המכסה"):
                print("::notice title=Site::daily Gemini quota used up - the rest continue tomorrow", flush=True)
                return


def retry_after_quota(sb):
    """Lessons (e.g. a YouTube lecture) that failed only on Gemini's daily quota: start each again in its own job.
    Run once a day just after the quota resets (~10:00 Israel), so a retry cannot fail on the same empty quota."""
    for r in (sb.table("lessons").select("id, error, transcript").eq("status", "error").like("error", "%מכסה%")
              .execute().data):
        if not (r.get("transcript") or "").startswith(SITE_NOTE):
            print(f"::notice title=Retry::{r['id']} after the quota reset -> {dispatch(r['id'])}", flush=True)


def cmd_pending(write=True):
    """Daily: re-read each imported site (new weeks, new files) and continue writing chapters.
    check (every half hour): the same re-read only - new recordings start processing right away."""
    sb = db()
    for m in sb.table("materials").select("course_id, storage_path").like("storage_path", f"%/{SITE_MD}").execute().data:
        try:
            first = sb.storage.from_(BUCKET).download(m["storage_path"]).decode("utf-8").split("\n", 1)[0]
            if first.startswith("מקור: "):
                cmd_import(m["course_id"], first[len("מקור: "):].strip(), write)
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Site {m['course_id']}::{str(e)[:300]}", flush=True)
    if write:
        process_pending(sb)
        try:  # exercises from homework / past-exam files of every course, with what is left of the quota
            import exercises
            exercises.run()
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Exercises::{str(e)[:300]}", flush=True)
        try:  # formula sheets of courses whose exam allows one, when lessons were added
            import docs
            docs.run()
        except Exception as e:  # noqa: BLE001
            print(f"::warning title=Formula sheet::{str(e)[:300]}", flush=True)
    else:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Asia/Jerusalem"))
        if now.hour == 10 and 30 <= now.minute < 60:  # one half-hourly run a day, after the reset
            retry_after_quota(sb)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "show":
        cmd_show(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "import":
        cmd_import(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 2 and sys.argv[1] == "pending":
        cmd_pending()
    elif len(sys.argv) >= 2 and sys.argv[1] == "check":
        cmd_pending(write=False)
    else:
        print(__doc__)
