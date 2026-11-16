/**
 * "📋 תמלול זום לאפליקציה" (16/11/2026: the Zoom recordings cannot be downloaded any more and he will not record the
 * screen). A bookmark he clicks on the Zoom recording page: it scrolls the Transcript panel that Zoom shows to every
 * viewer, collects all its lines in order, opens /zoom in the app and hands the text over with postMessage.
 * The app finds the lesson by the recording link and writes the chapter from the transcript.
 */
export function zoomBookmarklet(app: string) {
  const js = `(async()=>{const APP=${JSON.stringify(app)};const sleep=t=>new Promise(r=>setTimeout(r,t));
let best=null,score=0;for(const el of document.querySelectorAll('*')){const s=getComputedStyle(el);
if(!/(auto|scroll)/.test(s.overflowY)||el.scrollHeight<=el.clientHeight+20)continue;const r=el.getBoundingClientRect();
if(r.left<innerWidth*0.4||r.height<150)continue;const t=(el.innerText||'').length;if(t>score){score=t;best=el}}
if(!best){alert('לא מצאתי את חלונית התמלול. לפתוח את Transcript בצד ימין ולנסות שוב.');return}
const got=new Map();const grab=()=>{for(const n of best.querySelectorAll('*')){if(n.children.length)continue;
const t=(n.innerText||n.textContent||'').trim();if(!t)continue;const k=Math.round(n.getBoundingClientRect().top-best.getBoundingClientRect().top+best.scrollTop);
got.set(k+'|'+t,[k,t])}};best.scrollTop=0;await sleep(600);let last=-1,same=0;
while(same<4){grab();if(best.scrollTop===last)same++;else same=0;last=best.scrollTop;best.scrollTop+=Math.max(200,best.clientHeight*0.7);await sleep(450)}
const lines=[...got.values()].sort((a,b)=>a[0]-b[0]).map(x=>x[1]);const text=lines.join('\\n');
if(text.length<500){alert('התמלול קצר מדי ('+lines.length+' שורות). לגלול קצת בחלונית התמלול ולנסות שוב.');return}
const w=window.open(APP+'/zoom?src='+encodeURIComponent(location.href),'_blank');let ok=false;
addEventListener('message',e=>{if(e.origin===APP&&e.data==='zoom-ok')ok=true});
for(let i=0;i<60&&!ok;i++){try{w.postMessage({type:'zoom-transcript',src:location.href,text},APP)}catch(_){}await sleep(500)}
if(!ok)alert('האפליקציה לא אישרה. לוודא שאתה מחובר לאפליקציה באותו דפדפן ולנסות שוב.')})();`;
  return "javascript:" + encodeURIComponent(js.replace(/\n/g, ""));
}
