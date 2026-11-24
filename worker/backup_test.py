"""Which Gemini-API models still answer today on the free keys (each model has its own free quota)."""
import os

from google import genai

keys = [os.environ.get(k) for k in ("GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3", "GEMINI_API_KEY_4") if os.environ.get(k)]
c = genai.Client(api_key=keys[0])
names = [m.name.split("/")[-1] for m in c.models.list() if "generateContent" in (m.supported_actions or [])]
print("MODELS", ", ".join(names)[:2500], flush=True)
for m in [n for n in names if any(x in n for x in ("flash", "gemma", "pro"))][:30]:
    ok = []
    for i, k in enumerate(keys):
        try:
            r = genai.Client(api_key=k).models.generate_content(model=m, contents="כתוב מילה אחת בעברית: שלום")
            ok.append(f"k{i + 1}:ok")
        except Exception as e:  # noqa: BLE001
            ok.append(f"k{i + 1}:" + ("quota" if "429" in str(e) else "busy" if "503" in str(e) else str(e)[:40]))
    print("TRY", m, " ".join(ok), flush=True)
