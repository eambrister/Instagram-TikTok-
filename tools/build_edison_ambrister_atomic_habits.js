// Build "30 lessons from Atomic Habits": one 1080 x 1440 (3:4) Edison Ambrister
// infographic for Instagram and TikTok. Each lesson is paraphrased from James
// Clear's book and paired with a fitness example. Typographic / vector only.
//
// Usage: node tools/build_edison_ambrister_atomic_habits.js

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "outputs/edison-ambrister-atomic-habits");
const TOKENS = JSON.parse(fs.readFileSync(path.join(ROOT, "brand/tokens.json"), "utf8"));
const C = TOKENS.colors;
const W = 1080;
const H = 1440;
const FOOTER = TOKENS.post.footer;

const fontUrl = (f) => "file://" + path.join(ROOT, "brand/fonts", f);
const LOGO = "file://" + path.join(ROOT, "brand/assets/edison-ambrister/edison-ambrister-horizontal.png");

const LESSONS = [
  ["1% better daily compounds.", "10 push-ups a day is 3,650 a year."],
  ["Systems beat goals.", "Don't chase a number. Build the week."],
  ["You fall to your systems.", "No plan for Friday night? That is the plan."],
  ["Decide who you want to be.", "“I train” beats “I'm trying to.”"],
  ["Every action is a vote.", "Every logged meal counts."],
  ["Cue, craving, response, reward.", "Find what triggers the late-night snack."],
  ["Make it obvious.", "Water on the desk. Fruit on the counter."],
  ["Make it attractive.", "Save your best playlist for the gym."],
  ["Make it easy.", "Lay out gym clothes the night before."],
  ["Make it satisfying.", "Check off the workout the second it's done."],
  ["Plan the time and place.", "“I train at 6 PM at the gym.” Written down."],
  ["Stack it on a current habit.", "After I brush my teeth, I weigh in."],
  ["Environment beats motivation.", "Prep on Sunday so Wednesday is easy."],
  ["Make bad habits invisible.", "Snacks out of sight, or out of the house."],
  ["Pair need with want.", "Podcasts only while walking."],
  ["Join a group where it's normal.", "Train with people who don't skip."],
  ["Cut friction for good habits.", "Pick the gym on your route home."],
  ["Add friction to bad habits.", "Delete the delivery app."],
  ["Start with two minutes.", "Just put your shoes on and start."],
  ["Master showing up first.", "Four straight weeks, then add weight."],
  ["Lock in good choices early.", "Pre-log tomorrow's meals tonight."],
  ["Never miss twice.", "Missed Monday? Tuesday is non-negotiable."],
  ["Track it. Don't break the chain.", "Log food and workouts every day."],
  ["Make skipping cost something.", "Daily check-ins with someone who'll ask."],
  ["Results lag behind effort.", "Two flat weeks on the scale isn't failure."],
  ["Fall in love with boredom.", "Same meals. Same lifts. Keep going."],
  ["Planning isn't doing.", "Reading programs isn't training."],
  ["Reps build habits, not time.", "Count sessions, not days since you started."],
  ["Stay at the edge of ability.", "Add a rep or 5 lb when it feels easy."],
  ["Review your habits often.", "Check your week every Sunday."],
];

const IDEAS = [
  ["1% × 365", "Small gains compound"],
  ["SYSTEMS > GOALS", "Build the process"],
  ["CUE → REWARD", "Cue, craving, response, reward"],
  ["NEVER MISS TWICE", "Get back on the next day"],
];

