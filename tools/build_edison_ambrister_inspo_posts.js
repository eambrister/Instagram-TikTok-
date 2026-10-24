// Build the Edison Ambrister inspo post set: six 1080 x 1350 (4:5) posts for
// Instagram and TikTok photo mode, adapted from Pinterest reference ideas.
//
// Typographic / vector edition: no photos or generated imagery. Each post is an
// HTML page rendered with the pre-installed Playwright Chromium.
//
// Usage: node tools/build_edison_ambrister_inspo_posts.js

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "outputs/edison-ambrister-inspo-posts");
const TOKENS = JSON.parse(fs.readFileSync(path.join(ROOT, "brand/tokens.json"), "utf8"));
const C = TOKENS.colors;
const W = 1080;
const H = 1350;
const FOOTER = TOKENS.post.footer;

const fontUrl = (f) => "file://" + path.join(ROOT, "brand/fonts", f);
const LOGO = "file://" + path.join(ROOT, "brand/assets/edison-ambrister/edison-ambrister-horizontal.png");

const BASE_CSS = `
@font-face { font-family: Head; src: url(${fontUrl("BarlowCondensed-ExtraBold.ttf")}); }
@font-face { font-family: Body; src: url(${fontUrl("Montserrat-Medium.ttf")}); font-weight: 500; }
@font-face { font-family: Body; src: url(${fontUrl("Montserrat-Bold.ttf")}); font-weight: 700; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: ${W}px; height: ${H}px; overflow: hidden; }
body { font-family: Body, sans-serif; font-weight: 500; color: ${C.white};
  background: radial-gradient(120% 70% at 85% 0%, #1b1a16 0%, ${C.obsidian} 60%); position: relative; }
body.ivory { color: ${C.obsidian}; background: ${C.ivory}; }
.head { font-family: Head, sans-serif; text-transform: uppercase; line-height: .9; letter-spacing: .5px; }
.gold { color: ${C.gold}; }
.crimson { color: ${C.crimson}; }
.silver { color: ${C.silver}; }
header { position: absolute; top: 40px; left: 50px; right: 50px; height: 80px;
  display: flex; align-items: center; justify-content: space-between; }
header img { width: 210px; }
.ivory::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 158px; background: ${C.obsidian}; }
.ivory header { z-index: 1; }
.series { font-weight: 700; font-size: 19px; letter-spacing: 4px; color: ${C.gold}; }
.ivory .series { color: ${C.gold}; }
.ivory main { top: 190px; }
footer { position: absolute; left: 50px; right: 50px; bottom: 40px; text-align: center; }
footer .rule { height: 1px; background: ${C.silver}; opacity: .5; margin-bottom: 18px; }
footer .txt { font-weight: 700; font-size: 17px; letter-spacing: 3px; color: ${C.silver}; }
.ivory footer .txt { color: ${C.graphite}; }
.ivory footer .rule { background: ${C.graphite}; opacity: .35; }
main { position: absolute; top: 148px; left: 50px; right: 50px; bottom: 108px; display: flex; flex-direction: column; }
main > * { flex-shrink: 0; }
.note { font-size: 17px; line-height: 1.45; color: ${C.silver}; }
.ivory .note { color: #4a4d53; }
`;

function page(cls, series, body, extraCss = "") {
  return `<!doctype html><html><head><meta charset="utf-8"><style>${BASE_CSS}${extraCss}</style></head>
<body class="${cls}">
<header><img src="${LOGO}" alt=""><div class="series">${series}</div></header>
<main>${body}</main>
<footer><div class="rule"></div><div class="txt">${FOOTER}</div></footer>
</body></html>`;
}

// ------------------------------------------------------------ 01 nutrients

