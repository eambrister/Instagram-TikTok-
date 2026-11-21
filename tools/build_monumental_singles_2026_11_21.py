"""Nine single-image posts in the Monumental kit, inspired by reference posts Edison saved (21 Nov 2026).

body-types (AI torsos), repetition-mastery, protein-day, unbreakable-habits, consistency,
a-lot-goes-wrong, bad-day-not-bad-life, hydrating-foods, focus-foods. Claims corrected where the
references overstated them. Logo: Cutthroat Discipline emblem via furniture().

Usage: python3 tools/build_monumental_singles_2026_11_21.py
"""
import math

from PIL import Image, ImageDraw, ImageEnhance

from build_monumental_food_lists import items, place
from build_monumental_singles_2026_11_13 import body_lines, ctext, eyebrow, fit, folder, save
from monumental_type import (BODY, BONE, GOLD, HEAD, INK, LGOLD, NUMERAL, STONE, UTIL, H, W, font, frame,
                             surface, tracked, tracked_width)

CRIMSON = (158, 43, 37)
DIM = (58, 56, 52)


def title(d, eb, bone, gold, y=78, size=110):
    eyebrow(d, y, eb)
    y = ctext(d, y + 46, bone, fit(HEAD, bone, size, 940), BONE) + 20
    return ctext(d, y, gold, fit(HEAD, gold, size, 940), GOLD)


def check(d, cx, cy, r, colour, width=6):
    d.line((cx - r * .5, cy, cx - r * .12, cy + r * .4, cx + r * .55, cy - r * .45), fill=colour, width=width, joint="curve")


def cross(d, cx, cy, r, colour, width=6):
    k = r * .42
    d.line((cx - k, cy - k, cx + k, cy + k), fill=colour, width=width)
    d.line((cx - k, cy + k, cx + k, cy - k), fill=colour, width=width)


def badge(d, cx, cy, good, r=26):
    if good:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD)
        check(d, cx, cy, r, INK, 5)
    else:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=CRIMSON)
        cross(d, cx, cy, r, BONE, 5)


def arrow_down(d, x, y0, y1, colour=BONE):
    d.line((x, y0, x, y1), fill=colour, width=3)
    d.polygon([(x - 10, y1 - 14), (x + 10, y1 - 14), (x, y1 + 2)], fill=colour)


# ---------------------------------------------------------------- 1. body types

def body_types():
    slug = "body-types"
    img = surface(71, light=(0.5, 0.0))
    d = ImageDraw.Draw(img)
    y = title(d, "SAME FRAME  ·  DIFFERENT LEVELS", "BODY TYPES", "TWO DIALS YOU CONTROL", size=96)
    hf = font(UTIL, 18)
    a, b = "LESS MUSCLE", "MORE MUSCLE"
    wa, wb, gap = tracked_width(a, hf, 4), tracked_width(b, hf, 4), 150
    x = (W - wa - wb - gap) / 2
    tracked(d, x, y + 26, a, hf, STONE, 4)
    tracked(d, x + wa + gap, y + 26, b, hf, LGOLD, 4)
    ly = y + 26 + 9
    d.line((x + wa + 24, ly, x + wa + gap - 24, ly), fill=GOLD, width=2)
    d.polygon([(x + wa + gap - 24, ly - 7), (x + wa + gap - 24, ly + 7), (x + wa + gap - 12, ly)], fill=GOLD)
    rows = [("low", "LOW BODY FAT"), ("average", "AVERAGE BODY FAT"), ("higher", "HIGHER BODY FAT")]
    top, rh = y + 70, 262
    for i, (name, label) in enumerate(rows):
        y0 = top + i * rh
        d.line((70, y0, 1010, y0), fill=GOLD, width=1)
        tracked(d, 70, y0 + 14, label, font(UTIL, 18), LGOLD, 4)
        cuts = items(folder(slug) / f"source-images/{name}.png", 3)
        for k, cut in enumerate(cuts):
            cut = cut.crop((0, 0, cut.width, round(cut.height * .7)))
            rgb = ImageEnhance.Brightness(cut.convert("RGB")).enhance(1.25)
            rgb.putalpha(cut.getchannel("A"))
            place(img, rgb, 70 + 940 / 3 * (k + .5), y0 + 40 + 108, 300, 216)
    d.line((70, top + 3 * rh, 1010, top + 3 * rh), fill=GOLD, width=1)
    save(img, slug, "01-body-types")


# ---------------------------------------------------------------- 2. repetition

