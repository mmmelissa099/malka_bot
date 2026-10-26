"""
Semana 6 - Webhook para Instagram, conectado al agente real
================================================================

Recibe los mensajes directos que llegan a la cuenta de Malka y los
responde con el agente completo de src/agent.py (RAG + memoria + tools).

CONTROL DE ALCANCE
------------------
Tres mecanismos independientes evitan que el bot intervenga donde no
debe:

1. Lista blanca (BOT_ALLOWLIST): el bot responde UNICAMENTE a los
   sender_id que figuren en esa variable. Si esta vacia, no responde a
   nadie. Es un limite duro: no depende de que el bot "decida bien".

2. Silenciamiento por escalamiento: si el agente llama a
   escalar_a_humano, el bot envia el mensaje de derivacion y despues
   deja de responder en ese hilo. La conversacion queda en manos del
   equipo.

3. Silenciamiento por intervencion humana: si una persona del equipo
   responde el hilo desde la app de Instagram, el bot se calla en esa
   conversacion durante PAUSA_MINUTOS.

Los tres estados viven en memoria: reiniciar el servidor los borra.

Variables necesarias en .env:
- WEBHOOK_VERIFY_TOKEN     inventado por vos, el mismo que cargues en el
                           panel de Meta al configurar la URL del webhook
- INSTAGRAM_ACCESS_TOKEN   el que ya generaste y probaste
- BOT_ALLOWLIST            sender_id autorizados, separados por coma
- INSTAGRAM_API_VERSION    opcional, por defecto v25.0
- PAUSA_MINUTOS            opcional, por defecto 60

Antes de correr esto necesitas ngrok corriendo en paralelo:
  ngrok http 5000
"""

import os
import threading
import time

import requests
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()

from agent import agent  # noqa: E402  (despues de load_dotenv)

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
API_VERSION = os.getenv("INSTAGRAM_API_VERSION", "v25.0")
PAUSA_MINUTOS = int(os.getenv("PAUSA_MINUTOS", "60"))

ALLOWLIST = {
    x.strip() for x in os.getenv("BOT_ALLOWLIST", "").split(",") if x.strip()
}

GRAPH_URL = f"https://graph.instagram.com/{API_VERSION}/me/messages"

# mid de cada mensaje que envio el bot. Sirve para distinguir el eco de
# nuestras propias respuestas del eco de una respuesta humana.
_mids_propios = set()

# sender_id -> timestamp de la ultima intervencion humana en ese hilo.
_pausados = {}

# sender_id de los hilos que ya fueron derivados a una persona. A
# diferencia de _pausados, no vence: el bot no vuelve a hablar ahi.
_escalados = set()

_lock = threading.Lock()


