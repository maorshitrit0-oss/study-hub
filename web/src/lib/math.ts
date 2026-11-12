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
      // Tables and quotes can't hold a display formula without breaking; a list item can, indented to its text.
      if (/^\s*(\||>)/.test(line)) return line;
      const ind = " ".repeat((line.match(/^\s*(?:[-*+]|\d+[.)])\s+/)?.[0] ?? "").length);
      return line.replace(/(?<![$\\])\$(?!\$)([^$\n]+?)\$(?!\$)/g, (m, tex: string) =>
        visual(tex) > LONG ? `\n\n${ind}$$${splitEquation(tex.trim())}$$\n\n${ind}` : m);
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

/** Small repairs inside one formula (a scan of all chapters, 11/11/2026): \(..\) inside $..$, "/\m" units,
 *  unclosed braces. */
function cleanTex(tex: string) {
  tex = tex.replace(/\\[()]/g, "").replace(/\\m(?![A-Za-z])/g, "\\text{m}");
  const opens = (tex.match(/(?<!\\)\{/g) || []).length - (tex.match(/(?<!\\)\}/g) || []).length;
  return opens > 0 ? tex + "}".repeat(opens) : tex;
}

/** How wide a formula looks: commands count as one character, braces as none. */
const visual = (tex: string) => tex.replace(/\\(?:mathrm|text|operatorname|mathbf|boldsymbol)\{([^}]*)\}/g, "$1")
  .replace(/\\[A-Za-z]+/g, "x").replace(/[{}\s]/g, "").length;

function pairDollars(text: string) {
  // \(x\) / \[x\] written as delimiters -> $x$ / $$x$$
  text = text.replace(/\\\[([\s\S]+?)\\\]/g, (_, x) => `$$${x}$$`).replace(/\\\(([^\n]+?)\\\)/g, (_, x) => `$${x}$`);
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
  let out = "", pos = 0, open: { at: number; len: number } | null = null, afterDisplay = false;
  // the text right after a display formula already got the item's indent: drop its own leading spaces / comma
  const chunk = (a: number, b: number) => {
    const c = text.slice(a, b).replace(/\$/g, "");
    return afterDisplay ? c.replace(/^[ \t]*[,;]?[ \t]*/, "") : c;
  };
  for (const t of tokens) {
    if (!open) { open = t; continue; }
    const tex = text.slice(open.at + open.len, t.at);
    if (!tex.trim()) { open = t; continue; } // empty pair: the second one opens
    // "ה-$-$V_{CE} > 0.3$" (his screenshot 11/11/2026): a "pair" around a lone dash / punctuation, or an inline pair
    // across a paragraph break, is a stray opener - keep the text, the closer opens instead.
    if (/^[-–.,:;&^\\]$/.test(tex.trim()) || (open.len === 1 && t.len === 1 && tex.includes("\n"))) {
      const before = text.slice(pos, open.at).replace(/\$/g, "");
      out += before + (before.endsWith(tex.trim()) ? "" : tex);
      pos = t.at;
      open = t;
      continue;
    }
    if (HEBREW.test(tex.replace(/\\text\{[^}]*\}/g, ""))) { open = t; continue; } // text, not math: stray opener
    // Inside a list item a display formula is indented to the item's text, so it stays in the item and the text after
    // it keeps its place (his screenshots 11-12/11/2026: formulas mid-line in RTL text jumped around).
    const line = text.slice(text.lastIndexOf("\n", open.at) + 1, open.at);
    const ind = " ".repeat((line.match(/^\s*(?:[-*+]|\d+[.)])\s+/)?.[0] ?? "").length);
    const display = open.len === 2 || t.len === 2 || visual(tex) > LONG;
    out += chunk(pos, open.at) + (display ? `\n\n${ind}$$${cleanTex(tex.trim())}$$\n\n${ind}` : `$${cleanTex(tex.trim())}$`);
    afterDisplay = display;
    pos = t.at + t.len;
    open = null;
  }
  return (out + chunk(pos, text.length))
    .replace(/\$\$\n\n\s*([.,;:])(?=\s|$)/g, "$$$$\n\n") // the sentence's period after a display formula
    .replace(/\n{3,}/g, "\n\n");
}

function displayOnOwnLine(md: string) {
  return md.split(/(```[\s\S]*?```|`[^`\n]*`)/g).map((part, i) => (i % 2 === 1 ? part : pairDollars(part))).join("");
}

// The Arabic twin of a Hebrew one-letter prefix: Gemini writes "لבין" / "وטיפוסי" for "לבין" / "וטיפוסי" (04/11/2026).
const PREFIX: Record<string, string> = { "و": "ו", "ل": "ל", "ب": "ב", "ك": "כ", "ه": "ה", "م": "מ", "ش": "ש" };

/**
 * Gemini sometimes slips Arabic into Hebrew text: a prefix letter glued to a Hebrew word becomes the Hebrew letter,
 * any other Arabic ("ההנחתה هي 40 dB") is dropped - his courses have no Arabic.
 */
export function fixArabic(text: string) {
  return text
    .replace(/[\u0600-\u06FF](?=[\u0590-\u05FF])/g, (c) => PREFIX[c] ?? "")
    .replace(/[\u0600-\u06FF]+\s?/g, "");
}

export function wrapBareLatex(md: string) {
  // "3. > 🏠 מהחיים: ..." - a quote written as a numbered item shows a stray ">" (his screenshot 11/11/2026):
  // it becomes a quote of its own.
  md = fixArabic(md).replace(/^[ \t]*\d+\.[ \t]+>[ \t]*/gm, "\n> ");
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
