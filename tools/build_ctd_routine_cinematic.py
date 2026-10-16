from pathlib import Path
import html
import shutil

ROOT = Path('/workspace/Instagram-TikTok-')
OUT = ROOT / 'outputs/ctd-why-routine-matters'
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = [
    Path('/workspace/generated_images/exec-0cb75e73-9139-495c-8b7e-edb41b927bcb.png'),
    Path('/workspace/generated_images/exec-af66c508-ff65-4a69-80d8-103a5e130cee.png'),
    Path('/workspace/generated_images/exec-76bf8513-0b3d-4d69-8130-48d9c18f7c12.png'),
    Path('/workspace/generated_images/exec-0fef63fc-5fc9-479d-a2a9-d63ab27fb21d.png'),
    Path('/workspace/generated_images/exec-9e9c7042-f2af-4a6f-9f88-d58da4d175c9.png'),
    Path('/workspace/generated_images/exec-ed834c2e-41f6-4f9f-82e3-27fc5c2766ea.png'),
    Path('/workspace/generated_images/exec-0b352b99-2077-4405-9a1e-adee3c7fc838.png'),
    Path('/workspace/generated_images/exec-191db628-c93b-4180-8b66-e8555fd823ce.png'),
]

ASSETS = OUT / 'scene-assets'
ASSETS.mkdir(exist_ok=True)
for i, source in enumerate(SOURCES, 1):
    shutil.copy2(source, ASSETS / f'{i:02d}-scene.png')

INK = '#090908'
BONE = '#F0ECE3'
MUTED = '#C2BDB3'
GOLD = '#C19A58'
GOLD2 = '#E1BE77'
HEAD = 'Latin Modern Sans Demi Cond'
BODY = 'Liberation Sans'
LOGO_SOURCE = Path('/workspace/generated_images/exec-66c3afd4-fee1-46ee-81a3-4ab263151bb1.png')
LOGO = OUT / 'ctd-cinematic-logo.png'
shutil.copy2(LOGO_SOURCE, LOGO)

slides = [
    {
        'role': 'hook',
        'kicker': 'WHY ROUTINE MATTERS',
        'headline': ['YOUR ROUTINE', 'SHOULD WORK', 'EVEN WHEN YOU', 'DON’T FEEL LIKE IT.'],
        'body': ['Motivation changes.', 'Your next action should still be clear.'],
        'align': 'left', 'panel': 'left',
    },
    {
        'role': 'direction',
        'kicker': '01 · DIRECTION',
        'headline': ['A ROUTINE TELLS YOU', 'WHAT HAPPENS NEXT.'],
        'body': ['You spend less energy deciding when to train,', 'what to prepare and where to begin.'],
        'align': 'left', 'panel': 'top',
    },
    {
        'role': 'resistance',
        'kicker': '02 · LESS RESISTANCE',
        'headline': ['FEWER DECISIONS.', 'LESS NEGOTIATION.'],
        'body': ['When the cue and first step are already chosen,', 'starting requires less mental effort.'],
        'align': 'left', 'panel': 'left',
    },
    {
        'role': 'preparation',
        'kicker': '03 · PREPARATION',
        'headline': ['SET UP THE ACTION', 'BEFORE THE MOMENT.'],
        'body': ['Lay out the clothes. Prepare the food.', 'Choose the time. Remove the excuse.'],
        'align': 'right', 'panel': 'right',
    },
    {
        'role': 'evidence',
        'kicker': '04 · EVIDENCE',
        'headline': ['REPETITION BUILDS', 'PROOF YOU CAN TRUST.'],
        'body': ['Each completed action strengthens the belief', 'that you follow through on your word.'],
        'align': 'left', 'panel': 'left',
    },
    {
        'role': 'difficult days',
        'kicker': '05 · DIFFICULT DAYS',
        'headline': ['A REAL ROUTINE', 'SURVIVES A BAD DAY.'],
        'body': ['Reduce the minimum when necessary.', 'Keep the connection to the standard.'],
        'align': 'right', 'panel': 'right',
    },
    {
        'role': 'real life',
        'kicker': '06 · REAL LIFE',
        'headline': ['IF IT DOESN’T FIT', 'YOUR LIFE, IT WON’T', 'LAST IN YOUR LIFE.'],
        'body': ['Build around your actual schedule, energy,', 'responsibilities and available resources.'],
        'align': 'left', 'panel': 'left',
    },
    {
        'role': 'start',
        'kicker': 'START HERE',
        'headline': ['CHOOSE ONE ACTION', 'YOU CAN REPEAT.'],
        'body': ['Choose the cue. Choose the time.', 'Complete it for the next seven days.'],
        'prompt': 'WHAT WILL YOUR ONE ACTION BE?',
        'align': 'left', 'panel': 'top',
    },
]