@app.route("/webhook", methods=["GET"])
def verify():
    """
    Meta llama a esto UNA VEZ, cuando configures la URL en el panel
    (boton "Verificar y guardar"). Llega con tres query params:
    hub.mode, hub.verify_token, hub.challenge.
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403


def hubo_escalamiento(mensajes):
    """
    Revisa si el agente llamo a escalar_a_humano en ESTE turno.

    Recorre los mensajes de atras hacia adelante y corta en el mensaje
    del cliente, porque resultado["messages"] trae todo el historial
    del thread y un escalamiento viejo no deberia contar como nuevo.
    """
    for m in reversed(mensajes):
        if getattr(m, "type", None) == "human":
            return False
        if getattr(m, "name", None) == "escalar_a_humano":
            return True
    return False


def registrar_intervencion_humana(evento):
    """
    Un eco cuyo mid no generamos nosotras significa que una persona del
    equipo respondio desde la app de Instagram. Anotamos el hilo para
    que el bot no se meta encima.

    En un eco, recipient.id es el cliente (nosotras somos el sender).
    """
    mid = evento.get("message", {}).get("mid")
    cliente_id = evento.get("recipient", {}).get("id")

    if not cliente_id:
        return

    with _lock:
        es_nuestro = mid in _mids_propios

    if not es_nuestro:
        with _lock:
            _pausados[cliente_id] = time.time()
        print(f"[HUMANO] respondio en el hilo {cliente_id} - bot en pausa")


def debe_callarse(sender_id):
    """Devuelve el motivo por el que el bot no debe responder, o None."""
    with _lock:
        if sender_id in _escalados:
            return "el hilo ya fue derivado a una persona"
        desde = _pausados.get(sender_id)

    if desde is not None and (time.time() - desde) < PAUSA_MINUTOS * 60:
        return "lo esta atendiendo una persona"

    return None


def extraer_mensajes(payload):
    """
    Saca (sender_id, texto) de cada mensaje de texto entrante.

    Mete todo adentro de .get() porque Meta manda al mismo endpoint
    varios tipos de evento (comentarios, reacciones, confirmaciones de
    lectura) que NO tienen la estructura de un mensaje. Un KeyError aca
    devolveria 500 y Meta reintentaria el mismo evento varias veces.
    """
    for entry in payload.get("entry", []):
        for evento in entry.get("messaging", []):
            mensaje = evento.get("message", {})

            # Eco: o es nuestra propia respuesta, o es una persona del
            # equipo respondiendo. En ninguno de los dos casos hay que
            # contestarlo, pero el segundo caso hay que registrarlo.
            if mensaje.get("is_echo"):
                registrar_intervencion_humana(evento)
                continue

            texto = mensaje.get("text")
            sender_id = evento.get("sender", {}).get("id")

            if sender_id and texto:
                yield sender_id, texto


def responder(sender_id, texto_mensaje):
    """
    Invoca al agente y manda la respuesta por la API de Meta.
    Corre en un thread aparte para no demorar el 200 que espera Meta.
    """
    try:
        resultado = agent.invoke(
            {"messages": [{"role": "user", "content": texto_mensaje}]},
            config={"configurable": {"thread_id": sender_id}},
        )
        mensajes = resultado["messages"]
        respuesta = mensajes[-1].content

        r = requests.post(
            GRAPH_URL,
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            json={"recipient": {"id": sender_id}, "message": {"text": respuesta}},
            timeout=15,
        )

        if r.status_code != 200:
            print(f"[ERROR ENVIO] {r.status_code}: {r.text}")
            return

        mid = r.json().get("message_id")
        if mid:
            with _lock:
                _mids_propios.add(mid)

        print(f"[OK] -> {sender_id}: {respuesta}")

        if hubo_escalamiento(mensajes):
            with _lock:
                _escalados.add(sender_id)
            print(f"[DERIVADO] {sender_id} - el bot no responde mas en este hilo")

    except Exception as e:
        print(f"[ERROR AGENTE] {type(e).__name__}: {e}")


@app.route("/webhook", methods=["POST"])
def receive_message():
    """
    Meta llama a esto cada vez que llega un mensaje real a la cuenta
    de Malka. Devolvemos 200 enseguida y procesamos en segundo plano:
    si tardamos demasiado, Meta da el envio por fallido y reintenta,
    y el usuario recibe la misma respuesta repetida.
    """
    payload = request.get_json(silent=True) or {}

    for sender_id, texto in extraer_mensajes(payload):
        if sender_id not in ALLOWLIST:
            print(f"[IGNORADO] {sender_id} no esta en la lista blanca")
            continue

        motivo = debe_callarse(sender_id)
        if motivo:
            print(f"[EN SILENCIO] {sender_id} - {motivo}")
            continue

        print(f"[MENSAJE] {sender_id}: {texto}")
        threading.Thread(
            target=responder, args=(sender_id, texto), daemon=True
        ).start()

    return "OK", 200


if __name__ == "__main__":
    if not VERIFY_TOKEN or not ACCESS_TOKEN:
        raise RuntimeError(
            "Falta WEBHOOK_VERIFY_TOKEN o INSTAGRAM_ACCESS_TOKEN en tu .env"
        )

    if not ALLOWLIST:
        print(
            "AVISO: BOT_ALLOWLIST esta vacia. El bot NO va a responder a "
            "nadie. Agrega los sender_id autorizados en tu .env."
        )
    else:
        print(f"Lista blanca activa: {len(ALLOWLIST)} cuenta(s) autorizada(s)")

    app.run(port=5000)