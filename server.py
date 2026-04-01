from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import json
from pathlib import Path
from openai import AzureOpenAI

app = Flask(__name__)

DATA_FILE = Path("leads.json")

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
)

SYSTEM_PROMPT = """
Eres un agente comercial profesional especializado en comercio internacional.

Tu misión es hablar por WhatsApp de forma natural, breve y profesional.

Objetivos:
- Detectar si el contacto quiere comprar o vender
- Recoger información comercial útil
- Hacer solo una pregunta cada vez
- Avanzar la conversación sin sonar robótico
- Cuando falten datos clave, pedirlos con naturalidad

Datos que debes intentar obtener:
- nombre
- tipo de cliente (comprador, vendedor o intermediario)
- producto
- cantidad
- origen
- destino
- presupuesto
- urgencia
- problemas logísticos o necesidades especiales

Reglas:
- No hagas listas largas al cliente
- No hagas más de una pregunta por mensaje
- Sé concreto
- Mensajes cortos, cómodos para WhatsApp
- Si el cliente ya dio información, no la repitas innecesariamente
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

def load_data():
    if not DATA_FILE.exists():
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def merge_lead_data(old, new):
    merged = old.copy()
    for key, value in new.items():
        if value and str(value).strip():
            merged[key] = value.strip()
    return merged

def get_chat_reply(user_message, lead_data):
    context = f"""
Datos actuales del lead:
{json.dumps(lead_data, ensure_ascii=False)}
"""

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": context},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=180,
    )

    return response.choices[0].message.content.strip()

def extract_lead_data(user_message):
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
        max_tokens=250,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content.strip()
    return json.loads(content)

def build_summary(phone, lead_data):
    return f"""
NUEVO CLIENTE DETECTADO

WhatsApp: {phone}
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

def is_lead_complete(lead_data):
    required_fields = ["tipo_cliente", "producto", "cantidad"]
    filled = sum(1 for field in required_fields if lead_data.get(field))
    return filled >= 3

@app.route("/")
def home():
    return "OK FUNCIONANDO", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.form.get("Body", "").strip()
    phone = request.form.get("From", "").strip()

    response = MessagingResponse()
    message = response.message()

    if not incoming_msg:
        message.body("No recibí ningún mensaje.")
        return str(response), 200

    try:
        data = load_data()

        if phone not in data:
            data[phone] = {
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

        extracted = extract_lead_data(incoming_msg)
        data[phone] = merge_lead_data(data[phone], extracted)

        ai_reply = get_chat_reply(incoming_msg, data[phone])

        if is_lead_complete(data[phone]):
            summary = build_summary(phone, data[phone])
            print(summary)

        save_data(data)
        message.body(ai_reply)

    except Exception as e:
        message.body(f"Error IA: {str(e)}")

    return str(response), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)