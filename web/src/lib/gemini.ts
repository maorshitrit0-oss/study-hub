import { GoogleGenAI, type Part } from "@google/genai";

export const geminiModel = () => process.env.GEMINI_MODEL || "gemini-flash-latest";

/**
 * Structured JSON from Gemini. Some models reject `responseJsonSchema` with 400 INVALID_ARGUMENT,
 * so on that error retry with plain JSON mode and the schema written into the prompt.
 */
export async function generateJson<T>(parts: Part[], schema: object, system?: string): Promise<T> {
  if (!process.env.GEMINI_API_KEY) throw new Error("לא הוגדר GEMINI_API_KEY ב-Vercel");
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
  const model = geminiModel();
  try {
    const res = await ai.models.generateContent({
      model,
      contents: [{ role: "user", parts }],
      config: { systemInstruction: system, responseMimeType: "application/json", responseJsonSchema: schema },
    });
    return parseJson<T>(res.text);
  } catch (e) {
    if (!/INVALID_ARGUMENT|400/.test(String((e as Error).message))) throw e;
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
}

function parseJson<T>(text: string | undefined): T {
  const t = (text ?? "").trim().replace(/^```(?:json)?\s*|\s*```$/g, "");
  return JSON.parse(t) as T;
}
