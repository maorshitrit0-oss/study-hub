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

/**
 * Gemini's $ delimiters are not always paired: "$$x$" , "$$$$y$", a display formula mid-sentence. Pair them again in
 * order: a pair whose content is empty is dropped, and a "pair" whose content is Hebrew text means the opener was a
 * stray - the closer opens instead. Every formula then gets a clean delimiter: $$ on its own line when it was meant
 * as a display formula or is long, $...$ otherwise. Code is left alone.
 */
const HEBREW = /[\u0590-\u05FF]/;

function pairDollars(text: string) {
  const tokens: { at: number; len: number }[] = [];
  for (const m of text.matchAll(/\$+/g)) {
    // "$$$$" = two delimiters; "$$$" = a display one and an inline one.
    for (let k = 0, n = m[0].length; n > 0; ) {
      const len = n >= 2 ? 2 : 1;
      tokens.push({ at: m.index! + k, len });
      k += len;
      n -= len;
    }
  }
  let out = "", pos = 0, open: { at: number; len: number } | null = null;
  for (const t of tokens) {
    if (!open) { open = t; continue; }
    const tex = text.slice(open.at + open.len, t.at);
    if (!tex.trim()) { open = t; continue; } // empty pair: the second one opens
    if (HEBREW.test(tex.replace(/\\text\{[^}]*\}/g, ""))) { open = t; continue; } // text, not math: stray opener
    const display = open.len === 2 || t.len === 2 || tex.length > LONG;
    out += text.slice(pos, open.at).replace(/\$/g, "") + (display ? `\n\n$$${tex.trim()}$$\n\n` : `$${tex.trim()}$`);
    pos = t.at + t.len;
    open = null;
  }
  return (out + text.slice(pos).replace(/\$/g, ""))
    .replace(/\$\$\n\n\s*([.,;:])(?=\s|$)/g, "$$$$\n\n") // the sentence's period after a display formula
    .replace(/\n{3,}/g, "\n\n");
}

function displayOnOwnLine(md: string) {
  return md.split(/(```[\s\S]*?```|`[^`\n]*`)/g).map((part, i) => (i % 2 === 1 ? part : pairDollars(part))).join("");
}

export function wrapBareLatex(md: string) {
  // Gemini sometimes slips an Arabic word into Hebrew text ("ההנחתה هي 40 dB"); his courses have no Arabic.
  md = md.replace(/[\u0600-\u06FF]+\s?/g, "");
  // JSON turned "\b", "\f", "\t", "\r" at the start of \bar, \frac, \theta, \rho into control characters.
  const text = displayOnOwnLine(md.replace(/\x08/g, "\\b").replace(/\x0c/g, "\\f").replace(/\t(?=[a-z]{2,})/g, "\\t").replace(/\r(?=[a-z]{2,})/g, "\\r"));
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
