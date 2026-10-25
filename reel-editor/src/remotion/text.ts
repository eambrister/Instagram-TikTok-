import { measureText } from "@remotion/layout-utils";

/** Greedy wrap at the largest size (step 2px) that fits maxLines inside the box. Fonts must be loaded first. */
export function wrapFit(text: string, family: string, box: { w: number; h: number }, maxSize: number, minSize: number, maxLines = 3, lineHeight = 1.05) {
  const words = text.split(/\s+/).filter(Boolean);
  const width = (s: string, size: number) => measureText({ text: s, fontFamily: family, fontSize: size, validateFontIsLoaded: false }).width;
  for (let size = maxSize; size >= minSize; size -= 2) {
    const lines: string[] = [];
    let cur = "";
    let ok = true;
    for (const w of words) {
      const next = cur ? `${cur} ${w}` : w;
      if (width(next, size) <= box.w) cur = next;
      else {
        if (!cur) {
          ok = false;
          break;
        }
        lines.push(cur);
        cur = w;
      }
    }
    if (cur) lines.push(cur);
    if (ok && lines.length <= maxLines && lines.length * size * lineHeight <= box.h) return { size, lines };
  }
  return { size: minSize, lines: [text] };
}
