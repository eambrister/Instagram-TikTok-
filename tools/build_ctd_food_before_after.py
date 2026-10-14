from pathlib import Path
import html
import shutil

ROOT = Path('/workspace/Instagram-TikTok-')
OUT = ROOT / 'outputs/ctd-food-before-after'
OUT.mkdir(parents=True, exist_ok=True)

BEFORE_SOURCE = Path('/workspace/generated_images/exec-f8ec153f-bb85-49f3-8920-a13691a6aa30.png')
NOW_SOURCE = Path('/workspace/generated_images/exec-193111c6-97f7-46d7-bcf1-89e0404e9c4c.png')
BEFORE = OUT / 'source-before-sheet.png'
NOW = OUT / 'source-now-sheet.png'
shutil.copy2(BEFORE_SOURCE, BEFORE)
shutil.copy2(NOW_SOURCE, NOW)

INK = '#0A0A09'
BONE = '#EEE9DF'
MUTED = '#B6B0A5'
GOLD = '#BE995C'
GOLD2 = '#D9BC78'

def esc(value):
    return html.escape(value, quote=True)

def text(lines, x, y, size, color=BONE, leading=None, anchor='start', serif=False,
         weight=700, spacing=0):
    leading = leading or int(size * 1.18)
    family = 'DejaVu Serif' if serif else 'DejaVu Sans'
    return '\n'.join(
        f'<text x="{x}" y="{y + i * leading}" text-anchor="{anchor}" fill="{color}" '
        f'font-family="{family}" font-size="{size}" font-weight="{weight}" '
        f'letter-spacing="{spacing}">{esc(line)}</text>'
        for i, line in enumerate(lines)
    )

def frame(i, role, media=''):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1080" height="1080" viewBox="0 0 1080 1080">
<defs>
  <radialGradient id="bg" cx="72%" cy="18%" r="95%"><stop offset="0" stop-color="#272219"/><stop offset=".38" stop-color="#171511"/><stop offset="1" stop-color="{INK}"/></radialGradient>
  <linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#0A0A09" stop-opacity=".12"/><stop offset=".62" stop-color="#0A0A09" stop-opacity=".18"/><stop offset="1" stop-color="#0A0A09" stop-opacity=".9"/></linearGradient>
  <filter id="grain"><feTurbulence baseFrequency=".72" numOctaves="3" seed="{i+29}" type="fractalNoise"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 .045"/></feComponentTransfer></filter>
</defs>
<rect width="1080" height="1080" fill="url(#bg)"/>
{media}
'''

def chrome(i, role, dark=True):
    color = BONE if dark else INK
    muted = MUTED if dark else '#48443D'
    return f'''<path d="M45 34 H1035 M45 1046 H1035" stroke="{GOLD}" stroke-width="1" opacity=".55"/>
<text x="62" y="75" fill="{GOLD2}" font-family="DejaVu Sans" font-size="17" font-weight="700" letter-spacing="3">CUT THROAT DISCIPLINE</text>
<text x="1018" y="75" text-anchor="end" fill="{muted}" font-family="DejaVu Sans" font-size="15" letter-spacing="2">{i:02d} / 09 · {esc(role.upper())}</text>
<text x="62" y="1020" fill="{muted}" font-family="DejaVu Sans" font-size="14" letter-spacing="2">COMMIT · TRACK · EXECUTE</text>
<rect width="1080" height="1080" filter="url(#grain)" opacity=".33" pointer-events="none"/>
</svg>'''

def image_rect(path, x, y, w, h, clip_id, opacity=1):
    uri = path.resolve().as_uri()
    return f'''<clipPath id="{clip_id}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>
