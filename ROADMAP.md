# Roadmap: hacia una IA energética

Este documento registra el estado actual del proyecto y el plan a futuro
para evolucionarlo de un sistema de monitoreo con heurísticas a un
sistema que use modelos de IA/ML de verdad.

## v1 — Estado actual (completado)

La base de datos y el pipeline sobre el cual construir una IA energética.
Todavía no es IA (es estadística clásica y reglas fijas), pero es la
infraestructura que cualquier proyecto de IA necesita antes de poder
entrenar algo.

- **Recolección automatizada**: `logger.py` corre cada 5 minutos vía
  GitHub Actions (`cron.yml`), lee el dispositivo Tuya y guarda la
  lectura en `historico_energia.csv`.
- **Datos limpios y estructurados**: timestamp (UTC), potencia (W) y
  energía acumulada (kWh, calculada por regla trapezoidal).
- **Backfill histórico**: `backfill.py` recuperó el histórico disponible
  desde los logs de Tuya (`getdevicelog`).
- **Panel público en vivo**: `index.html` publicado en GitHub Pages
  (`https://arcomisp.github.io/MonitoreoEnergia/`), sin costo, instalable
  como PWA en el celular.
- **Heurísticas de "insights"**:
  - Detección de anomalías por z-score (umbral configurable, actualmente 2.0σ)
  - Proyección de consumo mensual por extrapolación lineal del ritmo diario
  - Resumen en texto generado por plantilla (no por un modelo de lenguaje)

## v2 — Camino a IA real (a futuro)

1. **Más historia**: acumular semanas/meses de datos para que un modelo
   pueda aprender patrones reales (día de semana vs. fin de semana, hora
   pico, estacionalidad). Las heurísticas actuales no necesitan esto,
   pero cualquier modelo sí.
2. **Modelo de predicción de consumo**: reemplazar la proyección lineal
   por un modelo de series de tiempo (ej. Prophet, ARIMA, o una red
   simple) que capture estacionalidad y tendencia real.
3. **Modelo de detección de anomalías**: reemplazar el z-score fijo por
   un modelo que aprenda el patrón "normal" específico del dispositivo
   (ej. isolation forest, autoencoder, o un modelo estacional que sepa
   que 80W a las 2pm es normal pero a las 3am no).
4. **Dónde entrenar y correr el modelo**: GitHub Pages es estático y no
   puede entrenar nada. Opciones:
   - Un GitHub Action que reentrena periódicamente (ej. una vez por
     semana) y exporta el resultado (parámetros o predicciones) como un
     JSON que el panel consume — mantiene todo gratis y sin servidor.
   - Un servicio externo si el modelo se vuelve pesado de entrenar.
5. **Métrica de éxito**: el modelo nuevo solo se adopta si mejora
   objetivamente al baseline de heurísticas actual (menos falsos
   positivos en anomalías, menor error de predicción de consumo).

## Ideas descartadas / pendientes de decisión

- **Notificaciones proactivas** (Telegram/email) de resúmenes o alertas:
  el usuario eligió por ahora que todo se consulte desde el panel, sin
  push. Si esto cambia, requiere secrets nuevos (token de bot o SMTP).
- **Dominio propio**: no es necesario, GitHub Pages ya da hosting y
  subdominio gratis (`github.io`). Solo tendría sentido por estética.
