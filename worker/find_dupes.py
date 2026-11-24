"""Lessons that are the same recording twice (24/11/2026: lessons he never uploaded, made from a second copy of a file).
Prints pairs whose transcripts are almost the same."""
import re

import hub


def sh(t, k=8):
    w = re.findall(r"[\w֐-׿]+", t or "")
    return {" ".join(w[i:i + k]) for i in range(0, max(0, len(w) - k), 3)}


sb = hub.db()
for c in sb.table("courses").select("id, name").eq("archived", False).execute().data:
    ls = [l for l in sb.table("lessons").select("id, kind, number, title, created_at, read_at, source_path, source_url, transcript")
          .eq("course_id", c["id"]).execute().data if len(l.get("transcript") or "") > 2000]
    S = {l["id"]: sh(l["transcript"][:20000]) for l in ls}
    for i, a in enumerate(ls):
        for b in ls[i + 1:]:
            x, y = S[a["id"]], S[b["id"]]
            if not x or not y:
                continue
            sim = len(x & y) / min(len(x), len(y))
            if sim > 0.6:
                print(f"DUPE {c['name'][:20]} | {sim:.2f} | A {a['id']} {a['kind']} {a.get('number')} {a['created_at'][:16]} read={bool(a.get('read_at'))} "
                      f"src={'file' if a.get('source_path') else 'link'} | B {b['id']} {b['kind']} {b.get('number')} {b['created_at'][:16]} "
                      f"read={bool(b.get('read_at'))} src={'file' if b.get('source_path') else 'link'}", flush=True)
