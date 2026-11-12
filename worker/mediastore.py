"""The second storage (his own free Supabase organization "study-media", 12/11/2026): explainer videos and podcasts
live there, so they use its own 1 GB storage and 5 GB monthly download quota instead of the app's. Public bucket
"media" (no personal data: only the explainers, at random ids). lesson_media.storage_path = "m:<path>" for files here;
the app builds the public URL (web/src/lib/studio.ts). The key is the GitHub secret MEDIA_SUPABASE_KEY (never in code).
"""
import os

import requests

URL = "https://zpjjrsgosphapghxlbsl.supabase.co"
BUCKET = "media"
PREFIX = "m:"


def enabled():
    return bool(os.environ.get("MEDIA_SUPABASE_KEY"))


def _headers(ctype=None):
    key = os.environ["MEDIA_SUPABASE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}", "x-upsert": "true"}
    if ctype:
        h["content-type"] = ctype
    return h


def upload(path, data, ctype):
    """Uploads and returns the storage_path to keep ("m:<path>")."""
    r = requests.post(f"{URL}/storage/v1/object/{BUCKET}/{path}", data=data, headers=_headers(ctype), timeout=600)
    r.raise_for_status()
    return PREFIX + path


def public_url(storage_path):
    return f"{URL}/storage/v1/object/public/{BUCKET}/{storage_path[len(PREFIX):]}"


def ping():
    """A request a day keeps the free project from pausing (paused after 7 idle days)."""
    r = requests.post(f"{URL}/storage/v1/object/list/{BUCKET}", json={"prefix": "", "limit": 1}, headers=_headers("application/json"), timeout=60)
    return r.status_code



def move_all():
    """Copies every ready studio file still in the app's storage to the media project, checks the copy (same size via
    the public URL), and only then points lesson_media.storage_path at it. The original stays (deleted only when he
    says so) - "never delete his study data"."""
    from supabase import create_client
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    rows = sb.table("lesson_media").select("id, kind, storage_path").eq("status", "ready").execute().data
    rows = [r for r in rows if r.get("storage_path") and not r["storage_path"].startswith(PREFIX)]
    moved = failed = 0
    for r in rows:
        path = r["storage_path"]
        try:
            data = sb.storage.from_("study").download(path)
            ctype = "audio/mpeg" if path.endswith(".mp3") else "video/mp4" if path.endswith(".mp4") else "application/octet-stream"
            new = upload(path, data, ctype)
            h = requests.head(public_url(new), timeout=60)
            if h.status_code != 200 or int(h.headers.get("content-length", -1)) != len(data):
                raise RuntimeError(f"check failed: {h.status_code} {h.headers.get('content-length')} != {len(data)}")
            sb.table("lesson_media").update({"storage_path": new}).eq("id", r["id"]).execute()
            moved += 1
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"::warning title=Media move::{path}: {str(e)[:200]}", flush=True)
    print(f"::notice title=Media move::{moved} moved and checked, {failed} failed, originals kept", flush=True)


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["move"]:
        move_all()
    if sys.argv[1:] == ["test"]:
        print("ping", ping())
        p = upload("test/hello.txt", b"hello", "text/plain")
        r = requests.get(public_url(p), timeout=60)
        print("upload", p, "public read", r.status_code, r.text[:20])