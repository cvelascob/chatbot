import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Hugging Face API Settings
HF_API_TOKEN = os.getenv("")  # Tu token de Hugging Face
HF_MODEL = "microsoft/DialoGPT-medium"    # Modelo que deseas usar
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# Telegram Bot Functionality
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("¡Hola! Soy un bot con inteligencia artificial. Envíame un mensaje y te responderé.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text

    # Enviar el mensaje al modelo de Hugging Face
    try:
        response = query_huggingface(user_message)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text("Lo siento, hubo un error al procesar tu mensaje. Intenta nuevamente.")
        print(f"Error: {e}")

# Hugging Face Query Function
def query_huggingface(prompt):
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": prompt}

    response = requests.post(HF_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0]["generated_text"]  # Respuesta generada
        return "Lo siento, no pude entender tu mensaje."
    else:
        raise Exception(f"Error en la API de Hugging Face: {response.status_code}, {response.text}")

# Main Function to Run the Bot
def main():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN or not HF_API_TOKEN:
        print("Error: TELEGRAM_TOKEN o HF_API_TOKEN no está configurado.")
        return

    # Crear la aplicación del bot
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Agregar manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Iniciando el bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
