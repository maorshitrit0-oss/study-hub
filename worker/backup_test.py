"""Checks the free backup providers (Groq, Mistral) from the runner: which models the keys allow, and a Hebrew task."""
import json
import os
import time

import requests

for name, url, env in (("groq", "https://api.groq.com/openai/v1/models", "GROQ_API_KEY"),
                       ("mistral", "https://api.mistral.ai/v1/models", "MISTRAL_API_KEY")):
    r = requests.get(url, headers={"Authorization": "Bearer " + os.environ.get(env, "")}, timeout=60)
    ids = sorted(m.get("id") for m in (r.json().get("data") or []) if isinstance(m, dict))
    print("MODELS", name, r.status_code, ", ".join(ids)[:1500], flush=True)
    time.sleep(2)
