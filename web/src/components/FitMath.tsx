"use client";
import { useEffect } from "react";

/**
 * A display formula wider than the screen is shrunk until it fits (down to 60%); only then does it scroll. His
 * screenshot 12/11/2026: a boxed formula was cut at the edge of the phone. Mounted once in the app layout.
 */
export default function FitMath() {
  useEffect(() => {
    const fit = () => {
      for (const d of document.querySelectorAll<HTMLElement>(".katex-display")) {
        d.style.fontSize = "";
        let k = 1;
        while (d.scrollWidth > d.clientWidth + 1 && k > 0.6) {
          k -= 0.05;
          d.style.fontSize = `${k * 0.92}em`;
        }
      }
    };
    // again after the math fonts load, when a fold opens, and when a new page / chapter appears
    let t = setTimeout(fit, 300);
    const later = () => { clearTimeout(t); t = setTimeout(fit, 150); };
    const mo = new MutationObserver(later);
    mo.observe(document.body, { childList: true, subtree: true });
    document.addEventListener("toggle", later, true);
    window.addEventListener("resize", later);
    return () => { clearTimeout(t); mo.disconnect(); document.removeEventListener("toggle", later, true); window.removeEventListener("resize", later); };
  }, []);
  return null;
}
