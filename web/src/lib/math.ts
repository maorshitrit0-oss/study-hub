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

// LaTeX that Gemini wrote without $ around it (seen in exercises, 31/10/2026) shows as raw code. Outside code and
// outside existing $...$, an ASCII run that contains a LaTeX command (\frac, \hat, \cos...) is a formula: wrap it.
const RUN = /[A-Za-z0-9\\{}()[\]^_+\-=*/|.,:;<>!'~ ]*\\[A-Za-z]+[A-Za-z0-9\\{}()[\]^_+\-=*/|.,:;<>!'~ ]*/g;

export function wrapBareLatex(md: string) {
  // JSON turned "\b", "\f", "\t", "\r" at the start of \bar, \frac, \theta, \rho into control characters.
  const text = md.replace(/\x08/g, "\\b").replace(/\x0c/g, "\\f").replace(/\t(?=[a-z]{2,})/g, "\\t").replace(/\r(?=[a-z]{2,})/g, "\\r");
  return text.split(/(```[\s\S]*?```|`[^`\n]*`|\$\$[\s\S]+?\$\$|\$[^$\n]+?\$)/g).map((part, i) => {
    if (i % 2 === 1) return part;
    return part.replace(RUN, (run) => {
      // English words at either end are prose, not part of the formula.
      const lead = run.match(/^([\s.,:;]*[A-Za-z]{2,}[\s.,:;]+)*[\s.,:;]*/)![0];
      const tail = run.slice(lead.length).match(/([\s.,:;]+[A-Za-z]{2,}(?![\w{(^_]))*[\s.,:;]*$/)![0];
      const tex = run.slice(lead.length, run.length - tail.length);
      if (!tex) return run;
      return tex.length > 40 ? `${lead}\n\n$$${tex}$$\n\n${tail}` : `${lead}$${tex}$${tail}`;
    });
  }).join("");
}
