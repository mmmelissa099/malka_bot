---
fecha: 2026-09-17
contexto: Semana 5 - demo local interactiva (demo_local.py)
modelo: Groq (openai/gpt-oss-120b) + embeddings Google + LangGraph
relacionado: TDD-0001, observaciones/semana4.md
---

# Observaciones: Semana 5 - Demo local interactiva

## Contexto

Se construyó `src/demo_local.py`, un loop de terminal con conversación
real de ida y vuelta (a diferencia de las pruebas anteriores, que
usaban listas de preguntas prearmadas). Esta es la primera vez que se
prueba el agente con input genuinamente en vivo, y salieron a la luz
hallazgos que no habían aparecido en ninguna prueba prearmada.

## Hallazgo 1: regresión de "conocimiento general" no cubierta por reglas específicas

Al preguntar "¿qué día es hoy?" (la misma pregunta de control usada
desde la Semana 1), el agente respondió con la fecha real en vez de
rechazar la pregunta — una regresión respecto al comportamiento base.

**Causa**: el `system_prompt` actual tiene una regla específica ("no
uses tu conocimiento general **para recomendar razas**"), pero no una
regla general que cubra cualquier otro uso de conocimiento externo. Al
volverse más específico el prompt, el modelo interpretó que fuera de
ese caso puntual, usar conocimiento general estaba permitido.

**Corrección**: se agregó una regla general y explícita ("solo
respondé con información de los tools disponibles; si preguntan algo
sin relación al negocio o que ningún tool responde, decí que no podés
ayudar con eso"), en vez de sumar otra excepción puntual.

**Lección**: una regla muy específica puede reducir, sin intención, el
alcance de una protección más general que ya existía — vale la pena
revisar el conjunto completo de reglas cada vez que se agrega una
nueva, no solo agregarla y probar el caso puntual que la motivó.

## Hallazgo 2: ambigüedad de lectura en un dato correcto (no contradicción de datos)

Con las FAQs ya corregidas (sin contradicción real entre "Caucásicas"
y "Caucasit"), el agente igual respondió con incoherencia interna
("también disponemos de reinas Caucásicas... las reinas Caucásicas
puras no están disponibles", en el mismo mensaje).

**Causa real**: el documento sobre Caucasit menciona su origen
genético ("cruzamiento de Caucásicas puras con zánganos Italianos"),
y el modelo interpretó esa mención de "Caucásicas" como una oferta de
producto, no como información de linaje genético — un dato
correctamente escrito, pero ambiguo de interpretar.

**Corrección**: se reescribió el documento agregando una aclaración
explícita ("Malka NO vende reinas Caucásicas puras como producto -
únicamente se ofrece el híbrido Caucasit"), eliminando la ambigüedad
en el dato en vez de depender de que el modelo infiera correctamente
la distinción entre "origen genético" y "producto ofrecido".

**Lección**: no toda inconsistencia del agente viene de datos
contradictorios (ver Semana 4) — a veces el dato es correcto pero
ambiguo de leer, y la corrección más robusta sigue siendo a nivel de
dato, no de prompt.

## Hallazgo 3 (limitación conocida, no resuelta): ruteo de respuestas cortas y ambiguas

En una conversación real, ante la respuesta corta "Dale" (aceptando
una oferta del bot de ampliar información sobre Caucasit), el agente
llamó a `consultar_disponibilidad` con un producto ("reinas_nacional")
que no había sido mencionado en ningún momento de la conversación —
un enrutamiento incorrecto completo, no una mezcla de datos.

**Decisión**: se documenta como limitación conocida del enfoque de
tool-calling, en vez de intentar cerrarla con más reglas de prompt.
Respuestas cortas y ambiguas ("Dale", "Sí", "Ok") son un problema
abierto real en agentes conversacionales — no hay garantía de que una
regla adicional cubra todos los casos, y el tiempo restante del
proyecto se prioriza en otros frentes.

**Para el informe**: este hallazgo solo pudo detectarse con una
conversación genuinamente interactiva — ninguna de las pruebas
prearmadas de semanas anteriores lo hubiera revelado, porque todas
usaban preguntas completas y no ambiguas. Refuerza el valor de probar
con input real antes de dar un sistema por cerrado.

## Hallazgo 4: falla mecánica de tool-calling (nombre de parámetro)

Ante una pregunta que requería reformular una referencia ambigua
("cuál es la diferencia" → "diferencia entre Italiana, Buckfast y
Caucasit"), el modelo resolvió el contenido correctamente, pero armó
el JSON de la llamada al tool con la clave `question` en vez de
`pregunta` (el nombre real del parámetro). Groq valida los argumentos
contra el schema antes de ejecutar la función, y rechazó la llamada
con un error 400 antes de que el código Python llegara a correr.

**Distinción importante**: a diferencia del Hallazgo 3 ("Dale"), que
es una falla de *razonamiento* (decidir mal qué tool usar), este es
una falla *mecánica* de formato (decidir bien, pero escribir mal el
JSON de la llamada) — capas distintas del mismo proceso.

**Mitigación aplicada**: se envolvió `agent.invoke()` en `demo_local.py`
con `try/except`, para que este tipo de error no interrumpa toda la
demo — no corrige la causa (no determinística), pero evita que una
sola falla tumbe la sesión completa.

## Hallazgo 5: duplicación de respuesta (no determinístico, sin diagnosticar del todo)

En una prueba posterior, una respuesta sobre diferencias de razas
salió repetida dos veces seguidas, pegada sin separación. No se
reprodujo en una pregunta casi idéntica en el mismo tipo de
conversación. Queda como hallazgo abierto, sin causa confirmada.

## Decisión de cierre: deuda técnica aceptada, no bugs pendientes

Con el proyecto orientado a una demo académica (no a un producto en
producción), se decidió **dejar de perseguir cada comportamiento no
determinístico** encontrado en esta sesión de pruebas interactivas, y
documentarlos como deuda técnica conocida en lugar de bugs abiertos.
Quedan sin resolver, de forma deliberada:

- **Ruteo inconsistente ante respuestas ambiguas** (Hallazgo 3, "Dale").
- **Nombre de parámetro incorrecto en la llamada al tool** (Hallazgo 4,
  `question` vs `pregunta`) — mitigado con manejo de errores, no
  corregido en la causa.
- **Duplicación ocasional de respuesta** (Hallazgo 5) — sin diagnóstico
  confirmado.
- **Inferencia geográfica de cobertura** (ej: "¿envían a Saladillo?"
  resuelto correctamente por conocimiento general de que es una
  localidad de Buenos Aires) — aceptado como comportamiento válido,
  distinto de una recomendación de opinión (como el caso de Cafayate),
  por tratarse de un hecho verificable de alta confiabilidad.

**Justificación para el informe**: un agente construido sobre un LLM
de inferencia rápida (no el modelo más grande disponible) tiene
comportamiento no determinístico real, documentado con evidencia a lo
largo de las cinco semanas. La decisión de priorizar cobertura y
tiempo de entrega por sobre perseguir el 100% de determinismo es una
decisión de gestión de proyecto válida y consciente, no una limitación
oculta.

## Próximo paso

`demo_local.py` queda funcional para la demo: conversación de ida y
vuelta con memoria real, manejo de Ctrl+C/EOF, thread_id nuevo por
sesión, y manejo de errores (`try/except`) para que una falla puntual
no corte toda la sesión en vivo. Con la deuda técnica documentada y
aceptada, el trabajo de desarrollo de la Semana 5 queda cerrado.