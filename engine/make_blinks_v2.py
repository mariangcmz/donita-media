"""Parpadeo para el kit v2: detecta las pupilas (manchas oscuras verticales dentro de los lentes)
y genera cabeza_*_blink.png. Cansada y escéptica no llevan parpadeo (ya tienen párpado a media asta).
Uso: python3 make_blinks_v2.py"""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, os
from scipy import ndimage as nd
BASE = os.path.dirname(os.path.abspath(__file__)); P = f'{BASE}/pieces_v2'
ESP = (60, 36, 32)
def pupils(a):
    rgb = a[..., :3].astype(int); dark = (rgb.sum(2) < 200) & (a[..., 3] > 200)
    lab, n = nd.label(dark); out = []
    for i, sl in enumerate(nd.find_objects(lab)):
        ys, xs = sl; h, w = ys.stop - ys.start, xs.stop - xs.start
        area = (lab[sl] == i + 1).sum()
        if 180 < area < 900 and h > w * 1.2 and 220 < ys.start < 380:
            out.append(((xs.start + xs.stop) / 2, (ys.start + ys.stop) / 2, w / 2, h / 2))
    best = None
    for i in range(len(out)):
        for j in range(i + 1, len(out)):
            a_, b_ = sorted([out[i], out[j]])
            dx = b_[0] - a_[0]
            if not 80 < dx < 170: continue
            cost = abs(a_[1] - b_[1]) + 2 * abs(a_[3] - b_[3]) + abs(a_[2] - b_[2])
            if best is None or cost < best[0]: best = (cost, [a_, b_])
    return best[1] if best else []
for name in ['cabeza_neutral', 'cabeza_emocionada', 'cabeza_enojada', 'cabeza_preocupada']:
    im = Image.open(f'{P}/{name}.png').convert('RGBA'); a = np.array(im); out = im.copy()
    eyes = pupils(a); assert len(eyes) == 2, (name, eyes)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    for cx, cy, hw, hh in eyes:
        r = ((xx - cx) / (hw + 10)) ** 2 + ((yy - cy) / (hh + 8)) ** 2
        px = a[(r > 1.3) & (r < 2.2) & (a[..., 3] > 200)][:, :3].astype(int)
        px = px[(px.mean(1) > 140)]
        col = tuple(int(v) for v in np.median(px, 0))
        mask = Image.new('L', im.size, 0)
        ImageDraw.Draw(mask).ellipse((cx - hw - 6, cy - hh - 6, cx + hw + 6, cy + hh + 6), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(2))
        layer = Image.new('RGBA', im.size, col + (255,)); layer.putalpha(mask); out.alpha_composite(layer)
        d = ImageDraw.Draw(out); w = hw + 9
        d.arc((cx - w, cy - 10, cx + w, cy + 10), start=15, end=165, fill=ESP, width=5)
    out.save(f'{P}/{name}_blink.png'); print('ok', name, [tuple(round(v) for v in e) for e in eyes])
