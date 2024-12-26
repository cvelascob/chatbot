from flask import Flask, request
import os
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Configuración de Hugging Face
HF_API_TOKEN = os.getenv("HF_API_TOKEN")  # Token de Hugging Face
HF_MODEL = "microsoft/DialoGPT-medium"    # Modelo que deseas usar
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
    user_message = update.message.text
    print(f"Mensaje recibido del usuario: {user_message}")  # Log

    try:
        print("Llamando a Hugging Face...")
        response = query_huggingface(user_message)
        print(f"Respuesta generada por Hugging Face: {response}")  # Log
        await update.message.reply_text(response)
    except Exception as e:
        print(f"Error al procesar el mensaje: {e}")  # Log
        await update.message.reply_text("Lo siento, hubo un error al procesar tu mensaje. Intenta nuevamente.")

# Función para consultar Hugging Face
def query_huggingface(prompt):
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": prompt}
    print(f"Enviando consulta a Hugging Face con el mensaje: {prompt}")  # Log

    response = requests.post(HF_API_URL, headers=headers, json=payload)
    print(f"Respuesta de Hugging Face: {response.status_code}, {response.text}")  # Log completo

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0]["generated_text"]
        return "No entendí tu mensaje."
    else:
        raise Exception(f"Error en Hugging Face API: {response.status_code}, {response.text}")

# Servidor Flask
app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    """Verifica que el servidor esté funcionando."""
    print("Solicitud GET recibida en '/'")  # Log
    return "El bot está funcionando correctamente.", 200

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    """Procesa las actualizaciones enviadas por Telegram al webhook."""
    print("Actualización POST recibida desde Telegram")  # Log
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run(initialize_and_process_update(update))
        return "OK", 200
    except Exception as e:
        print(f"Error procesando la actualización de Telegram: {e}")  # Log
        return "ERROR", 500

async def initialize_and_process_update(update):
    """Inicializa la aplicación y procesa la actualización."""
    print("Inicializando y procesando la actualización de Telegram")  # Log
    await application.initialize()
    print("Aplicación inicializada")  # Log
    await application.process_update(update)
    print("Actualización procesada")  # Log
    await application.shutdown()

if __name__ == "__main__":
    # Agregar manejadores a la aplicación de Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Configurar el webhook en Telegram
    webhook_url = f"https://chatbot-cwi2.onrender.com/{TELEGRAM_TOKEN}"  # Cambia <YOUR_RENDER_URL> por tu URL de Render
    response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}")
    print("Respuesta del webhook:", response.json())  # Log de la configuración del webhook

    # Ejecutar el servidor Flask
    PORT = int(os.environ.get("PORT", 5000))  # Render asigna el puerto a través de esta variable de entorno
    print(f"Ejecutando Flask en el puerto {PORT}")  # Log
    app.run(host="0.0.0.0", port=PORT)


