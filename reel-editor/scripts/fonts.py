"""Font resolution and text measurement.

  python -I fonts.py resolve <brand_fonts_dir> <repo_fonts_dir> <inter_dir> <public_fonts_dir> <out.json>
      Reads real family names from font files. Uses Heading Now / Gotham when supplied,
      otherwise open-license fallbacks, and records which was chosen.
  python -I fonts.py measure <request.json>
      request: {"font": path, "items": [{"text", "size"}]} -> prints widths in px.
"""
import json
import os
import shutil
import sys

from fontTools.ttLib import TTFont


def family_of(path: str):
    try:
        f = TTFont(path, lazy=True)
        names = {n.nameID: n.toUnicode() for n in f["name"].names if n.nameID in (1, 2, 4, 16, 17)}
        return names.get(16) or names.get(1), names.get(17) or names.get(2), names.get(4)
    except Exception:
        return None, None, None


def pick(candidates, family_word, weight_words):
    for path, fam, sub, full in candidates:
        label = f"{fam} {sub} {full}".lower()
        if family_word in label and any(w in label for w in weight_words):
            return path, fam, sub
    for path, fam, sub, full in candidates:
        if family_word in f"{fam} {full}".lower():
            return path, fam, sub
    return None


def resolve(brand_dir, repo_fonts, inter_dir, public_dir, out):
    os.makedirs(public_dir, exist_ok=True)
    cands = []
    for root, _, files in os.walk(brand_dir):
        for fn in files:
            if fn.lower().endswith((".ttf", ".otf")):
                p = os.path.join(root, fn)
                fam, sub, full = family_of(p)
                if fam:
                    cands.append((p, fam, sub or "", full or ""))

    def install(src, name):
        dst = os.path.join(public_dir, name)
        shutil.copyfile(src, dst)
        return dst

    def inter(weight):
        dst = os.path.join(public_dir, f"Inter-{weight}.ttf")
        if not os.path.exists(dst):
            f = TTFont(os.path.join(inter_dir, f"inter-latin-{weight}-normal.woff2"))
            f.flavor = None
            f.save(dst)
        return dst

    result, notes = {}, []
    h = pick(cands, "heading now", ["bold", "heavy", "black"])
    if h:
        ext = os.path.splitext(h[0])[1]
        result["heading"] = {"file": install(h[0], "Heading" + ext), "family": "EddieHeading", "source": f"{h[1]} {h[2]}", "fallback": False}
    else:
        result["heading"] = {"file": install(os.path.join(repo_fonts, "BarlowCondensed-ExtraBold.ttf"), "Heading.ttf"),
                             "family": "EddieHeading", "source": "Barlow Condensed ExtraBold (OFL fallback)", "fallback": True}
        notes.append("Heading Now not supplied: using Barlow Condensed ExtraBold.")
    g_bold = pick(cands, "gotham", ["black", "ultra", "bold"])
    g_book = pick(cands, "gotham", ["medium", "book"])
    if g_bold:
        ext = os.path.splitext(g_bold[0])[1]
        result["caption"] = {"file": install(g_bold[0], "Caption" + ext), "family": "EddieCaption", "source": f"{g_bold[1]} {g_bold[2]}", "fallback": False}
    else:
        result["caption"] = {"file": install(inter(900), "Caption.ttf"), "family": "EddieCaption", "source": "Inter Black (OFL fallback)", "fallback": True}
        notes.append("Gotham not supplied: captions use Inter Black.")
    if g_book:
        ext = os.path.splitext(g_book[0])[1]
        result["body"] = {"file": install(g_book[0], "Body" + ext), "family": "EddieBody", "source": f"{g_book[1]} {g_book[2]}", "fallback": False}
    else:
        result["body"] = {"file": install(inter(700), "Body.ttf"), "family": "EddieBody", "source": "Inter Bold (OFL fallback)", "fallback": True}
    result["notes"] = notes
    result["scanned"] = [{"file": c[0], "family": c[1], "style": c[2]} for c in cands]
    for k in ("heading", "caption", "body"):
        result[k]["url"] = "fonts/" + os.path.basename(result[k]["file"])
    with open(out, "w") as f:
        json.dump(result, f, indent=1)
    print(json.dumps({k: result[k]["source"] for k in ("heading", "caption", "body")}))


def measure(req_path):
    from PIL import ImageFont
    req = json.load(open(req_path))
    cache, widths = {}, []
    for it in req["items"]:
        size = int(round(it["size"]))
        if size not in cache:
            cache[size] = ImageFont.truetype(req["font"], size)
        widths.append(cache[size].getlength(it["text"]))
    print(json.dumps(widths))


if __name__ == "__main__":
    if sys.argv[1] == "resolve":
        resolve(*sys.argv[2:7])
    elif sys.argv[1] == "measure":
        measure(sys.argv[2])