def repetition():
    slug = "repetition-mastery"
    img = surface(72, light=(0.5, 0.0))
    frame(img)
    d = ImageDraw.Draw(img)
    eyebrow(d, 96, "THE ONLY SHORTCUT")
    f = font(HEAD, 92)
    y = 160
    for i in range(7):
        t = i / 6
        colour = tuple(round(DIM[c] + (BONE[c] - DIM[c]) * t) for c in range(3))
        y = ctext(d, y, "REPETITION", f, colour) + 30
    y = ctext(d, y + 14, "MASTERY.", font(HEAD, 150), GOLD) + 40
    body_lines(d, y, "Same rep. Same meal. Same bedtime. Until it's who you are.", 28, 900, STONE)
    save(img, slug, "01-repetition-mastery")


# ---------------------------------------------------------------- 3. protein day

MEALS = [
    ("BREAKFAST", "EGGS + COTTAGE CHEESE TOAST", "3 eggs, 1 slice wholegrain toast, 100g cottage cheese", "~34G"),
    ("LUNCH", "CHICKEN + QUINOA BOWL", "120g cooked chicken breast, ½ cup quinoa, veg", "~41G"),
    ("SNACK", "GREEK YOGURT + BERRIES", "200g plain non-fat Greek yogurt", "~20G"),
    ("DINNER", "SALMON + BROCCOLI", "150g cooked salmon, broccoli, lemon", "~39G"),
]


def protein_day():
    slug = "protein-day"
    img = surface(73, light=(0.9, 0.05))
    frame(img)
    d = ImageDraw.Draw(img)
    title(d, "EDISON EATS  ·  ONE SIMPLE DAY", "HOW TO HIT", "120G+ PROTEIN", size=112)
    top, rh, x = 380, 165, 120
    d.line((x, top + 10, x, top + 3 * rh + 40), fill=GOLD, width=2)
    for i, (when, meal, detail, grams) in enumerate(MEALS):
        y0 = top + i * rh
        d.ellipse((x - 9, y0 + 1, x + 9, y0 + 19), fill=GOLD)
        tracked(d, x + 40, y0, when, font(UTIL, 20), LGOLD, 4)
        mf = fit(HEAD, meal, 48, 640)
        d.text((x + 40, y0 + 38 - mf.getbbox("H")[1]), meal, font=mf, fill=BONE)
        df = fit(BODY, detail, 24, 640)
        d.text((x + 40, y0 + 104), detail, font=df, fill=STONE)
        nf = font(NUMERAL, 64)
        d.text((990 - nf.getlength(grams), y0 + 30 - nf.getbbox("0")[1]), grams, font=nf, fill=GOLD)
    y = top + 4 * rh + 8
    d.line((92, y, 988, y), fill=GOLD, width=1)
    tf = font(HEAD, 60)
    d.text((120, y + 26 - tf.getbbox("H")[1]), "TOTAL", font=tf, fill=BONE)
    nf = font(NUMERAL, 72)
    d.text((990 - nf.getlength("~134G"), y + 20 - nf.getbbox("0")[1]), "~134G", font=nf, fill=GOLD)
    sf = font(BODY, 20)
    note = "Approximate values. Check your labels and portions."
    d.text(((W - sf.getlength(note)) / 2, y + 112), note, font=sf, fill=STONE)
    save(img, slug, "01-protein-day")


# ---------------------------------------------------------------- 4. unbreakable habits

HABITS = ["7–9 HOURS SLEEP", "LESS ADDED SUGAR", "LITTLE TO NO ALCOHOL", "WATER ALL DAY", "STRENGTH TRAINING",
          "PROTEIN EVERY MEAL", "MORNING DAYLIGHT", "8–10K STEPS", "LESS DOOMSCROLLING", "A REAL PURPOSE"]


def habits():
    slug = "unbreakable-habits"
    img = surface(74, light=(0.1, 0.05))
    frame(img)
    d = ImageDraw.Draw(img)
    title(d, "DAILY HABITS THAT BUILD YOU", "HOW TO BE", "UNBREAKABLE", size=120)
    top, rh = 400, 132
    for i, h in enumerate(HABITS):
        col, row = divmod(i, 5)
        x, y0 = 92 + col * 470, top + row * rh
        d.line((x, y0, x + 430, y0), fill=GOLD, width=1)
        nf = font(NUMERAL, 52)
        num = f"{i + 1:02d}"
        d.text((x, y0 + 28 - nf.getbbox("0")[1]), num, font=nf, fill=GOLD)
        hf = fit(HEAD, h, 40, 320)
        d.text((x + 100, y0 + 40 - hf.getbbox("H")[1]), h, font=hf, fill=BONE)
    y = top + 5 * rh + 26
    ctext(d, y, "NOT SUPERHUMAN. JUST CONSISTENT.", fit(HEAD, "NOT SUPERHUMAN. JUST CONSISTENT.", 52, 900), GOLD)
    save(img, slug, "01-unbreakable-habits")


# ---------------------------------------------------------------- 5. consistency

