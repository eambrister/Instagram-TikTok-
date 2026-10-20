#!/usr/bin/env python3
"""Render the nine-slide Holiday Unholy Trinity carousel."""
from pathlib import Path
from base64 import b64encode
from zipfile import ZipFile, ZIP_DEFLATED
import html, os, shutil, subprocess, tempfile
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/ctd-holiday-unholy-trinity"
SCENES = OUT / "scene-assets"
LOGO = OUT / "ctd-cinematic-logo.png"
FONT_DIR = ROOT / "brand/fonts"
HEAD_FONT = FONT_DIR / "BarlowCondensed-ExtraBold.ttf"
BODY_MED = FONT_DIR / "Montserrat-Medium.ttf"
BODY_BOLD = FONT_DIR / "Montserrat-Bold.ttf"
W, H = 1080, 1350
INK, WHITE, SILVER = "#090A0C", "#F3EFE6", "#AEB3BA"
GOLD, CRIMSON = "#D6A928", "#8D1721"
HEAD, BODY = "Barlow Condensed", "Montserrat"
FOOTER = "DISCIPLINE - ACCOUNTABILITY - CONSISTENCY"

slides = [
 {"slug":"hook","scene":"01-cover.png","kicker":"THE SEASONAL WARNING","headline":["THE HOLIDAY","UNHOLY TRINITY"],"gold":[1],
  "sub":"OCTOBER. NOVEMBER. DECEMBER.","body":["Three celebrations can become one long excuse", "to abandon the standards you built all year."]},
 {"slug":"ninety-day-slide","scene":"02-calendar.png","kicker":"THE REAL THREAT","headline":["ONE MEAL ISN'T","THE PROBLEM.","THE 90-DAY SLIDE IS."],"gold":[2],
  "sub":"REPEATED EXCEPTIONS BECOME A NEW ROUTINE.","body":["Training fades. Movement drops. Sleep suffers.","January inherits the consequences."]},
 {"slug":"october","scene":"03-halloween.png","kicker":"PHASE 01  /  OCTOBER","headline":["HALLOWEEN","OPENS THE DOOR."],"gold":[1],
  "sub":"TEMPTATION BECOMES CONSTANT.","body":["Candy stays visible. Parties multiply.","One missed workout becomes “I'll restart Monday.”"]},
 {"slug":"november","scene":"04-thanksgiving.png","kicker":"PHASE 02  /  NOVEMBER","headline":["EXCESS STARTS","TO FEEL MANDATORY."],"gold":[1],
  "sub":"THE MEAL ISN'T THE PROBLEM.","body":["The celebration becomes a weekend.","The weekend becomes another postponed week."]},
 {"slug":"december","scene":"05-christmas.png","kicker":"PHASE 03  /  DECEMBER","headline":["DECEMBER FINISHES","WHAT OCTOBER STARTED."],"gold":[1],
  "sub":"THEN JANUARY GETS BLAMED.","body":["Parties. Alcohol. Travel. Desserts.","Poor sleep and another month of skipped sessions."]},
 {"slug":"two-paths","scene":"06-two-paths.png","kicker":"TWO DIFFERENT CONSEQUENCES","headline":["THE SEASON HITS","TWO PEOPLE DIFFERENTLY."],"gold":[1],"special":"paths",
  "left_title":"IF YOU'VE BEEN LOCKED IN","left":["You risk losing the routine, momentum", "and self-trust you spent the year building."],
  "right_title":"IF YOU HAVEN'T STARTED","right":["You risk entering January further away", "with another three months of delay."]},
 {"slug":"erosion","scene":"07-erosion.png","kicker":"HOW PROGRESS GETS WRECKED","headline":["IT RARELY DISAPPEARS","IN ONE NIGHT."],"gold":[1],"special":"erosion",
  "sub":"IT ERODES THROUGH REPEATED DECISIONS.","items":["MORE LIQUID CALORIES","MORE FREQUENT OVEREATING","FEWER WORKOUTS","LESS DAILY MOVEMENT","POORER SLEEP + RECOVERY"]},
 {"slug":"defense","scene":"08-defense.png","kicker":"THE HOLIDAY DEFENSE SYSTEM","headline":["ENJOY THE HOLIDAY.","KEEP YOUR STANDARDS."],"gold":[1],"special":"defense",
  "sub":"YOU DON'T NEED PERFECTION. YOU NEED BOUNDARIES.","items":["KEEP A MINIMUM TRAINING SCHEDULE","PRIORITIZE PROTEIN + WHOLE FOODS","MAINTAIN A DAILY STEP TARGET","CHOOSE INDULGENCES INTENTIONALLY","SET AN ALCOHOL LIMIT FIRST","RETURN AT THE NEXT MEAL"]},
 {"slug":"closing","scene":"09-january.png","kicker":"THE CLOSING STANDARD","headline":["JANUARY SHOULD NOT","HAVE TO RESCUE YOU."],"gold":[1],
  "sub":"ENJOY THE SEASON. DON'T ABANDON YOURSELF.","body":["Celebrate. Choose the food. Be with your people.","Then return before one day becomes three months."]},
]

