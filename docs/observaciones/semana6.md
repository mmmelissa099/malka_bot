# Semana 6 — Integración con Meta: el webhook, el alcance y los límites del modelo

## Objetivo

Conectar el agente completo (RAG + memoria + tools) al canal real de
Instagram, reemplazando el adaptador de terminal (`demo_local.py`) por
un endpoint que reciba los mensajes directos de la cuenta de Malka.

## Qué se implementó

`src/webhook_server.py`, un servidor Flask con dos rutas sobre el mismo
path `/webhook`:

- `GET`: responde el handshake de verificación de Meta. Compara el
  `hub.verify_token` que llega por query param contra la variable
  `WEBHOOK_VERIFY_TOKEN` del `.env` y devuelve el `hub.challenge`.
- `POST`: recibe las notificaciones de mensajes y las deriva al agente.

El `thread_id` del checkpointer de LangGraph se setea con el `sender_id`
de Instagram, de modo que cada cliente mantiene su propio hilo de
conversación sin trabajo adicional. Esto valida la decisión de la
Semana 4 de migrar a `InMemorySaver`: el mismo mecanismo que servía para
separar sesiones en el notebook funciona sin cambios para separar
clientes reales.

Durante el desarrollo se expuso el servidor local con ngrok, ya que Meta
exige HTTPS con certificado válido y no acepta certificados
autofirmados.

## Hallazgo 1: el fallo silencioso del modo desarrollo

El webhook quedó verificado correctamente en el panel de Meta (handshake
`GET` respondido con 200), el campo `messages` suscripto, la cuenta
habilitada vía `POST /me/subscribed_apps` con respuesta `success: true`,
y el servidor corriendo y accesible desde internet.

Aun así, **al enviar un mensaje directo real no llegaba ningún evento**.
Ni al servidor ni al inspector de ngrok: silencio total, sin error, sin
timeout, sin código de estado. Nada que diagnosticar.

La causa estaba en la documentación de Meta: las aplicaciones deben
estar en modo **Live** en el App Dashboard para recibir notificaciones
de webhook. La app estaba en modo Desarrollo.

Lo relevante del caso es la **distancia entre el síntoma y la causa**.
En modo desarrollo todo lo demás funciona con normalidad: el token es
válido, el envío manual de mensajes desde el panel funciona, la
verificación del webhook devuelve 200. El único componente que queda
inhabilitado es la emisión de eventos, y se inhabilita sin emitir
ninguna señal de error. Un fallo que no produce mensaje de error no
deja rastro para buscar, lo que invierte el método de diagnóstico
habitual: en vez de leer un error y rastrear su origen, hubo que
descartar hipótesis una por una contra la documentación oficial.

El orden de descarte fue: tunnel accesible → URL coincidente entre panel
y ngrok → campo `messages` suscripto → suscripción de cuenta activa →
modo de la aplicación.

Al activar el modo Live, los eventos empezaron a llegar de inmediato.
No hubo cola de revisión ni demora de propagación.

## Correcciones aplicadas sobre el esqueleto inicial

El primer borrador del endpoint tenía tres problemas que se detectaron
antes de probarlo contra tráfico real:

**Loop de ecos.** Meta notifica al mismo webhook los mensajes que envía
la propia cuenta, con la propiedad `is_echo` en `true`. Sin filtrarlos,
el bot interpreta su propia respuesta como un mensaje entrante nuevo y
contesta de nuevo, indefinidamente.

**Bloqueo del acknowledgment.** El agente tarda alrededor de 4,75
segundos por consulta con tool (medido en LangSmith). Meta reintenta los
envíos fallidos de forma inmediata y luego con frecuencia decreciente
durante 36 horas, de modo que un `200` lento produce respuestas
duplicadas del lado del cliente. Se separó el acknowledgment del
procesamiento: la ruta devuelve `200` de inmediato y el agente se
ejecuta en un thread aparte.

**Parseo frágil.** La suscripción a webhooks es por aplicación, no por
campo: la app recibe notificaciones de todos los campos suscriptos, no
solo de `messages`. El acceso directo por índice
(`payload["entry"][0]["messaging"][0]`) lanza `KeyError` ante cualquier
evento con otra estructura, y un `KeyError` devuelve `500`, que a su vez
dispara el ciclo de reintentos descrito arriba. Se reescribió el parseo
recorriendo las listas completas con `.get()` en cada nivel.

## Hallazgo 2: el alcance real del bot y el incidente con un cliente

La documentación de Meta indica que con **Standard Access** una
aplicación sólo accede a datos de personas con un rol asignado
(administradores, desarrolladores, testers). De ahí se infirió que, una
vez en modo Live, el bot únicamente recibiría mensajes de las cuentas
agregadas como testers.

**La inferencia era incorrecta.** Con la aplicación en Live y Standard
Access, el webhook recibió mensajes de clientes reales que no tenían
ningún rol en la aplicación.

Esto se descubrió del peor modo posible: el bot intervino en una
conversación que una persona del equipo ya estaba atendiendo. Un cliente
consultó por un envío al exterior; el equipo le respondió desde la app
de Instagram; y a partir del siguiente mensaje el bot empezó a
contestarle en paralelo, pidiendo desambiguaciones y derivando a un
humano que ya estaba presente.

