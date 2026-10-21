# Banco de clips (generador de video)

Clips generados con Gemini a partir de la doñita de referencia. Sin texto: el texto se monta encima en Canva.
Formato: 720x1280 (9:16), 10 s, con audio del generador (quitar o reemplazar por música al editar).

## reel_pedidos_whatsapp — "Deja de copiar pedidos de WhatsApp a mano"
| # | Archivo | Escena | Estado |
|---|---------|--------|--------|
| 1 | 01_hook_estres.mp4 | Hook: globitos de chat le caen encima, cabeza estrés | ✅ |
| 2 | 02_problema_cansada.mp4 | Problema: libreta tachada + copa, cansada | ✅ |
| 3 | 03_paso1_form.mp4 | Paso 1: Google Form flotando con nodos | ✅ (chongo un poco más rizado, pasa) |
| 4 | 04_paso2_sheets.mp4 | Paso 2: form conectado a tabla que se llena | ✅ (v1 con cabello claro guardada como blooper) |
| 5 | 05_cambio.mp4 | Globitos se vuelven filas ordenadas | ✅ |
| 6 | 06_cta_brindis.mp4 | CTA: brindis con copa + confeti | ✅ |

## Cómo se usan
- Armado: `cd engine && python3 compose_clips.py guiones/clips_<tema>.json salida.mp4` (clip encogido al 73 %, fondo empatado con crema, texto bold grande, música lo-fi).
- Primer reel: `reels/pedidos_whatsapp_tip.mp4` (guion `engine/guiones/clips_pedidos_whatsapp.json`, contado como tip).
- Recetas para reutilizar los clips y reglas (no repetir clip en días seguidos, máx. 2 reels de banco por semana): sistema de diseño "La Doñita Dev", sección **Banco de clips**.
