"""Import a lecturer's course website (a public Notion page, with its sub-pages and attached files) into a course.

  python course_site.py show <url>                  print what would be imported (pages as Markdown, files, links)
  python course_site.py import <course_id> <url>    files -> course files (materials), all text -> "אתר הקורס.md",
                                             review questions / past exams / sub-pages -> lessons that get a chapter

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
    m = re.findall(r"[0-9a-f]{32}", urlparse(url).path.replace("-", ""))
    if not m:
        raise SystemExit("זה לא קישור לדף Notion (חסר מזהה הדף בסוף הכתובת)")
    return dashed(m[-1])


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
        for _ in range(10):
            missing = []
            for bid in self.tree_ids(pid):
                missing += [c for c in self.blocks.get(bid, {}).get("content", []) if c not in self.blocks]
            missing = list(dict.fromkeys(missing))
            if not missing:
                return
            space = self.blocks.get(pid, {}).get("space_id")
            for i in range(0, len(missing), 100):
                reqs = [{"pointer": {"table": "block", "id": b, **({"spaceId": space} if space else {})}, "version": -1}
                        for b in missing[i:i + 100]]
                self._add((self.api("syncRecordValues", {"requests": reqs}) or {}).get("recordMap") or {})
            if all(m not in self.blocks for m in missing):
                return

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
    """All pages from the root: [(page_id, title, markdown)], files [{...}], links [{...}]."""
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

        def rich(r):
            out = []
            for seg in r or []:
                text, ann = seg[0], (seg[1] if len(seg) > 1 else [])
                for a in ann:
                    if a[0] == "a" and len(a) > 1:
                        href = unwrap(a[1])
                        if href.startswith("/"):
                            href = n.base + href
                        links.append({"page": title, "text": text, "url": href})
                        text = f"[{text}]({href})"
                    elif a[0] == "p" and len(a) > 1:
                        sub = dashed(a[1])
                        queue.append((sub, depth + 1))
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
            text = rich(props.get("title"))
            children = b.get("content", [])
            if t == "page" and bid != pid:
                queue.append((bid, depth + 1))
                lines.append(f"{pad}- 📄 [{plain(props.get('title')) or 'דף'}]({n.page_url(bid)})")
                return
            if t in FILE_TYPES or t in ("bookmark", "embed"):
                src = (props.get("source") or props.get("link") or [[""]])[0][0]
                src = unwrap(src or b.get("format", {}).get("display_source", ""))
                name = plain(props.get("title")) or unquote(Path(urlparse(src).path).name) or t
                if t in ("bookmark", "embed") or (t == "video" and not src.startswith("attachment:")):
                    links.append({"page": title, "text": name, "url": src})
                    lines.append(f"{pad}- 🔗 [{name}]({src})")
                elif t == "image":
                    lines.append(f"{pad}- 🖼️ {name}")
                else:
                    files.append({"page": title, "name": name, "block": bid, "src": src})
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
                lines.append(pad + "| " + " | ".join(rich(props.get(c)) for c in cols) + " |")
            elif text:
                lines.append(f"{pad}{prefix}{text}")
            nested = indent + 1 if t in ("bulleted_list", "numbered_list", "toggle", "to_do") else indent
            for c in children:
                block(c, nested)

        for c in n.blocks.get(pid, {}).get("content", []):
            block(c, 0)
        pages.append((pid, title, "\n".join(lines)))
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
        show(url)
    print(buf.getvalue())
    annotate(buf.getvalue())


def show(url):
    n = Notion(url)
    pages, files, links = walk(n)
    for pid, title, md in pages:
        print(f"\n===== PAGE {title} ({pid}) =====\n{md}")
    print(f"\n===== {len(files)} FILES =====")
    for f in files:
        u = n.file_url(f["block"], f["src"])
        try:
            r = n.http.head(u, allow_redirects=True, timeout=30)
            info = f"{r.status_code} {r.headers.get('content-type', '')} {r.headers.get('content-length', '?')}"
        except requests.RequestException as e:
            info = f"ERR {e}"
        print(f"- [{f['page']}] {f['name']} :: {info}")
    print(f"\n===== {len(links)} LINKS =====")
    for l in links:
        print(f"- [{l['page']}] {l['text']} -> {l['url']}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "show":
        cmd_show(sys.argv[2])
    else:
        print(__doc__)
