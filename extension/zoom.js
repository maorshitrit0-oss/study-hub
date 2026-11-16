// Study Hub (16/11/2026): on a Zoom recording page he opened himself, collect the Transcript panel Zoom shows to
// every viewer and hand it to the app. Runs once per recording per browser session.
(async () => {
  const sleep = (t) => new Promise((r) => setTimeout(r, t));
  const key = "studyhub-sent:" + location.pathname;
  if (sessionStorage.getItem(key)) return;
  // wait for the page (a JS app) to draw the transcript panel
  let best = null;
  for (let tries = 0; tries < 40 && !best; tries++) {
    await sleep(1500);
    let score = 0;
    for (const el of document.querySelectorAll("*")) {
      const s = getComputedStyle(el);
      if (!/(auto|scroll)/.test(s.overflowY) || el.scrollHeight <= el.clientHeight + 20) continue;
      const r = el.getBoundingClientRect();
      if (r.left < innerWidth * 0.4 || r.height < 150) continue;
      const t = (el.innerText || "").length;
      if (t > 300 && t > score) { score = t; best = el; }
    }
  }
  if (!best) return; // no transcript on this recording
  const got = new Map();
  const grab = () => {
    const top0 = best.getBoundingClientRect().top;
    for (const n of best.querySelectorAll("*")) {
      if (n.children.length) continue;
      const t = (n.innerText || n.textContent || "").trim();
      if (!t) continue;
      const k = Math.round(n.getBoundingClientRect().top - top0 + best.scrollTop);
      got.set(k + "|" + t, [k, t]);
    }
  };
  best.scrollTop = 0;
  await sleep(600);
  let last = -1, same = 0;
  while (same < 4) {
    grab();
    if (best.scrollTop === last) same++; else same = 0;
    last = best.scrollTop;
    best.scrollTop += Math.max(200, best.clientHeight * 0.7);
    await sleep(450);
  }
  best.scrollTop = 0;
  const text = [...got.values()].sort((a, b) => a[0] - b[0]).map((x) => x[1]).join("\n");
  if (text.length < 500) return;
  sessionStorage.setItem(key, "1");
  chrome.runtime.sendMessage({ type: "zoom-transcript", src: location.href, text });
})();
