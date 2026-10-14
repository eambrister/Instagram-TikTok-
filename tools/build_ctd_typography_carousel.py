from pathlib import Path
import html

OUT = Path('/workspace/Instagram-TikTok-/outputs/ctd-execution-cycle')
OUT.mkdir(parents=True, exist_ok=True)

INK = '#0A0A09'
INK2 = '#171511'
BONE = '#EEE9DF'
MUTED = '#B6B0A5'
GOLD = '#BE995C'
GOLD2 = '#D9BC78'

slides = [
    {
        'role': 'hook',
        'headline': [('STOP', BONE), ('RESTARTING.', GOLD2), ('START', BONE), ('EXECUTING.', GOLD2)],
        'body': ['A FITNESS PLAN ONLY WORKS WHEN YOU CAN FOLLOW IT', 'AFTER MOTIVATION FADES.'],
        'layout': 'hero',
    },
    {
        'role': 'diagnosis',
        'headline': [('YOU DON\'T NEED', BONE), ('MORE MOTIVATION.', GOLD2)],
        'body': ['YOU NEED REALISTIC COMMITMENTS, HONEST TRACKING,', 'AND A SYSTEM THAT SURVIVES DIFFICULT WEEKS.'],
        'layout': 'left',
    },
    {
        'role': 'mechanism',
        'headline': [('THE CTD', BONE), ('EXECUTION CYCLE', GOLD2)],
        'steps': ['COMMIT', 'TRACK', 'DIAGNOSE', 'ADJUST', 'EXECUTE AGAIN', 'REVIEW'],
        'layout': 'cycle',
    },
    {
        'role': 'commit',
        'headline': [('SET A STANDARD', BONE), ('YOU CAN EXECUTE.', GOLD2)],
        'body': ['YOUR TRAINING SCHEDULE, NUTRITION TARGETS, AND WEEKLY', 'COMMITMENTS MUST FIT YOUR ACTUAL LIFE—NOT AN', 'IMAGINARY PERFECT WEEK.'],
        'layout': 'arch',
    },
    {
        'role': 'track',
        'headline': [('MAKE YOUR', BONE), ('EXECUTION VISIBLE.', GOLD2)],
        'body': ['DAILY CHECK-INS REVEAL WHAT YOU COMPLETED,', 'WHAT YOU MISSED, AND WHERE YOUR PLAN', 'BEGINS TO BREAK DOWN.'],
        'layout': 'ledger',
    },
    {
        'role': 'adjust',
        'headline': [('STOP CALLING EVERYTHING', BONE), ('A MOTIVATION PROBLEM.', GOLD2)],
        'body': ['WE IDENTIFY THE REAL OBSTACLE AND ADJUST THE PLAN,', 'ENVIRONMENT, CALORIES, MACROS, OR EXPECTATIONS', 'WHEN APPROPRIATE.'],
        'layout': 'split',
    },
    {
        'role': 'execute again',
        'headline': [('ONE MISS DOESN\'T', BONE), ('REQUIRE ANOTHER', BONE), ('MONDAY.', GOLD2)],
        'body': ['COMPLETE THE NEXT SCHEDULED ACTION.', '', 'DISCIPLINE IS MEASURED BY HOW QUICKLY YOU RETURN.'],
        'layout': 'reset',
    },
    {
        'role': 'offer',
        'headline': [('DIRECT SUPPORT.', BONE), ('CLEAR EXPECTATIONS.', GOLD2)],
        'steps': ['GYM OR HOME TRAINING PLAN', 'CALORIE + MACRO TARGETS', 'DAILY ACCOUNTABILITY CHECK-INS', 'WEEKLY PROGRESS ADJUSTMENTS', 'ONE 30-MINUTE REVIEW CALL'],
        'layout': 'offer',
    },
    {
        'role': 'invitation',
        'headline': [('READY TO STOP', BONE), ('RESTARTING?', GOLD2)],
        'body': ['FOUNDING COACHING', '$100 USD/BSD PER FOUR WEEKS', '', 'FOR ADULTS PREPARED TO TRACK, COMMUNICATE, AND EXECUTE.', '', 'APPLY AT THE LINK IN BIO.'],
        'layout': 'cta',
    },
]


def esc(s):
    return html.escape(s, quote=True)


def tspan_lines(lines, x, y, size, color, leading, anchor='start', family='sans', weight='400', spacing='0'):
    fam = 'DejaVu Serif' if family == 'serif' else 'DejaVu Sans'
    body = []
    for i, line in enumerate(lines):
        body.append(f'<text x="{x}" y="{y + i*leading}" text-anchor="{anchor}" fill="{color}" font-family="{fam}" font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}">{esc(line)}</text>')
    return '\n'.join(body)


