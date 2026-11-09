"""Build Edison's "GLP-1s vs DISCIPLINE" talking-head Reel (edison-full-message + cut rule §4b).

Single ~82 s indoor selfie (Drive id 15BdPHYwUeIPAJl4mqxdUe0b8bWG5XNDf). Cut with
tools/ea_cut_edit.py. Health topic: on-screen titles stay with Edison's own opinion and
behaviour words; no statistic or medical claim is put on screen. No vignette.

    python3 -I tools/build_ea_glp1_discipline.py SRC.MOV WORDS.json SELFIE.tflite OUT_DIR [--only a:b] [--final OUT.mp4]
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_ea_50_more_days import (  # noqa: E402
    BARLOW, BODONI, IVORY, PALE_GOLD, SILVER, dimensional, font)

# Word ranges to cut (indices in outputs/edison-ambrister-glp1-discipline/transcript-words.json).
CUTS = [
    (0, 1, "filler opener: 'And then'"),
    (17, 18, "filler: 'it's like'"),
    (255, 276, "restates the 'put it all back on' point with a flubbed restart, then 'So yeah.'"),
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

    depth(0.70, 2.05, gold("GLP-1s", huge), slam=True)
    depth(3.55, 4.95, ivory("NOT THE SHOT."))
    depth(6.45, 7.75, gold("BY YOURSELF.", serif, 0))
    depth(14.50, 15.85, silver("LESS APPETITE"))
    depth(18.85, 20.25, silver("EAT LESS"))
    depth(21.55, 22.55, gold("CALORIE DEFICIT."), slam=True)
    depth(26.65, 28.85, gold("DISCIPLINE.", serif, 0))
    depth(34.85, 36.50, ivory("HABITS."))
    depth(45.40, 47.30, gold("MINDSET.", serif, 0))
    depth(53.90, 55.90, gold("MORE REWARDING.", serif, 0))
    depth(56.05, 57.80, crimson("FIGHT YOUR MIND."), slam=True)
    depth(60.50, 61.60, silver("THE EASY WAY OUT"))
    depth(72.15, 74.20, gold("MENTAL DISCIPLINE."), slam=True)
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
