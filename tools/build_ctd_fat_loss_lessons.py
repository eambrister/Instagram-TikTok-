from pathlib import Path
import build_ctd_typography_carousel as base

OUT = Path('/workspace/Instagram-TikTok-/outputs/ctd-fat-loss-lessons')
OUT.mkdir(parents=True, exist_ok=True)

slides = [
    {
        'role': 'hook',
        'headline': [('I LOST', base.BONE), ('80 POUNDS.', base.GOLD2), ('THESE LESSONS', base.BONE), ('KEPT IT OFF.', base.GOLD2)],
        'body': ['MY RESULT IS PERSONAL. THE PRINCIPLES BEHIND IT', 'CAN STILL HELP YOU BUILD YOUR OWN SYSTEM.'],
        'layout': 'hero',
        'headline_size': 80,
        'headline_step': 100,
    },
    {
        'role': 'lesson 01',
        'headline': [('MOTIVATION', base.BONE), ('STARTED IT.', base.GOLD2)],
        'body': ['A REPEATABLE ROUTINE HAD TO CARRY THE PROCESS', 'AFTER THE INITIAL EXCITEMENT DISAPPEARED.'],
        'layout': 'left',
    },
    {
        'role': 'lesson 02',
        'headline': [('THE PLAN HAD TO', base.BONE), ('FIT REAL LIFE.', base.GOLD2)],
        'steps': ['REAL SCHEDULE', 'REAL ENERGY', 'REAL FOOD', 'REAL LIMITS', 'REAL ADJUSTMENTS', 'REPEATED ACTION'],
        'layout': 'cycle',
    },
    {
        'role': 'lesson 03',
        'headline': [('ONE BAD DAY', base.BONE), ('WASN\'T FAILURE.', base.GOLD2)],
        'body': ['THE REAL DAMAGE CAME FROM USING ONE MISS AS', 'PERMISSION TO ABANDON THE REST OF THE WEEK.'],
        'layout': 'arch',
    },
    {
        'role': 'lesson 04',
        'headline': [('HONEST TRACKING', base.BONE), ('BEAT GUESSING.', base.GOLD2)],
        'body': ['I NEEDED TO SEE WHAT I WAS ACTUALLY DOING—', 'NOT WHAT I INTENDED TO DO OR REMEMBERED DOING.'],
        'layout': 'ledger',
    },
    {
        'role': 'lesson 05',
        'headline': [('ADJUSTMENT WORKED BETTER', base.BONE), ('THAN PUNISHMENT.', base.GOLD2)],
        'body': ['WHEN PROGRESS OR EXECUTION CHANGED, THE ANSWER WAS', 'TO REVIEW THE SYSTEM—NOT ATTACK MYSELF.'],
        'layout': 'split',
        'headline_size': 44,
    },
    {
        'role': 'lesson 06',
        'headline': [('CONSISTENCY HAD TO', base.BONE), ('SURVIVE IMPERFECT', base.BONE), ('DAYS.', base.GOLD2)],
        'body': ['THE STANDARD WASN\'T PERFECTION.', '', 'THE STANDARD WAS RETURNING TO THE NEXT ACTION.'],
        'layout': 'reset',
    },
    {
        'role': 'lesson 07',
        'headline': [('MAINTENANCE IS PART', base.BONE), ('OF THE TRANSFORMATION.', base.GOLD2)],
        'steps': ['KEEP THE ROUTINES', 'NOTICE OLD PATTERNS', 'ADJUST WITH EVIDENCE', 'PROTECT RECOVERY', 'RETURN QUICKLY'],
        'layout': 'offer',
        'headline_size': 52,
    },
    {
        'role': 'reflection',
        'headline': [('DON\'T COPY', base.BONE), ('MY RESULT.', base.GOLD2)],
        'body': ['BUILD THE SYSTEM YOUR LIFE CAN REPEAT.', '', 'SAVE THIS. THEN CHOOSE THE ONE LESSON', 'YOU NEED TO PRACTICE THIS WEEK.', '', 'YOUR STARTING POINT AND RESULTS WILL BE YOUR OWN.'],
        'layout': 'reflection',
    },
]

for i, slide in enumerate(slides, 1):
    (OUT / f'{i:02d}-{slide["role"].replace(" ", "-")}.svg').write_text(base.render(i, slide), encoding='utf-8')

transcript = []
for i, slide in enumerate(slides, 1):
    transcript.append(f'{i:02d} — {slide["role"].upper()}')
    transcript.extend(line[0] for line in slide.get('headline', []))
    transcript.extend(slide.get('body', []))
    transcript.extend(slide.get('steps', []))
    transcript.append('')
(OUT / 'copy.txt').write_text('\n'.join(transcript), encoding='utf-8')

(OUT / 'caption.txt').write_text('''Losing 80 pounds changed my body. Keeping it off changed how I understand discipline.

Motivation helped me begin, but it could not carry nearly two years of work or everything that came afterward.

I needed a routine that fit real life. I needed honest tracking. I needed to stop treating one difficult day like proof that the entire week was lost.

The most useful shift was learning to adjust instead of punish myself.

When execution slipped, I had to identify why. When circumstances changed, the plan had to change with them. When I missed, the next action mattered more than the guilt surrounding the previous one.

Maintenance taught me that transformation does not end when the scale reaches a particular number. The routines still need protection. Old patterns still need attention. The standard still needs to be practiced.

This is my experience, not a promise that another person will achieve the same result. Your starting point, health, circumstances, timeline, and outcome will be your own.

Which lesson do you need to practice this week?

#CutThroatDiscipline #WeightLossJourney #FitnessDiscipline #WorkoutConsistency #SustainableFitness

80 pound weight loss journey, sustainable weight loss habits, maintaining weight loss, fitness consistency, realistic fitness routine, workout accountability, discipline and motivation, recovering after missed workouts, long term fitness habits, fitness journey Bahamas, healthy routine, stop restarting fitness
''', encoding='utf-8')

(OUT / 'production-notes.txt').write_text('''CUT THROAT DISCIPLINE — FAT-LOSS LESSONS\n\nFormat: 9 individual 1080 x 1080 sRGB PNG slides.\nObjective: trust and education through Edison's documented personal experience.\nArt direction: cinematic black, bone, and muted-gold typography based on the supplied V3 guides.\nFonts: DejaVu Serif Bold and DejaVu Sans, used as available substitutes.\nClaim boundary: the 80-pound loss and maintenance are presented as personal experience, not a typical or guaranteed result.\nCTA: save the post and choose one lesson to practice; no coaching offer.\n''', encoding='utf-8')
