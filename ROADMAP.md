# Roadmap: hacia una IA energética

Este documento registra el estado actual del proyecto y el plan a futuro
para evolucionarlo de un sistema de monitoreo con heurísticas a un
sistema que use modelos de IA/ML de verdad.

## Principio guía: ser competitivos frente a Smart Life

Cualquier feature nueva se mide contra esta pregunta: **¿esto compite con
Smart Life, o lo complementa?** Tratar de igualar a Smart Life en control
de dispositivos y amplitud de ecosistema es una batalla perdida — es de
Tuya mismo, gratis, con años de desarrollo, y soporta cualquier
dispositivo de su catálogo. Ahí no competimos.

Los huecos reales donde sí hay ventaja posible:

1. **Es genérica, no está pensada para energía.** Smart Life solo
   muestra un dato suelto de kWh por dispositivo, sin análisis,
   proyección, ni anomalías. Eso es exactamente lo que ya construimos
   (Resumen e Insights, detección de anomalías, proyección mensual).
2. **Es un jardín cerrado de un solo fabricante.** Solo dispositivos
   Tuya. Nuestro panel, al ser propio, puede combinar datos de
   cualquier fabricante (Tuya, eWeLink/Sonoff, otros) en un solo lugar.
3. **No traduce a plata real.** Muestra kWh, no costo real según la
   tarifa eléctrica del usuario (que en muchos países tiene tramos).
4. **No compara ni da contexto.** Un número suelto no dice si es mucho
   o poco; comparar contra el propio histórico, contra hogares
   similares, o contra una meta, sí genera valor.
5. **No es multi-propiedad ni multi-usuario con roles.** Compartir una
   vista de solo lectura, o administrar varias propiedades, no es su
   caso de uso.

**Posicionamiento**: no reemplazamos a Smart Life, somos la capa de
inteligencia energética que corre *sobre* lo que el usuario ya tiene
instalado (incluso si es Smart Life). El pitch: *Smart Life te dice qué
hace cada dispositivo; nosotros te decimos qué significa eso para tu
bolsillo — a través de dispositivos y marcas, con análisis real, no
solo el número crudo.*

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

### Otros fabricantes: Sonoff / eWeLink

Investigado el mismo día — Sonoff usa la plataforma **eWeLink** (de
CoolKit Technologies), y el patrón comercial es casi idéntico al de Tuya:

- **Plan "Personal Developer" (gratis)**: solo soporta login OAuth 2.0,
  con una credencial de acceso válida por 1 año, documentación limitada,
  una lista reducida de APIs, y sin soporte técnico.
- **Plan "Enterprise Developer" (pago)**: requerido para uso comercial.
  Más APIs, mejor estabilidad, soporte técnico y de negocio. Precio no
  publicado — contactar a `bd@coolkit.cn`.
- **OAuth 2.0 para multi-usuario** ya existe, igual que "Link App
  Account" de Tuya.
- **Alcance mayor**: eWeLink es la nube detrás de varias marcas de
  enchufes inteligentes económicos, no solo Sonoff — soportar eWeLink
  da acceso a varios fabricantes con una sola integración.

**Conclusión**: ningún fabricante de IoT relevante tiene un plan
gratuito que permita uso comercial — es su modelo de negocio. Soportar
múltiples fabricantes (Tuya + eWeLink, y potencialmente más) aumenta el
alcance de usuarios posibles, pero multiplica también los acuerdos
comerciales y las integraciones a mantener.

