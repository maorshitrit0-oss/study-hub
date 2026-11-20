// Puts the in-browser ffmpeg (recording upload: shrink a lecture before it goes up) under public/ffmpeg, same origin,
// so the page's CSP (no foreign scripts) allows it. Run on every install (postinstall); public/ffmpeg is not in git.
import { cpSync, mkdirSync, readdirSync } from "node:fs";

const out = "public/ffmpeg";
mkdirSync(out, { recursive: true });
for (const dir of ["node_modules/@ffmpeg/ffmpeg/dist/esm", "node_modules/@ffmpeg/core/dist/esm"]) {
  for (const f of readdirSync(dir)) if (/\.(js|wasm)$/.test(f)) cpSync(`${dir}/${f}`, `${out}/${f}`);
}
console.log("ffmpeg copied to", out);
