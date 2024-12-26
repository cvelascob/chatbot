from telegram.ext import ApplicationBuilder
import os
async def start(update, context):
    await update.message.reply_text("¡Hola! Soy tu bot.")

async def handle_message(update, context):
    user_message = update.message.text
    await update.message.reply_text(f"Recibí tu mensaje: {user_message}")

def main():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # URL pública de tu Render Service

    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    # Configura manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Configura Webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8443)),
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
