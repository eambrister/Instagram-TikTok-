"""Six single-image posts in the Monumental kit, recreated from reference posts Edison saved.

Day one / one day, push-up mistakes, muscles ranked, face fat loss, sleep 7+ vs 4 hours,
workout fuel. Scenes are original AI images (ElevenLabs); claims are corrected where the
references overstated them. Logo: Cutthroat Discipline emblem via furniture().

Usage: python3 tools/build_monumental_singles_2026_11_13.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from build_monumental_food_lists import items, place
from monumental_type import (BODY, BONE, GOLD, HEAD, INK, LGOLD, NUMERAL, STONE, UTIL, H, W, font, frame,
                             furniture, surface, tracked, tracked_width, wrap)

ROOT = Path(__file__).resolve().parents[1]
OUTS = ROOT / "outputs"


def folder(slug):
    out = OUTS / f"edison-ambrister-{slug}"
    (out / "jpg").mkdir(parents=True, exist_ok=True)
    return out


def save(img, slug, name):
    out = folder(slug)
    furniture(img, 1, 1)
    img.save(out / f"{name}.png", optimize=True)
    img.save(out / "jpg" / f"{name}.jpg", quality=93)
    print(slug)


def ctext(d, y, text, f, fill, cx=W / 2):
    """Draw text centred on cx with its cap top at y; return the cap bottom."""
    cap = f.getbbox("H")
    d.text((cx - f.getlength(text) / 2, y - cap[1]), text, font=f, fill=fill)
    return y + cap[3] - cap[1]


def fit(path, text, size, width):
    f = font(path, size)
    while f.getlength(text) > width:
        f = font(path, f.size - 2)
    return f


def eyebrow(d, y, text, colour=GOLD, size=22, cx=W / 2):
    f = font(UTIL, size)
    tracked(d, cx - tracked_width(text, f, 4) / 2, y, text, f, colour, 4)


def outlined(d, text, cx, cy, f, fill):
    b = f.getbbox(text)
    x, y = cx - f.getlength(text) / 2, cy - (b[1] + b[3]) / 2
    for dx in range(-4, 5, 2):
        for dy in range(-4, 5, 2):
            d.text((x + dx, y + dy), text, font=f, fill=INK)
    d.text((x, y), text, font=f, fill=fill)


def faded(im, edge=80, sides=(True, True, False, False)):
    """Alpha mask that fades the top/bottom/left/right edges of im into the background."""
    m = np.ones((im.height, im.width), dtype=np.float32)
    ramp = np.linspace(0, 1, edge, dtype=np.float32)
    top, bottom, left, right = sides
    if top:
        m[:edge] *= ramp[:, None]
    if bottom:
        m[-edge:] *= ramp[::-1, None]
    if left:
        m[:, :edge] *= ramp[None, :]
    if right:
        m[:, -edge:] *= ramp[None, ::-1]
    return Image.fromarray((m * 255).astype("uint8"))


def cutout(path, pad=10):
    """Crop a subject on black to its bounds and matte it by luminance."""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im, dtype=np.float32).mean(axis=2)
    ys, xs = np.where(a > 30)
    im = im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), min(im.width, xs.max() + pad), min(im.height, ys.max() + pad)))
    lum = np.asarray(im, dtype=np.float32).mean(axis=2)
    im.putalpha(Image.fromarray((np.clip((lum - 14) / 26, 0, 1) * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(1.5)))
    return im


def body_lines(d, y, text, size, width, fill=BONE, lead=1.4, cx=W / 2):
    f = font(BODY, size)
    for line in wrap(f, text, width):
        d.text((cx - f.getlength(line) / 2, y), line, font=f, fill=fill)
        y += round(size * lead)
    return y


# ------------------------------------------------------------------ 1. day one / one day

def day_one():
    slug = "day-one"
    src = Image.open(folder(slug) / "source-images/scene.png").convert("RGB").crop((100, 0, 1150, 720))
    s = W / src.width
    src = src.resize((W, round(src.height * s)), Image.LANCZOS)
    img = Image.new("RGB", (W, H), INK)
    top = 110
    img.paste(src, (0, top), faded(src, 90, (True, True, False, False)))
    d = ImageDraw.Draw(img)
    outlined(d, "DAY 1.", 290, top + 560, font(HEAD, 76), BONE)
    outlined(d, "ONE DAY.", 812, top + 300, font(HEAD, 76), GOLD)
    y = top + src.height + 40
    y = ctext(d, y, "SAME PERSON.", font(HEAD, 92), BONE) + 22
    y = ctext(d, y, "DIFFERENT DECISIONS.", fit(HEAD, "DIFFERENT DECISIONS.", 92, 940), GOLD) + 36
    body_lines(d, y, "Day one or one day. You decide.", 32, 900)
    save(img, slug, "01-day-one")


# ------------------------------------------------------------------ 2. push-up mistakes

def push_up_mistakes():
    slug = "push-up-mistakes"
    img = surface(21, light=(0.5, 0.0))
    frame(img)
    d = ImageDraw.Draw(img)
    eyebrow(d, 78, "EDISON TRAINS  ·  CALISTHENICS")
    ctext(d, 122, "PUSH-UP MISTAKES", fit(HEAD, "PUSH-UP MISTAKES", 116, 940), BONE)
    panels = [
        ("wrong", "WRONG", STONE, "Hips sag  ·  Elbows flared to 90°  ·  Head cranked up", 285),
        ("correct", "CORRECT", GOLD, "Straight line head to heels  ·  Elbows about 45°  ·  Neck neutral", 680),
    ]
    for name, tag, colour, cues, top in panels:
        tf = font(UTIL, 26)
        tracked(d, 92, top, tag, tf, colour, 5)
        mx = 92 + tracked_width(tag, tf, 5) + 22
        if name == "wrong":
            d.line((mx, top, mx + 22, top + 22), fill=colour, width=4)
            d.line((mx, top + 22, mx + 22, top), fill=colour, width=4)
        else:
            d.line((mx, top + 12, mx + 8, top + 22, mx + 26, top - 2), fill=colour, width=4, joint="curve")
        d.line((92, top + 44, 988, top + 44), fill=colour, width=1)
        im = cutout(folder(slug) / f"source-images/{name}.png")
        place(img, im, W / 2, top + 60 + 125, 900, 250)
        cf = fit(BODY, cues, 27, 900)
        ctext(d, top + 334, cues, cf, BONE if name == "correct" else STONE)
    ctext(d, 1095, "FORM > REPS", font(HEAD, 64), GOLD)
    save(img, slug, "01-push-up-mistakes")


# ------------------------------------------------------------------ 3. muscles ranked

TIERS = [
    ("I", "GROW EASIEST", "GLUTES  ·  TRAPS  ·  QUADS"),
    ("II", "STEADY WITH WORK", "CHEST  ·  BICEPS  ·  TRICEPS  ·  LATS"),
    ("III", "NEED FOCUSED VOLUME", "SIDE DELTS  ·  REAR DELTS  ·  HAMSTRINGS"),
    ("IV", "MOST STUBBORN", "CALVES  ·  FOREARMS"),
]


def muscles_ranked():
    slug = "muscles-ranked"
    img = surface(31, light=(0.9, 0.05))
    frame(img)
    d = ImageDraw.Draw(img)
    eyebrow(d, 92, "FOR MOST PEOPLE  ·  GENETICS VARY")
    y = ctext(d, 140, "MUSCLES RANKED", font(HEAD, 120), BONE) + 22
    ctext(d, y, "BY HOW STUBBORN THEY ARE", fit(HEAD, "BY HOW STUBBORN THEY ARE", 70, 900), GOLD)
    y = 400
    for num, tier, muscles in TIERS:
        d.line((92, y, 988, y), fill=GOLD, width=1)
        nf = font(NUMERAL, 84)
        d.text((92, y + 30 - nf.getbbox("I")[1]), num, font=nf, fill=GOLD)
        tf = font(UTIL, 20)
        tracked(d, 250, y + 30, tier, tf, LGOLD, 4)
        mf = fit(HEAD, muscles, 58, 740)
        d.text((250, y + 72 - mf.getbbox("H")[1]), muscles, font=mf, fill=BONE)
        y += 155
    d.line((92, y, 988, y), fill=GOLD, width=1)
    y += 40
    y = ctext(d, y, "ABS? BUILT BY TRAINING. SHOWN BY BODY FAT.", fit(HEAD, "ABS? BUILT BY TRAINING. SHOWN BY BODY FAT.", 46, 900), GOLD) + 26
    body_lines(d, y, "Stubborn just means more weekly sets, more patience.", 28, 880, STONE)
    save(img, slug, "01-muscles-ranked")


# ------------------------------------------------------------------ 4. face fat loss

def face_fat_loss():
    slug = "face-fat-loss"
    img = surface(41, light=(0.5, 0.0))
    d = ImageDraw.Draw(img)
    eyebrow(d, 74, "EDISON EXPLAINS")
    y = ctext(d, 116, "HOW FAT LOSS", font(HEAD, 104), BONE) + 18
    ctext(d, y, "CHANGES YOUR FACE", fit(HEAD, "CHANGES YOUR FACE", 104, 940), GOLD)
    src = Image.open(folder(slug) / "source-images/faces.png").convert("RGB")
    src = src.resize((W, round(src.height * W / src.width)), Image.LANCZOS)
    top = 330
    img.paste(src, (0, top), faded(src, 70, (True, True, False, False)))
    d = ImageDraw.Draw(img)
    lf = font(UTIL, 22)
    for text, cx, colour in (("HIGHER BODY FAT", W / 4, STONE), ("LOWER BODY FAT", 3 * W / 4, GOLD)):
        tw = tracked_width(text, lf, 4)
        d.rectangle((cx - tw / 2 - 16, top + 20, cx + tw / 2 + 16, top + 62), fill=INK)
        tracked(d, cx - tw / 2, top + 30, text, lf, colour, 4)
    y = top + src.height + 34
    y = ctext(d, y, "YOU CAN'T SPOT-REDUCE YOUR FACE.", fit(HEAD, "YOU CAN'T SPOT-REDUCE YOUR FACE.", 64, 940), BONE) + 28
    y = body_lines(d, y, "Your face leans out when your whole body does: a calorie deficit, enough protein, "
                         "strength training and sleep. Your bones don't change. They just show more.", 28, 900)
    save(img, slug, "01-face-fat-loss")


# ------------------------------------------------------------------ 5. sleep

GOOD = ["Better recovery between sessions", "Steadier hunger and cravings", "Sharper focus in training",
        "Better mood", "Easier to stick to the plan"]
BAD = ["Slower recovery", "More hunger, more cravings", "Foggy focus, weaker sessions", "Shorter fuse",
       "Harder to stick to the plan"]


def sleep():
    slug = "sleep-7-vs-4"
    img = surface(51, light=(0.5, 0.0))
    d = ImageDraw.Draw(img)
    y = ctext(d, 76, "SLEEP MORE.", font(HEAD, 104), BONE) + 18
    ctext(d, y, "RECOVER BETTER.", font(HEAD, 104), GOLD)
    src = Image.open(folder(slug) / "source-images/sleep.png").convert("RGB").crop((60, 0, 780, 720))
    rested = src.resize((470, 470), Image.LANCZOS)
    tired = ImageEnhance.Brightness(ImageEnhance.Color(rested).enhance(0.25)).enhance(0.62)
    cols = ((40, "7–9 HOURS", GOLD, rested, GOOD, BONE), (570, "4 HOURS", STONE, tired, BAD, STONE))
    for x, head, colour, im, lines, txt in cols:
        cx = x + 235
        hf = font(HEAD, 54)
        ctext(d, 300, head, hf, colour, cx)
        img.paste(im, (x, 372), faded(im, 40, (True, True, True, True)))
        d = ImageDraw.Draw(img)
        d.line((x + 20, 862, x + 450, 862), fill=colour, width=1)
        yy = 884
        for line in lines:
            f = fit(BODY, line, 24, 440)
            d.text((cx - f.getlength(line) / 2, yy), line, font=f, fill=txt)
            yy += 44
    ctext(d, 1124, "ADULTS NEED 7+ HOURS. PROTECT IT LIKE A WORKOUT.",
          fit(UTIL, "ADULTS NEED 7+ HOURS. PROTECT IT LIKE A WORKOUT.", 24, 900), LGOLD)
    save(img, slug, "01-sleep-7-vs-4")


# ------------------------------------------------------------------ 6. workout fuel

ROWS = [
    ("BEFORE", "1–2 HRS OUT", "before", [("BANANA", "Quick carbs"), ("OATS", "Steady carbs"),
                                         ("GREEK YOGURT", "Easy protein"), ("HONEY", "Fast fuel")]),
    ("DURING", "60+ MIN ONLY", "during", [("WATER", "Hydration"), ("DATES", "Quick carbs"), ("BANANA", "Easy carbs")]),
    ("AFTER", "WITHIN A FEW HRS", "after", [("SALMON", "Protein + omega-3"), ("EGGS", "Complete protein"),
                                            ("WHITE RICE", "Refills glycogen"), ("SWEET POTATO", "Carbs + potassium")]),
]


def workout_fuel():
    slug = "workout-fuel"
    img = surface(61, light=(0.85, 0.05))
    d = ImageDraw.Draw(img)
    eyebrow(d, 66, "EDISON EATS")
    y = ctext(d, 106, "WHAT TO EAT", font(HEAD, 92), BONE) + 16
    ctext(d, y, "AROUND TRAINING", font(HEAD, 92), GOLD)
    top = 310
    rh = 262
    for i, (label, note, name, foods) in enumerate(ROWS):
        y0 = top + i * rh
        d.line((70, y0, 1010, y0), fill=GOLD, width=1)
        lf = font(HEAD, 54)
        d.text((70, y0 + 34 - lf.getbbox("H")[1]), label, font=lf, fill=BONE)
        nf = font(UTIL, 15)
        tracked(d, 70, y0 + 108, note, nf, LGOLD, 2)
        cuts = items(folder(slug) / f"source-images/{name}.png", len(foods))
        span, x0 = 760, 250
        step = span / 4
        for k, ((food, why), cut) in enumerate(zip(foods, cuts)):
            cx = x0 + step * (k + 0.5) if len(foods) == 4 else x0 + span / 3 * (k + 0.5)
            place(img, cut, cx, y0 + 92, step - 24, 140)
            ff = fit(HEAD, food, 30, step - 8)
            ctext(d, y0 + 178, food, ff, BONE, cx)
            wf = fit(BODY, why, 19, step - 8)
            ctext(d, y0 + 218, why, wf, STONE, cx)
    d.line((70, top + 3 * rh, 1010, top + 3 * rh), fill=GOLD, width=1)
    ctext(d, top + 3 * rh + 30, "DAILY PROTEIN FIRST. TIMING IS THE BONUS.",
          fit(UTIL, "DAILY PROTEIN FIRST. TIMING IS THE BONUS.", 24, 900), LGOLD)
    save(img, slug, "01-workout-fuel")


def main():
    for fn in (day_one, push_up_mistakes, muscles_ranked, face_fat_loss, sleep, workout_fuel):
        fn()


if __name__ == "__main__":
    main()