def consistency():
    slug = "consistency"
    img = surface(75, light=(0.5, 0.0))
    frame(img)
    d = ImageDraw.Draw(img)
    eyebrow(d, 110, "WHAT CONSISTENCY ACTUALLY MEANS")
    y = ctext(d, 170, "IT DOESN'T MEAN", font(HEAD, 84), BONE) + 18
    ctext(d, y, "NEVER MESSING UP.", font(HEAD, 84), STONE)
    row1 = [1, 1, 1, 0]
    gap = 120
    x0 = W / 2 - gap * (len(row1) - 1) / 2
    arrow_down(d, x0 + 3 * gap, 395, 445)
    for k, g in enumerate(row1):
        badge(d, x0 + k * gap, 490, g, 34)
    y = ctext(d, 640, "IT MEANS", font(HEAD, 84), BONE) + 18
    ctext(d, y, "NEVER GIVING UP.", font(HEAD, 84), GOLD)
    row2 = [1, 1, 1, 0, 1, 1, 0, 1, 1]
    gap = 100
    x0 = W / 2 - gap * (len(row2) - 1) / 2
    arrow_down(d, x0 + 4 * gap, 865, 915)
    for k, g in enumerate(row2):
        badge(d, x0 + k * gap, 960, g, 32)
    body_lines(d, 1060, "Miss a day. Never miss two.", 30, 900, BONE)
    save(img, slug, "01-consistency")


# ---------------------------------------------------------------- 6. a lot goes wrong

def snake(n=26):
    """Sample a winding path (right, U-turn, left, U-turn, right) at n equal steps."""
    pts = []
    for x in range(-20, 900, 4):
        pts.append((x, 520))
    for a in range(0, 181, 3):
        t = math.radians(a)
        pts.append((900 + 95 * math.sin(t), 615 - 95 * math.cos(t)))
    for x in range(900, 180, -4):
        pts.append((x, 710))
    for a in range(0, 181, 3):
        t = math.radians(a)
        pts.append((180 - 95 * math.sin(t), 805 - 95 * math.cos(t)))
    for x in range(180, W + 20, 4):
        pts.append((x, 900))
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(seg)
    out, acc, j = [], 0.0, 0
    for k in range(n):
        target = total * (k + .6) / (n + .2)
        while acc + seg[j] < target:
            acc += seg[j]
            j += 1
        t = (target - acc) / seg[j]
        out.append((pts[j][0] + t * (pts[j + 1][0] - pts[j][0]), pts[j][1] + t * (pts[j + 1][1] - pts[j][1])))
    return pts, out


def lot_goes_wrong():
    slug = "a-lot-goes-wrong"
    img = surface(76, light=(0.5, 0.0))
    d = ImageDraw.Draw(img)
    ctext(d, 250, "A LOT GOES WRONG", fit(HEAD, "A LOT GOES WRONG", 104, 940), BONE)
    pts, marks = snake()
    d.line(pts, fill=BONE, width=3, joint="curve")
    pattern = [0] * 9 + [0, 1, 0, 1, 1, 0, 1, 0] + [1] * 9
    for (x, y), g in zip(marks, pattern):
        if -10 < x < W + 10:
            badge(d, x, y, g, 26)
    ctext(d, 1010, "BEFORE EVERYTHING GOES RIGHT.", fit(HEAD, "BEFORE EVERYTHING GOES RIGHT.", 76, 940), GOLD)
    save(img, slug, "01-a-lot-goes-wrong")


# ---------------------------------------------------------------- 7. bad day, not a bad life

def bad_day():
    slug = "bad-day-not-bad-life"
    img = surface(77, light=(0.9, 0.05))
    d = ImageDraw.Draw(img)
    eyebrow(d, 96, "ZOOM OUT")
    ctext(d, 142, "ONE BAD DAY ISN'T", font(HEAD, 92), BONE)
    ctext(d, 252, "THE WHOLE STORY.", font(HEAD, 92), GOLD)
    cols, rows, gx, gy, step = 20, 18, 395, 420, 31
    bad = {(1, 4), (2, 8), (2, 14), (3, 16), (4, 6), (5, 13), (6, 18), (7, 1), (8, 7), (9, 17), (10, 6), (10, 19),
           (12, 6), (12, 11), (12, 12), (13, 8), (13, 16), (14, 3), (14, 4), (15, 8), (15, 17), (16, 2), (16, 15)}
    for r in range(rows):
        for c in range(cols):
            x, y = gx + c * step, gy + r * step
            col = CRIMSON if (r, c) in bad else GOLD
            d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=col)
    lx, ly = 170, 700
    d.ellipse((lx - 16, ly - 16, lx + 16, ly + 16), fill=CRIMSON)
    lf = font(HEAD, 40)
    d.text((lx - 100, ly - 70 - lf.getbbox("H")[1]), "A BAD DAY.", font=lf, fill=BONE)
    end_x, base = gx + (cols - 1) * step, gy + (rows - 1) * step + 70
    d.line((lx, ly + 22, lx, base, end_x, base, end_x, base - 52), fill=BONE, width=3)
    d.polygon([(end_x - 10, base - 44), (end_x + 10, base - 44), (end_x, base - 60)], fill=BONE)
    nf = font(HEAD, 40)
    d.text((end_x - nf.getlength("NOT A BAD LIFE.") + 8, base + 24 - nf.getbbox("H")[1]), "NOT A BAD LIFE.", font=nf, fill=GOLD)
    body_lines(d, 1100, "Miss a workout. Eat badly once. Get back on the next one.", 28, 940, STONE)
    save(img, slug, "01-bad-day-not-bad-life")


