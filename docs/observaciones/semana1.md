---
fecha: 2026-09-07
contexto: Semana 1 - chain base sin RAG
modelo: gemini-3.6-flash
relacionado: TDD-0001
---

# Observación: Alucinación del LLM sin RAG

## Contexto

Se probó el chain base de la Semana 1 (`src/simple_chain.py`), que responde
únicamente a partir del system prompt, sin acceso a información real del
negocio (todavía sin RAG implementado).

## Prueba realizada

Se enviaron tres mensajes de prueba al chain:

1. "Hola! Que tipos de miel tienen?"
2. "Hacen envios a Cordoba?"
3. "Cual es la capital de Francia?" (control, fuera de dominio)

## Resultado observado

Ante la primera consulta, el sistema respondió mencionando variedades de
miel ("miel multifloral", "miel de eucalipto", "miel de monte", "miel
cremada") que no corresponden a ningún dato real cargado en el sistema —
el modelo las generó por plausibilidad, no por información real del
negocio.

Ante la segunda consulta, generó una respuesta genérica sobre envíos
("correo o transporte según la localidad") también sin base en ninguna
política real de Cabaña Apícola Malka.

La tercera consulta (control) fue respondida correctamente, reconduciendo
la conversación hacia los productos del negocio — lo que muestra que el
system prompt sí logra mantener el dominio de la conversación, aunque no
evita la invención de datos dentro de ese dominio.

## Interpretación

Este comportamiento es un caso de **alucinación**: el modelo rellena
huecos de información con contenido verosímil pero falso, al no tener
ningún mecanismo de verificación contra datos reales (*grounding*).

## Relación con el diseño técnico

Confirma empíricamente el riesgo identificado en `TDD-0001`, sección
"Casos de Borde y Errores" (fila: *"El RAG no encuentra ningún documento
relevante"*), y valida la necesidad del componente RAG definido en la
sección de Diseño Técnico del mismo documento.

## Nota técnica adicional

Durante la prueba se detectó que el modelo `gemini-3.6-flash` no respeta
el parámetro `temperature` (usa muestreo fijo interno — warning propio
del SDK: *"uses fixed sampling defaults"*). Esto invalida parcialmente
el ejercicio comparativo de temperature de la Semana 1. Se documenta
como limitación conocida del modelo, no como error de implementación.

## Próximo paso

La implementación del RAG (Semana 2) debería eliminar este comportamiento
al forzar que las respuestas se basen exclusivamente en documentos reales
indexados del negocio. Se recomienda repetir esta misma prueba después de
completar el RAG, para confirmar la corrección y poder documentar un
"antes/después" en la Sección 7 del informe.