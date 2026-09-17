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

## Fase 0 — Validar viabilidad comercial con Tuya (bloqueante para vender el servicio)

Antes de invertir en infraestructura multi-usuario o en modelos de IA,
hay que confirmar que el modelo de negocio es viable del lado de Tuya —
si esta puerta está cerrada o es cara, cambia el diseño completo (podría
implicar soportar otras marcas de dispositivos, no solo Tuya).

Investigado el 17-sep-2026 contra la documentación oficial de Tuya:

- **La cuenta que usamos hoy (Trial Edition) prohíbe explícitamente el
  uso comercial.** Es solo para desarrolladores individuales o para
  pruebas/debugging. Venderle esto a otros usuarios con esta cuenta
  viola los términos de Tuya.
- **Uso comercial requiere "IoT Core" de pago**, cotizado por proyecto
  según cantidad de dispositivos, región y mix de servicios — el precio
  no está publicado, hay que contactar ventas de Tuya para una cotización.
- **Límites de API generales**: 500 llamadas/segundo de tráfico API y
  500.000/día de tráfico de app (los límites reales del plan pago se
  negocian por proyecto, no son fijos).
- **Sí existe un camino multi-usuario real**: el flujo OAuth 2.0
  "Link App Account" permite que cada usuario autorice tu app sin que
  vos manejes su API key/secret personal (a diferencia de lo que
  hicimos nosotros, donde el usuario nos dio sus credenciales directo).
- **Opcional, no obligatorio**: si en el futuro se quisiera una app
  propia con branding (no solo un panel web), existe el "Smart App SDK"
  de Tuya, con un precio de referencia de ejemplo de ~USD 5.000/año
  inicial + USD 2.000/año de renovación.

**Acción concreta antes de seguir**: contactar a ventas de Tuya para
confirmar que el caso de uso (panel de monitoreo multi-usuario) califica
para su plan comercial, y obtener una cotización real según usuarios
proyectados.

Fuentes: [Pricing — Tuya Developer Platform](https://developer.tuya.com/en/docs/iot/membership-service?id=K9m8k45jwvg9j),
[Límites de frecuencia de API](https://developer.tuya.com/en/docs/iot/frequency-control?id=Kcojz2r2dg1f6),
[Integración de terceros / Link App Account](https://developer.tuya.com/en/docs/iot/thirdparty-login-support?id=Kaiuyr8ey0k6u),
[Flujo de autorización OAuth 2.0](https://developer.tuya.com/en/docs/iot/authorization-code-page-usage?id=Kdkyz44dz6a7r),
[Pricing — Smart App SDK](https://developer.tuya.com/en/docs/app-development/app-sdk-price?id=Kbu0tcr2cbx3o).

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
