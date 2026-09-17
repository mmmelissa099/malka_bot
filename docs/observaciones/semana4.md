---
fecha: 2026-09-17
contexto: Semana 4 - agente completo (RAG + memoria + tools con create_agent/LangGraph)
modelo: Groq (openai/gpt-oss-120b) + embeddings Google + LangGraph (InMemorySaver)
relacionado: TDD-0001, observaciones/semana1.md, semana2.md, semana3.md
---

# Observaciones: Semana 4 - El agente completo

## Contexto

Se integraron RAG, memoria y tools (construidos por separado en las
Semanas 2-3) en un agente real con `create_agent` de LangChain
(construido sobre LangGraph). El RAG dejó de ser un paso fijo de la
chain y pasó a ser un tool más (`buscar_en_faqs`), que el LLM decide
si invocar, junto a `consultar_disponibilidad` y un tool nuevo,
`escalar_a_humano`.

Durante la implementación se reorganizó también la estructura del
proyecto: `src/` (código de producción: `agent.py`, `tools.py`,
`rag.py`, `prompts.py`), `experiments/` (prototipos de semanas
anteriores) y `notebook/` (entorno interactivo de pruebas, con
`autoreload` para no reiniciar el kernel en cada cambio).

## Hallazgo 1: conflación de nombres de producto (Caucásicas vs. Caucasit)

Ante una pregunta sobre razas para un clima específico, el agente
mezcló dos productos reales y distintos ("Caucásicas" la raza pura,
"Caucasit" el híbrido propio de Malka) como si fueran lo mismo, e
inventó una pluralización inexistente ("caucasitas"). Se agregó una
regla de fidelidad de nombres al `system_prompt`.

**Causa raíz real (más profunda que el prompt)**: al investigar por
qué el comportamiento era inconsistente entre corridas (a veces decía
que Malka vendía ambos productos, otras veces solo Caucásicas), se
encontró que **las FAQs fuente eran contradictorias entre sí** — no
era el modelo alucinando, era el RAG recuperando datos reales pero
inconsistentes. Se confirmó con la dueña del negocio que Malka vende
únicamente Caucasit (no Caucásicas puras como producto separado), y
se corrigió la FAQ en el origen.

**Lección para el informe**: no todo comportamiento que parece
alucinación lo es — un RAG bien fundamentado puede reproducir
fielmente datos de origen que están mal, y la corrección correcta en
esos casos es arreglar el dato, no ajustar el prompt. Ajustar el
prompt sin corregir el dato hubiera ocultado el síntoma sin resolver
la causa.

## Hallazgo 2: cobertura insuficiente del retriever en preguntas amplias

Ante una pregunta genérica ("¿qué tipo de abejas venden?"), el
retriever (con `k=4` en ese momento) no traía los documentos
específicos de celdas reales, y la respuesta las omitía por completo
o las mencionaba sin ningún detalle. Diagnosticado con evidencia
directa (`retriever.invoke(...)` fuera del agente, mismo método que
en la Semana 2 para el caso de Chile). Resuelto con una combinación
de `k=6` y FAQs adicionales con mayor detalle por producto.

## Hallazgo 3: fidelidad de formato numérico

El agente reformateaba números de la FAQ (`"10.000"`, con punto) usando
caracteres Unicode no estándar (espacio angosto como separador de
miles), en vez de reproducir el formato original. Se agregó una regla
explícita de fidelidad numérica al `system_prompt`, en la misma línea
que la de fidelidad de nombres de producto.

## Hallazgo 4: bug de `escalar_a_humano` (texto de diagnóstico en el `return`)

El mensaje de log pensado para la terminal `print(f"[ESCALADO]
motivo: {motivo}")` terminó escrito dentro del `return` del tool, por
lo que el cliente recibía literalmente el texto de diagnóstico interno
en vez de un mensaje apropiado. Corregido separando el `print` (log
interno) del `return` (mensaje al cliente).

## Hallazgo 5: los LLMs no garantizan seguir instrucciones de "copiar textual"

Aun con una instrucción explícita de relayar el mensaje de
`escalar_a_humano` sin parafrasear, la primera versión del agente lo
resumió igual. Se resolvió reforzando la instrucción con un ejemplo
concreto de "hacé esto, no hagas aquello" en el prompt, en vez de solo
la regla abstracta — técnica que funcionó mejor.

## Trabajo de infraestructura adicional

- **Notebook Jupyter**: entorno interactivo para probar el
  agente sin correr el codigo agent.py por terminal.
- **Reorganización `src/` / `experiments/` / `notebook/`**: separa el
  código de producción de los prototipos de semanas anteriores.

## Cierre de la Semana 4

Con el agente integrando RAG, memoria y los tres tools (búsqueda,
disponibilidad, escalamiento) de forma estable, y con los seis
hallazgos de esta sesión corregidos y documentados, la Semana 4 queda
completa. El hallazgo 2 (causa raíz en los datos, no en el modelo) es
probablemente el más valioso de todo el proyecto para la Sección 7 del
informe: muestra criterio de diagnóstico más allá de "ajustar el
prompt hasta que ande".