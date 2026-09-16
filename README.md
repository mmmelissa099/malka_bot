# Bot de Instagram — Cabaña Apícola Malka

Caso práctico de LangChain para el Trabajo Práctico Integrador de
Administración de Sistemas de Información (UTN FRLP, 2026).

Automatiza la atención de mensajes directos de Instagram para Cabaña
Apícola Malka, un negocio familiar de cría de reinas y celdas reales:
responde consultas con información real del negocio (RAG), consulta
catálogo/stock (tool), recuerda el contexto de la charla (memoria), y
deriva a una persona cuando no puede resolver algo (escalamiento).

Diseño técnico completo en [`docs/TDDs`](docs/TDDs).

## Instalación

```bash
python -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # y pegá tu API key adentro
```

Conseguí la API key gratis (sin tarjeta) en:
https://aistudio.google.com/apikey

## Cómo correr cada semana

| Semana | Script | Qué demuestra | Estado |
|---|---|---|---|
| 1 | `src/simple_chain.py` | Prompt + modelo + output parser (LCEL) | ✅ hecho |
| 2 | `src/skeleton_rag.py` | RAG sobre FAQs del negocio | ✅ hecho |
| 3 | *(próximo)* | Memoria de conversación + tool de catálogo | ⏳ pendiente |
| 4 | *(próximo)* | Agente completo (router) | ⏳ pendiente |
| 5 | `src/demo_local.py` (plan B) + integración real | Demo local + canal de Instagram (Meta) | ⏳ pendiente |

```bash
python src/simple_chain.py
```
```bash
python src/skeleton_rag.py
```

## Arquitectura: dos formas de hablarle al mismo bot

El "cerebro" del bot (RAG + memoria + agente) es independiente del canal
por el que llega el mensaje. Esto permite tener un adaptador de entrada
real por Instagram (vía la API de Meta) y otro por terminal
(`src/demo_local.py`, Semana 5) sin duplicar lógica — sirve como plan B
si la integración de Meta falla justo el día de la exposición.

## Estructura

```
malka_bot/
├── .gitignore
├── requirements.txt
├── .env.example        # copiar a .env con tu key real (no subir a git)
├── README.md
├── docs/
│   └── TDDs/
│        └── TDD-0001.md
|         └── TDD-0001.md
│   └── observaciones/
│        └── semana2.md
|
│
└── src/
    ├── simple_chain.py
    └── skeleton_rag.py
```

