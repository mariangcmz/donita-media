"""Renderiza los Reels de una semana desde un JSON de guiones.
Uso: python3 render_week.py guiones/semana_01.json salida_dir [id ...]
"""
import sys, json, os, subprocess
import make_video as mv

SCENE_LEN = 3.4

def load(video):
    scenes, t = [], 0.0
    for e in video['escenas']:
        scenes.append(dict(t0=t, t1=t + SCENE_LEN, head=e['head'], arm_r=e['arm'], arm_l='arm_manga_izq',
                           text=e['text'], hl=e.get('hl'), note=e.get('note'),
                           props=e.get('props', []), shake=e.get('shake', False)))
        t += SCENE_LEN
    return scenes

def render(video, out):
    mv.SCENES = load(video)
    dur = mv.SCENES[-1]['t1']
    n = int(dur * mv.FPS)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{mv.W}x{mv.H}', '-r', str(mv.FPS), '-i', '-',
                          '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-shortest',
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