# ---------------------------------------------------------------- 8. hydrating foods

HYDRATE = [("ICEBERG LETTUCE", 95.6), ("CELERY", 95.4), ("CUCUMBER", 95.2), ("ZUCCHINI", 94.8),
           ("TOMATO", 94.5), ("WATERMELON", 91.4), ("STRAWBERRIES", 91.0), ("ORANGE", 86.8)]


def hydrating():
    slug = "hydrating-foods"
    img = surface(78, light=(0.5, 0.0))
    frame(img)
    d = ImageDraw.Draw(img)
    title(d, "WATER CONTENT PER 100G  ·  RAW", "HYDRATING FOODS", "RANKED", size=112)
    top, rh = 390, 86
    bx0, bx1 = 470, 860
    for i, (name, v) in enumerate(HYDRATE):
        y0 = top + i * rh
        nf = font(NUMERAL, 50)
        d.text((92, y0 + 8 - nf.getbbox("0")[1]), str(i + 1), font=nf, fill=GOLD)
        hf = fit(HEAD, name, 40, 310)
        d.text((150, y0 + 14 - hf.getbbox("H")[1]), name, font=hf, fill=BONE)
        w = (v - 80) / 20 * (bx1 - bx0)
        d.rectangle((bx0, y0 + 14, bx1, y0 + 42), fill=(30, 29, 27))
        d.rectangle((bx0, y0 + 14, bx0 + w, y0 + 42), fill=GOLD if i < 5 else LGOLD)
        vf = font(HEAD, 40)
        val = f"{v:.1f}%"
        d.text((988 - vf.getlength(val), y0 + 14 - vf.getbbox("0")[1]), val, font=vf, fill=BONE)
    y = top + 8 * rh + 20
    body_lines(d, y, "Approximate USDA values. Water-rich foods count toward hydration, but they don't replace drinking water.", 24, 880, STONE)
    save(img, slug, "01-hydrating-foods")


# ---------------------------------------------------------------- 9. focus foods

FOCUS = [("EGGS", "Protein + choline"), ("CHICKEN", "Protein, incl. tyrosine"), ("PUMPKIN SEEDS", "Iron + magnesium"),
         ("OATS", "Slow, steady carbs"), ("ALMONDS", "Healthy fats + vitamin E"), ("DARK CHOCOLATE", "A little caffeine. Small portion.")]


def focus():
    slug = "focus-foods"
    img = surface(79, light=(0.5, 0.0))
    frame(img)
    d = ImageDraw.Draw(img)
    title(d, "PROTEIN  ·  IRON  ·  STEADY ENERGY", "FOODS FOR", "FOCUS", size=120)
    top, rh = 420, 160
    for i, (food, why) in enumerate(FOCUS):
        col, row = i % 2, i // 2
        x, y0 = 92 + col * 470, top + row * rh
        d.line((x, y0, x + 430, y0), fill=GOLD, width=1)
        ff = fit(HEAD, food, 52, 430)
        d.text((x, y0 + 28 - ff.getbbox("H")[1]), food, font=ff, fill=BONE)
        wf = fit(BODY, why, 26, 430)
        d.text((x, y0 + 96), why, font=wf, fill=STONE)
    y = top + 3 * rh + 30
    y = ctext(d, y, "NO FOOD IS A DOPAMINE HACK.", fit(HEAD, "NO FOOD IS A DOPAMINE HACK.", 60, 900), GOLD) + 28
    body_lines(d, y, "Sleep, daylight, training and fewer screens do more for focus than any single food.", 26, 860, BONE)
    save(img, slug, "01-focus-foods")


def main():
    for fn in (repetition, protein_day, habits, consistency, lot_goes_wrong, bad_day, hydrating, focus):
        fn()
    if (folder("body-types") / "source-images/higher.png").exists():
        body_types()


if __name__ == "__main__":
    main()
