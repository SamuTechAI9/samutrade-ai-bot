from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
my_endpoint = "https://samuel-feria-1239-resource.services.ai.azure.com/api/projects/samuel_feria-1239"
project_client = AIProjectClient(
    endpoint=my_endpoint,
    credential=DefaultAzureCredential()
)
my_agent = "SamuTradeAI"
my_version = "1"
openai_client = project_client.get_openai_client()
HISTORIAL_FILE = "historial_samutrade.json"

# --- CONTEXTO GLOBAL ---
contexto_global = """
Actúa como SamuTradeAI, el asistente experto de Samuel Torres, Trader Internacional especializado en la ruta España-África.

Portafolio de Negocios:
1. VEHÍCULOS: Exportación de Scooters europeos (Peugeot/Piaggio). Compra 260€ (lote FCL ~100 unidades), Venta 700-900€. Margen 300-500€/ud.
2. CONSTRUCCIÓN: Suministro de materiales de obra y herramientas industriales desde España.
3. ALIMENTACIÓN: Exportación de contenedores (FCL/LCL) de productos alimenticios y commodities.
4. LOGÍSTICA: Gestión de contenedores completos, aduanas validadas en Mauritania, Senegal y Marruecos.

Reglas de comunicación:
- Tono: Profesional, ejecutivo, directo y confiable.
- No eres una IA, eres el brazo operativo de Samuel Torres.
- Prioriza la rentabilidad y la seguridad logística en tus respuestas.
- Siempre introduce sensación de oportunidad limitada (stock en movimiento, otros compradores activos).
- El precio de 260€/unidad aplica SOLO en lote de contenedor completo (~100 unidades).
"""

# --- GUARDAR EN HISTORIAL ---
def guardar_historial(tipo, prompt, respuesta):
    historial = []
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
            historial = json.load(f)
    historial.append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "tipo": tipo,
        "prompt": prompt,
        "respuesta": respuesta
    })
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)
    print(f"✅ Guardado en {HISTORIAL_FILE}")

# --- MENÚ ---
def mostrar_menu():
    print("\n" + "="*40)
    print("         SAMUTRADE AI v1.0")
    print("="*40)
    print("1. WhatsApp: Oferta de Scooters")
    print("2. WhatsApp: Materiales / Construcción")
    print("3. WhatsApp: Alimentos / Commodities")
    print("4. Pitch para Inversores")
    print("5. Consulta libre")
    print("0. Salir")
    return input("\nElige una opción: ")

# --- BUCLE PRINCIPAL ---
while True:
    opcion = mostrar_menu()

    if opcion == "0":
        print("\nCerrando sistema... ¡Buen trading! 🚀")
        break

    user_prompt = ""
    tipo_mensaje = ""

    if opcion == "1":
        pais = input("País destino: ")
        cantidad = input("Cantidad de scooters: ")
        user_prompt = f"Redacta un mensaje de WhatsApp para un cliente en {pais} interesado en un lote de {cantidad} scooters europeos. Destaca calidad, logística validada y urgencia por stock limitado."
        tipo_mensaje = f"Scooters - {pais} - {cantidad} uds"

    elif opcion == "2":
        material = input("Tipo de material (ej: cemento, azulejos, herramientas): ")
        user_prompt = f"Redacta una propuesta corta para exportación de {material} desde España a África."
        tipo_mensaje = f"Construcción - {material}"

    elif opcion == "3":
        producto = input("Producto alimenticio (ej: aceite, conservas, cereales): ")
        user_prompt = f"Crea un mensaje para un distribuidor interesado en importar {producto} en contenedores desde España."
        tipo_mensaje = f"Alimentos - {producto}"

    elif opcion == "4":
        user_prompt = "Crea un pitch ejecutivo para un inversor. Explica la alta rentabilidad de los contenedores FCL (300-500€ de margen por unidad en vehículos) y la seguridad en aduanas de Mauritania, Senegal y Marruecos."
        tipo_mensaje = "Pitch Inversor"

    elif opcion == "5":
        user_prompt = input("Escribe tu consulta: ")
        tipo_mensaje = "Consulta libre"

    else:
        print("\n[!] Opción no válida.")
        continue

    print("\n⏳ Consultando con el Agente...")

    full_prompt = f"{contexto_global}\n\nSOLICITUD: {user_prompt}"

    try:
        response = openai_client.responses.create(
            input=[{"role": "user", "content": full_prompt}],
            extra_body={
                "agent_reference": {
                    "name": my_agent,
                    "version": my_version,
                    "type": "agent_reference"
                }
            }
        )

        print("\n" + "-"*40)
        print("📈 RESPUESTA SAMUTRADE AI:")
        print("-"*40)
        print(response.output_text)
        print("-"*40)

        guardar = input("\n¿Guardar esta respuesta? (s/n): ")
        if guardar.lower() == "s":
            guardar_historial(tipo_mensaje, user_prompt, response.output_text)

    except Exception as e:
        print(f"\n❌ Error de conexión con Azure. Revisa 'az login'.\nDetalle: {e}")

    input("\nPresiona Enter para volver al menú...")