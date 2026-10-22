import { GoogleGenAI, type Part } from "@google/genai";

// Free-tier quotas are per project AND per model (e.g. 20 requests/day on the newest Flash), so we
// fall back across models, and across keys when GEMINI_API_KEY holds several comma-separated keys.
const WORK_MODELS = ["gemini-flash-latest", "gemini-2.5-flash", "gemini-flash-lite-latest", "gemini-2.5-flash-lite"];
const CHAT_MODELS = ["gemini-flash-lite-latest", "gemini-flash-latest", "gemini-2.5-flash-lite", "gemini-2.5-flash"];

const list = (v: string | undefined) => (v ?? "").split(",").map((x) => x.trim()).filter(Boolean);
export const geminiKeys = () => list(process.env.GEMINI_API_KEY);
export const geminiModel = () => list(process.env.GEMINI_MODELS)[0] ?? list(process.env.GEMINI_MODEL)[0] ?? WORK_MODELS[0];
function models(purpose: "work" | "chat") {
  const own = list(purpose === "chat" ? process.env.GEMINI_CHAT_MODELS : process.env.GEMINI_MODELS ?? process.env.GEMINI_MODEL);
  return [...new Set([...own, ...(purpose === "chat" ? CHAT_MODELS : WORK_MODELS)])];
}

const msg = (e: unknown) => String((e as Error)?.message ?? e);
const isQuota = (e: unknown) => /RESOURCE_EXHAUSTED|"code":429|\b429\b|quota/i.test(msg(e));
const isBusy = (e: unknown) => /UNAVAILABLE|"code":503|\b503\b|overloaded|high demand/i.test(msg(e));
const isMissingModel = (e: unknown) => /NOT_FOUND|"code":404|is not found|not supported/i.test(msg(e));

/** Turns raw Gemini errors into a short Hebrew explanation. */
export function friendlyGeminiError(e: unknown) {
  if (isQuota(e)) return "המכסה היומית החינמית של Gemini נגמרה בכל המודלים. היא מתאפסת כל יום בסביבות 10:00 בבוקר - אז ללחוץ שוב.";
  if (isBusy(e)) return "השרתים של Gemini עמוסים כרגע. לנסות שוב בעוד כמה דקות.";
  return msg(e).slice(0, 300);
}

/** Runs a Gemini call with retries on overload and fallback across models and keys on quota. */
export async function withGemini<T>(purpose: "work" | "chat", call: (ai: GoogleGenAI, model: string) => Promise<T>): Promise<T> {
  const keys = geminiKeys();
  if (!keys.length) throw new Error("לא הוגדר GEMINI_API_KEY ב-Vercel");
  let last: unknown;
  for (const key of keys) {
    const ai = new GoogleGenAI({ apiKey: key });
    for (const model of models(purpose)) {
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          return await call(ai, model);
        } catch (e) {
          last = e;
          if (isBusy(e) && attempt < 2) {
            await new Promise((r) => setTimeout(r, 2000 * (attempt + 1) ** 2));
            continue;
          }
          if (isQuota(e) || isBusy(e) || isMissingModel(e)) break; // try the next model
          throw e;
        }
      }
    }
  }
  throw new Error(friendlyGeminiError(last));
}

/**
 * Structured JSON from Gemini. Some models reject `responseJsonSchema` with 400 INVALID_ARGUMENT,
 * so on that error retry with plain JSON mode and the schema written into the prompt.
 */
export async function generateJson<T>(parts: Part[], schema: object, system?: string): Promise<T> {
  return withGemini("work", async (ai, model) => {
    try {
      const res = await ai.models.generateContent({
        model,
        contents: [{ role: "user", parts }],
        config: { systemInstruction: system, responseMimeType: "application/json", responseJsonSchema: schema },
      });
      return parseJson<T>(res.text);
    } catch (e) {
      if (!/INVALID_ARGUMENT|"code":400/.test(msg(e))) throw e;
      const res = await ai.models.generateContent({
        model,
        contents: [{
          role: "user",
          parts: [...parts, { text: `החזר אך ורק JSON תקין (בלי טקסט מסביב) לפי ה-JSON Schema הזה:\n${JSON.stringify(schema)}` }],
        }],
        config: { systemInstruction: system, responseMimeType: "application/json" },
      });
      return parseJson<T>(res.text);
    }
  });
}

function parseJson<T>(text: string | undefined): T {
  const t = (text ?? "").trim().replace(/^```(?:json)?\s*|\s*```$/g, "");
  return JSON.parse(t) as T;
}
