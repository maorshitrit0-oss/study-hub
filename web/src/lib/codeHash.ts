/** Key of a code block's line-by-line explanation. Same as worker/codelines.py code_hash (djb2 over UTF-16 units). */
export function codeHash(code: string, raw = false) {
  const s = raw ? code : code.replace(/\s+$/, "");
  let h = 5381;
  for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0;
  return (h >>> 0).toString(36);
}
