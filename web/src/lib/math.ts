// Inline formulas in Hebrew text break across lines and get reordered by the right-to-left layout.
// A long inline formula ($...$) is moved to its own line ($$...$$) - also in chapters written before this.
const LONG = 28; // characters of LaTeX

const WIDE = 45; // a display equation longer than this, with several "=", is split one step per line

/** Splits "a = b = c" at top-level "=" signs into aligned lines, so a long equation fits a phone screen. */
export function splitEquation(tex: string) {
  if (tex.length <= WIDE || /\\begin|\\\\/.test(tex)) return tex;
  const parts: string[] = [];
  let depth = 0, start = 0;
  for (let i = 0; i < tex.length; i++) {
    const c = tex[i];
    if (c === "{" || c === "(" || c === "[") depth++;
    else if (c === "}" || c === ")" || c === "]") depth--;
    else if (c === "=" && depth === 0 && tex[i - 1] !== "\\" && tex[i - 1] !== "<" && tex[i - 1] !== ">" && tex[i - 1] !== "!") {
      parts.push(tex.slice(start, i));
      start = i + 1;
    }
  }
  parts.push(tex.slice(start));
  if (parts.length < 3) return tex;
  return `\\begin{aligned}${parts[0].trim()} &= ${parts.slice(1).map((p) => p.trim()).join(" \\\\ &= ")}\\end{aligned}`;
}

export function promoteLongMath(md: string) {
  // Leave code untouched: fenced blocks and `inline code`.
  return md.split(/(```[\s\S]*?```|`[^`\n]*`)/g).map((part, i) => {
    if (i % 2 === 1) return part;
    return part.split("\n").map((line) => {
      // Tables and list items can't hold a display formula without breaking.
      if (/^\s*(\||[-*+]\s|\d+[.)]\s|>)/.test(line)) return line;
      return line.replace(/(?<![$\\])\$(?!\$)([^$\n]+?)\$(?!\$)/g, (m, tex: string) =>
        tex.length > LONG ? `\n\n$$${splitEquation(tex.trim())}$$\n\n` : m);
    }).join("\n")
      // Display equations already on their own line: split long ones too.
      .replace(/\$\$([^$]+?)\$\$/g, (_, tex: string) => `$$${splitEquation(tex.trim())}$$`);
  }).join("");
}
