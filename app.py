from telegram.ext import ApplicationBuilder, MessageHandler, filters

async def handle_message(update, context):
    user_message = update.message.text
    await update.message.reply_text(f"Recibido: {user_message}")

def main():
    import os
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN no está configurado.")
        return
    
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()