const nutrientRows = [
  ["Oysters", "Zinc", "Top zinc source: 3 oz cooked ≈ 32 mg."],
  ["Lean beef", "Zinc + protein", "3 oz cooked beef patty ≈ 5 mg zinc."],
  ["Pumpkin seeds", "Zinc + magnesium", "1 oz roasted ≈ 2 mg zinc. Easy snack."],
  ["Salmon", "Vitamin D + Omega-3", "3 oz cooked sockeye ≈ 14 mcg vitamin D."],
  ["Eggs", "Vitamin D", "Keep the yolk. 1 large egg ≈ 1 mcg."],
  ["Brazil nuts", "Selenium", "1–2 nuts covers the day. Do not overdo it."],
];

const pin01 = page("", "EDISON EATS", `
  <div class="head" style="font-size:132px">TESTOSTERONE</div>
  <div class="head gold" style="font-size:104px;margin-top:4px">NUTRIENTS · 6 FOODS</div>
  <p style="font-size:25px;line-height:1.4;margin-top:26px;max-width:860px">
    Zinc, vitamin D and selenium support <b>normal</b> hormone levels. Food covers a shortfall.
    It won't push you past normal.</p>
  <div class="rows">
    ${nutrientRows.map((r, i) => `
    <div class="row">
      <div class="num head">${String(i + 1).padStart(2, "0")}</div>
      <div class="food"><div class="head name">${r[0]}</div><div class="desc">${r[2]}</div></div>
      <div class="tag">${r[1]}</div>
    </div>`).join("")}
  </div>
  <p class="note" style="margin-top:auto">Values: NIH Office of Dietary Supplements. Low energy or libido? Get bloodwork from a doctor instead of guessing.</p>
`, `
.rows { margin-top: 22px; border-top: 1px solid ${C.graphite}; }
.row { display: grid; grid-template-columns: 92px 1fr 270px; align-items: center; gap: 14px;
  padding: 19px 0; border-bottom: 1px solid ${C.graphite}; }
.num { font-size: 64px; color: ${C.gold}; }
.name { font-size: 50px; }
.desc { font-size: 20px; color: ${C.silver}; margin-top: 6px; line-height: 1.3; }
.tag { justify-self: end; text-align: center; font-weight: 700; font-size: 17px; letter-spacing: 1px; text-transform: uppercase; white-space: nowrap;
  color: ${C.obsidian}; background: ${C.gold}; border-radius: 30px; padding: 10px 18px; }
`);

// ------------------------------------------------------------ 02 swaps

const swaps = [
  ["Pancakes + syrup", "Oatmeal or cream of wheat + fruit"],
  ["Pizza night", "Lean ground beef + rice bowl"],
  ["Ribs, mac & coleslaw", "Chicken breast, potatoes, vegetables"],
  ["Sushi & spring rolls", "Tuna + rice, made at home"],
  ["Cake & candy", "Fruit"],
  ["Eating whatever was there", "Repeatable meals, counted"],
];

const pin02 = page("ivory", "MY PROOF", `
  <div class="head" style="font-size:104px">6 FOOD SWAPS THAT</div>
  <div class="head" style="font-size:104px">HELPED ME LOSE <span style="color:${C.crimson}">80 LB</span></div>
  <p style="font-size:24px;line-height:1.4;margin-top:24px;max-width:880px">
    No food is good or bad. These swaps meant fewer calories, more protein and meals I could repeat.</p>
  <div class="cols"><div class="h">BEFORE</div><div></div><div class="h" style="color:#9a7a0e">NOW</div></div>
  <div class="swaps">
    ${swaps.map((s) => `
    <div class="swap">
      <div class="old">${s[0]}</div>
      <div class="arrow">→</div>
      <div class="new head">${s[1]}</div>
    </div>`).join("")}
  </div>
  <p class="note" style="margin-top:auto">My experience: 222 → 142 lb in under two years. Not a promise of your result.</p>
`, `
.cols, .swap { display: grid; grid-template-columns: 330px 60px 1fr; align-items: center; }
.cols { margin-top: 24px; font-weight: 700; font-size: 18px; letter-spacing: 4px; color: ${C.graphite}; padding-bottom: 12px;
  border-bottom: 2px solid ${C.obsidian}; }
.swap { padding: 21px 0; border-bottom: 1px solid #d8cfbd; }
.old { font-size: 27px; color: #6b6e74; text-decoration: line-through; text-decoration-color: ${C.crimson}; text-decoration-thickness: 2px; line-height: 1.25; }
.arrow { font-size: 34px; color: #9a7a0e; text-align: center; }
.new { font-size: 48px; line-height: .95; }
`);

