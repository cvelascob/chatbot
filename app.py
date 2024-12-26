from flask import Flask, request
import os
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Configuración de Hugging Face
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = "microsoft/DialoGPT-medium"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# Configuración de Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN or not HF_API_TOKEN:
    raise ValueError("TELEGRAM_TOKEN o HF_API_TOKEN no está configurado.")

# Crear la aplicación de Telegram
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Funciones de Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("Comando /start recibido")
    await update.message.reply_text("¡Hola! Soy un bot con inteligencia artificial. Envíame un mensaje y te responderé.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        print("No se recibió un mensaje válido.")
        return
    user_message = update.message.text
    print(f"Mensaje recibido del usuario: {user_message}")

    try:
        response = query_huggingface(user_message)
        print(f"Respuesta generada por Hugging Face: {response}")
        await update.message.reply_text(response)
    except Exception as e:
        print(f"Error al procesar el mensaje: {e}")
        await update.message.reply_text("Lo siento, hubo un error al procesar tu mensaje. Intenta nuevamente.")

# Función para consultar Hugging Face
def query_huggingface(prompt):
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": f"Usuario: {prompt}\nBot:",
        "parameters": {"max_length": 50, "temperature": 0.7, "top_p": 0.9},
    }
    print(f"Enviando consulta a Hugging Face: {prompt}")

    response = requests.post(HF_API_URL, headers=headers, json=payload)
    print(f"Respuesta de Hugging Face: {response.status_code}, {response.text}")

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
            return data[0]["generated_text"]
        return "Lo siento, no entendí tu mensaje."
    else:
        raise Exception(f"Error en Hugging Face API: {response.status_code}, {response.text}")

# Servidor Flask
app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    print("Solicitud GET recibida en '/'")
    return "El bot está funcionando correctamente.", 200

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    print("Actualización POST recibida desde Telegram")
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run(initialize_and_process_update(update))
        return "OK", 200
    except Exception as e:
        print(f"Error procesando la actualización de Telegram: {e}")
        return "ERROR", 500

async def initialize_and_process_update(update):
    print("Inicializando y procesando la actualización de Telegram")
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        print("Creando un nuevo ciclo de eventos...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    await application.initialize()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.process_update(update)
    print("Actualización procesada")

if __name__ == "__main__":
    webhook_url = f"https://chatbot-cwi2.onrender.com/{TELEGRAM_TOKEN}"
    response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}")
    print("Respuesta del webhook:", response.json())

    PORT = int(os.environ.get("PORT", 5000))
    print(f"Ejecutando Flask en el puerto {PORT}")
    app.run(host="0.0.0.0", port=PORT)