const item = ([lesson, spin], i) => `
  <div class="item">
    <div class="n head">${i + 1}</div>
    <div><div class="l">${lesson}</div><div class="s">${spin}</div></div>
  </div>`;

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face { font-family: Head; src: url(${fontUrl("BarlowCondensed-ExtraBold.ttf")}); }
@font-face { font-family: Body; src: url(${fontUrl("Montserrat-Medium.ttf")}); font-weight: 500; }
@font-face { font-family: Body; src: url(${fontUrl("Montserrat-Bold.ttf")}); font-weight: 700; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: ${W}px; height: ${H}px; overflow: hidden; }
body { font-family: Body, sans-serif; font-weight: 500; color: ${C.white}; position: relative;
  background: radial-gradient(120% 60% at 85% 0%, #1b1a16 0%, ${C.obsidian} 60%); }
.head { font-family: Head, sans-serif; text-transform: uppercase; line-height: .9; letter-spacing: .5px; }
header { position: absolute; top: 40px; left: 50px; right: 50px; height: 80px; display: flex; align-items: center; justify-content: space-between; }
header img { width: 210px; }
.series { font-weight: 700; font-size: 19px; letter-spacing: 4px; color: ${C.gold}; }
main { position: absolute; top: 140px; left: 50px; right: 50px; bottom: 96px; display: flex; flex-direction: column; }
main > * { flex-shrink: 0; }
.title { font-size: 96px; }
.top { display: grid; grid-template-columns: 300px 1fr; gap: 20px; margin-top: 22px; height: 170px; }
.book { border: 2px solid ${C.gold}; border-radius: 16px; background: linear-gradient(160deg, #1d1c18, #0b0c0e);
  display: flex; flex-direction: column; justify-content: center; padding: 0 26px; position: relative; overflow: hidden; }
.book::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 10px; background: ${C.gold}; }
.book .k { font-weight: 700; font-size: 14px; letter-spacing: 4px; color: ${C.silver}; }
.book .bt { font-size: 56px; color: ${C.white}; margin-top: 8px; }
.book .ba { font-weight: 700; font-size: 17px; letter-spacing: 3px; color: ${C.gold}; margin-top: 10px; }
.quote { border: 1px solid ${C.graphite}; border-radius: 16px; background: rgba(41,45,52,.35); padding: 22px 28px;
  display: flex; flex-direction: column; justify-content: center; }
.quote .q { font-size: 25px; line-height: 1.35; font-weight: 700; }
.quote .q b { color: ${C.gold}; }
.quote .a { font-size: 16px; color: ${C.silver}; margin-top: 10px; letter-spacing: 1px; }
.list { flex: 1; margin: 22px 0 18px; display: grid; grid-template-columns: 1fr 1fr; grid-auto-flow: column;
  grid-template-rows: repeat(15, 1fr); column-gap: 30px; border-top: 1px solid ${C.graphite}; padding-top: 10px; }
.item { display: grid; grid-template-columns: 42px 1fr; align-items: center; border-bottom: 1px solid rgba(41,45,52,.7); }
.n { font-size: 30px; color: ${C.gold}; }
.l { font-weight: 700; font-size: 20px; line-height: 1.15; white-space: nowrap; }
.s { font-size: 16px; color: ${C.silver}; line-height: 1.2; margin-top: 2px; white-space: nowrap; }
.ideas { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; height: 92px; }
.idea { border: 1px solid ${C.gold}; border-radius: 12px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
.idea .ih { font-size: 30px; white-space: nowrap; color: ${C.gold}; }
.idea .is { font-size: 13px; color: ${C.silver}; margin-top: 6px; }
footer { position: absolute; left: 50px; right: 50px; bottom: 38px; text-align: center; }
footer .rule { height: 1px; background: ${C.silver}; opacity: .5; margin-bottom: 16px; }
footer .txt { font-weight: 700; font-size: 17px; letter-spacing: 3px; color: ${C.silver}; }
</style></head><body>
<header><img src="${LOGO}" alt=""><div class="series">EXECUTION SYSTEMS</div></header>
<main>
  <div class="head title">30 LESSONS FROM<br><span style="color:${C.gold}">ATOMIC HABITS</span></div>
  <div class="top">
    <div class="book"><div class="k">THE BOOK</div><div class="head bt">ATOMIC HABITS</div><div class="ba">JAMES CLEAR</div></div>
    <div class="quote">
      <div class="q">“You do not rise to the level of your goals. You <b>fall to the level of your systems.</b>”</div>
      <div class="a">JAMES CLEAR, ATOMIC HABITS</div>
    </div>
  </div>
  <div class="list">${LESSONS.map(item).join("")}</div>
  <div class="ideas">${IDEAS.map(([h, s]) => `<div class="idea"><div class="head ih">${h}</div><div class="is">${s}</div></div>`).join("")}</div>
</main>
<footer><div class="rule"></div><div class="txt">${FOOTER}</div></footer>
</body></html>`;

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const pg = await browser.newPage({ viewport: { width: W, height: H } });
  const tmp = path.join(OUT, ".atomic-habits.html");
  fs.writeFileSync(tmp, html);
  await pg.goto("file://" + tmp);
  await pg.evaluate(() => document.fonts.ready);
  const problems = await pg.evaluate(() => {
    const out = [];
    const m = document.querySelector("main");
    if (m.scrollHeight - m.clientHeight > 10) out.push(`main overflows by ${m.scrollHeight - m.clientHeight}px`);
    document.querySelectorAll(".item").forEach((el, i) => {
      const box = el.getBoundingClientRect();
      el.querySelectorAll(".l, .s").forEach((t) => {
        if (t.getBoundingClientRect().right > box.right + 1) out.push(`lesson ${i + 1} text runs past its column`);
      });
    });
    return out;
  });
  problems.forEach((p) => console.warn("WARNING:", p));
  await pg.screenshot({ path: path.join(OUT, "atomic-habits-30-lessons.png") });
  fs.unlinkSync(tmp);
  await browser.close();
  console.log("wrote atomic-habits-30-lessons.png");
})();