// ------------------------------------------------------------ 03 fridge

const zones = [
  ["FRONT · TOP SHELF", "Fruit you can see", "Washed and ready. Visible food gets eaten."],
  ["EYE LEVEL", "Cooked protein, portioned", "Chicken, lean beef, eggs. Grab and go."],
  ["MIDDLE SHELF", "Ready carbs", "Rice and potatoes, cooked and portioned."],
  ["DRAWERS", "Vegetables, prepped", "Cut on Sunday so there's no excuse on Wednesday."],
  ["DOOR", "Sauces you measure", "Lighter condiments. Count the spoonful."],
  ["FREEZER", "The backup plan", "Frozen veg, berries, lean meat for bad weeks."],
];

const shelfFill = (n, color) => Array.from({ length: n }, () => `<span class="box" style="background:${color}"></span>`).join("");

const pin03 = page("", "EXECUTION SYSTEMS", `
  <div class="head" style="font-size:116px">THE FAT-LOSS</div>
  <div class="head gold" style="font-size:116px">FRIDGE SETUP</div>
  <p style="font-size:24px;line-height:1.4;margin-top:20px;max-width:860px">
    Make the plan the easiest thing to grab. Organize by how often you should eat it.</p>
  <div class="grid">
    <div class="fridge">
      <div class="cab">
        <div class="shelf">${shelfFill(3, "#7a2a33")}</div>
        <div class="shelf">${shelfFill(3, C.gold)}</div>
        <div class="shelf">${shelfFill(3, "#c9c2b2")}</div>
        <div class="drawers"><span></span><span></span></div>
        <div class="door"></div>
      </div>
      <div class="frz"><span></span><span></span><span></span></div>
    </div>
    <div class="zones">
      ${zones.map((z, i) => `
      <div class="zone">
        <div class="zl"><span class="dot">${i + 1}</span>${z[0]}</div>
        <div class="head zt">${z[1]}</div>
        <div class="zd">${z[2]}</div>
      </div>`).join("")}
    </div>
  </div>
`, `
.grid { margin-top: 26px; display: grid; grid-template-columns: 340px 1fr; gap: 40px; flex: 1; }
.fridge { display: flex; flex-direction: column; gap: 10px; }
.cab { position: relative; flex: 1; border: 3px solid ${C.silver}; border-radius: 18px; padding: 20px 64px 20px 18px;
  display: flex; flex-direction: column; justify-content: space-around; background: linear-gradient(#15171b, #0d0e11); }
.shelf { display: flex; gap: 10px; align-items: flex-end; border-bottom: 3px solid ${C.graphite}; padding-bottom: 10px; height: 90px; }
.box { flex: 1; height: 54px; border-radius: 8px; opacity: .9; }
.drawers { display: flex; gap: 10px; height: 110px; }
.drawers span { flex: 1; border: 3px solid ${C.graphite}; border-radius: 10px; background: rgba(110,140,90,.35); }
.door { position: absolute; right: 12px; top: 20px; bottom: 20px; width: 38px; border-left: 3px solid ${C.graphite};
  background: repeating-linear-gradient(transparent 0 70px, ${C.graphite} 70px 74px); }
.frz { height: 130px; border: 3px solid ${C.silver}; border-radius: 18px; display: flex; gap: 10px; padding: 18px; background: #0f1216; }
.frz span { flex: 1; border-radius: 8px; background: rgba(170,176,185,.25); }
.zones { display: flex; flex-direction: column; justify-content: space-between; }
.zone { border-left: 3px solid ${C.gold}; padding: 2px 0 2px 20px; }
.zl { font-weight: 700; font-size: 16px; letter-spacing: 3px; color: ${C.gold}; display: flex; align-items: center; gap: 10px; }
.dot { display: inline-grid; place-items: center; width: 26px; height: 26px; border-radius: 50%; background: ${C.gold}; color: ${C.obsidian}; font-size: 15px; letter-spacing: 0; }
.zt { font-size: 40px; margin-top: 8px; }
.zd { font-size: 19px; color: ${C.silver}; margin-top: 6px; line-height: 1.3; }
`);