def esc(s):
    return html.escape(s, quote=True)

def lines(values, x, y, size, color, leading, anchor='start', family=BODY,
          weight='700', spacing='0'):
    return '\n'.join(
        f'<text x="{x}" y="{y + i*leading}" text-anchor="{anchor}" fill="{color}" '
        f'font-family="{family}" font-size="{size}" font-weight="{weight}" '
        f'letter-spacing="{spacing}">{esc(value)}</text>'
        for i, value in enumerate(values)
    )

def render(i, slide):
    image_uri = (ASSETS / f'{i:02d}-scene.png').resolve().as_uri()
    logo_uri = LOGO.resolve().as_uri()
    align = slide['align']
    x = 72 if align == 'left' else 1008
    anchor = 'start' if align == 'left' else 'end'
    panel = slide['panel']
    if panel == 'left':
        shade = '<rect width="760" height="1350" fill="url(#leftShade)"/>'
        text_y = 400
    elif panel == 'right':
        shade = '<rect x="320" width="760" height="1350" fill="url(#rightShade)"/>'
        text_y = 400
    else:
        shade = '<rect width="1080" height="780" fill="url(#topShade)"/>'
        text_y = 290
    headline_size = 68 if len(slide['headline']) < 4 else 62
    body_y = text_y + len(slide['headline']) * 79 + 54
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1080" height="1350" viewBox="0 0 1080 1350">
<defs>
  <linearGradient id="leftShade"><stop stop-color="#090908" stop-opacity=".97"/><stop offset=".72" stop-color="#090908" stop-opacity=".72"/><stop offset="1" stop-color="#090908" stop-opacity="0"/></linearGradient>
  <linearGradient id="rightShade" x1="1" x2="0"><stop stop-color="#090908" stop-opacity=".97"/><stop offset=".72" stop-color="#090908" stop-opacity=".72"/><stop offset="1" stop-color="#090908" stop-opacity="0"/></linearGradient>
  <linearGradient id="topShade" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#090908" stop-opacity=".97"/><stop offset=".75" stop-color="#090908" stop-opacity=".72"/><stop offset="1" stop-color="#090908" stop-opacity="0"/></linearGradient>
  <linearGradient id="bottomFade" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#090908" stop-opacity="0"/><stop offset="1" stop-color="#090908" stop-opacity=".84"/></linearGradient>
  <filter id="grain"><feTurbulence baseFrequency=".78" numOctaves="3" seed="{i+40}" type="fractalNoise"/><feComponentTransfer><feFuncA type="table" tableValues="0 .035"/></feComponentTransfer></filter>
