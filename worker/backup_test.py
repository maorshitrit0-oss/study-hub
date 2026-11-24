"""Which Gemini-API models still answer today on the free keys (each model has its own free quota)."""
import os

from google import genai

import author
keys = author._keys()
print("NKEYS", len(keys), flush=True)
c = genai.Client(api_key=keys[0])
names = [m.name.split("/")[-1] for m in c.models.list() if "generateContent" in (m.supported_actions or [])]
print("MODELS", ", ".join(names)[:2500], flush=True)
for m in ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.6-flash",
          "gemini-3.7-flash", "gemma-4-31b-it", "gemma-4-26b-a4b-it"]:
    ok = []
    for i, k in enumerate(keys):
        try:
            cl = genai.Client(api_key=k)
            r = cl.models.generate_content(model=m, contents="כתוב מילה אחת בעברית: שלום")
            ok.append(f"k{i + 1}:ok")
        except Exception as e:  # noqa: BLE001
            ok.append(f"k{i + 1}:" + ("quota" if "429" in str(e) else "busy" if "503" in str(e) else str(e)[:40]))
    print("TRY", m, " ".join(ok), flush=True)