// ------------------------------------------------------------ 04 choose your hard

const pin04 = page("", "THE STANDARD", `
  <div style="margin-top:6px">
    <div class="head silver" style="font-size:90px">STARTING OVER</div>
    <div class="head silver" style="font-size:90px">EVERY MONDAY</div>
    <div class="head silver" style="font-size:90px">IS HARD.</div>
    <div class="head" style="font-size:90px;margin-top:36px">SHOWING UP</div>
    <div class="head" style="font-size:90px">ON A TUESDAY</div>
    <div class="head" style="font-size:90px">IS HARD.</div>
    <div class="bar"></div>
    <div class="head gold" style="font-size:190px;line-height:.86">CHOOSE<br>YOUR HARD.</div>
  </div>
  <p style="font-size:26px;line-height:1.45;margin-top:auto;max-width:820px">
    Both cost you something. Only one of them builds anything.</p>
`, `.bar { width: 160px; height: 6px; background: ${C.crimson}; margin: 34px 0 28px; }`);

// ------------------------------------------------------------ 05 protein shake

const shake = [
  ["Skim milk", "1 cup / 240 ml", 8, 83],
  ["Whey protein", "1 scoop / 30 g", 24, 120],
  ["Plain nonfat Greek yogurt", "170 g", 17, 100],
  ["Rolled oats", "40 g", 5, 150],
  ["Banana", "1 medium", 1, 105],
  ["Peanut butter", "1 tbsp / 16 g", 4, 94],
  ["Unsweetened cocoa", "1 tbsp", 1, 12],
];

const pin05 = page("ivory", "EDISON EATS", `
  <div class="head" style="font-size:150px;line-height:.86"><span style="color:#9a7a0e">60 G</span> PROTEIN</div>
  <div class="head" style="font-size:150px;line-height:.86">SHAKE</div>
  <p style="font-size:24px;line-height:1.4;margin-top:22px;max-width:860px">
    A full meal in a glass for busy mornings. Blend with ice for 45 seconds.</p>
  <div class="tbl">
    <div class="tr th"><div>INGREDIENT</div><div>AMOUNT</div><div>PROTEIN</div><div>KCAL</div></div>
    ${shake.map((r) => `<div class="tr"><div class="ing">${r[0]}</div><div class="amt">${r[1]}</div><div class="p head">${r[2]} g</div><div class="k">${r[3]}</div></div>`).join("")}
  </div>
  <div class="tot">
    <div><div class="head big">≈61 G</div><div class="lbl">PROTEIN</div></div>
    <div><div class="head big">≈670</div><div class="lbl">KCAL</div></div>
    <div><div class="head big">≈81 G</div><div class="lbl">CARBS</div></div>
    <div><div class="head big">≈14 G</div><div class="lbl">FAT</div></div>
  </div>
  <p class="note" style="margin-top:auto">Approximate values; brands vary, so check your labels. Cutting? Drop the oats and peanut butter: ≈52 g protein, ≈420 kcal.</p>
`, `
.tbl { margin-top: 20px; }
.tr { display: grid; grid-template-columns: 1fr 200px 120px 90px; align-items: center; padding: 12px 0; border-bottom: 1px solid #d8cfbd; }
.th { font-weight: 700; font-size: 16px; letter-spacing: 3px; color: ${C.graphite}; border-bottom: 2px solid ${C.obsidian}; padding-bottom: 12px; }
.ing { font-size: 25px; font-weight: 700; }
.amt { font-size: 21px; color: #4a4d53; }
.p { font-size: 40px; color: #9a7a0e; text-align: right; }
.k { font-size: 21px; color: #4a4d53; text-align: right; }
.th div:nth-child(3), .th div:nth-child(4) { text-align: right; }
.tot { margin-top: 20px; display: grid; grid-template-columns: repeat(4, 1fr); background: ${C.obsidian}; border-radius: 18px; padding: 18px 10px; text-align: center; }
.big { font-size: 56px; color: ${C.gold}; }
.lbl { font-weight: 700; font-size: 15px; letter-spacing: 3px; color: ${C.silver}; margin-top: 8px; }
`);

