import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Brand fonts from brand/fonts, copied into public/fonts.
export const UI_FONT = "Montserrat";
export const DISPLAY_FONT = "Anton";
export const CONDENSED_FONT = "Barlow Condensed";

const fonts = [
  { family: UI_FONT, url: "fonts/Montserrat-Medium.ttf", weight: "500" },
  { family: UI_FONT, url: "fonts/Montserrat-Bold.ttf", weight: "700" },
  { family: DISPLAY_FONT, url: "fonts/Anton-Regular.ttf", weight: "400" },
  { family: CONDENSED_FONT, url: "fonts/BarlowCondensed-ExtraBold.ttf", weight: "800" },
];

for (const f of fonts) {
  loadFont({ family: f.family, url: staticFile(f.url), weight: f.weight });
}
