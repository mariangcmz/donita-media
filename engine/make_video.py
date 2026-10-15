"""Render de un Reel de La Doñita Dev a partir de un guion por escenas.
Uso: python3 make_video.py salida.mp4
"""
import sys, math, subprocess, random
from rig import *

FPS = 24

def ease_out_back(x, s=1.7):
    x = max(0, min(1, x)); x -= 1
    return x * x * ((s + 1) * x + s) + 1

def ease_io(x):
    x = max(0, min(1, x)); return x * x * (3 - 2 * x)

# ---------------- Guion de prueba ----------------
SCENES = [
    dict(t0=0.0, t1=3.4, head='head_cansada', arm_r='arm_baja_taza', arm_l='arm_manga_izq',
         text=['Mija, ¿otra vez', 'copiando y pegando', 'datos a mano?'], hl='a mano?',
         note=None, props=['laptop']),
    dict(t0=3.4, t1=6.6, head='head_estres', arm_r='arm_alza_taza', arm_l='arm_manga_izq', shake=1.0,
         text=['Yo también.', 'Tres horas', 'cada lunes.'], hl='Tres horas',
         note='(y el café, frío)', props=['laptop']),
    dict(t0=6.6, t1=10.2, head='head_emocionada', arm_r='arm_senala', arm_l='arm_manga_izq',
         text=['Hasta que le enseñé', 'a la compu a', 'hacerlo sola.'], hl='hacerlo sola.',
         note=None, props=['nodes']),
    dict(t0=10.2, t1=13.5, head='head_emocionada', arm_r='arm_alza_taza', arm_l='arm_manga_izq',
         text=['Mañana te enseño', 'cómo. Sin saber', 'programar.'], hl='programar.',
         note='sí, tú también', props=['mug']),
]
DUR = SCENES[-1]['t1']

F_TITLE = lambda: font('Nunito[wght].ttf', 86, 800)
F_NOTE = lambda: font('Kalam-Bold.ttf', 58)
F_HANDLE = lambda: font('Nunito[wght].ttf', 38, 700)

