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

def text_layout(sc):
    """Tamaño y posición del bloque de texto. <=3 líneas: como siempre (86 px desde y=230).
    4-5 líneas o líneas largas: se encoge para no tapar a la doñita."""
    lines = sc['text']; n = len(lines)
    size = 86 if n <= 3 else (72 if n == 4 else 62)
    f = font('Nunito[wght].ttf', size, 800)
    d = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    widest = max(d.textlength(l, font=f) for l in lines)
    if sc.get('estilo') == 'post':      # tarjeta de post: letra más chica, arriba del chongo
        size = min(size, 64); f = font('Nunito[wght].ttf', size, 800)
        widest = max(d.textlength(l, font=f) for l in lines)
    if widest > 940:
        size = int(size * 940 / widest); f = font('Nunito[wght].ttf', size, 800)
    lh = int(size * 1.21)
    y0 = 230 if n <= 3 else 170
    if sc.get('estilo') == 'post': y0 = 200
    return f, size, lh, y0

def draw_post_card(c, sc, lt, y0, y1):
    """Estilo 'post': el texto va dentro de una tarjeta blanca genérica de red social (sin logos)."""
    k = ease_io(lt / 0.3)
    if k <= 0: return
    card = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    x0, x1 = 60, W - 60; top = y0 - 112
    d.rounded_rectangle((x0 + 6, top + 10, x1 + 6, y1 + 50), radius=34, fill=ESPRESSO + (40,))
    d.rounded_rectangle((x0, top, x1, y1 + 40), radius=34, fill=(255, 255, 255, 245), outline=ESPRESSO, width=4)
    d.ellipse((x0 + 34, top + 26, x0 + 104, top + 96), fill=(214, 206, 196))
    d.rounded_rectangle((x0 + 124, top + 36, x0 + 380, top + 54), radius=9, fill=(214, 206, 196))
    d.rounded_rectangle((x0 + 124, top + 68, x0 + 280, top + 82), radius=7, fill=(232, 226, 218))
    card.putalpha(card.split()[3].point(lambda v: int(v * k)))
    c.alpha_composite(card)

