"""Reel a partir de clips del banco (videos de Gemini) + texto animado de marca + música.
Uso: python3 compose_clips.py guiones/clips_xxx.json salida.mp4

El clip se encoge y se apoya abajo, con orillas difuminadas sobre el papel crema;
arriba queda aire para el texto (mismo estilo que los Reels animados por código).
JSON: {"musica": "musica/lofi_suave.wav", "escenas": [
   {"clip": "../banco/.../01.mp4", "desde": 1.0, "dur": 3.5, "text": [...], "hl": "...", "note": "..."}]}
"""
import sys, json, os, subprocess, numpy as np
from PIL import Image, ImageFilter
import make_video as mv
from rig import W, H, paper_bg, ImageDraw, font, ESPRESSO, CREMA

FPS = mv.FPS
BASE = os.path.dirname(os.path.abspath(__file__))
CLIP_S = 0.73                       # escala del clip (720x1280 -> ancho 788 en 1080)
CW, CH = int(1080 * CLIP_S) // 2 * 2, int(1920 * CLIP_S) // 2 * 2
CX, CY = (W - CW) // 2, H - CH + 10   # apoyado abajo

def feather_mask():
    m = Image.new('L', (CW, CH), 0)
    ImageDraw.Draw(m).rounded_rectangle((40, 40, CW - 40, CH - 10), radius=60, fill=255)
    return m.filter(ImageFilter.GaussianBlur(28))

def read_clip(path, start, dur):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(dur), '-i', path,
           '-vf', f'fps={FPS},scale={CW}:{CH}:flags=lanczos', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (CW * CH * 3)
    return np.frombuffer(raw, np.uint8)[:n * CW * CH * 3].reshape(n, CH, CW, 3)

def match_paper(frames):
    """Empata el fondo del clip con el papel crema (corrige el tono con las esquinas del primer cuadro)."""
    f0 = frames[0].astype(np.float32)
    corners = np.concatenate([f0[:60, :60].reshape(-1, 3), f0[:60, -60:].reshape(-1, 3)])
    off = np.array(CREMA, np.float32) - np.median(corners, 0)
    return np.clip(frames.astype(np.float32) + off * 0.9, 0, 255).astype(np.uint8)

def main(src, out):
    spec = json.load(open(src)); here = os.path.dirname(os.path.abspath(src))
    mask = feather_mask(); bg = paper_bg()
    scenes, t = [], 0.0
    for e in spec['escenas']:
        frames = read_clip(os.path.normpath(os.path.join(here, e['clip'])), e.get('desde', 0), e['dur'])
        scenes.append(dict(t0=t, t1=t + e['dur'], text=e['text'], hl=e.get('hl'), note=e.get('note'),
                           note_pos=e.get('note_pos', 'margen'), estilo=e.get('estilo'), grande=spec.get('grande', True),
                           frames=match_paper(frames)))
        t += e['dur']
    dur = t; n = int(round(dur * FPS))
    audio = ['-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo']
    if spec.get('musica'):
        audio = ['-i', os.path.join(BASE, spec['musica']), '-af', f'afade=t=in:d=0.8,afade=t=out:st={dur - 1.5:.2f}:d=1.5']
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', *audio, '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                          '-crf', '20', '-preset', 'medium', '-c:a', 'aac', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    fh = font('Nunito[wght].ttf', 38, 700)
    for fi in range(n):
        tt = fi / FPS
        sc = next(s for s in scenes if s['t0'] <= tt < s['t1'] + 1e-9)
        lt = tt - sc['t0']
        k = min(int(lt * FPS), len(sc['frames']) - 1)
        c = bg.copy()
        c.paste(Image.fromarray(sc['frames'][k]), (CX, CY), mask)
        mv.draw_text_block(c, sc, tt)
        d = ImageDraw.Draw(c)
        d.text((W / 2 - d.textlength('@ladonitadev', font=fh) / 2, 1858), '@ladonitadev', font=fh, fill=ESPRESSO + (170,))
        if lt < 0.08 and sc['t0'] > 0:
            c.alpha_composite(Image.new('RGBA', (W, H), CREMA + (120,)))
        p.stdin.write(c.convert('RGB').tobytes())
    p.stdin.close(); p.wait(); print('ok', out, round(dur, 2), 's')

if __name__ == '__main__':
    main(*sys.argv[1:3])
