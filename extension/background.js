// Opens the app's /zoom page and gives it the transcript (the page saves it into the lesson with this recording link).
const APP = "https://study-hub-tawny-mu-63.vercel.app";
chrome.runtime.onMessage.addListener((msg) => {
  if (msg?.type !== "zoom-transcript") return;
  chrome.tabs.create({ url: `${APP}/zoom?src=${encodeURIComponent(msg.src)}`, active: true }, (tab) => {
    const onUpdated = (id, info) => {
      if (id !== tab.id || info.status !== "complete") return;
      chrome.tabs.onUpdated.removeListener(onUpdated);
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (d) => {
          let n = 0;
          const t = setInterval(() => {
            window.postMessage({ type: "zoom-transcript", src: d.src, text: d.text }, location.origin);
            if (++n > 40) clearInterval(t);
          }, 500);
          window.addEventListener("message", (e) => { if (e.data === "zoom-ok") clearInterval(t); });
        },
        args: [{ src: msg.src, text: msg.text }],
      });
    };
    chrome.tabs.onUpdated.addListener(onUpdated);
  });
});