def draw_text_block(c, sc, t):
    lt = t - sc['t0']
    f, size, lh, y0 = text_layout(sc); d = ImageDraw.Draw(c)
    if sc.get('estilo') == 'post':
        draw_post_card(c, sc, lt, y0, y0 + lh * len(sc['text']))
    y = y0
    for i, line in enumerate(sc['text']):
        k = ease_out_back((lt - 0.12 * i) / 0.35)
        if k <= 0: y += lh; continue
        tw = d.textlength(line, font=f)
        layer = Image.new('RGBA', (int(tw) + 40, int(size * 1.5)), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
        is_hl = sc['hl'] and sc['hl'] in line
        if is_hl:  # subrayado salmón tipo marcador, se dibuja de izq a der
            u = ease_io((lt - 0.12 * i - 0.25) / 0.4)
            ld.rounded_rectangle((14, size * 0.77, 14 + (tw + 12) * u, size * 1.21), radius=10, fill=SALMON + (235,))
        ld.text((20, size * 0.09), line, font=f, fill=ESPRESSO)
        s = 0.6 + 0.4 * k
        layer = layer.resize((max(1, int(layer.width * s)), max(1, int(layer.height * s))), Image.BICUBIC)
        c.alpha_composite(layer, (int(W / 2 - layer.width / 2), int(y + (1 - s) * 60)))
        y += lh
    if sc['note']:
        k = ease_out_back((lt - 0.7) / 0.3)
        if k > 0:
            fn = font('Kalam-Bold.ttf', 50); tw = d.textlength(sc['note'], font=fn)
            layer = Image.new('RGBA', (int(tw) + 30, 100), (0, 0, 0, 0))
            ImageDraw.Draw(layer).text((10, 5), sc['note'], font=fn, fill=SALMON)
            layer = layer.rotate(3, expand=True, resample=Image.BICUBIC)
            layer = layer.resize((max(1, int(layer.width * k)), max(1, int(layer.height * k))))
            pos = sc.get('note_pos') or ('margen' if KIT == 'v2' else 'abajo')
            if pos == 'margen':   # margen izquierdo, a la altura del pecho: no tapa la cara ni los nodos
                c.alpha_composite(layer, (max(24, 360 - layer.width), 625))
            else:
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

# ---------------- Actuación (principios de animación) ----------------
def spring(tl, amp, k=6.0, w=16.0, phase=0.0):
    """Resorte amortiguado para follow-through: 0 antes de tl=0."""
    if tl < 0: return 0.0
    return amp * math.exp(-k * tl) * math.sin(w * tl + phase)

def _hash(n):
    return (math.sin(n * 12.9898) * 43758.5453) % 1.0

def is_blinking(t, lt):
    """Parpadeo cada ~2.8-4.4 s (semilla fija), 4 frames cerrados; nunca durante el pop de entrada."""
    if lt < 0.35: return False
    k = int(t // 3.6)
    for kk in (k - 1, k):
        tb = kk * 3.6 + 0.4 + 1.6 * _hash(kk + 7)
        if 0 <= t - tb < 4 / FPS: return True
    return False

def glance(t, lt):
    """Miradas a los lados: holds de ~2.2 s con transición de 0.15 s (acción secundaria)."""
    if lt < 0.9: return 0.0
    seg = int(t // 2.2); targets = [0, -5, 0, 4]
    cur = targets[seg % 4]; prev = targets[(seg - 1) % 4]
    u = ease_io(((t % 2.2)) / 0.15)
    return prev + (cur - prev) * u

def performance(sc, t, lt):
    """Devuelve la pose del personaje en este frame según la emoción de la escena."""
    emo = emo_kind(sc['head']); arm = gesture_kind(sc['arm_r'])
    sy, dy = 1.0, 0.0
    land = 0.0                        # momento en que el cuerpo 'aterriza' (para follow-through)
    if emo == 'emocionada':           # anticipación (squash) -> brinco (stretch) -> aterriza (squash) -> asienta
        if lt < 0.12:   sy = 1 - 0.07 * ease_io(lt / 0.12)
        elif lt < 0.26: u = ease_io((lt - 0.12) / 0.14); sy = 0.93 + 0.13 * u; dy = -18 * u
        elif lt < 0.40: u = (lt - 0.26) / 0.14; sy = 1.06 - 0.06 * u; dy = -18 * (1 - u * u)
        else:           tl = lt - 0.40; sy = 1 - 0.06 * math.exp(-7 * tl) * math.cos(13 * tl)
        land = 0.40; lean_target = 2.0
    elif emo == 'tensa':              # se tensa de golpe (squash corto) y se queda rígida
        sy = 1 - 0.05 * math.exp(-9 * lt) * math.cos(18 * lt) - 0.015 * ease_io(lt / 0.2)
        land = 0.05; lean_target = 0.0
    else:                             # cansada: suspiro lento, se hunde y se ladea
        sy = 1 - 0.035 * math.sin(min(1, lt / 0.9) * math.pi) - 0.01 * ease_io(lt / 0.9)
        land = 0.45; lean_target = -2.0
    sx = 1 / math.sqrt(sy)            # volumen constante
    lean = lean_target * ease_io(lt / 0.5)
    tl = lt - land
    # cabeza: llega después que el cuerpo (overlapping) y se asienta con resorte (follow-through)
    head_lean = lean_target * 1.6 * ease_io((lt - 0.1) / 0.5)
    if sc.get('shake'):
        head_ang = 5 * math.sin(lt * 26) * math.exp(-lt * 4)
    else:
        head_ang = head_lean + spring(tl, 4.0 if emo == 'emocionada' else 2.5) + 1.2 * math.sin(t * 1.1)
    # brazo con gesto: anticipación hacia abajo -> sube con overshoot -> hold con leve vaivén
    v2 = KIT == 'v2'
    if arm == 'alza':
        # v1: alzar = ángulo positivo; v2 (brazo en el lado derecho): alzar = negativo
        base, sg = (-25, -1) if v2 else (18, 1)
        if lt < 0.15: arm_ang = base + sg * (-6 - 6 * ease_io(lt / 0.15))
        else:         arm_ang = base + sg * (-12 + 12 * ease_out_back((lt - 0.15) / 0.45))
        arm_ang += 1.2 * math.sin(t * 1.9)
    elif arm == 'senala':
        base = -6 if v2 else -28   # mano a la altura del hombro: deja aire entre brazo y torso (silueta)
        if lt < 0.15: arm_ang = base - 5 * ease_io(lt / 0.15)
        else:         arm_ang = base - 5 + 5 * ease_out_back((lt - 0.15) / 0.4)
        arm_ang += 2 * math.sin(t * 2.2)
    else:
        arm_ang = 1.0 * math.sin(t * 1.5)
    # manga: cuelga y sigue el movimiento del cuerpo con retraso
    sleeve = spring(tl - 0.06, 6.0, k=5, w=13) - lean * 0.8 - 1.2 * math.sin(t * 1.4)
    pop = math.sin(lt / 0.25 * math.pi) * (1 - lt / 0.25) if lt < 0.25 else 0.0
    return dict(sx=sx, sy=sy, dy=dy, lean=lean, head_ang=head_ang, arm=arm_ang, sleeve=sleeve,
                pop=pop, blink=is_blinking(t, lt), head_dx=glance(t, lt))

def draw_character(layer, sc, t, acting, boil=0, blink=True):
    """Dibuja a la doñita (kit v1 o v2 según DONITA_KIT) en `layer` con la pose de `performance()`."""
    if KIT == 'v2':
        character_v2(layer, t, 540, 1800, head=sc['head'], head_pop=acting['pop'], gesture=gesture_kind(sc['arm_r']),
                     gesture_ang=acting['arm'], rest_ang=acting['sleeve'], head_ang=acting['head_ang'],
                     head_dx=acting['head_dx'], blink=blink and acting['blink'], boil_seed=boil)
    else:
        # brazo con gesto (pieza original) en el lado izq de la imagen; manga espejo en el derecho; ambos al frente
        character(layer, t, 540, 1800, head=sc['head'], head_pop=acting['pop'], arm_l=sc['arm_r'], arm_r='arm_manga_izq',
                  arm_l_ang=acting['arm'], arm_r_ang=acting['sleeve'], head_ang=acting['head_ang'],
                  head_dx=acting['head_dx'], blink=blink and acting['blink'], boil_seed=boil, shadow=False)

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
    acting = performance(sc, t, lt)
    # sombra en el piso: se encoge cuando brinca
    sh_k = 1 - min(0.35, -acting['dy'] / 80)
    ImageDraw.Draw(c).ellipse((540 - 230 * sh_k, 1782, 540 + 230 * sh_k, 1822), fill=(74, 46, 39, int(38 * sh_k)))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    # brazo con gesto (pieza original) en el lado izq de la imagen; manga espejo en el derecho; ambos al frente
    draw_character(layer, sc, t, acting, boil)
    composite_transformed(c, layer, (540, 1800), sx=acting['sx'], sy=acting['sy'],
                          angle=acting['lean'], dy=acting['dy'])
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