def draw_text_block(c, sc, t):
    lt = t - sc['t0']
    f = F_TITLE(); d = ImageDraw.Draw(c)
    y = 230
    for i, line in enumerate(sc['text']):
        k = ease_out_back((lt - 0.12 * i) / 0.35)
        if k <= 0: y += 104; continue
        tw = d.textlength(line, font=f)
        layer = Image.new('RGBA', (int(tw) + 40, 130), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
        is_hl = sc['hl'] and sc['hl'] in line
        if is_hl:  # subrayado salmón tipo marcador, se dibuja de izq a der
            u = ease_io((lt - 0.12 * i - 0.25) / 0.4)
            ld.rounded_rectangle((14, 66, 14 + (tw + 12) * u, 104), radius=10, fill=SALMON + (235,))
        ld.text((20, 8), line, font=f, fill=ESPRESSO)
        s = 0.6 + 0.4 * k
        layer = layer.resize((max(1, int(layer.width * s)), max(1, int(layer.height * s))), Image.BICUBIC)
        c.alpha_composite(layer, (int(W / 2 - layer.width / 2), int(y + (1 - s) * 60)))
        y += 104
    if sc['note']:
        k = ease_out_back((lt - 0.7) / 0.3)
        if k > 0:
            fn = F_NOTE(); tw = d.textlength(sc['note'], font=fn)
            layer = Image.new('RGBA', (int(tw) + 30, 100), (0, 0, 0, 0))
            ImageDraw.Draw(layer).text((10, 5), sc['note'], font=fn, fill=SALMON)
            layer = layer.rotate(-3, expand=True, resample=Image.BICUBIC)
            layer = layer.resize((max(1, int(layer.width * k)), max(1, int(layer.height * k))))
            c.alpha_composite(layer, (W - layer.width - 70, y + 40))

NODES = [(0, 0), (120, -60), (230, 10), (190, 120), (60, 110)]
EDGES = [(0, 1), (1, 2), (2, 3), (1, 4), (4, 3)]
def draw_nodes(c, ox, oy, lt):
    d = ImageDraw.Draw(c)
    for j, (a, b) in enumerate(EDGES):
        u = ease_io((lt - 0.3 - 0.18 * j) / 0.3)
        if u <= 0: continue
        (x1, y1), (x2, y2) = NODES[a], NODES[b]
        d.line([(ox + x1, oy + y1), (ox + x1 + (x2 - x1) * u, oy + y1 + (y2 - y1) * u)], fill=ESPRESSO, width=7)
    for j, (x, y) in enumerate(NODES):
        k = ease_out_back((lt - 0.12 * j) / 0.3)
        if k <= 0: continue
        r = 24 * k
        d.ellipse((ox + x - r - 5, oy + y - r - 5, ox + x + r + 5, oy + y + r + 5), fill=(255, 255, 255))
        d.ellipse((ox + x - r, oy + y - r, ox + x + r, oy + y + r), fill=SALMON, outline=ESPRESSO, width=5)

def frame(fi):
    t = fi / FPS
    sc = next(s for s in SCENES if s['t0'] <= t < s['t1'] + 1e-9)
    lt = t - sc['t0']
    c = paper_bg().copy()
    boil = fi // 4  # boiling suave a 6 fps
    # props detrás del personaje
    if 'laptop' in sc['props']:
        lp = piece('laptop_a', 2.2)
        k = ease_out_back(lt / 0.4)
        paste_rot(c, lp, (lp.width / 2, lp.height / 2), (200, 1230 + 6 * math.sin(t * 1.6)), -6 + 1.5 * math.sin(t * 1.2), sx=k, sy=k)
    if 'nodes' in sc['props']:
        draw_nodes(c, 740, 690, lt)
    # cabeza: pop al cambiar de expresión
    pop = max(0.0, 1 - lt / 0.25) * math.sin(lt / 0.25 * math.pi) if lt < 0.25 else 0.0
    arm_ang = 0.0
    if sc['arm_r'] == 'arm_alza_taza':
        arm_ang = 15 + 8 * (1 - ease_out_back(lt / 0.6)) + 2 * math.sin(t * 2.2)
    if sc['arm_r'] == 'arm_senala':
        arm_ang = -40 + 3 * math.sin(t * 2.4)
    if sc.get('shake'):  # un solo "resoplido" al entrar, luego quieta
        head_ang = 5 * math.sin(lt * 28) * math.exp(-lt * 4)
    else:
        head_ang = 2 * math.sin(t * 1.3)
    # gesto en el lado izquierdo de la imagen (pieza espejo), manga en el derecho
    # brazo con gesto (pieza original) en el lado izq de la imagen; manga espejo en el derecho; ambos al frente
    character(c, t, 540, 1800, head=sc['head'], head_pop=pop, arm_l=sc['arm_r'], arm_r='arm_manga_izq',
              arm_l_ang=arm_ang, arm_r_ang=-1.5 * math.sin(t * 1.8), head_ang=head_ang, boil_seed=boil)
    if 'mug' in sc['props']:
        m = piece('mug_mascota', 1.9)
        hop = abs(math.sin(t * 3.5)) * 26
        k = ease_out_back(lt / 0.4)
        paste_rot(c, m, (m.width / 2, m.height), (915, 1800 - hop), 3 * math.sin(t * 3.5), sx=k, sy=k * (1 + 0.04 * math.sin(t * 7)))
    draw_text_block(c, sc, t)
    # firma
    d = ImageDraw.Draw(c); fh = F_HANDLE()
    d.text((W / 2 - d.textlength('@ladonitadev', font=fh) / 2, 1850), '@ladonitadev', font=fh, fill=ESPRESSO + (170,))
    # transición: corte con pequeño "flash" de papel
    if lt < 0.08 and sc['t0'] > 0:
        c.alpha_composite(Image.new('RGBA', (W, H), CREMA + (120,)))
    return c.convert('RGB')

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'test.mp4'
    n = int(DUR * FPS)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-shortest',
                          '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', '-c:a', 'aac', '-movflags', '+faststart', out],
                         stdin=subprocess.PIPE)
    for fi in range(n):
        p.stdin.write(frame(fi).tobytes())
    p.stdin.close(); p.wait(); print('ok', out, n, 'frames')
