#!/usr/bin/env python3
"""Recreate original diagrams and silent MP4 (requires Pillow and ffmpeg)."""
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / 'images'
VIDEO = ROOT / 'assets/videos'
IMAGES.mkdir(exist_ok=True)
VIDEO.mkdir(parents=True, exist_ok=True)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def font(size):
    return ImageFont.truetype(FONT, size)

def svg_world():
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 700"><defs><pattern id="grid" width="44" height="44" patternUnits="userSpaceOnUse" patternTransform="matrix(1 .45 -1 .45 350 90)"><path d="M44 0H0V44" fill="none" stroke="#b7c8a6" stroke-width=".6"/></pattern><filter id="shadow"><feGaussianBlur stdDeviation="14"/></filter></defs><circle cx="350" cy="346" r="264" fill="url(#grid)" opacity=".55"/><ellipse cx="350" cy="520" rx="220" ry="57" fill="#8baf8f" opacity=".18" filter="url(#shadow)"/><ellipse cx="350" cy="377" rx="293" ry="129" fill="none" stroke="#b9c9ab" stroke-dasharray="3 8" transform="rotate(-17 350 377)"/>']
    def point(x,y,z):
        return 350+(x-y)*42,335+(x+y)*20-z*43
    def poly(vertices,color):
        points=' '.join(f'{x:.1f},{y:.1f}' for x,y in vertices)
        parts.append(f'<polygon points="{points}" fill="{color}"/>')
    def block(x,y,z,w,d,h,colors):
        poly([point(x,y+d,z),point(x+w,y+d,z),point(x+w,y+d,z+h),point(x,y+d,z+h)],colors[1])
        poly([point(x+w,y,z),point(x+w,y+d,z),point(x+w,y+d,z+h),point(x+w,y,z+h)],colors[2])
        poly([point(x,y,z+h),point(x+w,y,z+h),point(x+w,y+d,z+h),point(x,y+d,z+h)],colors[0])
    block(-3,-3,-1,6,6,.85,['#91b09b','#346954','#204f43'])
    block(-3,-3,-.15,6,6,.23,['#b9d0a2','#729b79','#578670'])
    for x,y,w,d in [(-3,-3,3,2),(1,-3,2,2),(-3,0,2,3),(0,0,3,3)]:
        block(x,y,.08,w,d,.17,['#c8d9af','#82a884','#6c967b'])
    block(-.85,-3,.09,1,5.8,.06,['#dce4ca','#a4b99b','#a4b99b'])
    block(-3,-.85,.09,5.7,.85,.06,['#dce4ca','#a4b99b','#a4b99b'])
    for i in range(8):
        block(-.72,-2.9+i*.68,.16,.74,.52,.015,['#c5d2b7','#c5d2b7','#c5d2b7'])
    block(.5,.1,.25,1.7,1.7,.7,['#85b9a4','#3e806e','#286a5b'])
    block(.6,.2,.95,1.5,1.5,.12,['#d9e6c8','#8bb397','#68957e'])
    block(.92,.52,1.07,.86,.86,1.17,['#d2e4ba','#69a88e','#488d7b'])
    block(.88,.48,2.24,.94,.94,.08,['#e2edd0','#9ac6a6','#88b99a'])
    def tree(x,y,size=1):
        block(x-.04,y-.04,.25,.1,.1,.55*size,['#73846b','#536c54','#435f4b'])
        for z,r in [(.85,.40),(1.13,.31),(1.4,.22)]:
            top=point(x,y,(z+.67)*size)
            base=[point(x-r*size,y-r*size,z*size),point(x+r*size,y-r*size,z*size),point(x+r*size,y+r*size,z*size),point(x-r*size,y+r*size,z*size)]
            for a,b,c in [(0,1,'#80ae83'),(1,2,'#3c7d62'),(2,3,'#5d9970'),(3,0,'#93b888')]:
                poly([base[a],base[b],top],c)
    for x,y,s in [(-2.1,-2.0,1.1),(1.9,-2.1,.9),(-2.0,1.7,1.1),(-1.9,.6,.8),(2.3,2.35,.85)]:
        tree(x,y,s)
    block(-1.8,-1.3,3.4,.65,.65,.65,['#dce9bd','#67ac8e','#3e8d77'])
    for x,y,z in [(-2.8,.1,2.5),(2,-2,2.7),(3,1.2,2.8)]:
        px,py=point(x,y,z)
        parts.append(f'<path d="M{px-4} {py}h8m-4-4v8" stroke="#7ca27c"/>')
    parts.append('<path d="M104 531h54m-54 0v-24M543 157h54v24" fill="none" stroke="#96b08a"/><text x="108" y="552" font-family="monospace" font-size="9" letter-spacing="2" fill="#7a9471">X / Y / Z</text><circle cx="596" cy="236" r="4" fill="#9cba80"/><circle cx="122" cy="449" r="3" fill="#b3c79a"/></svg>')
    (IMAGES/'world.svg').write_text(''.join(parts))