<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" xlink:href="{uri}" clip-path="url(#{clip_id})" opacity="{opacity}"/>'''

def cropped_image(path, sx, sy, sw, sh, x, y, w, h, clip_id):
    # Source sheets are 1254 square. Scale and offset to fill the target rectangle.
    scale = max(w / sw, h / sh)
    ix, iy = x - sx * scale, y - sy * scale
    uri = path.resolve().as_uri()
    return f'''<clipPath id="{clip_id}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2"/></clipPath>
<image x="{ix:.2f}" y="{iy:.2f}" width="{1254*scale:.2f}" height="{1254*scale:.2f}" preserveAspectRatio="none" xlink:href="{uri}" clip-path="url(#{clip_id})"/>'''

slides = []

# 01 — split photographic hook
defs = image_rect(BEFORE, 0, 0, 540, 1080, 'left') + image_rect(NOW, 540, 0, 540, 1080, 'right')
s = frame(1, 'hook', defs)
s += '<rect width="1080" height="1080" fill="#0A0A09" opacity=".38"/><rect y="600" width="1080" height="480" fill="url(#shade)"/>'
s += '<path d="M540 90 V990" stroke="#D9BC78" stroke-width="2" opacity=".75"/>'
s += text(['BEFORE'], 88, 155, 21, GOLD2, spacing=4) + text(['NOW'], 992, 155, 21, GOLD2, anchor='end', spacing=4)
s += text(['WHAT I ATE', 'AT 222 LBS'], 540, 690, 72, BONE, 82, 'middle', True)
s += text(['VS WHAT I EAT NOW'], 540, 870, 51, GOLD2, anchor='middle', serif=True)
s += text(['THE FOOD DEFAULTS I CHANGED WHILE LOSING 80 POUNDS—AND KEEPING IT OFF.'], 540, 940, 19, BONE, anchor='middle', spacing=.3)
s += chrome(1, 'hook')
slides.append(('01-hook', s))

# 02 — context
s = frame(2, 'context')
s += text(['THIS ISN’T A LIST OF', '“GOOD” AND “BAD” FOODS.'], 72, 285, 61, BONE, 76, serif=True)
s += '<path d="M72 470 H1008" stroke="#BE995C" stroke-width="3"/>'
s += text(['MY RESULTS CAME FROM CHANGING THE OVERALL PATTERN:'], 72, 545, 24, GOLD2, spacing=1)
items = ['PORTIONS + FREQUENCY', 'ADDED SUGAR', 'PROTEIN + PRODUCE', 'TOTAL CALORIES + MACROS']
for j, item in enumerate(items):
    yy = 645 + j * 76
    s += f'<circle cx="91" cy="{yy-8}" r="12" fill="none" stroke="{GOLD}" stroke-width="2"/>'
    s += text([item], 126, yy, 27, BONE, weight=600, spacing=.5)
s += chrome(2, 'context')
slides.append(('02-context', s))

# 03 — before sheet
defs = image_rect(BEFORE, 0, 160, 1080, 920, 'photo')
s = frame(3, 'before-pattern', defs)
s += '<rect y="150" width="1080" height="930" fill="url(#shade)"/>'
s += '<rect x="56" y="610" width="968" height="330" fill="#0A0A09" opacity=".82"/>'
s += text(['BEFORE:'], 74, 215, 23, GOLD2, spacing=4)
s += text(['THE OLD DEFAULTS'], 74, 710, 61, BONE, serif=True)
s += text(['RIBS · PEAS & RICE · COLESLAW · MACARONI'], 74, 800, 22, BONE, spacing=.7)
s += text(['SUSHI · SPRING ROLLS · QUESADILLAS · PIZZA · DESSERTS'], 74, 845, 20, MUTED, spacing=.4)
s += text(['THE PATTERN WAS EASY TO OVEREAT AND HARD FOR ME TO TRACK.'], 74, 905, 20, GOLD2, spacing=.4)
s += chrome(3, 'before pattern')
slides.append(('03-before-pattern', s))

# 04 — now sheet
defs = image_rect(NOW, 0, 160, 1080, 920, 'photo')
s = frame(4, 'current-pattern', defs)
s += '<rect y="150" width="1080" height="930" fill="url(#shade)"/>'
s += '<rect x="56" y="610" width="968" height="330" fill="#0A0A09" opacity=".82"/>'
s += text(['NOW:'], 74, 215, 23, GOLD2, spacing=4)
s += text(['SIMPLER DEFAULTS'], 74, 710, 61, BONE, serif=True)
s += text(['EGGS · OATMEAL · CREAM OF WHEAT · TUNA'], 74, 800, 22, BONE, spacing=.7)
s += text(['CHICKEN · GROUND BEEF · RICE · POTATOES · FRUIT · VEGETABLES'], 74, 845, 19, MUTED, spacing=.25)
s += text(['PROTEIN FIRST. PLANNED PORTIONS. EASIER TO REPEAT.'], 74, 905, 20, GOLD2, spacing=.4)
s += chrome(4, 'current pattern')
slides.append(('04-current-pattern', s))

# 05 — breakfast
defs = cropped_image(NOW, 627, 0, 627, 627, 590, 170, 430, 730, 'breakfast')
s = frame(5, 'breakfast', defs)
s += '<rect x="590" y="170" width="430" height="730" fill="#0A0A09" opacity=".17"/>'
s += text(['BREAKFAST'], 72, 205, 19, GOLD2, spacing=4)
s += text(['BEFORE'], 72, 310, 20, MUTED, spacing=3)
s += text(['LOADS OF WAFFLES', '+ PANCAKES WITH', 'SUGARY SYRUP'], 72, 385, 39, BONE, 50, serif=True)
s += '<path d="M72 575 H510" stroke="#BE995C" stroke-width="2"/>'
s += text(['NOW'], 72, 650, 20, GOLD2, spacing=3)
s += text(['SOMETIMES I SKIP IT.', 'OTHER DAYS: EGGS,', 'OATMEAL OR', 'CREAM OF WHEAT.'], 72, 715, 29, BONE, 40, weight=600)
s += text(['THE WIN WAS INTENTION—NOT BREAKFAST MAGIC.'], 72, 925, 17, GOLD2, spacing=.2)
s += chrome(5, 'breakfast')
slides.append(('05-breakfast', s))

# 06 — lunch and dinner comparison
defs = cropped_image(BEFORE, 0, 0, 627, 627, 56, 240, 456, 590, 'oldmeal') + cropped_image(NOW, 0, 627, 418, 627, 568, 240, 456, 590, 'newmeal')
s = frame(6, 'lunch + dinner', defs)
s += text(['LUNCH + DINNER'], 540, 170, 53, BONE, anchor='middle', serif=True)
s += '<rect x="56" y="760" width="456" height="170" fill="#0A0A09" opacity=".9"/><rect x="568" y="760" width="456" height="170" fill="#0A0A09" opacity=".9"/>'
s += text(['BEFORE'], 82, 812, 18, MUTED, spacing=3)
s += text(['LARGE COMBO PLATES', 'AND FREQUENT TAKEOUT'], 82, 858, 22, BONE, 33, weight=600)
s += text(['NOW'], 594, 812, 18, GOLD2, spacing=3)
s += text(['PROTEIN + A PLANNED', 'CARB OR VEGETABLES'], 594, 858, 22, BONE, 33, weight=600)
s += chrome(6, 'lunch + dinner')
slides.append(('06-lunch-dinner', s))

# 07 — snacks
defs = cropped_image(BEFORE, 418, 627, 418, 627, 56, 245, 456, 520, 'dessert') + cropped_image(NOW, 0, 0, 627, 627, 568, 245, 456, 520, 'fruit')
s = frame(7, 'snacks', defs)
s += text(['SNACKS'], 540, 175, 53, BONE, anchor='middle', serif=True)
s += text(['BEFORE'], 82, 830, 18, MUTED, spacing=3) + text(['SKITTLES, FRUIT SNACKS', '+ OTHER SWEETS'], 82, 875, 22, BONE, 33, weight=600)
s += text(['NOW'], 594, 830, 18, GOLD2, spacing=3) + text(['FRUIT—OR NO SNACK', 'WHEN I’M NOT HUNGRY'], 594, 875, 22, BONE, 33, weight=600)
s += chrome(7, 'snacks')
slides.append(('07-snacks', s))

# 08 — actual changes
defs = cropped_image(NOW, 836, 627, 418, 627, 650, 160, 374, 760, 'prep')
s = frame(8, 'what changed', defs)
s += text(['THE 3 BIGGEST', 'CHANGES I MADE'], 72, 245, 56, BONE, 68, serif=True)
changes = [('01', 'FOCUSED ON MORE', 'WHOLE FOODS'), ('02', 'ATE MORE FRUIT', '+ VEGETABLES'), ('03', 'PRIORITIZED', 'PROTEIN')]
for j, (num, a, b) in enumerate(changes):
    yy = 470 + j * 145
    s += text([num], 72, yy, 20, GOLD2, spacing=2)
    s += text([a, b], 126, yy, 26, BONE, 34, weight=600)
s += '<rect x="72" y="884" width="520" height="50" fill="#BE995C"/>'
s += text(['I ALSO TRACKED CALORIES + MACROS.'], 332, 916, 17, INK, anchor='middle', weight=700, spacing=.5)
s += chrome(8, 'what changed')
slides.append(('08-what-changed', s))

# 09 — reflection
s = frame(9, 'reflection')
s += '<rect x="80" y="125" width="920" height="815" fill="none" stroke="#BE995C" stroke-width="2" opacity=".65"/>'
s += text(['DON’T COPY', 'MY PLATE.'], 540, 315, 77, BONE, 91, 'middle', True)
s += text(['EXAMINE YOUR DEFAULTS.'], 540, 535, 46, GOLD2, anchor='middle', serif=True)
s += '<path d="M330 605 H750" stroke="#BE995C" stroke-width="3"/>'
s += text(['WHICH REPEATED MEAL, SNACK, DRINK', 'OR PORTION COULD YOU CHANGE THIS WEEK?'], 540, 690, 24, BONE, 38, 'middle', weight=600)
s += text(['MY EXPERIENCE IS PERSONAL—YOUR NEEDS AND RESULTS WILL BE YOUR OWN.'], 540, 850, 16, MUTED, anchor='middle', spacing=.35)
s += chrome(9, 'reflection')
slides.append(('09-reflection', s))

for name, svg in slides:
    (OUT / f'{name}.svg').write_text(svg, encoding='utf-8')

(OUT / 'copy.txt').write_text('''01 — HOOK
WHAT I ATE AT 222 LBS VS WHAT I EAT NOW
The food defaults I changed while losing 80 pounds—and keeping it off.

02 — CONTEXT
This isn’t a list of “good” and “bad” foods.
My results came from changing the overall pattern: portions and frequency, added sugar, protein and produce, total calories and macros.

03 — BEFORE PATTERN
Ribs, peas and rice, coleslaw, macaroni; sushi, spring rolls, quesadillas, pizza and desserts.
The pattern was easy to overeat and hard for me to track.

04 — CURRENT PATTERN
Eggs, oatmeal, cream of wheat, tuna, chicken, ground beef, rice, potatoes, fruit and vegetables.
Protein first. Planned portions. Easier to repeat.

05 — BREAKFAST
Before: loads of waffles and pancakes with sugary syrup.
Now: sometimes I skip it. Other days: eggs, oatmeal or cream of wheat.
The win was intention—not breakfast magic.

06 — LUNCH + DINNER
Before: large combo plates and frequent takeout.
Now: protein plus a planned carb or vegetables.

07 — SNACKS
Before: Skittles, fruit snacks and other sweets.
Now: fruit—or no snack when I’m not hungry.

08 — WHAT CHANGED
1. Focused on more whole foods.
2. Ate more fruit and vegetables.
3. Prioritized protein.
I also tracked calories and macros.

09 — REFLECTION
Don’t copy my plate. Examine your defaults.
Which repeated meal, snack, drink or portion could you change this week?
My experience is personal—your needs and results will be your own.
''', encoding='utf-8')

(OUT / 'caption.txt').write_text('''My diet at 222 pounds was not defined by one “bad” food. It was the pattern I kept repeating.

Breakfast often meant loads of waffles or pancakes with sugary syrup. Lunch and dinner could be ribs, peas and rice, coleslaw and macaroni—or sushi, spring rolls, quesadillas and pizza. Snacks were usually Skittles, fruit snacks and other sweets.

None of those foods alone explains my former weight. For me, the combination of portions, frequency, added sugar and total calories made the pattern easy to overeat and difficult to track.

Now my regular meals are simpler: eggs, oatmeal, cream of wheat, rice, ground beef, potatoes, chicken, tuna, vegetables and fruit. I prioritize protein, plan portions and track calories and macros instead of guessing.

I chose to remove sweets because that approach works better for me. You do not have to copy that choice, and skipping breakfast is not required for fat loss.

Don’t copy my plate. Examine your defaults.

Which repeated meal, snack, drink or portion could you change this week?

#CutThroatDiscipline #WeightLossJourney #NutritionHabits #FitnessDiscipline #SustainableFitness

80 pound weight loss journey, foods for weight loss, sustainable nutrition habits, high protein meals, calorie and macro tracking, meal prep ideas, fitness discipline, Bahamas fitness journey
''', encoding='utf-8')

(OUT / 'production-notes.txt').write_text('''CUT THROAT DISCIPLINE — FOOD BEFORE VS NOW

Format: 9 individual 1080 x 1080 sRGB PNG slides.
Objective: personal nutrition education and trust building; no coaching offer.
Art direction: cinematic black, bone and muted gold with documentary food photography.
Sequence: hook, context, old pattern, current pattern, breakfast, lunch/dinner, snacks, key changes, reflection.
Claim boundary: the 80-pound loss and maintenance are Edison's personal experience, not a promised or typical outcome.
Nutrition boundary: the carousel does not call foods universally good or bad, prescribe skipping breakfast, or present Edison's plate as an individualized plan.
CTA: examine one repeated food default; no sales CTA.
Source assets: two editorial contact sheets prepared from the user's supplied food photographs are included in this folder.
''', encoding='utf-8')

print(OUT)
