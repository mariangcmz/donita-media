# La Doñita Dev — content engine

Repo de Mariana (@ladonitadev). Aquí viven el motor de video y los videos publicados.
Los videos se sirven públicos desde `raw.githubusercontent.com/mariangcmz/donita-media/main/...`
y Metricool los descarga de ahí.

## Estructura
- `engine/` — rig de la doñita (Python + PIL + ffmpeg)
  - `rig.py` personaje por piezas, `make_video.py` escenas y texto, `render_week.py` render desde JSON
  - `pieces/` PNGs del personaje, `fonts/` Nunito, Quicksand, Kalam (OFL)
  - `guiones/semana_XX.json` guiones por semana
- `semana_XX/` — MP4 finales, nombres ASCII: `01_lunes.mp4` … `07_domingo.mp4`
- `TEMAS.md` — banco de temas reales y lo ya publicado

## Render
```
pip install pillow numpy scipy --break-system-packages   # si faltan
cd engine && python3 render_week.py guiones/semana_XX.json ../semana_XX
```
~6 min por video; con 2 CPUs corre dos procesos en paralelo (pasando ids distintos).
Después renombra a ASCII (`01_lunes.mp4`…), `git add`, commit y push.

## Formato de guion (JSON)
Lista de videos; cada uno: `dia`, `id`, `escenas` (4). Cada escena:
`head` (head_cansada | head_estres | head_emocionada), `arm` (arm_baja_taza | arm_alza_taza | arm_senala),
`text` (2-3 líneas, máx ~19 caracteres c/u), `hl` (texto de una línea a subrayar o null),
opcionales: `note` (notita Kalam corta), `props` (laptop | nodes | mug), `shake` (true en escenas de estrés).
Arco típico: 1) gancho/dolor 2) estrés o giro 3) solución (señala + nodes) 4) cierre (taza + mug).

## Reglas de marca (no negociables)
- Voz: mujer mexicana 35-40, cálida, irónica, cercana. "mija" a veces, no siempre. Nunca "pa'", siempre "para".
- Cero lenguaje corporativo/de agencia: nada de "potencia", "revolucionario", "descubre", "sumérgete", "desbloquea", "transforma tu vida".
- Cero entusiasmo falso. Humor cotidiano, vulnerabilidad, realismo.
- Público: emprendedoras mexicanas; en segundo lugar jóvenes interesadas en programar.
- **Honestidad:** solo historias que estén en `TEMAS.md` como reales. No inventar experiencias de Mariana.
  Si un tema es una idea a futuro, el guion lo dice así ("lo voy a automatizar", no "ya lo hice").
- Si un video dice "mañana te enseño", el día siguiente debe ser esa segunda parte.
- Paleta: crema #F4E8D7, espresso #4A2E27, salmón #E78668. Nada de logos de marcas en props.

## Programación en Metricool
Marca `La Doñita Dev`, blogId `7429323`, zona America/Mexico_City.
Un post por día a las 10:00, redes: instagram (REEL, isAiGenerated true), tiktok (isAigc true, sin autoAddMusic: no se permite con video),
youtube (type short, title con #shorts, madeForKids false), facebook (REEL).
Copy: 2-3 frases en la voz de la marca + 4-5 hashtags, siempre #ladonitadev.
