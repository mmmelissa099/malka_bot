---
fecha: 2026-09-15
contexto: Semana 3 - memoria de conversacion (RunnableWithMessageHistory)
modelo: Groq (openai/gpt-oss-120b) + embeddings Google
relacionado: TDD-0001, observaciones/semana2.md
---

# Observaciones: Semana 3 - Memoria de conversación

## Contexto

Se implementó memoria de conversación sobre el RAG de la Semana 2,
usando `RunnableWithMessageHistory` en vez del enfoque clásico
(`ConversationBufferMemory`), que LangChain marca como deprecado en
favor de este patrón, más alineado con LCEL. La memoria se organiza
por `session_id` — en el bot real, el ID de Instagram de cada
cliente — para que la conversación de un cliente nunca se mezcle con
la de otro.

## Decisión de diseño: historial custom en vez del incorporado

LangChain ofrece `InMemoryChatMessageHistory`, una implementación
lista para usar. Se optó, en cambio, por definir una clase propia
(`InMemoryHistory`) heredando de `BaseChatMessageHistory`, siguiendo
un patrón documentado oficialmente por LangChain. Fue una decisión
deliberada: al ser una clase propia, permite en el futuro sobreescribir
`add_messages` y `clear` para persistir la conversación en disco o una
base de datos (necesario para que la memoria sobreviva a un reinicio
del servidor), sin depender de la implementación interna de la
librería.

## Bug encontrado y corregido

Al escribir la clase custom, se usaron `BaseChatMessageHistory` (para
heredar) y `BaseMessage` (para tipar la lista de mensajes) sin
importarlas — el archivo solo importaba `InMemoryChatMessageHistory`,
la clase lista para usar que terminó no utilizándose. Esto generaba
`NameError` al ejecutar el script. Se corrigió agregando:

```python
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage
```

## Prueba realizada

Se probó una conversación de dos turnos en la misma sesión
(`session_id` fijo), donde la segunda pregunta solo tiene sentido si
el sistema recuerda la primera respuesta:

1. *"¿Qué diferencia hay entre una celda real y una reina fecundada?"*
2. *"Y esa opción que dijiste primero, hacen envíos a mi zona?"*

La segunda pregunta no nombra "celda real" explícitamente, depende
enteramente de que el sistema recuerde cuál fue "la opción que se dijo
primero" en el turno anterior.

## Resultado observado

El sistema identificó correctamente que "esa opción que dijiste
primero" se refería a la celda real (mencionada primero en la
respuesta anterior), y respondió con el dato real correspondiente:
que las celdas reales solo se envían dentro de la provincia de Buenos
Aires. La respuesta combinó dos fuentes correctamente en el mismo
turno: el historial de conversación (para resolver la referencia
"esa opción") y el RAG (para la información real de cobertura).

## Interpretación

La combinación de memoria + RAG en un mismo chain funciona sin
conflicto: `RunnableWithMessageHistory` inyecta el historial como
mensajes adicionales en el prompt, mientras que `context` sigue
resolviéndose de forma independiente a partir de la pregunta nueva
(no del historial completo) — evitando que preguntas de turnos
anteriores contaminen la búsqueda en el vector store del turno actual.


## Nota técnica: deprecación de `RunnableWithMessageHistory`

Al ejecutar `skeleton_memory.py` aparece:
`LangChainDeprecationWarning: RunnableWithMessageHistory is deprecated.
Use LangGraph's built-in persistence instead.`

No es un simple cambio de preferencia arquitectónica: la deprecación
está parcialmente vinculada a un aviso de seguridad de LangChain sobre
riesgo de exposición de credenciales en ciertos patrones de uso
avanzado de esta clase (no aplica al uso hecho en este proyecto,
memoria en RAM simple sin objetos serializados de fuentes externas).
El reemplazo oficial es el modelo de *checkpointers* de LangGraph
(`MemorySaver`, `SqliteSaver`, etc.), que implica aprender un paradigma
distinto (`StateGraph`, nodos y edges), no solo cambiar un import.

**Decisión tomada**: no migrar ahora. El código actual funciona sin
errores (solo emite un warning) y la Semana 4 (agente/router) va a
requerir LangGraph de todas formas para los agentes modernos de
LangChain — se pospone la migración de memoria para hacerla en
conjunto con esa migración, en vez de migrar dos veces. Se documenta
como limitación conocida y deuda técnica planificada, no como un
descuido.

## Tool de disponibilidad: implementación y hallazgos

### Contexto

Se implementó el segundo componente de la Semana 3: un tool
(`consultar_disponibilidad`, en `src/skeleton_tools.py`) que compara
la fecha actual contra la disponibilidad vigente de cada producto
(celdas, reinas_nacional, reinas_exportacion). A diferencia de una
FAQ estática, estos valores se actualizan a mano en `stock_data.py` a
medida que se llenan los cupos de cada temporada — no son fechas fijas
de calendario, sino un reflejo de la demanda real de pedidos.

A diferencia del RAG (que siempre se ejecuta ante cualquier pregunta),
un tool es una pieza que el LLM decide si invocar o no. Esta semana se
construyó y probó como pieza aislada, con `.invoke()` directo, sin
conectarla todavía a ningún agente — esa integración es la Semana 4.

### Resultado final

El tool responde correctamente las 4 pruebas: fecha de apertura distinta y correcta para cada categoría, y un rechazo claro ante un producto no reconocido.


## Cierre de la Semana 3

Con memoria de conversación y el tool de disponibilidad funcionando
de forma independiente, la Semana 3 queda completa. La Semana 4 los
integra a ambos (junto con el RAG) en un agente/router que decide
autónomamente qué acción tomar ante cada mensaje.