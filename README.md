# Bot de Instagram — Cabaña Apícola Malka

Caso práctico de LangChain y LangGraph para el Trabajo Práctico Integrador de
Administración de Sistemas de Información (UTN FRLP, 2026).

Automatiza la atención de mensajes directos de Instagram para Cabaña
Apícola Malka, un negocio familiar de cría de reinas y celdas reales:
responde consultas con información real del negocio (RAG), consulta
disponibilidad (tool), recuerda el contexto de la charla (memoria), y
deriva a una persona cuando no puede resolver algo (escalamiento) — todo
orquestado por un agente construido con LangChain y LangGraph.

Diseño técnico completo en [`docs/TDDs`](docs/TDDs).
Hallazgos y decisiones de cada semana en [`docs/observaciones`](docs/observaciones).

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # y completá las dos API keys (ver abajo)
```

Necesitás **dos** API keys en tu `.env`:
- `GOOGLE_API_KEY` — para los embeddings del RAG. Gratis, sin tarjeta, en
  [aistudio.google.com](https://aistudio.google.com/apikey).
- `GROQ_API_KEY` — para el modelo de chat del agente. Gratis, sin tarjeta,
  en [console.groq.com](https://console.groq.com).

### Datos del negocio (paso obligatorio, sin esto el código tira error)

Los datos reales de Malka (precios, disponibilidad, contacto) **no están
en este repositorio** por privacidad del negocio. Lo que sí está versionado son plantillas con datos ficticios, con la misma estructura:

```bash
cp src/faqs_data.example.py src/faqs_data.py
cp src/stock_data.example.py src/stock_data.py
```

Sin este paso, `src/agent.py` (y cualquier script que importe `rag.py` o
`tools.py`) va a fallar al arrancar, porque esos dos archivos no existen
hasta que los copîs. Con los datos de ejemplo el bot corre igual, solo
que responde con información inventada en vez de la real de Malka.

## Cómo correr cada semana

| Semana | Script | Qué demuestra | Estado |
|---|---|---|---|
| 1 | `experiments/simple_chain.py` | Prompt + modelo + output parser (LCEL) | ✅ hecho |
| 2 | `experiments/skeleton_rag.py` | RAG sobre FAQs del negocio | ✅ hecho |
| 3 | `experiments/skeleton_memory.py` y `src/tools.py` | Memoria de conversación + tool de disponibilidad | ✅ hecho |
| 4 | `src/agent.py` | Agente completo (RAG + memoria + tools, LangGraph) | ✅ hecho |
| 5 | `src/demo_local.py` | Demo interactiva de ida y vuelta, por terminal | ✅ hecho |

Para correr la demo completa:
```bash
python src/demo_local.py
```

## Arquitectura

El "cerebro" del bot (RAG + memoria + agente, en `src/`) es independiente
del canal por el que llega el mensaje. La demo del TPI usa un canal de
terminal (`src/demo_local.py`) con conversación real de ida y vuelta.

La integración con la API real de Instagram (Meta) quedó fuera del
alcance obligatorio del trabajo y se deja como extensión opcional a
futuro, no como una entrega pendiente.

### Notebook interactivo (opcional, para desarrollo)

`notebook/probar_agente.ipynb` permite iterar sobre el agente sin
reiniciar el proceso en cada prueba. Requiere el mismo `.venv` como
kernel. Antes de tu primer commit de cualquier notebook, corré:
```bash
nbstripout --install
```
Así las salidas de las celdas (que pueden mostrar datos del negocio) se
limpian automáticamente antes de cada commit, sin que dependa de que te
acuerdes de hacerlo a mano.

## Estructura

```
malka_bot/
├── .gitignore
├── requirements.txt
├── .env.example                # plantilla de variables de entorno
├── README.md
│
├── docs/                       # Documentación y seguimiento del TPI
│   ├── TDDs/
│   │   └── TDD-0001.md
│   └── observaciones/
│       ├── semana1.md
│       ├── semana2.md
│       ├── semana3.md
│       ├── semana4.md
│       └── semana5.md
│
├── experiments/                # Prototipos evolutivos (Semanas 1 a 3)
│   ├── simple_chain.py
│   ├── skeleton_rag.py
│   └── skeleton_memory.py
│
├── notebook/                   # Entorno interactivo de pruebas (opcional)
│   └── probar_agente.ipynb
│
└── src/                        # Código de producción (Semana 4+)
    ├── agent.py                # Agente ReAct principal (LangGraph)
    ├── tools.py                # Herramientas del agente (disponibilidad, FAQs, escalado)
    ├── rag.py                  # Configuración de Chroma y embeddings
    ├── prompts.py              # System prompt centralizado
    ├── demo_local.py           # Demo interactiva de terminal
    ├── faqs_data.example.py    # Plantilla de FAQs (ficticia, versionada)
    ├── stock_data.example.py   # Plantilla de disponibilidad (ficticia, versionada)
    ├── faqs_data.py            # Datos reales (NO versionado, ver .gitignore)
    └── stock_data.py           # Datos reales (NO versionado, ver .gitignore)
```