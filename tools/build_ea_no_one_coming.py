"""Build Edison's "NO ONE'S COMING TO SAVE YOU" talking-head Reel (edison-full-message + cut rule §4b).

Single ~85 s indoor selfie (Drive id 1xxOLCI04O2KMdAUCZQGN1BP3tG3nN3N1). Cut with
tools/ea_cut_edit.py. No vignette (standing rule).

    python3 -I tools/build_ea_no_one_coming.py SRC.MOV WORDS.json SELFIE.tflite OUT_DIR [--only a:b] [--final OUT.mp4]
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_ea_50_more_days import (  # noqa: E402
    BARLOW, BODONI, IVORY, PALE_GOLD, SILVER, dimensional, font)

# Word ranges to cut (indices in outputs/edison-ambrister-no-one-coming/transcript-words.json).
CUTS = [
    (0, 0, "filler opener: 'So'"),
    (20, 22, "filler: 'saying, you know,'"),
    (60, 91, "rambling aside restating 'people will help you' ('Like, if you call up someone right now... bind or something, right?')"),
    (308, 311, "filler sign-off: 'Just so you know.'"),
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

    depth(3.95, 5.95, ivory("NO ONE'S COMING"))
    depth(9.15, 11.95, silver("\"I HAVE FRIENDS\""))
    depth(16.05, 17.80, ivory("PEOPLE WILL HELP."))
    depth(27.65, 29.95, gold("ONLY YOU.", huge), slam=True)
    depth(36.25, 37.50, silver("DARK PATH"))
    depth(38.55, 40.40, gold("YOUR DECISION.", serif, 0))
    depth(41.00, 42.15, silver("STOP THIS."))
    depth(42.15, 43.50, gold("START THAT."))
    depth(48.95, 51.40, crimson("PUSH YOURSELF."), slam=True)
    depth(53.55, 55.70, ivory("CONSUMED."))
    depth(61.55, 63.50, gold("FOR YOURSELF.", serif, 0))
    depth(66.55, 68.10, silver("FINANCIAL"))
    depth(68.35, 69.90, silver("PHYSICAL"))
    depth(70.35, 73.95, gold("MAKE UP YOUR MIND.", serif, 0))
    depth(79.05, 81.40, ivory("ONLY SO MUCH."))
    depth(81.55, 83.30, crimson("YOU DO EVERYTHING."), slam=True)
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
