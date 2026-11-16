"""Build Edison's "NO HALF-REP PULL-UPS" form PSA (EDISON TRAINS, saved style).

Single ~58 s wide outdoor take at the bars (Drive id 1SzRm3hCASTuq87TmbbvrZTpt1LVY4_A-): the rule,
a full-rep demo, a half-rep demo and the verdict. Cut with tools/ea_cut_edit.py; the two silent demos
are protected from dead-air trimming so every rep plays in full. Head-tracked depth titles in the
sky, FULL REP / HALF REP labels over the demos, word-timed captions, CTD end card, no vignette.

    python3 -I tools/build_ea_pullup_form.py SRC.MOV WORDS.json SELFIE.tflite OUT_DIR [--only a:b] [--final OUT.mp4]
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_ea_50_more_days import (  # noqa: E402
    BARLOW, BODONI, IVORY, PALE_GOLD, dimensional, font)

WORDS = None
# Word ranges to cut (indices in outputs/edison-ambrister-pullup-form/transcript-words.json).
CUTS = [
    (40, 45, "repeat: first 'That's what I want to see.' (restated as 'This is what I want to see' before the demo)"),
]
GOOD_DEMO = (26.0, 37.9)   # full-rep demonstration (source seconds)
BAD_DEMO = (45.1, 51.4)    # half-rep demonstration
PROTECT = [GOOD_DEMO, BAD_DEMO]


def _w(i):
    return WORDS[i]["t"] if i < len(WORDS) else WORDS[-1]["t"] + 0.9


def build_events():
    big = font(BARLOW, 230)
    huge = font(BARLOW, 300)
    serif = font(BODONI, 190)
    ev = []

    def depth(t0, t1, img, slam=False):
        ev.append(dict(t0=t0, t1=t1, img=img, y=None, rise=0, slam=slam, kind="depth"))

    gold = lambda s, f=big, tr=4: dimensional(s, f, face=PALE_GOLD, edge=(110, 80, 8), tracking=tr, glow=0.8)
    ivory = lambda s, f=big, tr=4: dimensional(s, f, face=IVORY, edge=(90, 90, 96), tracking=tr, glow=0.8)
    crimson = lambda s, f=huge, tr=2: dimensional(s, f, face=(214, 52, 70), edge=(70, 10, 20), tracking=tr, glow=0.8)

    depth(_w(15) - 0.05, _w(18) - 0.05, crimson("NO HALF REPS."), slam=True)
    depth(_w(22) - 0.05, _w(27) - 0.05, ivory("FULL LOCKOUT"))
    depth(_w(27) - 0.05, _w(33) - 0.05, gold("CHIN OVER BAR"))
    depth(_w(33) - 0.05, _w(40) - 0.05, gold("90°", huge))
    depth(GOOD_DEMO[0], GOOD_DEMO[1], gold("FULL REP.", serif, 0))
    depth(_w(60) - 0.05, _w(71) - 0.05, ivory("NOT THIS."))
    depth(BAD_DEMO[0], BAD_DEMO[1], crimson("HALF REP."))
    depth(_w(72) - 0.05, _w(77) + 1.0, crimson("GARBAGE."), slam=True)
    return ev


def main():
    global WORDS
    import ea_cut_edit as eng
    ap = argparse.ArgumentParser()
    for k in ("src", "words", "selfie", "out"):
        ap.add_argument(k)
    ap.add_argument("--only")
    ap.add_argument("--final")
    a = ap.parse_args()
    WORDS = json.load(open(a.words))
    film = sys.modules[__name__]
    eng.render(a.src, a.words, a.selfie, a.out, film, a.only)
    if not a.only:
        eng.mix(a.src, a.out, film)
        if a.final:
            eng.finish(a.out, a.final)


if __name__ == "__main__":
    main()
