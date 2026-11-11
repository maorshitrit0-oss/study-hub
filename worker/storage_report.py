"""What fills the Supabase storage (free plan: 1 GB). Read-only: sums sizes by folder and file type, lists the largest.

  python storage_report.py
"""
import collections
import os

from supabase import create_client

PAGE = 1000


def walk(store, prefix=""):
    out, offset = [], 0
    while True:
        items = store.list(prefix, {"limit": PAGE, "offset": offset, "sortBy": {"column": "name", "order": "asc"}})
        for it in items:
            path = f"{prefix}/{it['name']}" if prefix else it["name"]
            if it.get("id") is None:
                out += walk(store, path)
            else:
                out.append((path, int((it.get("metadata") or {}).get("size") or 0)))
        if len(items) < PAGE:
            return out
        offset += PAGE


def main():
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    files = walk(sb.storage.from_("study"))
    mb = lambda n: f"{n / 1024 ** 2:.0f}MB"  # noqa: E731
    by_dir, by_ext = collections.Counter(), collections.Counter()
    for p, n in files:
        parts = p.split("/")
        by_dir[parts[1] if len(parts) > 2 else "(root)"] += n
        by_ext[p.rsplit(".", 1)[-1].lower() if "." in parts[-1] else "-"] += n
    total = sum(n for _, n in files)
    print(f"::notice title=Storage total::{len(files)} files, {mb(total)}")
    print("::notice title=By folder::" + "; ".join(f"{k} {mb(v)}" for k, v in by_dir.most_common()))
    print("::notice title=By type::" + "; ".join(f"{k} {mb(v)}" for k, v in by_ext.most_common(12)))
    big = sorted(files, key=lambda x: -x[1])[:25]
    print("::notice title=Largest::" + "; ".join(f"{p.split('/', 1)[-1]} {mb(n)}" for p, n in big))
    media = {p.rsplit("/", 1)[-1].split(".")[0]: n for p, n in files if "/media/" in p}
    rows = sb.table("lesson_media").select("id, kind, status, course_id, lesson_ids, created_at, duration_sec").execute().data
    names = {c["id"]: c["name"] for c in sb.table("courses").select("id, name").execute().data}
    known = {r["id"] for r in rows}
    orphan = sum(n for k, n in media.items() if k not in known)
    per, mins = collections.Counter(), collections.Counter()
    newest = {}
    for r in sorted(rows, key=lambda r: r["created_at"]):
        if r["status"] == "ready":
            newest[(r["kind"], tuple(sorted(r["lesson_ids"] or [])))] = r["id"]
    superseded = 0
    for r in rows:
        n = media.get(r["id"], 0)
        key = f"{names.get(r['course_id'], '?')}/{r['kind']}"
        per[key] += n
        mins[key] += (r.get("duration_sec") or 0) / 60 if n else 0
        if n and newest.get((r["kind"], tuple(sorted(r["lesson_ids"] or [])))) not in (None, r["id"]):
            superseded += n
    print(f"::notice title=Media::no row {mb(orphan)}; older copies replaced by a newer ready one {mb(superseded)}")
    print("::notice title=Media by course::" + "; ".join(f"{k} {mb(v)} ({mins[k]:.0f} min)" for k, v in per.most_common()))

if __name__ == "__main__":
    main()
