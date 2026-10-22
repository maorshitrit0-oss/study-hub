import { unzip } from "fflate";

export type ZipEntry = { name: string; data: Uint8Array };

// Hebrew file names from Windows zips are often in the old DOS code page (CP862), not UTF-8.
function fixName(name: string) {
  if (![...name].some((c) => c.charCodeAt(0) > 0x7f && c.charCodeAt(0) <= 0xff)) return name;
  const bytes = Uint8Array.from([...name].map((c) => c.charCodeAt(0) & 0xff));
  try {
    return new TextDecoder("utf-8", { fatal: true }).decode(bytes);
  } catch {
    return [...bytes].map((b) => (b >= 0x80 && b <= 0x9a ? String.fromCharCode(0x5d0 + b - 0x80) : String.fromCharCode(b))).join("");
  }
}

/** Unzips in the browser; skips folders and OS junk files. */
export function readZip(file: File): Promise<ZipEntry[]> {
  return file.arrayBuffer().then((buf) => new Promise((resolve, reject) => {
    unzip(new Uint8Array(buf), (err, files) => {
      if (err) return reject(err);
      resolve(Object.entries(files)
        .filter(([path, data]) => data.length > 0 && !path.endsWith("/") && !/(^|\/)(__MACOSX|\.DS_Store|Thumbs\.db|desktop\.ini)/i.test(path))
        .map(([path, data]) => ({ name: fixName(path.split("/").pop() ?? path), data })));
    });
  }));
}

const MIME: Record<string, string> = {
  pdf: "application/pdf", docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  pptx: "application/vnd.openxmlformats-officedocument.presentationml.presentation", txt: "text/plain", md: "text/plain",
  png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", webp: "image/webp",
};
export const mimeOf = (name: string) => MIME[name.toLowerCase().split(".").pop() ?? ""] ?? "application/octet-stream";

/** Guess a material type from its file name. */
export function guessKind(name: string, isLab: boolean) {
  const n = name.toLowerCase();
  if (/syl|סילבוס/.test(n)) return "syllabus";
  if (/פתרון|פתרונות|solution|sol\b/.test(n)) return "solution";
  if (/דוח.?מסכם|summary.?report/.test(n) || (isLab && /דוח|report/.test(n) && !/מכין|prelab/.test(n))) return "prev_report";
  if (/מבחן|בחינה|מועד|exam|בוחן|בחני|quiz/.test(n)) return "past_exam";
  if (/חוברת|ניסוי|מכין|prelab|experiment|lab/.test(n)) return "lab_guide";
  if (/הרצאה|lecture|מצגת|שקפים|slides|תרגול|tutorial|\.pptx$/.test(n)) return "slides";
  return "other";
}
