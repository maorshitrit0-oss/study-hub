// The site's own pipeline (Chapter.tsx): wrapBareLatex -> promoteLongMath -> remark-math + breaks -> KaTeX.
import fs from 'fs';
import {unified} from 'unified';import remarkParse from 'remark-parse';import remarkGfm from 'remark-gfm';import remarkMath from 'remark-math';import remarkBreaks from 'remark-breaks';import remarkRehype from 'remark-rehype';import rehypeKatex from 'rehype-katex';
const {promoteLongMath, wrapBareLatex, fixTextSymbols, noIndentedCode} = await import('./src/lib/math.ts');
const proc=unified().use(remarkParse).use(remarkGfm).use(remarkMath).use(remarkBreaks).use(remarkRehype).use(rehypeKatex,{throwOnError:false,strict:'ignore'});
const raw=fs.readFileSync(process.argv[2],'utf8'); const md=promoteLongMath(wrapBareLatex(fixTextSymbols(noIndentedCode(raw))));
// 27/11/2026: an unknown command inside \\text renders red without the katex-error class - the source is checked too
for (const m of raw.matchAll(/\\text\{\s*\\[a-zA-Z]+\s*\}/g)) console.log('ERR', JSON.stringify(m[0])); const tree=proc.runSync(proc.parse(md));
const walk=(x)=>{ if(x.type==='element'){ const c=(x.properties&&x.properties.className)||[]; const st=String((x.properties&&x.properties.style)||''); if(c.includes('katex-error')||/#cc0000/.test(st)){ console.log('ERR', JSON.stringify((x.children||[]).map(c=>c.value||'').join('').slice(0,200))); return;} if(c.includes('katex')) return; if(x.tagName==='code'||x.tagName==='pre') return;} if(x.type==='text' && /\\(frac|tilde|vec|hat|text|cos|eta|sqrt|sum|int)\b/.test(x.value)) console.log('RAW', JSON.stringify(x.value.slice(0,200))); (x.children||[]).forEach(walk); };
walk(tree);
