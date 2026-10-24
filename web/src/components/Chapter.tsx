import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { promoteLongMath } from "@/lib/math";
import Wave from "./Wave";

/** Renders a reading chapter; images written as ![..](slide:N) resolve to signed slide URLs. */
export default function Chapter({ md, slideUrls }: { md: string; slideUrls: Record<number, string> }) {
  return (
    <div className="chapter">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        urlTransform={(url) => url}
        components={{
          img: ({ src, alt }) => {
            const m = typeof src === "string" ? src.match(/^slide:(\d+)$/) : null;
            const url = m ? slideUrls[Number(m[1])] : typeof src === "string" ? src : undefined;
            if (!url) return null;
            return (
              <a href={url} target="_blank" rel="noreferrer">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={url} alt={alt ?? ""} loading="lazy" />
              </a>
            );
          },
          // ```wave blocks become computed timing diagrams.
          pre: ({ node, children }) => {
            const code = node?.children?.[0];
            const cls = code && "properties" in code ? String(code.properties?.className ?? "") : "";
            if (/language-wave/.test(cls) && code && "children" in code) {
              const text = code.children.map((c) => ("value" in c ? c.value : "")).join("");
              return <Wave src={text} />;
            }
            return <pre>{children}</pre>;
          },
          a: ({ href, children }) => <a href={href} target="_blank" rel="noreferrer" className="text-accent underline">{children}</a>,
        }}
      >
        {promoteLongMath(md)}
      </ReactMarkdown>
    </div>
  );
}

/** A short text with formulas (quiz question, option, explanation): same math rendering, no block margins. */
export function Rich({ text }: { text: string }) {
  return (
    <span className="rich">
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}
        components={{ p: ({ children }) => <span className="block">{children}</span> }}>
        {text}
      </ReactMarkdown>
    </span>
  );
}