</defs>
<rect width="1080" height="1350" fill="{INK}"/>
<image x="0" y="0" width="1080" height="1350" preserveAspectRatio="xMidYMid slice" xlink:href="{image_uri}"/>
{shade}
<rect y="1050" width="1080" height="300" fill="url(#bottomFade)"/>
<path d="M45 34 H1035 M45 1316 H1035" stroke="{GOLD}" stroke-width="1" opacity=".62"/>
<image x="52" y="43" width="118" height="118" preserveAspectRatio="xMidYMid meet" xlink:href="{logo_uri}"/>
<text x="1018" y="75" text-anchor="end" fill="{MUTED}" font-family="{BODY}" font-size="15" letter-spacing="2">{i:02d} / 08 · {esc(slide['role'].upper())}</text>
{lines([slide['kicker']], x, text_y-78, 19, GOLD2, 1, anchor, BODY, '700', '3')}
{lines(slide['headline'], x, text_y, headline_size, BONE, 79, anchor, HEAD, '700', '-1')}
<path d="M{72 if align == 'left' else 700} {body_y-34} H{380 if align == 'left' else 1008}" stroke="{GOLD}" stroke-width="3"/>
{lines(slide['body'], x, body_y+18, 24, BONE, 37, anchor, BODY, '600', '.2')}
'''
    if slide.get('prompt'):
        svg += f'<rect x="72" y="1032" width="520" height="66" fill="{GOLD}"/>'
        svg += lines([slide['prompt']], 332, 1074, 17, INK, 1, 'middle', BODY, '700', '.8')
    svg += f'''<text x="62" y="1288" fill="{MUTED}" font-family="{BODY}" font-size="13" font-weight="700" letter-spacing="1.8">DISCIPLINE · ACCOUNTABILITY · CONSISTENCY</text>
<rect width="1080" height="1350" filter="url(#grain)" opacity=".42" pointer-events="none"/>
</svg>'''
    return svg

for i, slide in enumerate(slides, 1):
    name = slide['role'].replace(' ', '-').replace('+', 'and')
    (OUT / f'{i:02d}-{name}.svg').write_text(render(i, slide), encoding='utf-8')

copy = []
for i, slide in enumerate(slides, 1):
    copy.append(f'{i:02d} — {slide["role"].upper()}')
    copy.append(slide['kicker'])
    copy.extend(slide['headline'])
    copy.extend(slide['body'])
    if slide.get('prompt'):
        copy.append(slide['prompt'])
    copy.append('')
(OUT / 'copy.txt').write_text('\n'.join(copy), encoding='utf-8')

(OUT / 'caption.txt').write_text('''Motivation can get you started. A routine tells you what to do after the feeling disappears.

Without a routine, the same decisions return every day:

When will I train?
What will I eat?
Do I have enough energy?
Should I wait until tomorrow?

Every decision creates another opportunity to negotiate with yourself.

A useful routine removes some of that friction. It gives your day a cue, a time and a clear first action. It also creates evidence. Each time you follow through, you strengthen the belief that your word means something.

The routine still has to fit your real life. A schedule built for perfect days will collapse during a difficult week. Build around your actual responsibilities, and reduce the minimum when necessary without abandoning the standard completely.

Start with one repeatable action. Choose its cue and time, then complete it for the next seven days.

What will your one action be?

#CutThroatDiscipline #DailyRoutine #FitnessDiscipline #BuildBetterHabits #Consistency

importance of routine, fitness routine, how to become consistent, daily discipline, building better habits, workout consistency, reduce decision fatigue, accountability habits
''', encoding='utf-8')

(OUT / 'production-notes.txt').write_text('''CUT THROAT DISCIPLINE — WHY ROUTINE MATTERS

Format: 8 individual 1080 × 1350 sRGB PNG slides (Instagram 4:5).
Objective: educational authority and reflection; no coaching offer.
Art direction: original cinematic 3D scenes in obsidian, charcoal, muted gold and bone.
Typography: Latin Modern Sans Demi Cond is the temporary Heading Now substitute; Liberation Sans is the temporary Gotham substitute because the licensed font files are not installed.
Brand lockup: cinematic CTD monogram and wordmark at the top-left of every slide.
Footer standard: DISCIPLINE · ACCOUNTABILITY · CONSISTENCY.
Sequence: hook, direction, resistance, preparation, evidence, difficult days, real-life fit, seven-day action prompt.
CTA: choose one repeatable action and name it; no sales CTA.
''', encoding='utf-8')

print(OUT)
