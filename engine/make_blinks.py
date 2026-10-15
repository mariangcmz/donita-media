"""Genera variantes de cabeza con ojos cerrados (para parpadeo). Uso: python3 make_blinks.py"""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, os
BASE = os.path.dirname(os.path.abspath(__file__))
ESP = (74, 46, 39)
# centro (x,y), semiancho, semialto del ojo en coords de la pieza; modo de muestreo de color
EYES = {
    'head_emocionada': ('ring',  [((131, 245), 13, 20), ((222, 236), 13, 20)]),
    'head_estres':     ('ring',  [((130, 234), 14, 14), ((197, 234), 14, 14)]),
    'head_cansada':    ('inner', [((120, 250), 27, 17), ((226, 244), 27, 17)]),
}
def sample(a, cx, cy, hw, hh, mode):
    ys, xs = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    r = ((xs - cx) / hw) ** 2 + ((ys - cy) / hh) ** 2
    m = ((r > 1.4) & (r < 2.2)) if mode == 'ring' else (r < 1.0)
    px = a[m & (a[..., 3] > 200)][:, :3].astype(int)
    px = px[(px.mean(1) > 120) & (px.mean(1) < 235)]   # sin líneas oscuras ni blancos de ojo
    return tuple(int(v) for v in np.median(px, 0))
for name, (mode, eyes) in EYES.items():
    im = Image.open(f'{BASE}/pieces/{name}.png').convert('RGBA')
    a = np.array(im); out = im.copy()
    for (cx, cy), hw, hh in eyes:
        col = sample(a, cx, cy, hw, hh, mode)
        mask = Image.new('L', im.size, 0)
        ImageDraw.Draw(mask).ellipse((cx - hw, cy - hh, cx + hw, cy + hh), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(2.5)).point(lambda v: min(255, v * 2))
        layer = Image.new('RGBA', im.size, col + (0,)); layer.putalpha(mask)
        out.alpha_composite(layer)
    d = ImageDraw.Draw(out)
    for (cx, cy), hw, hh in eyes:
        w = max(hw - 2, 12)
        d.arc((cx - w, cy - 9, cx + w, cy + 9), start=10, end=170, fill=ESP, width=5)  # ojo cerrado
    out.save(f'{BASE}/pieces/{name}_blink.png')
    print('ok', name)
