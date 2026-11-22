import fs from 'fs';
import {unified} from 'unified';import remarkParse from 'remark-parse';import remarkGfm from 'remark-gfm';import remarkMath from 'remark-math';import remarkBreaks from 'remark-breaks';import remarkRehype from 'remark-rehype';import rehypeKatex from 'rehype-katex';
const proc=unified().use(remarkParse).use(remarkGfm).use(remarkMath).use(remarkBreaks).use(remarkRehype).use(rehypeKatex,{throwOnError:false,strict:'ignore'});
const CMD=/\\(frac|theta|bar|int|sqrt|begin|end|left|right|text|sum|hat|vec|times|cdot|omega|alpha|beta|gamma|lambda|sigma|mu|epsilon|eta|Delta|delta|approx|le|ge|infty|partial|nabla|mathrm|min|max)\b/g;
function score(md){ const tree=proc.runSync(proc.parse(md)); let n=0, txt=''; const walk=(x)=>{ if(x.type==='element'){ const c=(x.properties&&x.properties.className)||[]; if(c.includes('katex-error')) n+=3; if(c.includes('katex')) return; if(x.tagName==='code'||x.tagName==='pre') return;} if(x.type==='text') txt+=x.value+' '; (x.children||[]).forEach(walk); }; walk(tree); return n+(txt.match(CMD)||[]).length; }
const [cur,cands,outp]=process.argv.slice(2); const A=JSON.parse(fs.readFileSync(cur)); const B={};
for(const f of process.argv.slice(5)) for(const c of JSON.parse(fs.readFileSync(f))) for(const l of c.lessons) for(const k of ['chapter_md','summary_md']) if(l[k]) (B[l.id+k]=B[l.id+k]||[]).push(l[k]);
const out=[]; let tot=0;
for(const c of A) for(const l of c.lessons) for(const k of ['chapter_md','summary_md']){ const v=l[k]; if(!v) continue; let best=v, bs=score(v); for(const w of (B[l.id+k]||[])){ if(w===v) continue; const s=score(w); if(s<bs){best=w;bs=s;} } tot+=bs; if(best!==v) out.push({table:'lessons',id:l.id,field:k,value:best}); }
fs.writeFileSync(outp,JSON.stringify(out)); console.error('rows',out.length,'remaining',tot);
