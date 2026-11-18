"""Build Edison's "PULL-UP VARIATIONS" grip explainer (EDISON TRAINS, saved style, no music).

Single ~56 s wide outdoor take at the bars (Drive id 1vxLoLfah4m4yP4NkLGouw6arUgAn4K1Q): he names and
demonstrates five grips (wide, close, deadlift/mixed, commando, extra wide), then the point: vary the
pull-up instead of only doing wide grip. Cut with tools/ea_cut_edit.py; every grip demo is protected
from dead-air trimming. Head-tracked depth titles naming each grip, word-timed captions, CTD end
card, no vignette, voice + SFX only.

    python3 -I tools/build_ea_pullup_variations.py SRC.MOV WORDS.json SELFIE.tflite OUT_DIR [--only a:b] [--final OUT.mp4]
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_ea_50_more_days import (  # noqa: E402
    BARLOW, BODONI, IVORY, PALE_GOLD, dimensional, font)

WORDS = None
# Word ranges to cut (indices in outputs/edison-ambrister-pullup-variations/transcript-words.json).
CUTS = [
    (11, 12, "filler: 'You know,'"),
]
WIDE = (8.0, 11.2)          # grip demos (source seconds)
CLOSE = (13.4, 17.0)
MIXED = (20.6, 23.6)
COMMANDO = (29.3, 33.3)
EXTRA_WIDE = (41.8, 45.0)
PROTECT = [WIDE, CLOSE, MIXED, COMMANDO, EXTRA_WIDE]
# Dead air between grips (source seconds). Outdoor wind keeps the VAD from seeing these as silence.
DEAD = [
    (6.20, 6.70, "dead air before 'you could do the wide grip'"),
    (11.20, 11.75, "dead air after the wide-grip demo"),
    (17.00, 18.45, "dead air after the close-grip demo"),
    (19.30, 20.25, "pause before 'deadlift'"),
    (23.60, 26.05, "dead air after the deadlift-grip demo"),
    (26.95, 27.42, "pause before 'I can't remember'"),
    (34.30, 35.00, "dead air before 'it's multiple pull-up variations'"),
]
MUSIC_LEVEL = 0              # Edison asked for no music (voice + SFX only)


def _w(i):
    return WORDS[i]["t"] if i < len(WORDS) else WORDS[-1]["t"] + 0.9


def build_events():
    big = font(BARLOW, 230)
    huge = font(BARLOW, 300)
    serif = font(BODONI, 190)
    ev = []

    def depth(t0, t1, img, slam=False):
        ev.append(dict(t0=t0, t1=t1, img=img, y=None, rise=0, slam=slam, kind="depth"))

    gold = lambda s, f=serif, tr=0: dimensional(s, f, face=PALE_GOLD, edge=(110, 80, 8), tracking=tr, glow=0.8)
    ivory = lambda s, f=big, tr=4: dimensional(s, f, face=IVORY, edge=(90, 90, 96), tracking=tr, glow=0.8)
    crimson = lambda s, f=huge, tr=2: dimensional(s, f, face=(214, 52, 70), edge=(70, 10, 20), tracking=tr, glow=0.8)

    depth(_w(3) - 0.05, _w(7) - 0.05, ivory("A FEW TYPES"))
    depth(_w(7) - 0.05, _w(13) - 0.05, crimson("PULL-UPS."), slam=True)
    depth(_w(17) - 0.05, WIDE[1], gold("WIDE GRIP."))
    depth(CLOSE[0], CLOSE[1], gold("CLOSE GRIP."))
    depth(_w(30) - 0.05, MIXED[1], gold("DEADLIFT GRIP."))
    depth(_w(35) - 0.05, COMMANDO[0], ivory("THIS ONE?"))
    depth(COMMANDO[0], COMMANDO[1], gold("COMMANDO GRIP."))
    depth(_w(48) - 0.05, _w(54) - 0.05, crimson("VARIATIONS."), slam=True)
    depth(_w(64) - 0.05, EXTRA_WIDE[1], gold("EXTRA WIDE."))
    depth(_w(69) - 0.05, _w(75) + 0.2, ivory("MIX IT UP."))
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