Cada respuesta del agente fue, por separado, correcta: consultó la
disponibilidad cuando correspondía, pidió precisión cuando la pregunta
era ambigua y escaló cuando no tenía información suficiente. **El
sistema falló sin que ningún componente fallara.** El problema no
estuvo en la calidad de las respuestas sino en que nada limitaba a
quién podía responder ni en qué circunstancias.

Dos conclusiones de diseño salieron de esto:

**El control de alcance tiene que ser un límite duro, no un criterio.**
Se implementó una lista blanca (`BOT_ALLOWLIST`): el bot responde
únicamente a los `sender_id` explícitamente autorizados, y si la lista
está vacía no responde a nadie. No es una decisión que el agente evalúe;
es una condición previa a invocarlo. Cuando el costo de un falso
positivo recae sobre un tercero y no sobre quien desarrolla, el
mecanismo correcto es el que no depende de que el sistema razone bien.

**Un canal compartido con personas necesita handover.** Se agregó un
silenciamiento por intervención humana: guardando el `mid` de cada
mensaje enviado por el bot, un eco con un `mid` desconocido indica que
una persona respondió desde la app, y el bot se calla en ese hilo
durante un tiempo configurable. Es una aproximación: el mecanismo
formal es el Handover Protocol de Meta, que requiere Advanced Access.

## Hallazgo 3: el razonamiento del modelo filtrado en la respuesta

Un cliente recibió un mensaje que contenía al modelo corrigiéndose a sí
mismo: una versión truncada de la respuesta, seguida de una crítica en
primera persona sobre no haber reproducido textualmente la salida de
`escalar_a_humano`, seguida de la versión corregida. Todo en el mismo
texto enviado por Instagram.

No era un error del código del webhook ni del agente. Los modelos de
razonamiento de Groq devuelven su cadena de razonamiento junto con la
respuesta final según cómo esté configurado el parámetro
correspondiente, y para los modelos de la familia GPT-OSS ese parámetro
es `include_reasoning`, no `reasoning_format`. Al no estar seteado
explícitamente, el razonamiento llegó al campo `content`.

El hallazgo tiene un segundo alcance: **probablemente explica la
duplicación de respuestas documentada en la Semana 5**. En esa
oportunidad se identificó con LangSmith que la repetición ocurría dentro
de la segunda llamada al modelo y se registró como comportamiento de
generación sin causa determinada. El patrón de este incidente
—respuesta, razonamiento, respuesta otra vez— coincide con lo
observado entonces.

Quedó además una conclusión de diseño: la regla del system prompt que
exige reproducir textualmente la salida de `escalar_a_humano` le pide
fidelidad literal a un componente generativo. El mensaje de derivación
es fijo y no necesita generarse. Lo robusto sería detectar la llamada a
la tool y enviar su texto directamente, sin pasar por la segunda llamada
al modelo. **Las respuestas que deben ser exactas no deberían pasar por
el modelo.**

## Hallazgo 4: inconsistencias en la base de conocimiento

La revisión de `faqs_data.py` a raíz del incidente expuso
contradicciones que el RAG no podía resolver porque estaban en los
datos:

- Un documento afirmaba una relación de precios entre productos que los
  precios cargados no sostenían. La afirmación había quedado de una
  actualización anterior. Se eliminó: una magnitud derivada de otros dos
  valores no debe almacenarse por separado, porque se desactualiza sin
  aviso.
- Los destinos de exportación estaban descritos de forma ambigua ("el
  foco está puesto en..."), lo que combinado con la regla anti-inferencia
  del system prompt llevaba al bot a negar envíos a destinos sobre los
  que el negocio no tenía una posición fija. Se reemplazó por un
  documento que deriva esas consultas a una persona, y se agregó la
  regla correspondiente al prompt.
- Las fechas de disponibilidad de un producto diferían entre
  `faqs_data.py` y `stock_data.py`, de modo que `buscar_en_faqs` y
  `consultar_disponibilidad` respondían distinto a la misma pregunta.

Es la tercera vez en el proyecto que un comportamiento que parecía
atribuible al modelo resultó ser una inconsistencia en los datos de
origen (ver Semana 2). El patrón se repite lo suficiente como para
tratarlo como hipótesis inicial antes que como última opción.

También se detectó que el system prompt describía el alcance de
`consultar_disponibilidad` de forma más laxa que el docstring de la
propia tool, revirtiendo en la práctica la corrección de fronteras de la
Semana 4. Cuando una instrucción se expresa en dos lugares, ambos tienen
que actualizarse juntos.

## Limitaciones conocidas

- **Standard Access.** No limita quién puede escribirle al bot, pero sí
  qué permisos tiene la aplicación. Atender clientes reales de forma
  deliberada requiere Advanced Access y verificación de negocio.
- **Sin handover formal.** El silenciamiento por eco es una
  aproximación con una condición de carrera conocida y estado en
  memoria.
- **Vigencia del token.** El token de Instagram dura 60 días. Sin lógica
  de refresco, la integración deja de funcionar pasado ese plazo.
- **ngrok como transporte.** Sirve para desarrollo y demostración, no
  para operación continua.
- **Estado en memoria.** Tanto el checkpointer como el índice de Chroma
  viven en el proceso. Un reinicio pierde las conversaciones en curso y
  obliga a reconstruir el índice contra la API de embeddings.
- **Mensaje de escalamiento único.** `escalar_a_humano` devuelve el
  mismo texto para todos los motivos, incluso cuando el motivo no es
  falta de información sino que el trámite lo maneja una persona.