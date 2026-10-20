"""Rig de La Doñita Dev: compone a la doñita por piezas (marioneta cutout) sobre lienzo 9:16."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math, random, functools

W, H = 1080, 1920
CREMA = (244, 232, 215); ESPRESSO = (74, 46, 39); SALMON = (231, 134, 104)
import os
BASE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(BASE, 'pieces') + '/'
F = os.path.join(BASE, 'fonts') + '/'

@functools.lru_cache(None)
def piece(name, scale=1.0):
    im = Image.open(P + name + '.png').convert('RGBA')
    if scale != 1.0:
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    return im

def font(name, size, wght=None):
    f = ImageFont.truetype(F + name, size)
    if wght:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f

@functools.lru_cache(None)
def paper_bg(seed=0):
    rng = np.random.default_rng(seed)
    base = np.zeros((H, W, 3)) + CREMA
    noise = rng.normal(0, 1, (H // 2, W // 2))
    noise = np.array(Image.fromarray(((noise + 3) * 40).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)) / 255 - 0.47
    fib = rng.normal(0, 1, (H, W)) * 3
    base = base + noise[..., None] * 14 + fib[..., None]
    # viñeta suave
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
    base = base * (1 - 0.10 * d[..., None] ** 2)
    return Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert('RGBA')

def paste_rot(canvas, im, pivot_in_im, at, angle=0.0, sx=1.0, sy=1.0):
    """Pega `im` girando sobre `pivot_in_im` (coords en im) para que ese pivote caiga en `at`."""
    if sx != 1 or sy != 1:
        im = im.resize((max(1, round(im.width * sx)), max(1, round(im.height * sy))), Image.BICUBIC)
        pivot_in_im = (pivot_in_im[0] * sx, pivot_in_im[1] * sy)
    pad = int(math.hypot(im.width, im.height))
    big = Image.new('RGBA', (pad * 2, pad * 2), (0, 0, 0, 0))
    ox, oy = pad - pivot_in_im[0], pad - pivot_in_im[1]
    big.paste(im, (round(ox), round(oy)))
    big = big.rotate(angle, resample=Image.BICUBIC, center=(pad, pad))
    canvas.alpha_composite(big, (round(at[0] - pad), round(at[1] - pad)))

# ---- Esqueleto -------------------------------------------------------------
G = 1.18
BODY_S = 1.85 * G
HEAD_S = 1.32 * G
ARM_S = 1.5 * G

def character(canvas, t, x, y, head='head_cansada', head_pop=0.0, arm_r='arm_baja_taza',
              arm_l='arm_manga_izq', arm_r_ang=0.0, arm_l_ang=0.0, head_ang=0.0, boil_seed=0, shake=0.0,
              blink=False, head_dx=0.0, shadow=True):
    """x,y = punto entre los pies. t en segundos.
    Convención: arm_l (lado izquierdo de la imagen) usa piezas *_izq (espejo); arm_r usa las originales.
    Así siempre queda un brazo izquierdo y uno derecho."""
    body = piece('body_sin_brazos', BODY_S)
    breath = 1 + 0.010 * math.sin(t * 2 * math.pi / 3.0)
    # boiling suave: 3 estados en loop, cambian a 6 fps, amplitud mínima
    BOIL = [(0.0, 0.0, 0.0), (0.5, -0.4, 0.25), (-0.4, 0.3, -0.2)]
    bx_, by_, br_ = BOIL[boil_seed % 3]
    bw = body.width
    by = y - body.height * breath
    if shadow:
        d = ImageDraw.Draw(canvas)
        d.ellipse((x - bw * 0.55, y - 18, x + bw * 0.55, y + 22), fill=(74, 46, 39, 38))
    neck = (x + shake, by + 0.035 * body.height)
    sh_r = (x + bw * 0.33, by + 0.12 * body.height)
    sh_l = (x - bw * 0.33, by + 0.12 * body.height)
    paste_rot(canvas, body, (bw / 2, body.height), (x + bx_, y), br_ * 0.5, sy=breath)
    # ambos brazos al frente del cuerpo
    if arm_r:
        a = piece(arm_r, ARM_S)
        paste_rot(canvas, a, ARM_PIVOT[arm_r](a), (sh_r[0] + bx_, sh_r[1]), arm_r_ang - br_)
    if arm_l:
        a = piece(arm_l, ARM_S)
        paste_rot(canvas, a, ARM_PIVOT[arm_l](a), (sh_l[0] + bx_, sh_l[1]), arm_l_ang + br_)
    hd = piece(head + ('_blink' if blink else ''), HEAD_S)
    # squash & stretch con volumen constante (sx = 1/sqrt(sy))
    sy = 1 - 0.08 * head_pop; sx = 1 / math.sqrt(sy)
    bob = 3 * math.sin(t * 2 * math.pi / 2.6)
    paste_rot(canvas, hd, (hd.width / 2, hd.height * 0.93), (neck[0] + by_ + head_dx, neck[1] + bob + 22),
              head_ang + br_, sx=sx, sy=sy)

# pivote (hombro) en cada pieza de brazo, como fracción del tamaño
ARM_PIVOT = {
    'arm_baja_taza':     lambda a: (a.width * 0.22, a.height * 0.12),
    'arm_baja_taza_izq': lambda a: (a.width * 0.78, a.height * 0.12),
    'arm_alza_taza':     lambda a: (a.width * 0.16, a.height * 0.22),
    'arm_alza_taza_izq': lambda a: (a.width * 0.84, a.height * 0.22),
    'arm_senala':        lambda a: (a.width * 0.22, a.height * 0.55),
    'arm_senala_izq':    lambda a: (a.width * 0.78, a.height * 0.55),
    'arm_manga':         lambda a: (a.width * 0.42, a.height * 0.10),
    'arm_manga_izq':     lambda a: (a.width * 0.58, a.height * 0.10),
}



# ---- Transformación global del personaje (squash/stretch, lean, hop) -------------
def composite_transformed(canvas, layer, foot, sx=1.0, sy=1.0, angle=0.0, dy=0.0):
    """Compone `layer` (mismo tamaño que canvas) escalado/rotado alrededor de `foot`.
    Escala primero y luego rota (ángulo en grados, positivo = antihorario en pantalla)."""
    if abs(sx - 1) < 1e-4 and abs(sy - 1) < 1e-4 and abs(angle) < 1e-3 and abs(dy) < 0.05:
        canvas.alpha_composite(layer); return
    th = math.radians(angle); c, s_ = math.cos(th), math.sin(th)
    fx, fy = foot; ox, oy = fx, fy + dy
    a, b = c / sx, -s_ / sx
    d_, e = s_ / sy, c / sy
    cc = fx - a * ox - b * oy
    f = fy - d_ * ox - e * oy
    out = layer.transform(layer.size, Image.AFFINE, (a, b, cc, d_, e, f), resample=Image.BICUBIC)
    canvas.alpha_composite(out)


# =====================================================================================
# KIT V2 (plantilla nueva, oct 2026): 6 cabezas, cuerpo sin cabeza, brazos recto / taza / señala.
# Se activa por defecto; DONITA_KIT=v1 vuelve al kit anterior.
# =====================================================================================
KIT = os.environ.get('DONITA_KIT', 'v2')
P2 = os.path.join(BASE, 'pieces_v2') + '/'
S2 = 0.95                      # escala global del kit v2 en el lienzo 1080x1920

# nombres del guion -> cabeza v2 (los nombres viejos siguen funcionando)
HEAD_V2 = {'head_cansada': 'cabeza_cansada', 'head_estres': 'cabeza_preocupada',
           'head_emocionada': 'cabeza_emocionada'}
NO_BLINK_V2 = {'cabeza_cansada', 'cabeza_esceptica'}   # ya tienen párpado a media asta

def head_v2(name):
    n = HEAD_V2.get(name, name)
    return n if n.startswith('cabeza_') else 'cabeza_' + n

def gesture_kind(arm):
    """Tipo de gesto del brazo, independiente del kit: alza | senala | taza | reposo."""
    if arm in ('arm_alza_taza', 'brazo_taza_alza', 'alza'): return 'alza'
    if arm in ('arm_senala', 'brazo_senala', 'senala'): return 'senala'
    if arm in ('arm_baja_taza', 'brazo_taza', 'taza'): return 'taza'
    return 'reposo'

def emo_kind(head):
    """Clase de actuación: emocionada | tensa | calmada."""
    h = head_v2(head)
    if h == 'cabeza_emocionada': return 'emocionada'
    if h in ('cabeza_preocupada', 'cabeza_enojada'): return 'tensa'
    return 'calmada'

@functools.lru_cache(None)
def piece2(name, scale=S2):
    im = Image.open(P2 + name + '.png').convert('RGBA')
    if name == 'cuerpo_sin_cabeza':          # quita el cuellito: el cuello lo pone la cabeza, detrás del suéter
        a = np.array(im); a[:BODY2_COLLAR_Y, 200:290, 3] = 0; im = Image.fromarray(a)
    if name.startswith('cabeza_'):            # el cuello se alarga hacia abajo para meterse bajo el cuello del suéter
        pass
    return im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)

# Anclas en coordenadas de la pieza SIN escalar (px de la plantilla)
BODY2_COLLAR_Y = 54
BODY2 = dict(foot=(222, 872), neck=(244, 66), sh_l=(138, 138), sh_r=(352, 138))
ARM2 = {   # pieza: pivote del hombro
    'brazo_recto_izq': lambda w, h: (w * 0.66, h * 0.05),
    'brazo_recto_der': lambda w, h: (w * 0.34, h * 0.05),
    'brazo_taza_der':  lambda w, h: (w * 0.76, h * 0.09),
    'brazo_taza_izq':  lambda w, h: (w * 0.24, h * 0.09),
    'brazo_senala_apunta_der': lambda w, h: (w * 0.14, h * 0.44),
    'brazo_senala_apunta_izq': lambda w, h: (w * 0.86, h * 0.44),
}
GESTURE_PIECE_V2 = {'alza': 'brazo_taza_der', 'taza': 'brazo_taza_der',
                    'senala': 'brazo_senala_apunta_der', 'reposo': 'brazo_recto_der'}

@functools.lru_cache(None)
def head_neck_pivot(name):
    """Centro del cuellito (abajo) de cada cabeza, sin escalar."""
    a = np.array(Image.open(P2 + name + '.png'))[..., 3]
    row = np.where(a[a.shape[0] - 12] > 128)[0]
    return ((row.min() + row.max()) / 2, a.shape[0] - 4)

def character_v2(canvas, t, x, y, head='cabeza_neutral', head_pop=0.0, gesture='reposo',
                 gesture_ang=0.0, rest_ang=0.0, head_ang=0.0, boil_seed=0, blink=False, head_dx=0.0):
    """x,y = punto entre los pies. Orden de capas: cabeza (cuello bajo el suéter) -> cuerpo -> brazos al frente.
    Brazo de gesto en el lado derecho de la imagen; brazo recto en el izquierdo."""
    s = S2
    body = piece2('cuerpo_sin_cabeza')
    breath = 1 + 0.010 * math.sin(t * 2 * math.pi / 3.0)
    BOIL = [(0.0, 0.0, 0.0), (0.5, -0.4, 0.25), (-0.4, 0.3, -0.2)]
    bx_, by_, br_ = BOIL[boil_seed % 3]
    fx, fy = BODY2['foot']
    def at(px, py):  # punto de la pieza del cuerpo -> lienzo (con respiración en y)
        return (x + (px - fx) * s + bx_, y - (fy - py) * s * breath)
    # cabeza
    hn = head_v2(head)
    hd = piece2(hn + ('_blink' if blink and hn not in NO_BLINK_V2 else ''))
    pvx, pvy = head_neck_pivot(hn)
    sy = 1 - 0.08 * head_pop; sx = 1 / math.sqrt(sy)
    bob = 3 * math.sin(t * 2 * math.pi / 2.6)
    nx, ny = at(*BODY2['neck'])
    paste_rot(canvas, hd, (pvx * s, pvy * s), (nx + by_ + head_dx, ny + bob), head_ang + br_, sx=sx, sy=sy)
    # cuerpo
    paste_rot(canvas, body, (fx * s, fy * s), (x + bx_, y), br_ * 0.5, sy=breath)
    # brazos
    rest = piece2('brazo_recto_izq')
    paste_rot(canvas, rest, ARM2['brazo_recto_izq'](rest.width, rest.height), at(*BODY2['sh_l']), rest_ang + br_)
    gp = GESTURE_PIECE_V2[gesture]; g = piece2(gp)
    paste_rot(canvas, g, ARM2[gp](g.width, g.height), at(*BODY2['sh_r']), gesture_ang - br_)
