# La Doñita Dev — content engine

Repo de Mariana (@ladonitadev). Aquí viven el motor de video y los videos publicados.
Los videos se sirven públicos desde `raw.githubusercontent.com/mariangcmz/donita-media/main/...`
y Metricool los descarga de ahí.

## Fuente de verdad (leer antes de escribir o diseñar)
Este repo no define la marca: la sigue. Si algo de aquí choca con estas fuentes, mandan ellas.
1. **Skill `politica-editorial`**: qué se produce, cómo se decide y qué se rechaza. Manda sobre todo lo demás.
   Documento completo y anexo de la marca (sección 10, fila "La Doñita Dev"):
   https://claude.ai/artifact/3MQfaXvXPFxNUvkSzCfbij
2. **Skill `donita-dev-contenido`**: posicionamiento, mezcla editorial, voz e identidad visual.
3. **Sistema de diseño "La Doñita Dev"** (fondo blanco, cian): https://claude.ai/artifact/XxPXYC5eM4KFWyujRimKMy
   Ojo: hay otro sistema con el mismo nombre (crema y salmón, CK1MGp12KbxdjtfdbsJDkc). Es el anterior; no se usa.
Si las skills no están disponibles en la sesión, lee los dos links con las herramientas de docs y de Artifact.

## Estructura
- `engine/` — rig de la doñita (Python + PIL + ffmpeg)
  - `rig.py` personaje por piezas, `make_video.py` escenas y texto, `render_week.py` render desde JSON
  - `pieces_v2/` PNGs del personaje, `fonts/` Nunito, Quicksand, Kalam, Space Mono (OFL)
  - `guiones/semana_XX.json` guiones por semana
- `semana_XX/` — MP4 finales, nombres ASCII: `01_lunes.mp4` … `07_domingo.mp4`
- `TEMAS.md` — banco de temas reales y lo ya publicado
- `portadas/`, `carruseles/`, `editorial/` — piezas fijas ya hechas con el sistema nuevo

## Render
```
pip install pillow numpy scipy --break-system-packages   # si faltan
cd engine && python3 render_week.py guiones/semana_XX.json ../semana_XX
```
~4 min por video; con 2 CPUs corre dos procesos en paralelo (pasando ids distintos).
`render_week.py` valida los guiones antes de renderizar y se detiene si algo no cabe: se acortan las
palabras, nunca se baja la letra. Después renombra a ASCII (`01_lunes.mp4`…), `git add`, commit y push.

## Estilo de video v3 (por defecto desde el 26 oct 2026)
Las medidas del Reel viven en el sistema de diseño: componente `ReelAnimado`, sección "Reel animado" del
README y los tokens `reel-*` (léelos con Artifact read en `project/components/ReelAnimado/README.md`).
`engine/make_video.py` (`frame_v3`) los implementa; si el sistema cambia, se ajusta el motor, no al revés.
Resumen: fondo blanco, tinta espresso, todo en x=80 dentro de la franja segura y=240…1680; etiqueta Space Mono
en y=300; titular Nunito Black en mayúsculas en y=400, de 150 a 180 px, máx. 3 líneas, clave en bloque cian
(sobre fondo cian: bloque espresso con letra cian); bajada 52 px en la columna izquierda de 500 px; nota Kalam;
la Doñita abajo a la derecha; @ladonitadev en y=1630.
Fondos por escena: `blanco` (default), `cian` (una o dos por semana), `espresso` (bitácora), `amarillo` (solo lead magnet).
`DONITA_ESTILO=v1` vuelve al estilo anterior (crema, centrado): solo para re-renderizar algo viejo si Mariana lo pide.

## Formato de guion (JSON)
Lista de videos. Cada video: `dia`, `id`, `etiqueta` (obligatoria, ej. `"// fiasco · make"`,
`"// bitácora · 12"`), opcionales `fondo`, `musica` (`musica/lofi_suave.wav`), y `escenas` (4). Cada escena:
- `head`: `head_cansada | head_estres | head_emocionada` o en v2 `cabeza_neutral | cabeza_enojada | cabeza_esceptica …`
- `arm`: `arm_baja_taza | arm_alza_taza | arm_senala | brazo_recto`
- `text`: el titular, 1 a 3 renglones cortos (a 150 px caben ~9 letras en mayúsculas por renglón)
- `hl`: la palabra clave que va en bloque cian; tiene que estar en el titular
- opcionales: `bajada` (≤20 palabras, lo que explica), `note` (notita Kalam corta), `props` (`nodes` | `mug`),
  `shake` (true en escenas de estrés), `fondo`, `dur` (segundos, default 3.4)
Arco típico: 1) gancho/dolor 2) estrés o giro 3) solución (señala + nodes) 4) cierre (taza + mug).
Ejemplo completo: `engine/guiones/prueba_v3.json`.

## Kit del personaje (v2 por defecto)
- `engine/pieces_v2/`: 6 cabezas, `cuerpo_sin_cabeza`, brazos `recto` / `taza` / `senala`.
  `DONITA_KIT=v1` vuelve al kit anterior (`engine/pieces/`). `_plantilla_original.png` es la hoja fuente.
- En v2 la cabeza va detrás del suéter, luego cuerpo, luego brazos al frente.
- Parpadeo v2: `python3 make_blinks_v2.py` (cansada y escéptica no parpadean).
- Los MP4 de `semana_01/` y `semana_02/` se quedan como están (Metricool los toma de esas URLs).

## Reels con clips del banco (videos de Gemini)
- `banco/<tema>/NN_accion_emocion.mp4` + `engine/compose_clips.py guiones/clips_<tema>.json salida.mp4`.
- PENDIENTE: `compose_clips.py` sigue con el estilo viejo. El sistema pide marco de clip (banda espresso arriba
  con el titular, banda cian abajo con la bajada; el crema nunca toca el blanco). Hasta que se actualice,
  no se programan Reels de clips.
- El banco es cerrado: lo ya generado se reutiliza, pero no se genera video nuevo con IA.

## Animación (skill animacion-cartoon-cutout)
La actuación vive en `performance()` de `make_video.py`: anticipación, squash & stretch con volumen constante,
follow-through, lean por emoción, parpadeo y miradas. Movimiento tranquilo, nada de temblores rápidos.
Antes de publicar cambios al rig corre `python3 qa_sheet.py guiones/semana_XX.json <id> /tmp/qa.png`.

## Reglas propias del engine
- **Honestidad:** solo historias que estén en `TEMAS.md` como reales. Ideas a futuro se cuentan como
  "lo voy a hacer". Si una pieza necesita una experiencia de Mariana que no está, es pendiente, no se inventa.
- Si un video dice "mañana te enseño", el día siguiente debe ser esa segunda parte.
- **Revisión del resultado real:** extrae con ffmpeg al menos un cuadro por escena (a mitad de escena) y uno
  de entrada (t≈0.4 s) y MÍRALOS contra el sistema de diseño en tamaño de celular: legibilidad, jerarquía,
  que nada se encime (nota, taza, bajada, Doñita) y tiempo de lectura. Si algo falla, corrige y re-renderiza
  antes de programar.

## Programación en Metricool
Marca `La Doñita Dev`, blogId `7429323`, zona America/Mexico_City.
Un post por día a las 10:00, redes: instagram (REEL, isAiGenerated true), tiktok (isAigc true, sin autoAddMusic: no se permite con video),
youtube (type short, title con #shorts, madeForKids false), facebook (REEL).
Copy: 2-3 frases en la voz de la marca + 4-5 hashtags, siempre #ladonitadev.