fonts = {"head":TTFont(HEAD_FONT),"medium":TTFont(BODY_MED),"bold":TTFont(BODY_BOLD)}
def esc(v): return html.escape(str(v), quote=True)
def uri(path): return "data:image/png;base64," + b64encode(path.read_bytes()).decode()
def width(value,size,face):
    font=fonts[face]; cmap=font.getBestCmap()
    units=sum(font["hmtx"][cmap.get(ord(c),".notdef")][0] for c in value)
    return units/font["head"].unitsPerEm*size
def fit(value,size,face,max_width):
    while width(value,size,face)>max_width and size>18: size-=1
    return size
def text(value,x,y,size,color=WHITE,face="head",anchor="start",tracking=0,max_width=952):
    size=fit(value,size,face,max_width); family=HEAD if face=="head" else BODY
    weight={"head":800,"medium":500,"bold":700}[face]
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{tracking}">{esc(value)}</text>'
def font_css():
    return "\n".join([
      f"@font-face{{font-family:'{HEAD}';font-weight:800;src:url('{uri(HEAD_FONT).replace('image/png','font/ttf')}')}}",
      f"@font-face{{font-family:'{BODY}';font-weight:500;src:url('{uri(BODY_MED).replace('image/png','font/ttf')}')}}",
      f"@font-face{{font-family:'{BODY}';font-weight:700;src:url('{uri(BODY_BOLD).replace('image/png','font/ttf')}')}}"])
def header(n):
    return [f'<image href="{uri(LOGO)}" x="54" y="34" width="76" height="76"/>',
      text("CUTTHROAT",145,64,16,WHITE,"bold",tracking=1.8), text("DISCIPLINE",145,88,16,SILVER,"bold",tracking=1.8),
      text(f"{n:02d} / 09",1022,72,17,SILVER,"bold","end",1.2),
      '<path d="M58 122 H1022" stroke="#686B71" stroke-opacity=".55"/>','<path d="M58 122 H270" stroke="#D6A928" stroke-width="4"/>']
