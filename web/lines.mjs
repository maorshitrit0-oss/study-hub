import fs from 'fs';
import {unified} from 'unified';import remarkParse from 'remark-parse';import remarkGfm from 'remark-gfm';import remarkMath from 'remark-math';import remarkRehype from 'remark-rehype';import rehypeKatex from 'rehype-katex';
const proc=unified().use(remarkParse).use(remarkGfm).use(remarkMath).use(remarkRehype).use(rehypeKatex,{throwOnError:false,strict:'ignore'});
const md=fs.readFileSync(process.argv[2],'utf8'); const tree=proc.runSync(proc.parse(md));
const walk=(x)=>{ if(x.type==='element'){ const c=(x.properties&&x.properties.className)||[]; if(c.includes('katex-error')){ console.log('ERR', JSON.stringify((x.children||[]).map(c=>c.value||'').join('').slice(0,200))); return;} if(c.includes('katex')) return; if(x.tagName==='code'||x.tagName==='pre') return;} if(x.type==='text' && /\\(frac|tilde|vec|hat|text|cos|eta)\b/.test(x.value)) console.log('RAW', JSON.stringify(x.value.slice(0,200))); (x.children||[]).forEach(walk); };
walk(tree);
