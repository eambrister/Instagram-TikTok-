"""Build Edison's "CALISTHENICS WORKS LEGS" explainer (EDISON TRAINS, saved style).

Single ~52 s wide outdoor take (Drive id 1mIAJuyajaekSxlSgro9scgo7NURsdIHa): the point (you always
work legs in calisthenics), squats + lunges, his favourite combo demo with his own spoken rep count
(one, two, three), and the goal (500). Cut with tools/ea_cut_edit.py; the demo is protected from
dead-air trimming. Head-tracked depth titles, his rep count as big numbers, word-timed captions,
CTD end card, no vignette.

    python3 -I tools/build_ea_calisthenics_legs.py SRC.MOV WORDS.json SELFIE.tflite OUT_DIR [--only a:b] [--final OUT.mp4]
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_ea_50_more_days import (  # noqa: E402
    BARLOW, BODONI, IVORY, PALE_GOLD, dimensional, font)

WORDS = None
# Word ranges to cut (indices in outputs/edison-ambrister-calisthenics-legs/transcript-words.json).
CUTS = [
    (0, 1, "filler opener: 'And then'"),
    (36, 36, "filler: 'like'"),
    (62, 63, "stutter: first 'a good' in 'a good a good start'"),
]
DEMO = (24.8, 39.2)          # squat + lunge combo demo with spoken count (source seconds)
PROTECT = [DEMO]
MUSIC_LEVEL = 0.22           # default bed, a little higher so it carries the demo


def _w(i):
    return WORDS[i]["t"] if i < len(WORDS) else WORDS[-1]["t"] + 0.9


def build_events():
    big = font(BARLOW, 230)
    huge = font(BARLOW, 300)
    giant = font(BARLOW, 380)
    serif = font(BODONI, 190)
    ev = []

    def depth(t0, t1, img, slam=False):
        ev.append(dict(t0=t0, t1=t1, img=img, y=None, rise=0, slam=slam, kind="depth"))

    gold = lambda s, f=big, tr=4: dimensional(s, f, face=PALE_GOLD, edge=(110, 80, 8), tracking=tr, glow=0.8)
    ivory = lambda s, f=big, tr=4: dimensional(s, f, face=IVORY, edge=(90, 90, 96), tracking=tr, glow=0.8)
    crimson = lambda s, f=huge, tr=2: dimensional(s, f, face=(214, 52, 70), edge=(70, 10, 20), tracking=tr, glow=0.8)

    depth(_w(6) - 0.05, _w(9) - 0.05, ivory("CALISTHENICS"))
    depth(_w(9) - 0.05, _w(10) - 0.05, crimson("LEGS."), slam=True)
    depth(_w(12) - 0.05, _w(20) - 0.05, gold("ALWAYS.", serif, 0))
    depth(_w(28) - 0.05, _w(29) - 0.05, ivory("SQUATS."))
    depth(_w(29) - 0.05, _w(30) - 0.05, ivory("LUNGES."))
    depth(_w(33) - 0.05, _w(35) - 0.05, gold("COMBINE IT.", serif, 0))
    depth(_w(37) - 0.05, _w(43) - 0.05, gold("MY FAVORITE.", serif, 0))
    # his own spoken rep count during the demo
    depth(_w(43) - 0.05, _w(45) - 0.05, gold("1", giant, 0), slam=True)
    depth(_w(45) - 0.05, _w(47) - 0.05, gold("2", giant, 0), slam=True)
    depth(_w(47) - 0.05, _w(49) - 0.05, gold("3", giant, 0), slam=True)
    depth(_w(52) - 0.05, _w(60) - 0.05, ivory("AS MANY AS POSSIBLE."))
    depth(_w(60) - 0.05, _w(67) + 0.2, crimson("500.", giant), slam=True)
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