def render(n,s):
    scene=SCENES/s["scene"]
    v=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350"><defs><style>{font_css()}</style>',
       '<linearGradient id="top" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#090A0C" stop-opacity=".98"/><stop offset=".78" stop-color="#090A0C" stop-opacity=".78"/><stop offset="1" stop-color="#090A0C" stop-opacity="0"/></linearGradient>',
       '<linearGradient id="bottom" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#090A0C" stop-opacity="0"/><stop offset=".2" stop-color="#090A0C" stop-opacity=".9"/><stop offset="1" stop-color="#090A0C"/></linearGradient></defs>',
       '<rect width="1080" height="1350" fill="#090A0C"/>',f'<image href="{uri(scene)}" width="1080" height="1350" preserveAspectRatio="xMidYMid slice"/>',
       '<rect width="1080" height="480" fill="url(#top)"/>', '<rect y="925" width="1080" height="425" fill="url(#bottom)"/>',*header(n),
       text(s["kicker"],58,166,17,GOLD,"bold",tracking=2)]
    y=252
    for i,line in enumerate(s["headline"]):
        v.append(text(line,58,y+i*94,90,GOLD if i in s["gold"] else WHITE,"head"))
    special=s.get("special")
    if special=="paths":
        v += ['<rect y="745" width="1080" height="605" fill="#090A0C" fill-opacity=".94"/>','<path d="M540 795 V1218" stroke="#686B71"/>',
              text(s["left_title"],58,842,24,GOLD,"bold",max_width=430), text(s["right_title"],578,842,24,WHITE,"bold",max_width=444)]
        for j,line in enumerate(s["left"]): v.append(text(line,58,902+j*39,22,SILVER,"medium",max_width=430))
        for j,line in enumerate(s["right"]): v.append(text(line,578,902+j*39,22,SILVER,"medium",max_width=444))
        v += [text("PROTECT WHAT YOU BUILT.",58,1085,31,WHITE,"bold",max_width=430),text("STOP DELAYING THE START.",578,1085,31,GOLD,"bold",max_width=444)]
    elif special in ("erosion","defense"):
        panel_y=690 if special=="erosion" else 650
        v += [f'<rect y="{panel_y}" width="1080" height="{1350-panel_y}" fill="#090A0C" fill-opacity=".94"/>',text(s["sub"],58,panel_y+60,23,WHITE,"bold",tracking=.3)]
        for j,item in enumerate(s["items"]):
            col=j%2; row=j//2; x=58+col*510; yy=panel_y+145+row*112
            v += [text(f"{j+1:02d}",x,yy,43,GOLD,"head",max_width=55),text(item,x+70,yy-3,23,WHITE,"bold",max_width=420),f'<path d="M{x+70} {yy+27} H{x+470}" stroke="#4B4E54"/>']
    else:
        v += [text(s["sub"],58,1084,26,GOLD,"bold",tracking=.2)]
        for j,line in enumerate(s["body"]): v.append(text(line,58,1141+j*38,24,SILVER,"medium"))
    v += ['<path d="M58 1270 H1022" stroke="#4B4E54"/>',text(FOOTER,540,1311,15,SILVER,"bold","middle",1.4),'</svg>']
    return "\n".join(v)

def main():
    pngs=[]
    with tempfile.TemporaryDirectory(prefix="ctd-holiday-") as td:
      td=Path(td); cache=td/"cache"; profile=td/"profile"; cache.mkdir(); profile.mkdir()
      cfg=td/"fonts.conf"; cfg.write_text(f'<?xml version="1.0"?><fontconfig><dir>{FONT_DIR}</dir><cachedir>{cache}</cachedir><config><rescan><int>0</int></rescan></config></fontconfig>')
      env=dict(os.environ); env.update(FONTCONFIG_FILE=str(cfg),XDG_CACHE_HOME=str(cache),INKSCAPE_PROFILE_DIR=str(profile))
      for n,s in enumerate(slides,1):
        stem=f'{n:02d}-{s["slug"]}'; sp=OUT/f"{stem}.svg"; pp=OUT/f"{stem}.png"
        sp.write_text(render(n,s)); subprocess.run(["inkscape",str(sp),"--export-filename",str(pp),"--export-width=1080","--export-height=1350"],check=True,env=env); pngs.append(pp)
    subprocess.run(["montage",*map(str,pngs),"-thumbnail","216x270","-tile","3x3","-geometry","+10+10","-background",INK,str(OUT/"overview.jpg")],check=True)
    shutil.copyfile(pngs[0],OUT/"preview.png")
    package=[*pngs,OUT/"caption.txt",OUT/"copy.txt",OUT/"alt-text.txt",OUT/"README.md",OUT/"preview.png",OUT/"overview.jpg"]
    with ZipFile(OUT/"final-carousel.zip","w",ZIP_DEFLATED,compresslevel=6) as z:
      for p in package:z.write(p,p.name)
if __name__=="__main__":main()
