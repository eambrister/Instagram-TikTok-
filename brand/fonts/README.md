# Carousel font substitutes

These open fonts are temporary substitutes, not the licensed Heading Now and Gotham requested by the brand owner.

- **Barlow Condensed ExtraBold**: uppercase headlines; Google Fonts, SIL Open Font License.
- **Montserrat Medium / Bold**: supporting copy, subheads and labels; Google Fonts, SIL Open Font License. Static instances of the upstream variable font at weights 500 and 700.

Upstream downloads:

- `https://github.com/google/fonts/tree/main/ofl/barlowcondensed`
- `https://github.com/google/fonts/tree/main/ofl/montserrat`

The accompanying OFL files contain the copyright and redistribution terms. Font files can be bundled with editable artwork under those terms. Install these three `.ttf` files before editing the SVGs in a desktop design application. The build script uses an isolated Fontconfig configuration and does not require global installation.

The font assets and all image references are also embedded into the generated SVG files. Browsers can use the embedded web-font declarations; Inkscape uses the accompanying local font files through Fontconfig. This keeps the PNG export reproducible while avoiding a hidden dependency on a machine's default fonts.