// ------------------------------------------------------------ 06 grocery list

const groceries = [
  ["PROTEIN", ["Chicken breast", "Lean ground beef", "Tuna", "Eggs"]],
  ["CARBS", ["Rice", "Potatoes", "Oatmeal", "Cream of wheat"]],
  ["PRODUCE", ["Fruit for snacks", "Vegetables for every plate"]],
];

const pin06 = page("", "MY PROOF", `
  <div class="head" style="font-size:108px">MY FAT-LOSS</div>
  <div class="head gold" style="font-size:108px">GROCERY LIST</div>
  <p style="font-size:24px;line-height:1.4;margin-top:20px;max-width:860px">
    The same 10 foods, most weeks. Fewer decisions means fewer chances to drift.</p>
  <div class="list">
    ${groceries.map((g) => `
    <div class="grp">
      <div class="gh">${g[0]}</div>
      ${g[1].map((x) => `<div class="item"><span class="chk"></span><span class="head">${x}</span></div>`).join("")}
    </div>`).join("")}
  </div>
  <div class="rule2"><span class="head gold">REPEATABLE BEATS PERFECT.</span></div>
`, `
.list { margin: 22px 0 20px; flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.gh { font-weight: 700; font-size: 18px; letter-spacing: 5px; color: ${C.gold}; padding-bottom: 6px; border-bottom: 1px solid ${C.graphite}; margin-bottom: 6px; }
.item { display: flex; align-items: center; gap: 22px; padding: 2px 0; }
.item .head { font-size: 46px; }
.chk { width: 34px; height: 34px; border: 3px solid ${C.gold}; border-radius: 6px; position: relative; flex: none; }
.chk::after { content: ""; position: absolute; left: 9px; top: 2px; width: 9px; height: 18px; border: solid ${C.gold}; border-width: 0 4px 4px 0; transform: rotate(45deg); }
.rule2 { border-top: 2px solid ${C.crimson}; padding-top: 16px; }
.rule2 .head { font-size: 56px; }
`);

const PINS = [
  ["01-testosterone-nutrient-foods", pin01],
  ["02-food-swaps-80-lb", pin02],
  ["03-fat-loss-fridge-setup", pin03],
  ["04-choose-your-hard", pin04],
  ["05-60g-protein-shake", pin05],
  ["06-fat-loss-grocery-list", pin06],
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const pg = await browser.newPage({ viewport: { width: W, height: H } });
  for (const [name, html] of PINS) {
    const tmp = path.join(OUT, `.${name}.html`);
    fs.writeFileSync(tmp, html);
    await pg.goto("file://" + tmp);
    await pg.evaluate(() => document.fonts.ready);
    const overflow = await pg.evaluate(() => {
      const m = document.querySelector("main");
      return m.scrollHeight - m.clientHeight > 10 ? m.scrollHeight - m.clientHeight : 0;
    });
    if (overflow) console.warn(`WARNING: ${name} content overflows the main area by ${overflow}px`);
    await pg.screenshot({ path: path.join(OUT, `${name}.png`) });
    fs.unlinkSync(tmp);
    console.log("wrote", name);
  }
  await browser.close();
})();
