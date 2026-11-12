"""Weekly backup of everything he has in Supabase (his request, 07/11/2026: "I need everything until the end of the
degree"; the free Supabase plan keeps no backups). Run by .github/workflows/backup.yml every week: every table (all rows)
and every storage file, packed, encrypted with backup/backup_pub.pem (the private key is only in his Google Drive) and
kept as a GitHub release "backup-<date>" (the last 8 are kept). Nothing here deletes or changes data.

  python backup.py dump <dir>        tables -> <dir>/tables/<name>.json, files -> <dir>/storage/<bucket>/<path>
  python backup.py restore <dir>     puts back rows (upsert by primary key) and files missing in storage - never deletes
"""
import json
import os
import sys
import urllib.request

from supabase import create_client

# Parents before children (restore order); any other table the database has comes after these.
ORDER = ["courses", "lessons", "questions", "attempts", "materials", "deadlines", "exercises", "chat_threads",
         "chat_messages", "settings", "course_facts", "schedule_slots", "recording_marks", "glossary", "grades",
         "skills", "lesson_media", "entry_reports", "push_subscriptions", "push_config", "usage_snapshot"]
PAGE = 1000


def db():
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def tables():
    """Every table the API exposes (so a table added later is backed up too), parents first."""
    key = os.environ["SUPABASE_SERVICE_KEY"]
    req = urllib.request.Request(os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1/",
                                 headers={"apikey": key, "Authorization": f"Bearer {key}"})
    try:
        spec = json.load(urllib.request.urlopen(req, timeout=60))
        found = [p.strip("/") for p in spec.get("paths", {}) if p.strip("/") and "rpc/" not in p]
    except Exception as e:  # noqa: BLE001
        print(f"::warning title=Backup::table list from the API failed ({e}) - using the known list", flush=True)
        found = ORDER
    return [t for t in ORDER if t in found] + sorted(t for t in found if t not in ORDER)


def walk(store, prefix="", since=""):
    """All file paths under prefix (folders have no id); with since, only files created / changed after it."""
    out, offset = [], 0
    while True:
        items = store.list(prefix, {"limit": PAGE, "offset": offset, "sortBy": {"column": "name", "order": "asc"}})
        for it in items:
            path = f"{prefix}/{it['name']}" if prefix else it["name"]
            if it.get("id") is None:
                out += walk(store, path, since)
            elif not since or max(it.get("updated_at") or "", it.get("created_at") or "") > since:
                out.append(path)
        if len(items) < PAGE:
            return out
        offset += PAGE


def dump(out, since=""):
    """since (ISO time): an incremental backup - every table, but only the files new or changed since the last backup
    (12/11/2026: a full copy every week was most of the free plan's monthly download traffic)."""
    sb = db()
    if since:  # the previous dump ran for over an hour before its release was created: overlap by 3 hours
        from datetime import datetime, timedelta
        since = (datetime.fromisoformat(since.replace("Z", "+00:00")) - timedelta(hours=3)).isoformat()
    report = {"tables": {}, "files": {}, "since": since or None}
    os.makedirs(f"{out}/tables", exist_ok=True)
    for t in tables():
        rows, start = [], 0
        while True:
            page = sb.table(t).select("*").range(start, start + PAGE - 1).execute().data
            rows += page
            if len(page) < PAGE:
                break
            start += PAGE
        with open(f"{out}/tables/{t}.json", "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False)
        report["tables"][t] = len(rows)
    failed = []
    for b in sb.storage.list_buckets():
        name = b.name if hasattr(b, "name") else b["name"]
        store = sb.storage.from_(name)
        paths = walk(store, since=since)
        for p in paths:
            dest = f"{out}/storage/{name}/{p}"
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            try:
                with open(dest, "wb") as f:
                    f.write(store.download(p))
            except Exception as e:  # noqa: BLE001
                failed.append(f"{name}/{p}: {e}")
        report["files"][name] = len(paths)
    report["failed"] = failed
    with open(f"{out}/manifest.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(f"::notice title=Backup::{sum(report['tables'].values())} rows in {len(report['tables'])} tables, "
          f"{sum(report['files'].values())} files, {len(failed)} files failed", flush=True)
    if failed:
        print("::warning title=Backup::" + "; ".join(failed)[:3000], flush=True)


def restore(src):
    """Puts the backup back: rows upserted by primary key, files uploaded only where missing. Never deletes."""
    sb = db()
    names = [f[:-5] for f in os.listdir(f"{src}/tables") if f.endswith(".json")]
    for t in [t for t in ORDER if t in names] + sorted(t for t in names if t not in ORDER):
        rows = json.load(open(f"{src}/tables/{t}.json", encoding="utf-8"))
        for i in range(0, len(rows), 500):
            sb.table(t).upsert(rows[i:i + 500]).execute()
        print(f"{t}: {len(rows)} rows", flush=True)
    root = f"{src}/storage"
    for bucket in os.listdir(root) if os.path.isdir(root) else []:
        store = sb.storage.from_(bucket)
        for d, _, files in os.walk(f"{root}/{bucket}"):
            for fn in files:
                path = os.path.relpath(os.path.join(d, fn), f"{root}/{bucket}").replace(os.sep, "/")
                try:
                    store.upload(path, open(os.path.join(d, fn), "rb").read(), {"upsert": "false"})
                except Exception:  # noqa: BLE001 - already there
                    pass
        print(f"storage {bucket}: done", flush=True)


if __name__ == "__main__":
    {"dump": dump, "restore": restore}[sys.argv[1]](*sys.argv[2:])
