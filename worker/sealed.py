"""Private material through the public repository (16/11/2026: his graded communication assignments - the solutions
must not be readable in the public repo). A key pair is derived from the SUPABASE_SERVICE_KEY secret, so only a
workflow run can open what Claude seals with the public key:
  python sealed.py pub                  -> prints the public key (base64)
  python sealed.py open <in.json> <out>  -> {"sealed": "<base64>"} -> the original bytes
Seal (locally): nacl.public.SealedBox(PublicKey(b64decode(pub))).encrypt(data)."""
import base64
import hashlib
import json
import os
import sys

from nacl.public import PrivateKey, SealedBox


def _key():
    seed = hashlib.sha256((os.environ["SUPABASE_SERVICE_KEY"] + ":sealed-v1").encode()).digest()
    return PrivateKey(seed)


if __name__ == "__main__":
    if sys.argv[1] == "pub":
        print(f"::notice title=Sealed public key::{base64.b64encode(bytes(_key().public_key)).decode()}", flush=True)
    elif sys.argv[1] == "open":
        blob = base64.b64decode(json.loads(open(sys.argv[2], encoding="utf-8").read())["sealed"])
        open(sys.argv[3], "wb").write(SealedBox(_key()).decrypt(blob))
