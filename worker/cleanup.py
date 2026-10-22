"""Free storage: keep only the board snapshots a finished chapter actually shows.

  python cleanup.py        prune every ready lesson (run daily by notify.yml)

A lecture yields ~80 snapshots (~2.5 MB) but the chapter shows ~10, so this keeps the free 1 GB
Supabase storage enough for the whole degree.
"""
import os
import re

from supabase import create_client

BUCKET = "study"


def prune_lesson(sb, lesson):
    if lesson.get("status") != "ready" or not lesson.get("chapter_md"):
        return 0
    keep = {f"slide_{int(n):03d}.webp" for n in re.findall(r"\(slide:(\d+)\)", lesson["chapter_md"])}
    prefix = f"{lesson['user_id']}/lessons/{lesson['id']}"
    store = sb.storage.from_(BUCKET)
    files = store.list(prefix, {"limit": 1000})
    drop = [f"{prefix}/{f['name']}" for f in files if f["name"].startswith("slide_") and f["name"] not in keep]
    for i in range(0, len(drop), 100):
        store.remove(drop[i:i + 100])
    return len(drop)


def main():
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    lessons = (sb.table("lessons").select("id, user_id, status, chapter_md").eq("status", "ready")
               .gt("slide_count", 0).execute().data)
    removed = sum(prune_lesson(sb, l) for l in lessons)
    print(f"removed {removed} unused snapshots from {len(lessons)} lessons")


if __name__ == "__main__":
    main()