def editor_diagram():
    image=Image.new('RGB',(1280,720),'#172b26')
    d=ImageDraw.Draw(image)
    d.rounded_rectangle((22,22,1258,74),8,fill='#263e34')
    d.text((40,36),'EDITOR MAP  /  UE5 FIELD GUIDE',font=font(18),fill='#c6d9bc')
    d.text((950,40),'ILLUSTRATION',font=font(13),fill='#91aa82')
    d.rounded_rectangle((22,92,945,528),8,fill='#1d352d')
    for i in range(10):
        d.line([(22,270+i*30),(945,270+i*30)],fill='#2d4939')
        d.line([(480,230),(22+i*110,528)],fill='#2d4939')
    for points,color in [([(400,279),(501,240),(601,280),(501,322)],'#bed1a3'),([(400,279),(501,322),(501,423),(400,379)],'#54957b'),([(501,322),(601,280),(601,379),(501,423)],'#347a66')]:
        d.polygon(points,fill=color)
    d.text((42,110),'01  VIEWPORT',font=font(22),fill='#d3e4c3')
    d.text((42,145),'Level / camera / transform',font=font(15),fill='#8eaa83')
    d.rounded_rectangle((963,92,1258,285),8,fill='#294137')
    d.text((983,110),'02  OUTLINER',font=font(19),fill='#d3e4c3')
    for n,t in enumerate(['Floor_Main','Cube_01','Light_Key','PlayerStart']):
        d.text((1003,151+n*28),t,font=font(14),fill='#9db38f')
    d.rounded_rectangle((963,303,1258,528),8,fill='#294137')
    d.text((983,324),'03  DETAILS',font=font(19),fill='#d3e4c3')
    for n,t in enumerate(['Location     X  Y  Z','Rotation     0  0  0','Scale        1  1  1','Mobility     Movable']):
        d.text((983,369+n*31),t,font=font(13),fill='#9db38f')
    d.rounded_rectangle((22,546,1258,698),8,fill='#294137')
    d.text((42,565),'04  CONTENT BROWSER',font=font(19),fill='#d3e4c3')
    for n,t in enumerate(['Maps','Blueprints','Materials','Meshes','Textures']):
        x=42+n*165
        d.rounded_rectangle((x,609,x+142,671),5,fill='#355443')
        d.text((x+14,630),t,font=font(14),fill='#c6d9bc')
    image.save(IMAGES/'editor-layout.png',optimize=True)

def frame(angle):
    im=Image.new('RGB',(960,540),'#182e28')
    d=ImageDraw.Draw(im)
    def project(p):
        x,y,z=p
        return 480+(x-z)*88,270+(x+z)*34-y*90
    for i in range(-6,7):
        d.line([project((i,-1.6,-6)),project((i,-1.6,6))],fill='#2c4738')
        d.line([project((-6,-1.6,i)),project((6,-1.6,i))],fill='#2c4738')
    d.ellipse((315,324,645,420),fill='#11251f')
    vertices=[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
    points=[(x*math.cos(angle)-z*math.sin(angle),y+.1,x*math.sin(angle)+z*math.cos(angle)) for x,y,z in vertices]
    faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2)]
    colors=['#4a997e','#72b99a','#4c9279','#c1d7a2','#34816d','#67a98b']
    for n,f in sorted(enumerate(faces),key=lambda entry:sum(points[v][0]+points[v][2] for v in entry[1])):
        d.polygon([project(points[v]) for v in f],fill=colors[n],outline='#bbd8a0',width=2)
    d.rectangle((0,0,960,57),fill='#152921')
    d.text((28,20),'SCENE 01 / ROTATING CUBE',font=font(15),fill='#bdd49d')
    d.text((720,22),'UE5 FIELD GUIDE',font=font(12),fill='#8daa7d')
    d.text((29,499),'45° / s   ·   Учебная иллюстрация',font=font(14),fill='#a1bd8d')
    return im

svg_world()
editor_diagram()
frame(.5).save(IMAGES/'test.jpg',quality=90,optimize=True)
(IMAGES/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#152725"/><path d="M17 16v25q0 14 15 14t15-14V16h-8v25q0 7-7 7t-7-7V16z" fill="#c9e5a4"/><path d="M22 9h20" stroke="#c9e5a4" stroke-width="3"/></svg>')
(IMAGES/'actor-components.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 380"><rect width="960" height="380" rx="12" fill="#edf2e7"/><g stroke="#9bb68a" stroke-width="2" fill="none"><path d="M480 105V175H130v70m350-70H365v70m115-70h115v70m-115-70h350v70"/></g><g fill="#fff" stroke="#c4d3b8"><rect x="350" y="40" width="260" height="70" rx="8"/><rect x="25" y="245" width="210" height="75" rx="8"/><rect x="260" y="245" width="210" height="75" rx="8"/><rect x="490" y="245" width="210" height="75" rx="8"/><rect x="725" y="245" width="210" height="75" rx="8"/></g><g font-family="Arial,sans-serif" font-size="22" text-anchor="middle" fill="#355940"><text x="480" y="85">Actor</text><text x="130" y="289">Scene</text><text x="365" y="289">Static Mesh</text><text x="595" y="289">Collision</text><text x="830" y="289">Audio</text></g><text x="480" y="355" font-family="Arial,sans-serif" font-size="14" text-anchor="middle" fill="#78916a">COMPOSITION / ONE ACTOR, MULTIPLE COMPONENTS</text></svg>''')
output=VIDEO/'rotation-demo.mp4'
proc=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size','960x540','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],stdin=subprocess.PIPE)
try:
    for i in range(288):
        proc.stdin.write(frame(.5+i/24*math.pi/4).tobytes())
finally:
    proc.stdin.close()
if proc.wait()!=0:
    raise SystemExit('ffmpeg failed')
(VIDEO/'rotation-demo-ru.vtt').write_text('''WEBVTT

00:00.000 --> 00:04.000
Куб вращается вокруг вертикальной оси.
Скорость — 45 градусов в секунду.

00:04.000 --> 00:08.000
Сетка помогает увидеть глубину пространства.
За 8 секунд куб совершает полный оборот.

00:08.000 --> 00:12.000
Повторите вращение в UE5 через Blueprint или C++.
Это учебная анимация, а не запись редактора.
''',encoding='utf-8')
print(f'Created 5 images and video ({output.stat().st_size:,} bytes)')
