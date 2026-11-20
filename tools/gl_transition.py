"""Apply any of ~300 gl-transitions shaders (vendored in tools/gl_transitions/shaders, MIT) between two
frame sequences, rendered on WebGL in the preinstalled headless Chromium via tools/gl_transitions/render.js.

    from gl_transition import run, names
    out = run("CrossZoom", frames_a, frames_b)      # uint8 arrays (N, H, W, 3) -> (N, H, W, 3)
"""
import json
import pathlib
import subprocess
import tempfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent / "gl_transitions"


def names():
    return sorted(p.stem for p in (HERE / "shaders").glob("*.glsl"))


def run(name, a, b, params=None, progress=None):
    a, b = np.asarray(a, np.uint8), np.asarray(b, np.uint8)
    n, h, w, _ = a.shape
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        a[:, ::-1].tofile(td / "a.rgb")  # GL textures are bottom-up: flip in, flip out
        b[:, ::-1].tofile(td / "b.rgb")
        (td / "p.json").write_text(json.dumps(params or {}))
        args = ["node", str(HERE / "render.js"), str(HERE / "shaders" / f"{name}.glsl"), str(w), str(h), str(n),
                str(td / "a.rgb"), str(td / "b.rgb"), str(td / "o.rgb"), str(td / "p.json")]
        if progress is not None:
            (td / "g.json").write_text(json.dumps([float(x) for x in progress]))
            args.append(str(td / "g.json"))
        subprocess.run(args, check=True, cwd=str(HERE.parent.parent))
        return np.fromfile(td / "o.rgb", np.uint8).reshape(n, h, w, 3)[:, ::-1].copy()
