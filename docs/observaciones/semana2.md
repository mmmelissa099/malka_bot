---
fecha: 2026-09-15
contexto: Semana 2 - RAG completo, en contraste con la Semana 1
modelo: gemini-3.6-flash + gemini-embedding-001 + Chroma
relacionado: TDD-0001, observaciones/semana1.md
---

# Observación: validación del RAG frente a la alucinación de la Semana 1

## Contexto

Se probó `src/skeleton_rag.py` (chain completo con RAG: retriever +
Chroma + 6 documentos reales del negocio) con las mismas categorías de
pregunta que en la Semana 1, más una pregunta de control diseñada
específicamente para detectar alucinación.

## Resultado observado

Las tres primeras preguntas (diferencia celda real/reina fecundada,
países de envío, precio y mínimo de compra) fueron respondidas con
datos exactos, coincidentes con los documentos indexados — sin
invención de información, a diferencia del comportamiento observado en
`observaciones/semana1.md`.

La pregunta de control, *"¿Hacen envíos a Chile?"* — sin ningún
documento que lo mencione — obtuvo la respuesta más relevante de la
prueba: el sistema no inventó una política de envío, y tampoco se
limitó a decir "no tengo información". En cambio, **razonó a partir
del contexto recuperado** (envíos de celdas limitados a la provincia
de Buenos Aires, envíos de reinas limitados a Argentina) para concluir
correctamente que Chile no está cubierto.

## Interpretación

Esto confirma empíricamente que el mecanismo de *grounding* del RAG
funciona según lo diseñado en TDD-0001: las respuestas quedan atadas a
información real, y el sistema es capaz de inferir límites de
cobertura sin necesidad de que cada caso negativo esté explícitamente
documentado.

## Comparación antes/después (para la Sección 7 del informe)

| | Sin RAG (Semana 1) | Con RAG (Semana 2) |
|---|---|---|
| Pregunta de producto | Inventó variedades de miel inexistentes | Respuesta exacta, basada en documentos reales |
| Pregunta fuera de cobertura | No se probó explícitamente | Razonó correctamente el límite de cobertura, sin inventar |

## Evidencia adicional: preguntas exploratorias no guionadas

Además de las cuatro preguntas originales, se probó el sistema con
preguntas espontáneas (no preparadas de antemano), para observar su
comportamiento ante exploración real de un cliente:

- **"¿Qué día es hoy?"** — rechazo limpio de una consulta totalmente
  fuera de dominio.
- **"¿Qué variedad me conviene?"** — el sistema no se limitó a un
  rechazo genérico: reconoció que no tiene información de
  recomendación, pero igual aportó los datos disponibles (precios de
  cada variedad) como contexto útil, en vez de negarse por completo.
- **"¿Cuál es la diferencia entre una Caucasit y una Buckfast?"**
  (con error de tipeo en "Caucasita", resuelto correctamente por la
  búsqueda semántica de embeddings, no por coincidencia exacta de
  texto) — la respuesta identificó **específicamente qué tipo de
  información falta** ("diferencias biológicas o de comportamiento"),
  en lugar de un rechazo genérico.

**Interpretación**: el grounding del RAG no es binario (sabe / no
sabe todo sobre un tema) — el sistema es capaz de responder
parcialmente con la información real disponible y señalar con
precisión qué parte de la pregunta queda fuera de su conocimiento.
Este comportamiento no fue programado explícitamente; emerge de la
combinación del prompt restrictivo con el contexto recuperado por el
RAG.

## Comparación entre proveedores y efecto de temperature

Al migrar de `gemini-3.6-flash` (Google) a `openai/gpt-oss-120b` (Groq)
por límite de cuota (ver más abajo), se pudo retomar el ejercicio de la
Semana 1 sobre `temperature` que había quedado invalidado — Groq sí
respeta este parámetro. Se probaron las mismas 4 preguntas
exploratorias en tres configuraciones: Gemini (temp 0.2, ignorado),
Groq (temp 0.2) y Groq (temp 0.8), **con el mismo system prompt sin
ajustar todavía** (sin restricción de formato ni de inferencia).

| Aspecto | Gemini (temp 0.2, ignorado) | Groq (temp 0.2) | Groq (temp 0.8) |
|---|---|---|---|
| Longitud de respuesta | Concisa (1-3 oraciones) | Extensa (listas, resúmenes) | Extensa, similar a 0.2 |
| Formato markdown espontáneo | No | Sí (tablas, negrita) | Sí (tablas, negrita) |
| Consistencia de formato entre llamadas similares | N/A | Alta | Menor (una respuesta usó tabla, otra similar no) |
| Rechazo de pregunta fuera de dominio | Correcto | Correcto | Correcto |
| Inferencias mas allá del contexto explícito | No observadas | Sí ("garantizada para eclosionar") | Sí, variante distinta ("no dependés de esas restricciones") |

**Hallazgos clave:**

1. **El uso de markdown no depende de la temperature** — aparece en
   Groq tanto a 0.2 como a 0.8. Es un hábito de formato propio del
   modelo, no un efecto de aleatoriedad. Confirma que la corrección
   correcta es ajustar el system prompt (instrucción explícita de texto
   plano), no la temperature.
