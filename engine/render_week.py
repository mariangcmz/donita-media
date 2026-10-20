"""Renderiza los Reels de una semana desde un JSON de guiones.
Uso: python3 render_week.py guiones/semana_01.json salida_dir [id ...]
"""
import sys, json, os, subprocess
import make_video as mv

SCENE_LEN = 3.4

def load(video):
    scenes, t = [], 0.0
    for e in video['escenas']:
        dur = e.get('dur', SCENE_LEN)
        scenes.append(dict(t0=t, t1=t + dur, head=e['head'], arm_r=e['arm'], arm_l='arm_manga_izq',
                           text=e['text'], hl=e.get('hl'), note=e.get('note'), note_pos=e.get('note_pos'),
                           estilo=e.get('estilo'), props=e.get('props', []), shake=e.get('shake', False)))
        t += dur
    return scenes

def audio_input(video, dur):
    """Música de fondo si el guion trae "musica" (ruta relativa a engine/), si no, silencio."""
    m = video.get('musica')
    if m:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), m)
        return ['-i', path, '-af', f'afade=t=in:d=0.8,afade=t=out:st={max(0, dur - 1.5):.2f}:d=1.5']
    return ['-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo']

def render(video, out):
    mv.SCENES = load(video)
    dur = mv.SCENES[-1]['t1']
    n = int(dur * mv.FPS)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{mv.W}x{mv.H}', '-r', str(mv.FPS), '-i', '-',
                          *audio_input(video, dur), '-shortest',
                          '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium',
                          '-c:a', 'aac', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for fi in range(n):
        p.stdin.write(mv.frame(fi).tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    src, outdir, *ids = sys.argv[1:]
    os.makedirs(outdir, exist_ok=True)
    videos = json.load(open(src))
    for i, v in enumerate(videos, 1):
        if ids and v['id'] not in ids:
            continue
        out = os.path.join(outdir, f"{i:02d}_{v['dia']}_{v['id']}.mp4")
        render(v, out)
        print('ok', out, flush=True)
