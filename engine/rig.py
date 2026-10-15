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
              arm_l='arm_manga_izq', arm_r_ang=0.0, arm_l_ang=0.0, head_ang=0.0, boil_seed=0, shake=0.0):
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
    hd = piece(head, HEAD_S)
    sx = 1 + 0.10 * head_pop; sy = 1 - 0.08 * head_pop
    bob = 3 * math.sin(t * 2 * math.pi / 2.6)
    paste_rot(canvas, hd, (hd.width / 2, hd.height * 0.93), (neck[0] + by_, neck[1] + bob + 22),
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

