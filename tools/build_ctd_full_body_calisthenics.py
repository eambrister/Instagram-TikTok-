#!/usr/bin/env python3
"""Build the Cut Throat Discipline full-body calisthenics post."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/ctd-full-body-calisthenics"
W, H = 1080, 1350

GOLD = "#D6A918"
PALE_GOLD = "#F3D878"
CRIMSON = "#981B2E"
WHITE = "#F3F0E9"
SILVER = "#AAB0B9"
MUTED = "#666C75"
BLACK = "#07080A"
CARD = "#101216"

HEAD = ROOT / "brand/fonts/BarlowCondensed-ExtraBold.ttf"
BODY = ROOT / "brand/fonts/Montserrat-Bold.ttf"
MEDIUM = ROOT / "brand/fonts/Montserrat-Medium.ttf"
LOGO = ROOT / "outputs/ctd-why-routine-matters/ctd-cinematic-logo.png"
ANATOMY = OUT / "anatomical-exercises-source.png"


def font(path, size):
    return ImageFont.truetype(str(path), size)


F = {
    "kicker": font(BODY, 18),
    "headline": font(HEAD, 83),
    "sub": font(BODY, 23),
    "name": font(HEAD, 39),
    "reps": font(BODY, 21),
    "target": font(MEDIUM, 15),
    "footer": font(BODY, 16),
}


def glow(base, box, color, blur=30, alpha=80):
    layer = Image.new("RGBA", base.size)
    d = ImageDraw.Draw(layer)
    d.ellipse(box, fill=color + f"{alpha:02x}")
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def skeleton(draw, ox, oy, s, points, equipment=None):
    """Draw an original geometric exercise pictogram from named joints."""
    p = {k: (ox + x*s, oy + y*s) for k, (x, y) in points.items()}
    limb = max(5, round(7*s))
    edge = max(2, round(2*s))
    pairs = [
        ("neck", "hip"), ("l_shoulder", "r_shoulder"),
        ("l_shoulder", "l_elbow"), ("l_elbow", "l_hand"),
        ("r_shoulder", "r_elbow"), ("r_elbow", "r_hand"),
        ("hip", "l_knee"), ("l_knee", "l_foot"),
        ("hip", "r_knee"), ("r_knee", "r_foot"),
    ]
    if equipment:
        for a, b in equipment:
            draw.line((ox+a[0]*s, oy+a[1]*s, ox+b[0]*s, oy+b[1]*s), fill=MUTED, width=max(3, round(4*s)))
    for a, b in pairs:
        if a in p and b in p:
            draw.line((*p[a], *p[b]), fill=GOLD, width=limb, joint="curve")
            draw.line((*p[a], *p[b]), fill=PALE_GOLD, width=edge, joint="curve")
    # torso mass
    if all(k in p for k in ("l_shoulder", "r_shoulder", "hip")):
        draw.polygon([p["l_shoulder"], p["r_shoulder"], p["hip"]], fill="#B7BDC6", outline=GOLD)
    hx, hy = p["head"]
    r = 11*s
    draw.ellipse((hx-r, hy-r, hx+r, hy+r), fill=WHITE, outline=GOLD, width=edge)
    for k in ("l_hand", "r_hand", "l_foot", "r_foot"):
        if k in p:
            x, y = p[k]
            rr = 3.5*s
            draw.ellipse((x-rr, y-rr, x+rr, y+rr), fill=CRIMSON)


POSES = {
    "PULL-UPS": ({
        "head": (50, 30), "neck": (50, 43), "l_shoulder": (39, 48), "r_shoulder": (61, 48), "hip": (50, 78),
        "l_elbow": (30, 30), "l_hand": (26, 12), "r_elbow": (70, 30), "r_hand": (74, 12),
        "l_knee": (42, 100), "l_foot": (36, 118), "r_knee": (58, 100), "r_foot": (64, 118),
    }, [((12, 10), (88, 10))]),
    "PUSH-UPS": ({
        "head": (25, 63), "neck": (37, 66), "l_shoulder": (41, 60), "r_shoulder": (44, 70), "hip": (70, 71),
        "l_elbow": (45, 87), "l_hand": (35, 105), "r_elbow": (55, 88), "r_hand": (48, 105),
        "l_knee": (88, 75), "l_foot": (103, 94), "r_knee": (88, 78), "r_foot": (103, 99),
    }, [((10, 108), (112, 108))]),
    "SQUATS": ({
        "head": (50, 22), "neck": (50, 36), "l_shoulder": (38, 42), "r_shoulder": (62, 42), "hip": (50, 72),
        "l_elbow": (25, 48), "l_hand": (15, 57), "r_elbow": (75, 48), "r_hand": (85, 57),
        "l_knee": (28, 90), "l_foot": (18, 112), "r_knee": (72, 90), "r_foot": (82, 112),
    }, None),
    "DIPS": ({
        "head": (50, 22), "neck": (50, 36), "l_shoulder": (38, 42), "r_shoulder": (62, 42), "hip": (50, 78),
        "l_elbow": (29, 64), "l_hand": (18, 54), "r_elbow": (71, 64), "r_hand": (82, 54),
        "l_knee": (40, 98), "l_foot": (58, 116), "r_knee": (58, 98), "r_foot": (75, 114),
    }, [((8, 55), (35, 55)), ((65, 55), (92, 55)), ((15, 55), (15, 115)), ((85, 55), (85, 115))]),
    "REVERSE LUNGES": ({
        "head": (48, 20), "neck": (48, 34), "l_shoulder": (37, 40), "r_shoulder": (59, 40), "hip": (49, 72),
        "l_elbow": (28, 58), "l_hand": (36, 75), "r_elbow": (69, 58), "r_hand": (62, 75),
        "l_knee": (28, 91), "l_foot": (14, 112), "r_knee": (72, 97), "r_foot": (96, 112),
    }, None),
    "GLUTE BRIDGES": ({
        "head": (20, 90), "neck": (33, 86), "l_shoulder": (38, 80), "r_shoulder": (41, 89), "hip": (68, 58),
        "l_elbow": (35, 100), "l_hand": (25, 108), "r_elbow": (50, 100), "r_hand": (44, 109),
        "l_knee": (89, 79), "l_foot": (100, 106), "r_knee": (83, 83), "r_foot": (88, 108),
    }, [((8, 110), (112, 110))]),
    "BURPEES": ({
        "head": (28, 62), "neck": (40, 65), "l_shoulder": (44, 59), "r_shoulder": (46, 70), "hip": (69, 73),
        "l_elbow": (42, 87), "l_hand": (31, 104), "r_elbow": (55, 88), "r_hand": (47, 105),
        "l_knee": (82, 91), "l_foot": (70, 108), "r_knee": (92, 85), "r_foot": (105, 101),
    }, [((10, 109), (112, 109))]),
    "HOLLOW HOLD": ({
        "head": (20, 70), "neck": (33, 73), "l_shoulder": (38, 70), "r_shoulder": (40, 77), "hip": (65, 82),
        "l_elbow": (26, 52), "l_hand": (16, 37), "r_elbow": (31, 55), "r_hand": (21, 42),
        "l_knee": (83, 69), "l_foot": (104, 55), "r_knee": (84, 76), "r_foot": (107, 66),
    }, [((8, 108), (112, 108))]),
}


WORKOUT = [
    ("PULL-UPS", "6–10 REPS", "BACK + BICEPS"),
    ("PUSH-UPS", "10–20 REPS", "CHEST + TRICEPS"),
    ("SQUATS", "15–25 REPS", "QUADS + GLUTES"),
    ("DIPS", "6–12 REPS", "CHEST + TRICEPS"),
    ("REVERSE LUNGES", "8–12 / LEG", "LEGS + BALANCE"),
    ("GLUTE BRIDGES", "15–20 REPS", "GLUTES + HIPS"),
    ("BURPEES", "6–10 REPS", "FULL BODY + CARDIO"),
    ("HOLLOW HOLD", "20–30 SEC", "CORE + CONTROL"),
]


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    source = Image.open(ANATOMY).convert("RGBA")
    im = Image.new("RGBA", (W, H), BLACK)
    glow(im, (-180, -220, 480, 400), CRIMSON, 110, 35)
    glow(im, (650, -220, 1280, 400), GOLD, 110, 25)
    d = ImageDraw.Draw(im)
    logo = Image.open(LOGO).convert("RGBA")
    logo.thumbnail((78, 78), Image.Resampling.LANCZOS)
    im.alpha_composite(logo, (38, 18))
    d.text((132, 31), "CUTTHROAT DISCIPLINE", font=F["sub"], fill=WHITE)
    d.text((1040, 34), "SAVE + EXECUTE", font=F["kicker"], fill=SILVER, anchor="ra")
    d.text((W//2, 82), "FULL BODY CALISTHENICS", font=font(HEAD, 67), fill=GOLD, anchor="mm")
    d.text((W//2, 139), "3 ROUNDS  •  60–90 SEC REST  •  QUALITY REPS", font=F["sub"], fill=SILVER, anchor="mm")
    d.line((38, 172, 1042, 172), fill=MUTED, width=2)

    # Crop each demonstration from the source sheet and give it a dedicated
    # image area. Labels live below the image, never over the athlete.
    crop_boxes = [
        (105, 170, 520, 462),   # pull-up
        (555, 310, 1065, 468),  # push-up
        (115, 500, 500, 770),   # squat
        (600, 495, 1015, 775),  # dip
        (65, 785, 510, 1065),   # reverse lunge
        (535, 800, 1055, 1060), # glute bridge
        (45, 1070, 500, 1325),  # burpee
        (505, 1085, 1070, 1325),# hollow hold
    ]
    card_w, card_h = 500, 252
    start_y, row_gap = 192, 16
    for i, (name, reps, target) in enumerate(WORKOUT):
        col, row = i % 2, i // 2
        x = 26 if col == 0 else 554
        y = start_y + row * (card_h + row_gap)
        d.rounded_rectangle((x, y, x+card_w, y+card_h), radius=16, fill="#08090B", outline="#292D34", width=2)
        crop = source.crop(crop_boxes[i])
        crop.thumbnail((468, 181), Image.Resampling.LANCZOS)
        px = x + (card_w - crop.width) // 2
        py = y + 5 + (181 - crop.height) // 2
        im.alpha_composite(crop, (px, py))
        d = ImageDraw.Draw(im)
        d.line((x+14, y+191, x+card_w-14, y+191), fill="#292D34", width=2)
        d.rectangle((x, y+190, x+7, y+card_h), fill=CRIMSON if col == 0 else GOLD)
        d = ImageDraw.Draw(im)
        d.text((x+20, y+205), name, font=font(HEAD, 31), fill=WHITE)
        d.text((x+480, y+211), reps, font=F["reps"], fill=GOLD, anchor="ra")

    d.line((38, 1282, 1042, 1282), fill=MUTED, width=2)
    d.text((W//2, 1318), "DISCIPLINE - ACCOUNTABILITY - CONSISTENCY", font=F["footer"], fill=SILVER, anchor="mm")

    final = im.convert("RGB")
    final.save(OUT / "full-body-calisthenics.png", optimize=True)
    final.save(OUT / "preview.jpg", quality=92)


if __name__ == "__main__":
    build()
