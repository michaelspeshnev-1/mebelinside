"""Рисует маскота «Инсайд» (Pillow, только цвета бренда). Запуск: python tools/mascot_insaid.py"""
from PIL import Image, ImageDraw, ImageFont
import os
INK,BRASS,CREAM=(28,29,32),(201,168,106),(241,235,221)
S=2; W,H=900,1300
FONT=os.path.join(os.path.dirname(__file__),'fonts/Manrope-Variable.ttf')
OUT=os.path.join(os.path.dirname(__file__),'..','media','mascot')

def font(sz,w=800):
    f=ImageFont.truetype(FONT,sz*S)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f

def limb(d,pts,w,col):
    pts=[(x*S,y*S) for x,y in pts]
    d.line(pts,fill=col,width=w*S,joint='curve')
    for x,y in (pts[0],pts[-1]): d.ellipse((x-w*S/2,y-w*S/2,x+w*S/2,y+w*S/2),fill=col)

def hand(d,x,y,r=26):
    d.ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S),fill=CREAM,outline=INK,width=6*S)

def draw(pose,bg=None):
    im=Image.new('RGBA',(W*S,H*S),bg+(255,) if bg else (0,0,0,0)); d=ImageDraw.Draw(im)
    R=lambda b,**k:d.rounded_rectangle([v*S for v in b],**k)
    # legs + boots
    for lx in (370,530):
        limb(d,[(lx,930),(lx,1080)],26,INK)
        R((lx-48,1070,lx+48,1130),radius=24,fill=BRASS,outline=INK,width=6*S)
    # arms (behind body edge)
    arms={'stand':([(300,640),(215,760),(205,860)],[(600,640),(685,760),(695,860)]),
          'point':([(300,640),(215,760),(205,860)],[(600,640),(710,560),(820,470)]),
          'tape':([(300,640),(250,730),(330,800)],[(600,640),(660,730),(590,800)])}[pose]
    for a in arms: limb(d,a,28,INK)
    # tip (wood cone) + lead
    d.polygon([(300*S,330*S),(600*S,330*S),(450*S,110*S)],fill=BRASS,outline=INK,width=6*S)
    d.polygon([(390*S,205*S),(510*S,205*S),(450*S,110*S)],fill=INK)
    d.line([(300*S,330*S),(450*S,110*S),(600*S,330*S)],fill=INK,width=6*S,joint='curve')
    # body
    R((280,320,620,960),radius=40,fill=INK)
    R((280,320,620,372),radius=20,fill=BRASS)   # ferrule band
    # face
    for ex in (390,510):
        d.ellipse(((ex-32)*S,(470-32)*S,(ex+32)*S,(470+32)*S),fill=CREAM)
        d.ellipse(((ex-14+(8 if pose=='point' else 0))*S,(474-14)*S,(ex+14+(8 if pose=='point' else 0))*S,(474+14)*S),fill=INK)
    d.arc((380*S,500*S,520*S,590*S),20,160,fill=BRASS,width=9*S)
    # apron
    R((300,640,600,960),radius=28,fill=BRASS)
    R((300,640,600,668),radius=14,fill=BRASS)
    d.rectangle((340*S,630*S,362*S,700*S),fill=BRASS); d.rectangle((538*S,630*S,560*S,700*S),fill=BRASS)
    R((375,790,525,890),radius=14,fill=CREAM,outline=INK,width=5*S)
    d.rectangle((405*S,760*S,418*S,800*S),fill=INK); d.rectangle((445*S,750*S,458*S,800*S),fill=INK); d.rectangle((485*S,765*S,498*S,800*S),fill=INK)
    # hands & props
    if pose=='stand':
        hand(d,205,870); hand(d,695,870)
    elif pose=='point':
        hand(d,205,870); hand(d,820,470)
        d.polygon([(845*S,455*S),(900*S,430*S),(850*S,490*S)],fill=INK)
    else:
        hand(d,330,800); hand(d,590,800)
        # tape measure: brass case, cream tape stretched between hands
        d.rounded_rectangle((330*S,780*S,590*S,820*S),radius=16*S,fill=CREAM,outline=INK,width=5*S)
        for i in range(350,580,22): d.line([(i*S,780*S),(i*S,(795 if (i-350)%44 else 805)*S)],fill=INK,width=3*S)
        d.ellipse((560*S,765*S,640*S,845*S),fill=BRASS,outline=INK,width=6*S)
        hand(d,330,800); 
    # name plaque
    R((170,1170,730,1270),radius=30,fill=BRASS)
    f=font(56); t='Мебель Inside'
    tw=d.textlength(t,font=f)
    d.text((450*S-tw/2,1190*S),t,font=f,fill=INK)
    return im.resize((W,H),Image.LANCZOS)

os.makedirs(OUT,exist_ok=True)
for pose in ('stand','point','tape'):
    t=draw(pose); c=draw(pose,CREAM)
    t.save(f'{OUT}/insaid-{pose}.png'); c.save(f'{OUT}/insaid-{pose}-cream.png')
draw('stand').save(f'{OUT}/insaid-final.png'); draw('stand',CREAM).save(f'{OUT}/insaid-final-cream.png')
sheet=Image.new('RGB',(W*3,H),CREAM)
for i,p in enumerate(('stand','point','tape')): sheet.paste(draw(p,CREAM).convert('RGB'),(i*W,0))
sheet.resize((W*3//2,H//2)).save(f'{OUT}/insaid-poses-cream.png')
