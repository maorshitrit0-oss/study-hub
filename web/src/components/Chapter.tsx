import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

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
          a: ({ href, children }) => <a href={href} target="_blank" rel="noreferrer" className="text-accent underline">{children}</a>,
        }}
      >
        {md}
      </ReactMarkdown>
    </div>
  );
}
