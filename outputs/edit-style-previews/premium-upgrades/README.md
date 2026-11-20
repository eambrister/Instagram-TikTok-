# Premium upgrades: open-source tools (previews for Edison's approval)

None of these are in the saved style yet. Each gets added only after Edison approves its preview.

| Tool | What it does | Preview | Where it lives |
|---|---|---|---|
| **gl-transitions** (MIT, 298 shaders) | Premium transitions (whip pan, cross zoom, light streaks, film burn, speed lines, glitch, overexposure, dreamy zoom, and ~290 more), run on WebGL in the preinstalled headless Chromium | `transitions-preview.mp4` | `tools/gl_transition.py`, `tools/gl_transitions/` |
| **RobustVideoMatting** (GPL-3.0, ONNX) | Clean, stable subject mattes for titles behind Edison: no sky holes between the arms, no background objects stuck to his head | `matte-comparison.jpg` | `tools/rvm_matte.py` (models below) |
| **Remotion** (free for individuals and companies of 3 or fewer) | After Effects–style motion graphics written in code: springy label cards, arrows that draw themselves, glowing highlights, pulsing targets, tag pills, particles. Rendered with transparency and laid over footage | `motion-callout-preview.mp4` | `tools/remotion/` (`npm install`, then `npx remotion render ...`) |
| DeepFilterNet (MIT/Apache) | AI wind/noise removal for outdoor voice | not installed yet | needs approval (see below) |

## Setup in a fresh session

- **Transitions:** none beyond Node and Playwright (already preinstalled).
- **RVM models** (GitHub releases), into the scratchpad `tools3/` folder:
  - `https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_resnet50_fp32.onnx` (HQ, about 0.2 s per 1080×1920 frame on CPU)
  - `https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx` (fast, about 0.1 s per frame)
- **Remotion:**
  1. `cd tools/remotion && npm install`
  2. Render overlays with `--codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`
