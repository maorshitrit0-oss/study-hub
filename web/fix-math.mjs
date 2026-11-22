// Repairs formulas that do not render, validated with the same renderer as the site. Paragraph by paragraph: try
// fixes, keep one only if it lowers the number of errors. Output: [{table,id,field,value}] for changed rows.
import fs from 'fs';
import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkBreaks from 'remark-breaks';
import remarkRehype from 'remark-rehype';
import rehypeKatex from 'rehype-katex';
const proc=unified().use(remarkParse).use(remarkGfm).use(remarkMath).use(remarkBreaks).use(remarkRehype).use(rehypeKatex,{throwOnError:false,strict:'ignore'});
const CMD=/\\(frac|theta|bar|int|sqrt|begin|end|left|right|text|sum|hat|vec|times|cdot|omega|alpha|beta|gamma|lambda|sigma|mu|epsilon|eta|Delta|delta|approx|le|ge|infty|partial|nabla|mathrm|min|max)\b/g;
function score(md){ const tree=proc.runSync(proc.parse(md)); let n=0, txt=''; const walk=(x)=>{ if(x.type==='element'){ const c=(x.properties&&x.properties.className)||[]; if(c.includes('katex-error')) n+=3; if(c.includes('katex')) return; if(x.tagName==='code'||x.tagName==='pre') return;} if(x.type==='text') txt+=x.value+' '; (x.children||[]).forEach(walk); }; walk(tree); return n+(txt.match(CMD)||[]).length; }
const mathSeg=(s,f)=>s.replace(/(\$\$?)([^$]+?)\1/g,(m,d,b)=>d+f(b)+d);
const FIXES=[
  s=>s.replace(/\\text\{#/g,'\\text{\\#'),
  s=>s.replace(/\\[֐-׿]+\s*/g,''),
  s=>s.replace(/(^|[^$])\$\$([^$\n]+?)\$(?!\$)/g,'$1$$$2$$'),          // $$x$  -> $$x$$
  s=>s.replace(/(^|[^$])\$([^$\n]+?)\$\$/g,'$1$$$2$$'),                  // $x$$  -> $$x$$
  s=>s.replace(/(^|[^$])\$\$([^$\n]+?)\$(?!\$)/g,'$1$$2$'),              // $$x$  -> $x$
  s=>s.replace(/(^|[^$])\$([^$\n]+?)\$\$/g,'$1$$2$'),                    // $x$$  -> $x$
  s=>s.split('\n').map(l=>l.trim().startsWith('|')?mathSeg(l,b=>b.replace(/\\(left|right)\|/g,'\\$1\\vert ').replace(/\|/g,'\\vert ')):l).join('\n'),
  s=>{ const o=(s.match(/\{/g)||[]).length, c=(s.match(/\}/g)||[]).length; return o>c? s.replace(/(\$\$?)([^$]+?)\1/g,(m,d,b)=>{ const k=(b.match(/\{/g)||[]).length-(b.match(/\}/g)||[]).length; return k>0? d+b+'}'.repeat(k)+d : m; }) : s; },
];
function fixLine(l){
  l=l.replace(/\\\(/g,'$').replace(/\\\)/g,'$').replace(/\\text\{#/g,'\\text{\\#').replace(/\\[֐-׿]+\s*/g,'');
  if(l.trim().startsWith('|')) l=mathSeg(l,b=>b.replace(/\\(left|right)\|/g,'\\$1\\vert ').replace(/(?<!\\)\|/g,'\\vert '));
  l=l.replace(/\$\$/g,'$');
  if(!l.includes('$') && CMD.test(l)){ CMD.lastIndex=0; const w=l.replace(/^(\s*(?:[-*]|\d+\.)?\s*)(.*?)\s*$/,'$1$$$2$$'); if(score(w)<score(l)) return w; }
  CMD.lastIndex=0;
  const n=(l.match(/(?<!\\)\$/g)||[]).length;
  if(n%2){ const cands=[l.replace(/(?<!\\)\$/,''), l.replace(/(?<!\\)\$(?!.*(?<!\\)\$)/,''), l+'$'];
    let best=cands[0], bs=score(best); for(const c of cands.slice(1)){ const s=score(c); if(s<bs){best=c;bs=s;} } l=best; }
  return l;
}
function fixMd(md){
  md=md.replace(/\$(\\eta_0)\n\$\$\n:\n\$\$\n/g,'$$$1$:\n$$$$\n')
       .replace(/\n\$\$\ns\n\$\$\nו-\$t\$/g,' $s$ ו-$t$')
       .replace(/עבור\n\$\$\ns > t\$\$: /g,'עבור $s > t$: ');
  const parts=md.split(/(```[\s\S]*?```)/); 
  for(let p=0;p<parts.length;p+=2){
    const lines=parts[p].split('\n'); let inside=false; const out=[];
    for(const raw of lines){
      const s=raw.trim();
      if(s==='$$'){ inside=!inside; out.push(raw); continue; }
      if(s.startsWith('\\[')&&!inside&&s!=='\\['){ out.push(raw); continue; }
      if(s==='\\['){ inside=true; out.push('$$'); continue; } if(s==='\\]'){ inside=false; out.push('$$'); continue; }
      if(inside){ out.push(raw); continue; }
      out.push(score(raw)?fixLine(raw):raw);
    }
    if(inside) out.push('$$');
    parts[p]=out.join('\n');
  }
  const v=parts.join(''); return v!==md? v : null;
}
const d=JSON.parse(fs.readFileSync(process.argv[2])); const out=[]; let before=0, after=0;
for(const c of d) for(const l of c.lessons) for(const f of ['chapter_md','summary_md']){ const md=l[f]; if(!md) continue;
  const s0=score(md); before+=s0; if(!s0) continue; const v=fixMd(md); const s1=v?score(v):s0; after+=s1;
  if(v && s1<s0) out.push({table:'lessons',id:l.id,field:f,value:v}); }
fs.writeFileSync(process.argv[3], JSON.stringify(out));
console.error(`problems before ${before}, after ${after}, rows changed ${out.length}`);
