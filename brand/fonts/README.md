# Carousel font substitutes

These open fonts are temporary substitutes, not the licensed Heading Now and Gotham requested by the brand owner.

- **Barlow Condensed ExtraBold**: uppercase headlines; Google Fonts, SIL Open Font License.
- **Montserrat Medium / Bold**: supporting copy, subheads and labels; Google Fonts, SIL Open Font License. Static instances of the upstream variable font at weights 500 and 700.

Upstream downloads:

- `https://github.com/google/fonts/tree/main/ofl/barlowcondensed`
- `https://github.com/google/fonts/tree/main/ofl/montserrat`

The accompanying OFL files contain the copyright and redistribution terms. Font files can be bundled with editable artwork under those terms. Install these three `.ttf` files before editing the SVGs in a desktop design application. The build script uses an isolated Fontconfig configuration and does not require global installation.

The font assets and all image references are also embedded into the generated SVG files. Browsers can use the embedded web-font declarations; Inkscape uses the accompanying local font files through Fontconfig. This keeps the PNG export reproducible while avoiding a hidden dependency on a machine's default fonts.

## Monumental kit substitutes

The second brand kit ([`../monumental/STYLE_GUIDE.md`](../monumental/STYLE_GUIDE.md)) uses two more open fonts. Neither is the exact lettering in the reference campaigns. That lettering came from an image generator and its font can't be identified.

- **Bodoni Moda Bold / Black**: the editorial serif for headlines. It is wider than the compressed Didone lettering in the references, so plan headline line breaks with that in mind. SIL Open Font License.
- **Anton Regular**: the heavy condensed headline face for the Operator-style variant. SIL Open Font License.

Both were taken from the Fontsource npm packages (`@fontsource/bodoni-moda`, `@fontsource/anton` 5.3.0, Latin subset) and converted from WOFF to TTF without changes. Montserrat Medium remains the utility and body face in both kits.