def base(i, role):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
<defs>
  <radialGradient id="bg" cx="72%" cy="18%" r="95%"><stop offset="0" stop-color="#272219"/><stop offset=".38" stop-color="{INK2}"/><stop offset="1" stop-color="{INK}"/></radialGradient>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{GOLD2}"/><stop offset="1" stop-color="#8B6737"/></linearGradient>
  <filter id="grain"><feTurbulence baseFrequency=".75" numOctaves="3" seed="{i+17}" type="fractalNoise"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 .055"/></feComponentTransfer></filter>
</defs>
<rect width="1080" height="1080" fill="url(#bg)"/>
<rect width="1080" height="1080" filter="url(#grain)" opacity=".42"/>
<path d="M45 34 H1035 M45 1046 H1035" stroke="{GOLD}" stroke-width="1" opacity=".42"/>
<text x="62" y="75" fill="{GOLD}" font-family="DejaVu Sans" font-size="17" font-weight="700" letter-spacing="3">CUT THROAT DISCIPLINE</text>
<text x="1018" y="75" text-anchor="end" fill="{MUTED}" font-family="DejaVu Sans" font-size="15" letter-spacing="2">{i:02d} / 09 · {esc(role.upper())}</text>
'''


def finish():
    return f'<text x="62" y="1020" fill="{MUTED}" font-family="DejaVu Sans" font-size="14" letter-spacing="2">COMMIT · TRACK · EXECUTE</text></svg>'


def render(i, s):
    v = [base(i, s['role'])]
    layout = s['layout']
    if layout == 'hero':
        v += ['<circle cx="878" cy="253" r="126" fill="none" stroke="url(#gold)" stroke-width="2" opacity=".55"/>',
              '<path d="M760 126 L1022 430" stroke="#BE995C" stroke-width="18" opacity=".12"/>']
        y = 290
        for n, c in s['headline']:
            v.append(tspan_lines([n], 72, y, 112, c, 1, family='serif', weight='700', spacing='-2'))
            y += 126
        v.append('<path d="M72 820 H390" stroke="#BE995C" stroke-width="4"/>')
        v.append(tspan_lines(s['body'], 72, 875, 25, MUTED, 38, weight='500', spacing='1'))
    elif layout == 'left':
        v += ['<circle cx="920" cy="536" r="268" fill="none" stroke="#BE995C" stroke-width="2" opacity=".28"/>',
              '<circle cx="920" cy="536" r="207" fill="none" stroke="#EEE9DF" stroke-width="1" opacity=".12"/>',
              '<path d="M824 268 V805" stroke="#BE995C" stroke-width="7" opacity=".4"/>']
        y=330
        for n,c in s['headline']:
            v.append(tspan_lines([n],72,y,76,c,1,family='serif',weight='700',spacing='-1'))
            y+=92
        v.append(tspan_lines(s['body'],72,600,27,MUTED,42,weight='500',spacing='.5'))
    elif layout == 'cycle':
        v.append(tspan_lines([x[0] for x in s['headline']],540,230,74,BONE,88,anchor='middle',family='serif',weight='700'))
        v.append('<path d="M190 388 H890" stroke="#BE995C" stroke-width="2"/>')
        for j, step in enumerate(s['steps']):
            col=j%2; row=j//2; x=180+col*455; y=500+row*145
            v.append(f'<circle cx="{x}" cy="{y-8}" r="31" fill="none" stroke="{GOLD}" stroke-width="2"/>')
            v.append(tspan_lines([str(j+1).zfill(2)],x,y,18,GOLD,1,anchor='middle',weight='700'))
            v.append(tspan_lines([step],x+58,y,30,BONE,1,weight='700',spacing='1'))
    elif layout == 'arch':
        v.append('<path d="M672 905 V398 A178 178 0 0 1 1028 398 V905" fill="none" stroke="#BE995C" stroke-width="3" opacity=".42"/>')
        v.append('<path d="M727 905 V432 A123 123 0 0 1 973 432 V905" fill="#BE995C" opacity=".055"/>')
        y=300
        for n,c in s['headline']:
            v.append(tspan_lines([n],72,y,72,c,1,family='serif',weight='700'))
            y+=86
        v.append(tspan_lines(s['body'],72,605,26,MUTED,43,weight='500',spacing='.4'))
    elif layout == 'ledger':
        for y in range(340,900,82): v.append(f'<path d="M620 {y} H1010" stroke="#EEE9DF" stroke-width="1" opacity=".12"/>')
        for x in [690,850,970]: v.append(f'<path d="M{x} 290 V900" stroke="#BE995C" stroke-width="1" opacity=".17"/>')
        y=300
        for n,c in s['headline']:
            v.append(tspan_lines([n],72,y,72,c,1,family='serif',weight='700'))
            y+=88
        v.append(tspan_lines(s['body'],72,610,27,MUTED,44,weight='500'))
    elif layout == 'split':
        v.append('<path d="M540 164 V922" stroke="#BE995C" stroke-width="2" opacity=".55"/>')
        v.append('<text x="820" y="570" text-anchor="middle" fill="#BE995C" opacity=".12" font-family="DejaVu Serif" font-size="410" font-weight="700">?</text>')
        y=285
        for n,c in s['headline']:
            v.append(tspan_lines([n],72,y,55,c,1,family='serif',weight='700'))
            y+=72
        v.append(tspan_lines(s['body'],72,650,23,MUTED,39,weight='500'))
    elif layout == 'reset':
        v.append('<text x="540" y="770" text-anchor="middle" fill="#BE995C" opacity=".075" font-family="DejaVu Serif" font-size="480" font-weight="700">1</text>')
        y=285
        for n,c in s['headline']:
            v.append(tspan_lines([n],540,y,65,c,1,anchor='middle',family='serif',weight='700'))
            y+=82
        v.append('<path d="M330 505 H750" stroke="#BE995C" stroke-width="3"/>')
        lines=[x for x in s['body'] if x]
        v.append(tspan_lines(lines,540,620,25,MUTED,76,anchor='middle',weight='500',spacing='.5'))
    elif layout == 'offer':
        y=250
        for n,c in s['headline']:
            v.append(tspan_lines([n],72,y,70,c,1,family='serif',weight='700'))
            y+=85
        v.append('<path d="M72 405 H1008" stroke="#BE995C" stroke-width="2"/>')
        for j,step in enumerate(s['steps']):
            y=505+j*88
            v.append(f'<rect x="74" y="{y-23}" width="30" height="30" fill="none" stroke="{GOLD}" stroke-width="2"/>')
            v.append(f'<path d="M82 {y-8} l8 8 17 -21" fill="none" stroke="{GOLD2}" stroke-width="3"/>')
            v.append(tspan_lines([step],135,y,27,BONE,1,weight='600',spacing='.5'))
    elif layout == 'cta':
        v.append('<rect x="80" y="125" width="920" height="815" fill="none" stroke="#BE995C" stroke-width="2" opacity=".6"/>')
        y=275
        for n,c in s['headline']:
            v.append(tspan_lines([n],540,y,72,c,1,anchor='middle',family='serif',weight='700'))
            y+=86
        body=s['body']
        v.append(tspan_lines([body[0]],540,500,22,MUTED,1,anchor='middle',weight='700',spacing='3'))
        v.append(tspan_lines([body[1]],540,565,38,GOLD2,1,anchor='middle',family='serif',weight='700'))
        v.append(tspan_lines([body[3]],540,690,20,MUTED,1,anchor='middle',weight='500',spacing='.6'))
        v.append('<rect x="328" y="766" width="424" height="75" fill="#BE995C"/>')
        v.append(tspan_lines([body[5]],540,815,22,INK,1,anchor='middle',weight='700',spacing='1.5'))
    v.append(finish())
    return '\n'.join(v)


for i, slide in enumerate(slides, 1):
    (OUT / f'{i:02d}-{slide["role"].replace(" ", "-")}.svg').write_text(render(i, slide), encoding='utf-8')

copy = []
for i, s in enumerate(slides, 1):
    copy.append(f'{i:02d} — {s["role"].upper()}')
    copy.extend(x[0] for x in s.get('headline', []))
    copy.extend(s.get('body', []))
    copy.extend(s.get('steps', []))
    copy.append('')
(OUT / 'copy.txt').write_text('\n'.join(copy), encoding='utf-8')

(OUT / 'production-notes.txt').write_text('''CUT THROAT DISCIPLINE — TYPOGRAPHY CAROUSEL\n\nFormat: 9 individual 1080 x 1080 sRGB PNG slides.\nArt direction: cinematic black, bone, and muted-gold typography system based on the supplied V3 guides.\nFonts: DejaVu Serif Bold and DejaVu Sans, used as available substitutes.\nImagery: typography and vector geometry only; no generated people, claims, testimonials, or photographic evidence.\nCTA: website application through the link in bio.\nPrice: founding coaching at $100 USD/BSD per four weeks.\n''', encoding='utf-8')
