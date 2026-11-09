"""Build "Back training, explained": muscle map, frequency, exercises, load. Monumental kit.

Format reference: a four-slide back-training infographic Edison saved. Copy and layout
are Edison's own; the muscle map is an AI illustration labelled by hand.

Usage: python3 tools/build_monumental_back_training.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from monumental_type import (BODY, BONE, GOLD, HEAD, INK, LGOLD, STONE, UTIL, H, W, font, frame, furniture,
                             surface, tracked, tracked_width, wrap)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/edison-ambrister-back-training"
SRC = OUT / "source-images"
CARD = (24, 24, 22)
RULE = (70, 62, 50)

# (label, point x, point y, label x, label y) on the 1080x1350 slide, placed on the chosen image.
MAP_LABELS = [
    ("Trapezius", 540, 540, 860, 350),
    ("Rear deltoid", 300, 635, 150, 790),
    ("Latissimus dorsi", 390, 800, 150, 900),
    ("Erector spinae", 500, 880, 150, 1010),
    ("Rhomboids", 640, 690, 870, 790),
    ("Teres major", 722, 705, 870, 880),
]


def header(d, title, sub, y=70):
    f = font(HEAD, 104)
    while f.getlength(title) > 960:
        f = font(HEAD, f.size - 4)
    cap = f.getbbox("H")
    d.text(((W - f.getlength(title)) / 2, y - cap[1]), title, font=f, fill=BONE)
    y += cap[3] - cap[1] + 26
    sf = font(BODY, 30)
    d.text(((W - sf.getlength(sub)) / 2, y), sub, font=sf, fill=STONE)
    y += 48
    d.line((W / 2 - 60, y, W / 2 + 60, y), fill=GOLD, width=2)
    return y + 30


def pill(d, text, px, py, lx, ly):
    f = font(UTIL, 25)
    tw = tracked_width(text, f, 1)
    d.line((px, py, lx, ly), fill=LGOLD, width=3)
    d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=LGOLD, outline=INK, width=2)
    tx = lx - tw - 16 if lx < px else lx + 16
    tx = max(40, min(W - 40 - tw, tx))
    b = f.getbbox(text)
    d.rounded_rectangle((tx - 14, ly - 25, tx + tw + 14, ly + 25), radius=25, fill=(8, 9, 9), outline=GOLD, width=1)
    tracked(d, tx, ly - (b[1] + b[3]) / 2, text, f, BONE, 1)


def map_slide():
    img = surface(1, light=(0.5, 0.0))
    d = ImageDraw.Draw(img)
    y = header(d, "BACK MUSCLE MAP", "It isn't just lats. Train the whole back.")
    im = Image.open(SRC / "back-map.png").convert("RGB")
    a = np.asarray(im, dtype=np.float32)
    ys, xs = np.where(a.mean(axis=2) > 40)
    im = im.crop((xs.min(), ys.min(), xs.max(), ys.max()))
    top, bottom = y + 10, 1200
    scale = min(980 / im.width, (bottom - top) / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    lum = np.asarray(im, dtype=np.float32).mean(axis=2)
    m = np.clip((lum - 30) / 30, 0, 1)
    fade = np.ones(im.height, dtype=np.float32)
    fade[:60] = np.linspace(0, 1, 60)
    fade[-120:] = np.linspace(1, 0, 120)
    mask = Image.fromarray((m * fade[:, None] * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(2))
    img.paste(im, ((W - im.width) // 2, top + (bottom - top - im.height) // 2), mask)
    for lab in MAP_LABELS:
        pill(d, *lab)
    return img


def card(d, box, title, lines, accent=GOLD):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=18, fill=CARD, outline=RULE, width=1)
    tf = font(HEAD, 46)
    d.text((x0 + 26, y0 + 22 - tf.getbbox("H")[1]), title, font=tf, fill=accent)
    y = y0 + 22 + tf.getbbox("H")[3] - tf.getbbox("H")[1] + 20
    bf = font(BODY, 27)
    for line in lines:
        for w in wrap(bf, line, x1 - x0 - 52):
            d.text((x0 + 26, y), w, font=bf, fill=BONE)
            y += 37
        y += 8


def frequency_slide():
    img = surface(2, light=(0.85, 0.05))
    d = ImageDraw.Draw(img)
    y = header(d, "HOW OFTEN TO TRAIN BACK", "Weekly sessions that hit the back hard.")
    cols = [("BEGINNER", "1–2× A WEEK", ["Learn the form.", "Basic pulls and rows.", "Keep volume low."]),
            ("INTERMEDIATE", "2× A WEEK", ["Best for most people.", "One width day, one thickness day."]),
            ("ADVANCED", "2–3× A WEEK", ["Only if you're recovering.", "Spread sets across the week."])]
    w = (920 - 2 * 20) / 3
    for i, (t, freq, lines) in enumerate(cols):
        x0 = 80 + i * (w + 20)
        d.rounded_rectangle((x0, y, x0 + w, y + 420), radius=18, fill=CARD, outline=RULE, width=1)
        tf = font(UTIL, 22)
        tracked(d, x0 + (w - tracked_width(t, tf, 3)) / 2, y + 26, t, tf, STONE, 3)
        ff = font(HEAD, 54)
        while ff.getlength(freq) > w - 30:
            ff = font(HEAD, ff.size - 2)
        d.text((x0 + (w - ff.getlength(freq)) / 2, y + 70), freq, font=ff, fill=GOLD)
        bf = font(BODY, 25)
        ly = y + 170
        for line in lines:
            for ln in wrap(bf, line, w - 40):
                d.text((x0 + 20, ly), ln, font=bf, fill=BONE)
                ly += 34
            ly += 12
    y += 450
    card(d, (80, y, 530, y + 300), "WIDTH DAY", ["Pull-ups, lat pulldowns, straight-arm pulldowns."])
    card(d, (550, y, 1000, y + 300), "THICKNESS DAY", ["Rows, rear delts, shrugs, back extensions."])
    y += 330
    nf = font(BODY, 30)
    for ln in wrap(nf, "Train it again when soreness is mostly gone and your lifts are back to normal.", 900):
        d.text(((W - nf.getlength(ln)) / 2, y), ln, font=nf, fill=BONE)
        y += 42
    return img


def exercises_slide():
    img = surface(3, light=(0.1, 0.05))
    d = ImageDraw.Draw(img)
    y = header(d, "MUSCLE + BEST EXERCISES", "Match each muscle to the movement that trains it.")
    rows = [("TRAPS", "Shrugs · Deadlifts"),
            ("REAR DELTS", "Reverse flys · Face pulls"),
            ("RHOMBOIDS", "Bent-over rows · Seated cable rows"),
            ("LATS", "Pull-ups · Lat pulldowns"),
            ("TERES MAJOR", "Pulldowns · One-arm DB rows"),
            ("ERECTORS", "Back extensions · Romanian deadlifts")]
    nf, ef = font(HEAD, 50), font(BODY, 30)
    row_h = 132
    for i, (m, ex) in enumerate(rows):
        ry = y + i * row_h
        d.line((80, ry, 1000, ry), fill=RULE, width=1)
        cap = nf.getbbox("H")
        d.text((80, ry + (row_h - (cap[3] - cap[1])) / 2 - cap[1]), m, font=nf, fill=GOLD)
        eb = ef.getbbox("Hg")
        d.text((470, ry + (row_h - (eb[3] - eb[1])) / 2 - eb[1]), ex, font=ef, fill=BONE)
    d.line((80, y + len(rows) * row_h, 1000, y + len(rows) * row_h), fill=RULE, width=1)
    y += len(rows) * row_h + 34
    t = "Pulls and pulldowns build width. Rows build thickness."
    d.text(((W - ef.getlength(t)) / 2, y), t, font=ef, fill=STONE)
    return img


def load_slide():
    img = surface(4, light=(0.9, 0.05))
    d = ImageDraw.Draw(img)
    y = header(d, "HOW HEAVY SHOULD YOU LIFT?", "Pick the weight by reps and effort, not ego.")
    cols = [("LIGHT", "15–20", "Warm-ups, learning form."),
            ("MODERATE", "10–15", "Most accessory work."),
            ("HEAVY", "6–10", "Rows, pulldowns, main lifts."),
            ("VERY HEAVY", "3–6", "Experienced lifters, big lifts only.")]
    w = (920 - 3 * 16) / 4
    for i, (t, reps, use) in enumerate(cols):
        x0 = 80 + i * (w + 16)
        d.rounded_rectangle((x0, y, x0 + w, y + 470), radius=18, fill=CARD, outline=RULE, width=1)
        tf = font(UTIL, 20)
        while tracked_width(t, tf, 2) > w - 20:
            tf = font(UTIL, tf.size - 1)
        tracked(d, x0 + (w - tracked_width(t, tf, 2)) / 2, y + 28, t, tf, STONE, 2)
        rf = font(HEAD, 84)
        while rf.getlength(reps) > w - 24:
            rf = font(HEAD, rf.size - 4)
        d.text((x0 + (w - rf.getlength(reps)) / 2, y + 74), reps, font=rf, fill=GOLD)
        lf = font(UTIL, 20)
        tracked(d, x0 + (w - tracked_width("REPS", lf, 3)) / 2, y + 190, "REPS", lf, STONE, 3)
        bf = font(BODY, 25)
        ly = y + 250
        for ln in wrap(bf, use, w - 30):
            d.text((x0 + (w - bf.getlength(ln)) / 2, ly), ln, font=bf, fill=BONE)
            ly += 34
    y += 510
    d.rounded_rectangle((80, y, 1000, y + 230), radius=18, fill=CARD, outline=GOLD, width=1)
    tf = font(HEAD, 54)
    d.text((112, y + 30 - tf.getbbox("H")[1]), "THE SIMPLE RULE", font=tf, fill=GOLD)
    bf = font(BODY, 30)
    ly = y + 104
    for ln in wrap(bf, "The last 2–3 reps should be hard, with clean form. Form breaks: too heavy. 5+ easy reps left: too light.", 860):
        d.text((112, ly), ln, font=bf, fill=BONE)
        ly += 42
    return img


def close_slide():
    img = surface(5, light=(0.5, 0.0), strength=1.2)
    frame(img)
    d = ImageDraw.Draw(img)
    y = 400
    for line, colour, size in (("SAVE THIS FOR", BONE, 130), ("BACK DAY.", GOLD, 210)):
        f = font(HEAD, size)
        while f.getlength(line) > 920:
            f = font(HEAD, f.size - 4)
        cap = f.getbbox("H")
        d.text(((W - f.getlength(line)) / 2, y - cap[1]), line, font=f, fill=colour)
        y += cap[3] - cap[1] + 30
    y += 30
    d.line((W / 2 - 48, y, W / 2 + 48, y), fill=GOLD, width=2)
    y += 44
    bf = font(BODY, 34)
    for ln in wrap(bf, "Follow for more ways to train smarter and stay consistent.", 860):
        d.text(((W - bf.getlength(ln)) / 2, y), ln, font=bf, fill=BONE)
        y += 48
    return img


def main():
    (OUT / "jpg").mkdir(parents=True, exist_ok=True)
    slides = [("01-muscle-map", map_slide()), ("02-frequency", frequency_slide()),
              ("03-exercises", exercises_slide()), ("04-how-heavy", load_slide()), ("05-close", close_slide())]
    pngs = []
    for i, (name, img) in enumerate(slides, 1):
        furniture(img, i, len(slides))
        img.save(OUT / f"{name}.png", optimize=True)
        img.save(OUT / "jpg" / f"{name}.jpg", quality=93)
        pngs.append(OUT / f"{name}.png")
        print(name)
    sheet = Image.new("RGB", (3 * 380 + 20, 2 * 470 + 20), INK)
    for k, p in enumerate(pngs):
        sheet.paste(Image.open(p).resize((360, 450), Image.LANCZOS), (20 + (k % 3) * 380, 20 + (k // 3) * 470))
    sheet.save(OUT / "preview.jpg", quality=90)


if __name__ == "__main__":
    main()
