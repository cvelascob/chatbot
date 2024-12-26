from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import os

async def start(update, context):
    await update.message.reply_text("¡Hola! Soy tu bot.")

async def handle_message(update, context):
    user_message = update.message.text
    await update.message.reply_text(f"Recibí tu mensaje: {user_message}")

def main():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN no está configurado.")
        return

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Iniciando el bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
