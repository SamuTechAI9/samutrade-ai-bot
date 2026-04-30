from flask import Flask, request, jsonify
import os
import json
import logging
import requests
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview",
)

SYSTEM_PROMPT = """
Eres el asistente comercial de Samuel Torres, un intermediario internacional de import-export que conecta compradores y vendedores de cualquier producto en grandes volúmenes (vehículos, maquinaria, alimentos, ropa, materias primas, coches de segunda mano EU, etc.) entre Europa, África, Asia y Latinoamérica en cualquier dirección.

Tu rol NO es cerrar ventas ni dar precios. Tu rol es cualificar al contacto, recoger información y prepararle el caso a Samuel para que él tome el relevo personalmente.

REGLAS DE CONDUCTA:
- Detecta el idioma del cliente en su primer mensaje y responde SIEMPRE en ese idioma (español, francés, inglés, portugués, árabe, etc.).
- Tono profesional pero humano y cercano. Mensajes cortos, estilo WhatsApp.
- Una sola pregunta por mensaje. Nunca listas largas.
- Nunca inventes precios, plazos, modelos, disponibilidad ni características técnicas.
- Nunca prometas nada en nombre de Samuel: ni descuentos, ni stock, ni fechas de entrega.
- Si el cliente insiste en precios, responde: "Samuel le prepara una cotización personalizada según volumen, origen y destino. Necesito unos datos antes para que pueda darle algo serio."
- No saludes con un nombre que el cliente no haya dicho explícitamente en ESTA conversación.
- Si detectas que el cliente no es serio (mensajes ofensivos, broma, sin intención real), redirige con educación una vez; si insiste, despídete cortésmente.

DATOS QUE DEBES OBTENER ANTES DE CERRAR EL LEAD:
1. Nombre y empresa (si aplica)
2. País desde donde escribe
3. ¿Quiere comprar o vender?
4. Producto concreto y especificaciones
5. Cantidad o volumen aproximado
6. País de destino del envío
7. Presupuesto orientativo o margen para negociar
8. Urgencia o plazo deseado
9. Email o número alternativo de contacto

Pídelos uno a uno, en orden natural según fluya la conversación. No los recites como formulario.

CIERRE DEL LEAD:
Cuando tengas al menos los puntos 1, 3, 4, 5, 6 y 8, cierra así:
"Perfecto [nombre], tengo lo que Samuel necesita para estudiar tu caso. Le paso ahora mismo tu consulta y se pondrá en contacto contigo personalmente. ¿Tienes alguna preferencia de horario para hablar con él?"

Después del cierre, no inventes seguimiento. Solo responde si el cliente añade más información, y agradécela.
"""

EXTRACTION_PROMPT = """
Extrae la información del lead en JSON válido.
Devuelve SOLO JSON, sin texto adicional.

Usa esta estructura exacta:
{
  "nombre": "",
  "tipo_cliente": "",
  "producto": "",
  "cantidad": "",
  "origen": "",
  "destino": "",
  "presupuesto": "",
  "urgencia": "",
  "problemas": "",
  "interes": ""
}

Si un dato no aparece, deja cadena vacía.
"""

# In-memory store: { chat_id: { lead_data: {}, history: [] } }
sessions = {}

EMPTY_LEAD = {
    "nombre": "",
    "tipo_cliente": "",
    "producto": "",
    "cantidad": "",
    "origen": "",
    "destino": "",
    "presupuesto": "",
    "urgencia": "",
    "problemas": "",
    "interes": "",
}


def get_session(chat_id):
    if chat_id not in sessions:
        sessions[chat_id] = {"lead_data": EMPTY_LEAD.copy(), "history": []}
    return sessions[chat_id]


def merge_lead_data(old, new):
    merged = old.copy()
    for key, value in new.items():
        if value and str(value).strip():
            merged[key] = value.strip()
    return merged


def extract_lead_data(user_message):
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_completion_tokens=250,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content.strip()
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return {"nombre": None, "pais": None, "cantidad": None, "presupuesto": None, "interes": "desconocido"}


def get_chat_reply(history, lead_data):
    context = f"""
Datos actuales del lead:
{json.dumps(lead_data, ensure_ascii=False)}
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": context},
        *history,
    ]

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=messages,
        max_completion_tokens=180,
    )

    logger.info("Response content: %s", response.choices[0].message.content)
    logger.info("Response finish_reason: %s", response.choices[0].finish_reason)

    content = response.choices[0].message.content
    if not content:
        content = getattr(response.choices[0].message, "reasoning_content", "") or ""
    return content.strip()


def is_lead_complete(lead_data):
    required_fields = ["tipo_cliente", "producto", "cantidad"]
    filled = sum(1 for field in required_fields if lead_data.get(field))
    return filled >= 3


def build_summary(chat_id, lead_data):
    return f"""
NUEVO CLIENTE DETECTADO (Telegram)

Chat ID: {chat_id}
Nombre: {lead_data.get("nombre", "")}
Tipo: {lead_data.get("tipo_cliente", "")}
Producto: {lead_data.get("producto", "")}
Cantidad: {lead_data.get("cantidad", "")}
Origen: {lead_data.get("origen", "")}
Destino: {lead_data.get("destino", "")}
Presupuesto: {lead_data.get("presupuesto", "")}
Urgencia: {lead_data.get("urgencia", "")}
Problemas: {lead_data.get("problemas", "")}
Interés: {lead_data.get("interes", "")}
""".strip()


def send_telegram_message(chat_id, text):
    payload = {"chat_id": chat_id, "text": text}
    try:
        resp = requests.post(TELEGRAM_API_URL, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception:
        logger.exception("Failed to send Telegram message to chat_id=%s", chat_id)


@app.route("/")
def home():
    return "OK FUNCIONANDO", 200


@app.route("/telegram-webhook", methods=["POST"])
def telegram_webhook():
    update = request.get_json(silent=True)
    if not update:
        return jsonify({"ok": True})

    message = update.get("message") or update.get("edited_message")
    if not message:
        return jsonify({"ok": True})

    chat_id = str(message.get("chat", {}).get("id", ""))
    incoming_msg = (message.get("text") or "").strip()

    if not chat_id:
        return jsonify({"ok": True})

    if not incoming_msg:
        logger.warning("Empty message received from chat_id=%s", chat_id)
        send_telegram_message(chat_id, "No recibí ningún mensaje.")
        return jsonify({"ok": True})

    logger.info("Incoming message from chat_id=%s: %s", chat_id, incoming_msg)

    try:
        session = get_session(chat_id)

        extracted = extract_lead_data(incoming_msg)
        session["lead_data"] = merge_lead_data(session["lead_data"], extracted)

        session["history"].append({"role": "user", "content": incoming_msg})

        ai_reply = get_chat_reply(session["history"], session["lead_data"])
        logger.info("Reply to chat_id=%s: %s", chat_id, ai_reply)

        session["history"].append({"role": "assistant", "content": ai_reply})

        if is_lead_complete(session["lead_data"]):
            summary = build_summary(chat_id, session["lead_data"])
            logger.info("Lead complete:\n%s", summary)

        send_telegram_message(chat_id, ai_reply)

    except Exception:
        logger.exception("Error processing message from chat_id=%s", chat_id)
        send_telegram_message(chat_id, "Disculpa, tengo un problema técnico. Inténtalo en un momento.")

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
