import { GoogleGenAI, type Part } from "@google/genai";
import type { SupabaseClient } from "@supabase/supabase-js";
import { geminiKeys } from "./gemini";

/** Materials are either in Supabase storage, or a shared Google Drive file stored as "drive:<id>". */
export const DRIVE_PREFIX = "drive:";

export function driveId(url: string) {
  const m = url.match(/\/d\/([-\w]{20,})/) ?? url.match(/[?&]id=([-\w]{20,})/);
  return m?.[1] ?? null;
}

export const driveViewUrl = (path: string) => `https://drive.google.com/file/d/${path.slice(DRIVE_PREFIX.length)}/view`;

/** Downloads a material's bytes from storage or from Drive ("anyone with the link" sharing). */
export async function materialBlob(sb: SupabaseClient, m: { storage_path: string; mime: string | null }) {
  if (!m.storage_path.startsWith(DRIVE_PREFIX)) {
    const { data, error } = await sb.storage.from("study").download(m.storage_path);
    if (!data) throw new Error(`לא הצלחתי להוריד את הקובץ: ${error?.message ?? ""}`);
    return data;
  }
  const id = m.storage_path.slice(DRIVE_PREFIX.length);
  const res = await fetch(`https://drive.usercontent.google.com/download?id=${id}&export=download&confirm=t`);
  const type = res.headers.get("content-type") ?? "";
  if (!res.ok || type.startsWith("text/html")) {
    throw new Error("לא הצלחתי להוריד מהדרייב - ודא שהקובץ משותף עם 'כל מי שיש לו את הקישור'");
  }
  return new Blob([await res.arrayBuffer()], { type: m.mime || type || "application/pdf" });
}

const INLINE_LIMIT = 15 * 1024 * 1024;
// Gemini keeps uploaded files for 48 hours; reuse them while this server instance lives.
const uploaded = new Map<string, { uri: string; mimeType: string; until: number }>();

/** A Gemini part for a file: small files inline, big ones through the Gemini Files API. */
export async function geminiFilePart(key: string, blob: Blob, mimeType: string): Promise<Part> {
  if (blob.size <= INLINE_LIMIT) {
    return { inlineData: { mimeType, data: Buffer.from(await blob.arrayBuffer()).toString("base64") } };
  }
  const cached = uploaded.get(key);
  if (cached && cached.until > Date.now()) return { fileData: { fileUri: cached.uri, mimeType: cached.mimeType } };
  const ai = new GoogleGenAI({ apiKey: geminiKeys()[0] });
  let file = await ai.files.upload({ file: blob, config: { mimeType } });
  for (let i = 0; i < 30 && file.state === "PROCESSING" && file.name; i++) {
    await new Promise((r) => setTimeout(r, 2000));
    file = await ai.files.get({ name: file.name });
  }
  if (!file.uri) throw new Error("העלאת הקובץ ל-Gemini נכשלה");
  uploaded.set(key, { uri: file.uri, mimeType, until: Date.now() + 40 * 3600e3 });
  return { fileData: { fileUri: file.uri, mimeType } };
}

/** Clean a file name for display (iOS sometimes adds direction marks / broken characters). */
export const cleanTitle = (name: string) => name.replace(/[‎‏‪-‮⁦-⁩�]/g, "").trim() || "קובץ";