2. **La temperature sí afecta la consistencia del formato entre
   llamadas** — a 0.8 se observó variación en si una respuesta usaba
   tabla o no ante preguntas estructuralmente similares; a 0.2 el
   formato fue más uniforme. Este es el efecto de temperature descrito
   en la teoría de la Semana 1, aunque se manifestó en el formato de
   salida más que en el contenido factual.
3. **El problema de sobre-inferencia (detectado antes de ajustar el
   prompt) persiste en ambas temperaturas de Groq**, con una variante
   distinta en cada caso. Esto indica que el origen del problema es el
   prompt (falta de restricción explícita contra inferencias), no la
   temperature — un dato importante para justificar por qué el ajuste
   de prompt, y no un cambio de temperature, es la solución correcta.
4. **Gemini fue más literal y conciso**; Groq es más elocuente pero con
   mayor tendencia a elaborar conclusiones no explícitas en el
   contexto. Es una diferencia de comportamiento real entre modelos
   usando exactamente el mismo RAG — evidencia relevante para la
   Sección 6/7 del informe sobre cómo el modelo subyacente afecta el
   comportamiento del sistema incluso sin cambiar la arquitectura.

Pendiente: repetir esta misma comparación después de actualizar el
system prompt (restricción de formato + anti-inferencia), para
confirmar si ambos problemas (markdown, sobre-inferencia) se corrigen
independientemente de la temperature usada.

## Confirmación: efecto del system prompt corregido

Se repitieron las mismas 4 preguntas exploratorias con Groq (temp 0.2)
y el system prompt corregido (texto plano, anti-inferencia, respuestas
acotadas a 2-4 oraciones). Resultado:

- **Markdown**: eliminado por completo en las 4 respuestas (antes
  aparecía en al menos 2 de 4).
- **Longitud**: las 4 respuestas quedaron en 1-3 oraciones, frente a
  párrafos con listas y resúmenes en la version sin ajustar.
- **Sobre-inferencia**: las dos afirmaciones no respaldadas detectadas
  antes ("garantizada para eclosionar", "reduce el riesgo de
  transporte") no reaparecieron. Persiste una imprecisión menor de
  redacción (aplicar el riesgo de "nacer deformada", propio de la
  celda real, a la reina fecundada por contraste) — no es una
  invención de dato nuevo, es una ambigüedad de fraseo.

**Conclusión para el informe**: el ajuste del system prompt fue
suficiente para corregir tanto el formato como la sobre-inferencia
observada, sin necesidad de cambiar el modelo ni la temperature. Esto
confirma el hallazgo de la sección anterior: el comportamiento
problemático dependía del prompt, no del proveedor ni de la
aleatoriedad del muestreo.

## Regresión detectada: alucinación confiada sobre cobertura de envíos

### Síntoma
Al ampliar las FAQs de 16 a 22 documentos, la pregunta de control
*"¿Hacen envíos a Chile?"* volvió a fallar — el bot respondió
afirmativamente, ofreciendo coordinar el envío con el mínimo de
exportación internacional, pese a que Chile no es un destino cubierto.
A diferencia de las alucinaciones anteriores (más elaboradas pero
tibias), esta fue una **afirmación comercial directa y confiada** —
el tipo de error con mayor costo real si llegara a un cliente.

### Diagnóstico con evidencia
En vez de asumir la causa, se instrumentó el retriever directamente:

```python
docs_recuperados = retriever.invoke("Hacen envios a Chile?")
for d in docs_recuperados:
    print(d.page_content)
```

Con `k=4`, el retriever trajo 4 documentos: envío de celdas (Buenos
Aires), envío de reinas (Argentina), precio de celda, y mínimo de
exportación internacional (100-300 unidades). El documento que declara
explícitamente "exportamos a países de la Unión Europea" **no entró**
entre los 4 recuperados.

### Hipótesis descartada
La hipótesis inicial fue que `k=4` seguía siendo insuficiente frente a
22 documentos totales, y que subir `k` alcanzaría para traer el
documento faltante al contexto.

### Causa real
Se confirmó que `k` ya estaba en 4 tanto en la corrida que fallaba
como en la que se probó después — mismo valor, resultado distinto.
Esto descarta el retrieval insuficiente como causa. El problema real
era que el prompt no tenía una regla explícita para el caso "el
contexto menciona exportación general pero no confirma el destino
puntual": ante esa ambigüedad, el modelo asumía cobertura en vez de
negarla.

### Fix confirmado
Se agregó al system prompt una regla explícita: ante preguntas sobre
cobertura geográfica, si el destino consultado no aparece mencionado
como cubierto en el contexto, la respuesta debe ser que no se hacen
envíos ahí — sin inferir cobertura a partir de menciones generales
como "exportación internacional". Tras el cambio, la respuesta pasó a
ser correcta y concisa: *"No, no hacemos envíos a Chile."*

### Conclusión para el informe
Para errores de tipo "afirmación comercial riesgosa", una regla de
comportamiento explícita en el prompt resultó más confiable que
ajustar `k`: el documento correcto puede no estar en el contexto
recuperado (como en este caso) o el modelo puede fallar en usarlo bien
aunque esté presente — una regla que fija el default seguro ("si no
está explícito, la respuesta es no") protege en ambos escenarios.

## Próximo paso

Con el RAG validado, el siguiente componente a construir es la memoria
de conversación y el tool de catálogo/stock (Semana 3).