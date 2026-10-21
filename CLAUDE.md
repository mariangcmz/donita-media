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

## Kit del personaje (v2 por defecto)
- `engine/pieces_v2/`: kit nuevo (oct 2026) — 6 cabezas, `cuerpo_sin_cabeza`, brazos `recto` / `taza` / `senala`.
  `DONITA_KIT=v1` vuelve al kit anterior (`engine/pieces/`). `_plantilla_original.png` es la hoja fuente.
- En v2 la cabeza va detrás del suéter (el cuello se mete bajo el cuello del suéter), luego cuerpo, luego brazos al frente.
  Brazo de gesto en el lado derecho de la imagen (apunta hacia los `nodes`), brazo recto en el izquierdo.
- `head` acepta: `cabeza_neutral | cabeza_cansada | cabeza_emocionada | cabeza_enojada | cabeza_preocupada | cabeza_esceptica`
  (los nombres viejos siguen sirviendo: head_cansada→cansada, head_estres→preocupada, head_emocionada→emocionada).
- `arm` acepta lo de siempre: `arm_baja_taza` (taza al frente), `arm_alza_taza` (alza la taza), `arm_senala`;
  o en v2 también `brazo_recto` (brazo en reposo, sin taza).
- Parpadeo v2: `python3 make_blinks_v2.py` (cansada y escéptica no parpadean: ya tienen párpado a media asta).
- Los MP4 de `semana_01/` se quedan con el kit v1 (Metricool los toma de esas URLs); no re-renderizar encima sin que Mariana lo pida.

## Reels con clips del banco (videos de Gemini)
- `banco/<tema>/NN_accion_emocion.mp4` + `engine/compose_clips.py guiones/clips_<tema>.json salida.mp4`.
- Texto en modo bold (`grande`, por defecto en clips): Nunito 800 de 112/100/86 px según líneas; notitas Kalam 64 px al margen.
- Recetas y reglas de reutilización: sistema de diseño "La Doñita Dev" → sección Banco de clips.
- El banco es cerrado: lo ya generado se reutiliza, pero no se depende de generar video con IA. Lo diario se anima por código.
- Ropa de la doñita: sudadera azul o suéter salmón, se pueden alternar.

## Formato de guion (JSON)
Lista de videos; cada uno: `dia`, `id`, `escenas` (4). Cada escena:
`head` (head_cansada | head_estres | head_emocionada), `arm` (arm_baja_taza | arm_alza_taza | arm_senala),
`text` (2-3 líneas, máx ~19 caracteres c/u), `hl` (texto de una línea a subrayar o null),
opcionales: `note` (notita Kalam corta), `props` (laptop | nodes | mug), `shake` (true en escenas de estrés).
Arco típico: 1) gancho/dolor 2) estrés o giro 3) solución (señala + nodes) 4) cierre (taza + mug).

## Animación (skill animacion-cartoon-cutout)
La actuación vive en `performance()` de `make_video.py`: anticipación, squash & stretch con volumen constante,
follow-through (cabeza y manga con resorte), lean por emoción, parpadeo (`pieces/*_blink.png`, se regeneran con
`make_blinks.py`) y miradas. Antes de publicar cambios al rig corre
`python3 qa_sheet.py guiones/semana_XX.json <id> /tmp/qa.png` y revisa la hoja (poses + siluetas + volumen ≤ 0.05).

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
