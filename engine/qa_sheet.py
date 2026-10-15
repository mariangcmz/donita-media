"""QA de animación: hoja de contacto, siluetas y volumen. Uso: python3 qa_sheet.py guiones/x.json id salida.png"""
import sys, json, math
import render_week as rw, make_video as mv
from PIL import Image, ImageDraw
src, vid, out = sys.argv[1:4]
v = next(x for x in json.load(open(src)) if x['id'] == vid)
mv.SCENES = rw.load(v)
times = []
for s in mv.SCENES:
    times += [s['t0'] + d for d in (0.06, 0.18, 0.30, 0.45, 1.2)]
cols = len(times) // len(mv.SCENES); tw, th = 180, 320
sheet = Image.new('RGB', (cols * tw, len(mv.SCENES) * th * 2), 'white')
worst = 0
for i, t in enumerate(times):
    s = next(x for x in mv.SCENES if x['t0'] <= t < x['t1'])
    a = mv.performance(s, t, t - s['t0']); worst = max(worst, abs(a['sx'] * a['sy'] - 1))
    f = mv.frame(int(round(t * mv.FPS)))
    r, c = divmod(i, cols)
    sheet.paste(f.resize((tw, th)), (c * tw, r * th * 2))
    # silueta: render solo el personaje en negro
    layer = Image.new('RGBA', (mv.W, mv.H), (0, 0, 0, 0))
    mv.character(layer, t, 540, 1800, head=s['head'], arm_l=s['arm_r'], arm_r='arm_manga_izq',
                 arm_l_ang=a['arm'], arm_r_ang=a['sleeve'], head_ang=a['head_ang'], shadow=False)
    sil = Image.new('RGB', (mv.W, mv.H), 'white'); sil.paste((0, 0, 0), mask=layer.split()[3])
    sheet.paste(sil.resize((tw, th)), (c * tw, r * th * 2 + th))
sheet.save(out)
print('volumen max |sx*sy-1| =', round(worst, 3))