Fuentes: [Pricing — Tuya Developer Platform](https://developer.tuya.com/en/docs/iot/membership-service?id=K9m8k45jwvg9j),
[Límites de frecuencia de API](https://developer.tuya.com/en/docs/iot/frequency-control?id=Kcojz2r2dg1f6),
[Integración de terceros / Link App Account](https://developer.tuya.com/en/docs/iot/thirdparty-login-support?id=Kaiuyr8ey0k6u),
[Flujo de autorización OAuth 2.0](https://developer.tuya.com/en/docs/iot/authorization-code-page-usage?id=Kdkyz44dz6a7r),
[Pricing — Smart App SDK](https://developer.tuya.com/en/docs/app-development/app-sdk-price?id=Kbu0tcr2cbx3o),
[eWeLink Pricing](https://github.com/CoolKit-Technologies/eWeLink-API/blob/main/en/Pricing.md),
[eWeLink CUBE Open API](https://ewelink.cc/ewelink-cube/introduce-open-api/).

### Alternativa: tener nuestra propia nube de IoT

En vez de depender 100% de los planes comerciales de Tuya/eWeLink, hay
tres caminos posibles, de menor a mayor independencia (y de menor a
mayor esfuerzo):

**Opción A — Control local, sin pasar por la nube del fabricante.**
Muchos dispositivos Tuya (y derivados) permiten control local en la red
propia, sin pasar por los servidores de Tuya (ej. `localtuya` de Home
Assistant). Se extrae una "local key" una sola vez con la app oficial y
después se controla el dispositivo directo por WiFi local.
- Sin límites de API ni tarifas por dispositivo.
- Zona gris legal para un producto comercial: se sigue usando hardware
  de Tuya, y extraer/usar la local key a escala para vender un servicio
  podría chocar con sus términos; Tuya puede cambiar el protocolo local
  cuando quiera.

**Opción B — Hardware propio con firmware abierto (independencia real).**
Muchos enchufes inteligentes "Tuya" usan chips ESP8266/ESP32 genéricos
por dentro, reflasheables con firmware abierto (Tasmota, ESPHome, vía
`tuya-convert`) que habla directo con un servidor MQTT propio — cero
dependencia de Tuya, eWeLink, ni nadie.
- 100% propio: sin cuotas, sin ToS de terceros, dueño total de los datos.
- Esfuerzo grande: hay que flashear cada dispositivo (o conseguir
  hardware ya compatible), armar el propio broker MQTT + backend, y
  hacerse cargo de actualizaciones de firmware/seguridad — se pasa de
  "usar una nube" a "operar una".

**Opción C — Nube propia de "inteligencia", usando Tuya/eWeLink solo
como capa de datos.** El camino intermedio, y hacia donde ya venimos
yendo en la práctica: pagar el plan comercial de Tuya/eWeLink (Fase 0)
solo para la comunicación con el dispositivo, pero todo lo demás (base
de datos, backend, dashboard, modelos de IA) es propio. El usuario final
no sabe ni le importa qué nube de dispositivo hay detrás.
- Mucho menos esfuerzo que la Opción B, control total sobre la
  experiencia y los datos.
- Se sigue dependiendo de que Tuya/eWeLink no suban precios o cambien
  reglas.

**Recomendación**: arrancar con la Opción C. Si el proyecto crece mucho
y los costos de Tuya/eWeLink se vuelven un problema real, evaluar la
Opción B — no como punto de partida, porque implica mucho hardware y
operación antes de validar si el negocio funciona.

#### Estimación de costos de la Opción C

Investigado el 17-sep-2026. Se separa lo estimable con confianza (la
infraestructura propia) de lo que requiere cotización real (Tuya/eWeLink).

**Infraestructura propia** (escala inicial: cientos a pocos miles de usuarios):

| Servicio | Costo estimado |
|---|---|
| Base de datos (Supabase Pro, series de tiempo) | $25/mes |
| Backend/API (Railway o similar) | $5-20/mes |
| Dominio propio (opcional) | ~$1/mes amortizado |
| **Total infra propia** | **~$30-50/mes para arrancar** |

Esto escala gradualmente — Supabase Pro cubre cómodamente hasta el orden
de decenas/cientos de miles de usuarios activos antes de necesitar
planes más caros (Team a $599/mes).

**Costo de Tuya/eWeLink: no estimable con confianza.** La variabilidad
encontrada es enorme:
- Mención de un plan básico de IoT Core desde ~$0.20/mes (posiblemente
  por dispositivo, pero la fuente no aclara la unidad con precisión).
- Caso real reportado en el foro de Home Assistant: a un desarrollador,
  al terminar su prueba gratuita, le cotizaron **USD 25.000/año** por la
  edición "Flagship" de Tuya Cloud.

Esa diferencia (de centavos a decenas de miles de dólares) confirma que
depende totalmente del plan/tier según volumen de dispositivos y
funcionalidades — no hay tarifa estándar publicada. La Fase 0
(contactar ventas de Tuya) sigue siendo el paso obligatorio antes de
poder armar un presupuesto real.

Fuentes: [Membership and fees — Tuya Support](https://support.tuya.com/en/help/_list?category=751038),
[Cost of Tuya Cloud — Home Assistant Community](https://community.home-assistant.io/t/cost-of-tuya-cloud/571623),
[Supabase Pricing 2026](https://makerkit.dev/blog/saas/supabase-pricing).

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

## Hardware: medición por circuito (totalizador + submedidores)

En vez de inferir con IA qué aparato consume qué (NILM, un problema de
investigación difícil y poco confiable), medir cada circuito por
separado con hardware real — el enfoque de los mejores productos
comerciales de monitoreo energético del hogar.

**Arquitectura propuesta:**
- 1 medidor totalizador en el breaker principal del panel (mide todo
  el apartamento)
- N medidores por circuito individual (cocina, iluminación, aire
  acondicionado, etc.)
- Validación cruzada automática: si la suma de los circuitos no
  coincide con el totalizador, hay un circuito sin instrumentar o un
  sensor fallando

**Productos Tuya-compatibles encontrados (17-sep-2026):**
- Medidor multi-circuito "todo en uno" (OWON): 2 pinzas CT de 200A para
  el totalizador + 2 pinzas CT de 50A para 2 circuitos, en un solo
  dispositivo
- Medidores individuales de pinza única (80A) — uno por circuito,
  varios fabricantes
- Totalizador trifásico (si el panel es trifásico): Zemismart SDM01,
  hasta 120A, 3 pinzas CT

**Consideraciones antes de instalar:**
1. Requiere abrir el panel eléctrico e instalar pinzas CT en cada
   circuito — normalmente necesita un electricista (trabajar dentro de
   un panel con corriente viva no es para hacerlo uno mismo).
2. Costo estimado: ~US$20-50 por medidor según el amperaje de la pinza;
   para un apartamento con 6-8 circuitos + totalizador, ~US$200-400 en
   hardware, más instalación.
3. Cambio de software necesario: `logger.py` hoy solo lee un
   dispositivo Tuya. Habría que rediseñarlo para leer una lista de
   dispositivos (cada uno con su circuito/nombre), guardar los datos
   con una columna de "circuito", y agregar una vista de desglose por
   circuito en el panel.

Fuentes: [Medidor multi-circuito (OWON)](https://www.owon-smart.com/tuya-wifi-split-phase-us-multi-circuit-power-meter-2-main-200a-ct-2-sub-50a-ct-product/),
[DIN rail dual CT (OWON PC472)](https://www.owon-smart.com/tuya-wi-fi-single-phase-power-meter-2-clamp-pc-472-product/),
[Medidor trifásico Zemismart](https://www.zemismart.com/products/sdm01-tw0-12-zm).

## Automatización eficiente de aires acondicionados

Objetivo: minimizar el consumo de los AC sin sacrificar confort — no con
magia, con un plan por etapas honesto sobre qué es heurística y qué es
IA real.

**Nota técnica importante**: cortar la corriente del circuito de golpe
(con un medidor+relé) no es ideal para un AC — puede acortar la vida
del compresor o hacer que el equipo "olvide" su configuración. La forma
correcta es enviar el comando real de apagado/temperatura por IR
(como ya permite el dispositivo "AC Companion-WiFi IR Switch" que
tenemos), simulando el control remoto real del fabricante.

**Etapa 1 — Reglas simples, sin hardware nuevo:**
- Usar el companion IR para ajustar la temperatura objetivo (24-25°C
  es mucho más eficiente que 18°C) en vez de cortar la corriente
- Inferir ocupación de forma aproximada a partir del consumo base de
  otros circuitos (luces, enchufes) — si está en su nivel base por
  varias horas, asumir que no hay nadie
- Evitar encendidos/apagados frecuentes (el arranque en frío del
  compresor es lo menos eficiente)
- Implementación: un script que use `cloud.sendcommand()` de tinytuya
  (misma librería que ya usamos para leer) según estas reglas

**Etapa 2 — Sensor de temperatura/humedad real (~US$10-15, sin
instalación eléctrica):** medir confort de verdad en vez de inferirlo,
y afinar mucho mejor las reglas de la Etapa 1.

**Etapa 3 — Optimización real con IA (a futuro):** con suficiente
historia de temperatura + ocupación + consumo, entrenar un modelo que
aprenda el punto óptimo específico del apartamento (cuánto tarda en
enfriar, cuánto se calienta cuando el AC está apagado, etc.) — ahí sí
es aprendizaje real, no reglas fijas.

## Ideas descartadas / pendientes de decisión

- **Notificaciones proactivas** (Telegram/email) de resúmenes o alertas:
  el usuario eligió por ahora que todo se consulte desde el panel, sin
  push. Si esto cambia, requiere secrets nuevos (token de bot o SMTP).
- **Dominio propio**: no es necesario, GitHub Pages ya da hosting y
  subdominio gratis (`github.io`). Solo tendría sentido por estética.
