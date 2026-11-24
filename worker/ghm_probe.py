"""What GitHub Models answers from a workflow (24/11/2026: it returned a plain "OK"). Prints status, redirect, body."""
import os

import requests

h = {"Authorization": "Bearer " + os.environ.get("GITHUB_TOKEN", ""), "Content-Type": "application/json",
     "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
b = {"model": "openai/gpt-4.1-mini", "messages": [{"role": "user", "content": "say hi in Hebrew"}]}
owner = os.environ.get("GITHUB_REPOSITORY", "x/x").split("/")[0]
for u in ["https://models.github.ai/inference/chat/completions",
          f"https://models.github.ai/orgs/{owner}/inference/chat/completions"]:
    try:
        r = requests.post(u, headers=h, json=b, timeout=120, allow_redirects=False)
        print("PROBE", u, r.status_code, r.headers.get("location"), r.headers.get("content-type"), repr(r.text[:300]), flush=True)
    except Exception as e:  # noqa: BLE001
        print("PROBE", u, "ERR", str(e)[:200], flush=True)
try:
    r = requests.get("https://models.github.ai/catalog/models", headers=h, timeout=60, allow_redirects=False)
    print("PROBE catalog", r.status_code, r.headers.get("location"), repr(r.text[:200]), flush=True)
except Exception as e:  # noqa: BLE001
    print("PROBE catalog ERR", str(e)[:200], flush=True)

import subprocess

for extra in ([], ["-H", "Accept: application/json"]):
    out = subprocess.run(["curl", "-sS", "-i", "-m", "60", "-X", "POST", "https://models.github.ai/inference/chat/completions",
                          "-H", "Authorization: Bearer " + os.environ.get("GITHUB_TOKEN", ""), "-H", "Content-Type: application/json",
                          *extra, "-d", '{"model":"openai/gpt-4.1-mini","messages":[{"role":"user","content":"say hi"}]}'],
                         capture_output=True, text=True)
    print("CURL", repr((out.stdout or out.stderr)[:700]), flush=True)
print("TOKEN kind", os.environ.get("GITHUB_TOKEN", "")[:4], len(os.environ.get("GITHUB_TOKEN", "")), flush=True)
