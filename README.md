# Bot de Instagram — Cabaña Apícola Malka

Agente conversacional que atiende los mensajes directos de
[@reinas.malka](https://www.instagram.com/reinas.malka/), un criadero
familiar de reinas y celdas reales. Responde con información real del
negocio (RAG), consulta disponibilidad, mantiene contexto por cliente y
deriva al equipo cuando corresponde.

Trabajo Práctico Integrador — Administración de Sistemas de Información,
UTN FRLP 2026.

## Arquitectura

El núcleo (`src/`) es independiente del canal. Dos adaptadores de entrada lo
consumen: `demo_local.py` por terminal y `webhook_server.py` contra la API
de Instagram. Esa separación permitió desarrollar el agente sin depender de
Meta y conservar una demo funcional cuando la integración no está levantada.

| | |
|---|---|
| Orquestación | LangChain + LangGraph (`create_agent`) |
| Chat | Groq — `openai/gpt-oss-120b` |
| Embeddings | Google — `gemini-embedding-001` |
| Vector store | Chroma (en memoria) |
| Memoria | `InMemorySaver`, `thread_id` = ID de Instagram del cliente |
| Observabilidad | LangSmith |
| Canal | Flask + Instagram API with Instagram Login |

Tres tools: `buscar_en_faqs` (RAG sobre la base del negocio),
`consultar_disponibilidad` (fechas de temporada, y solo eso) y
`escalar_a_humano`.

### Decisiones que conviene conocer

**Dos proveedores.** Los embeddings quedaron en Google; el chat migró a Groq
por los límites del nivel gratuito de Gemini.

**Fronteras explícitas entre tools.** `consultar_disponibilidad` acaparaba
consultas de mínimos y condiciones de compra. Se resolvió declarando el
ámbito exclusivo de cada tool en sus docstrings y en el system prompt — no
agregando reglas de comportamiento.

**Control de alcance en el canal, no en el agente.** El webhook recibe
mensajes de cualquier persona, no solo de los testers. El bot responde
únicamente a los IDs de `BOT_ALLOWLIST`, se retira del hilo cuando deriva a
una persona, y se silencia si alguien del equipo responde desde la app.
Los tres son condiciones previas a invocar al agente, no criterios que el
agente evalúe.

**Datos fuera del repositorio.** Precios, disponibilidad y condiciones de
venta no están versionados. Hay plantillas con la misma estructura y valores
ficticios.

El razonamiento detrás de cada una, con los errores que las motivaron, está
en [`docs/observaciones`](docs/observaciones). El diseño técnico, en
[`docs/TDDs`](docs/TDDs).

## Puesta en marcha

Requiere Python 3.12 o superior.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                              # completar las API keys
cp src/faqs_data_example.py src/faqs_data.py
cp src/stock_data_example.py src/stock_data.py
python src/demo_local.py
```

Los dos `cp` de datos son obligatorios: sin esos archivos, todo lo que
importe `rag.py` o `tools.py` falla al arrancar. Las variables disponibles
están documentadas en [`.env.example`](.env.example); solo `GOOGLE_API_KEY`
y `GROQ_API_KEY` son necesarias para la demo.

### Canal de Instagram

```bash
ngrok http 5000
python src/webhook_server.py
```

Callback URL en el panel de Meta: la URL de ngrok con sufijo `/webhook`.
Después, suscribir el campo `messages` y habilitar la cuenta vía
[`/me/subscribed_apps`](https://developers.facebook.com/docs/instagram-platform/webhooks).

La aplicación debe estar en modo **Live**: en modo desarrollo los webhooks
no emiten ningún evento y no devuelven error alguno. El diagnóstico de ese
caso está en
[`semana6-integracion-meta.md`](docs/observaciones/semana6-integracion-meta.md).

## Limitaciones conocidas

- **Estado en memoria.** Memoria de conversación, índice vectorial y
  controles de alcance se pierden al reiniciar el proceso.
- **Standard Access.** Sin Advanced Access no hay Handover Protocol; el
  silencio por intervención humana es una aproximación con estado local.
- **Token de 60 días.** Sin lógica de refresco.
- **ngrok como transporte.** Desarrollo, no operación.

Cada una, con su origen, en [`docs/observaciones`](docs/observaciones).