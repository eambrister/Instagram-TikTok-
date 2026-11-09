"""Build Edison's "ABOVE AVERAGE" talking-head Reel (edison-full-message + cut rule §4b).

Single ~54 s indoor selfie (Drive id 1bYQ87UeBJQCcesdp02iS3TV3RdkjjSqq). Cut with
tools/ea_cut_edit.py: filler, restated lines and dead air removed; titles authored in
source time and remapped. No vignette (standing rule).

    python3 -I tools/build_ea_above_average.py SRC.MOV WORDS.json SELFIE.tflite OUT_DIR [--only a:b] [--final OUT.mp4]
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_ea_50_more_days import (  # noqa: E402
    BARLOW, BODONI, IVORY, PALE_GOLD, SILVER, dimensional, font)

# Word ranges to cut (indices in outputs/edison-ambrister-above-average/transcript-words.json).
CUTS = [
    (26, 26, "filler: 'Like,'"),
    (74, 77, "repeat: second 'They ain't doing nothing.'"),
    (101, 104, "repeat: 'They just don't care.' restates 'People really don't care.'"),
]


def build_events():
    big = font(BARLOW, 230)
    huge = font(BARLOW, 300)
    serif = font(BODONI, 190)
    ev = []

    def depth(t0, t1, img, slam=False):
        ev.append(dict(t0=t0, t1=t1, img=img, y=None, rise=0, slam=slam, kind="depth"))

    gold = lambda s, f=big, tr=4: dimensional(s, f, face=PALE_GOLD, edge=(110, 80, 8), tracking=tr)
    ivory = lambda s, f=big, tr=4: dimensional(s, f, face=IVORY, edge=(90, 90, 96), tracking=tr)
    silver = lambda s, f=big, tr=4: dimensional(s, f, face=SILVER, edge=(60, 64, 72), tracking=tr)
    crimson = lambda s, f=huge, tr=2: dimensional(s, f, face=(214, 52, 70), edge=(70, 10, 20), tracking=tr)

    depth(3.30, 4.55, gold("ABOVE AVERAGE."), slam=True)
    depth(5.40, 6.65, ivory("OUTWORK EVERYBODY"))
    depth(9.70, 12.30, silver("THEY SAY…"))
    depth(15.20, 16.25, ivory("SET A GOAL."))
    depth(16.25, 19.10, gold("FOLLOW THROUGH.", serif, 0))
    depth(19.75, 21.60, gold("ABOVE 99%", huge), slam=True)
    depth(26.35, 28.70, ivory("FITNESS & HEALTH"))
    depth(29.00, 30.50, silver("NOT WORKING OUT"))
    depth(30.55, 32.60, silver("NO GOALS"))
    depth(33.20, 35.25, crimson("DON'T CARE."), slam=True)
    depth(37.35, 38.70, gold("EVERY SINGLE DAY.", serif, 0))
    depth(41.40, 42.45, ivory("ABOVE AVERAGE."))
    depth(42.75, 45.05, ivory("2027"))
    depth(47.10, 48.85, gold("AHEAD."))
    depth(49.75, 50.35, ivory("GOALS."))
    depth(50.35, 50.95, gold("SET THEM."))
    depth(50.95, 51.45, gold("HIT THEM."), slam=True)
    depth(51.50, 53.30, ivory("YOU'LL BE FINE."))
    return ev


def main():
    import ea_cut_edit as eng
    ap = argparse.ArgumentParser()
    for k in ("src", "words", "selfie", "out"):
        ap.add_argument(k)
    ap.add_argument("--only")
    ap.add_argument("--final")
    a = ap.parse_args()
    film = sys.modules[__name__]
    eng.render(a.src, a.words, a.selfie, a.out, film, a.only)
    if not a.only:
        eng.mix(a.src, a.out, film)
        if a.final:
            eng.finish(a.out, a.final)


if __name__ == "__main__":
    main()
