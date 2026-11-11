"""Makes the explainer videos smaller so storage stays inside the free 1 GB (his alert 11/11/2026: storage at 128%).
Nothing is deleted: each video is re-encoded (same pictures, same voice, same length) and replaces itself only when the
new file is clearly smaller and plays the same length. The weekly backup (backup.yml) keeps the originals.

  python shrink.py [--dry] [--limit N]
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from supabase import create_client

import media

BUCKET = "study"
MIN_MB = 3          # smaller videos are already fine
KEEP_IF = 0.75      # replace only when the new file is at most 75% of the old one
# Slides change only every few seconds: a long keyframe interval and a higher CRF keep the text sharp at a fraction of
# the size; speech needs no more than 48 kbps mono.
ARGS = ["-c:v", "libx264", "-preset", "slow", "-tune", "stillimage", "-crf", "27", "-g", "100", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "48k", "-ac", "1", "-movflags", "+faststart"]


def walk(store, prefix):
    out, offset = [], 0
    while True:
        items = store.list(prefix, {"limit": 1000, "offset": offset})
        for it in items:
            path = f"{prefix}/{it['name']}"
            if it.get("id") is None:
                out += walk(store, path)
            elif path.endswith(".mp4") and "/media/" in path:
                out.append((path, int((it.get("metadata") or {}).get("size") or 0)))
        if len(items) < 1000:
            return out
        offset += 1000


def main():
    dry = "--dry" in sys.argv
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 10 ** 6
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    store = sb.storage.from_(BUCKET)
    files = []
    for top in store.list("", {"limit": 1000}):
        if top.get("id") is None:
            files += walk(store, top["name"])
    files = sorted((f for f in files if f[1] > MIN_MB * 1024 ** 2), key=lambda f: -f[1])[:limit]
    before = after = 0
    done = 0
    for path, size in files:
        with tempfile.TemporaryDirectory() as d:
            src, dst = Path(d) / "in.mp4", Path(d) / "out.mp4"
            try:
                src.write_bytes(store.download(path))
                media.run_ffmpeg(["-i", str(src), *ARGS, str(dst)])
                a, b = media.duration(src), media.duration(dst)
            except Exception as e:  # noqa: BLE001
                print(f"::warning title=Shrink::{path}: {e}", flush=True)
                continue
            new = dst.stat().st_size
            if dry:  # picture similarity to the original (1.0 = identical; above ~0.97 the text reads the same)
                r = subprocess.run([media.FFMPEG, "-i", str(dst), "-i", str(src), "-lavfi", "ssim", "-f", "null", "-"],
                                   capture_output=True, text=True, errors="ignore")
                print(next((x for x in r.stderr.splitlines() if "SSIM" in x), "ssim ?")[-60:], flush=True)
            ok = new <= size * KEEP_IF and abs(a - b) < 1.5
            print(f"{path.rsplit('/', 1)[-1]} {size / 1e6:.1f}MB -> {new / 1e6:.1f}MB, {a:.0f}s/{b:.0f}s {'ok' if ok else 'kept'}",
                  flush=True)
            if ok and not dry:
                store.update(path, dst.read_bytes(), {"content-type": "video/mp4", "upsert": "true"})
            before += size
            after += new if ok else size
            done += ok
    print(f"::notice title=Shrink{' (dry)' if dry else ''}::{done}/{len(files)} videos: {before / 1e6:.0f}MB -> {after / 1e6:.0f}MB",
          flush=True)


if __name__ == "__main__":
    main()
