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


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["test"]:
        print("ping", ping())
        p = upload("test/hello.txt", b"hello", "text/plain")
        r = requests.get(public_url(p), timeout=60)
        print("upload", p, "public read", r.status_code, r.text[:20])
