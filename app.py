from telegram.ext import ApplicationBuilder, MessageHandler, filters
import os
# Asegúrate de que el puerto esté configurado
PORT = os.getenv("PORT", "8080")

def main():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN no está configurado.")
        return
    
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.run_polling()

if __name__ == "__main__":
    # Esto es solo para satisfacer el requisito de Render
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is running!")

    # Inicia un servidor de salud en el puerto necesario
    server = HTTPServer(("0.0.0.0", int(PORT)), HealthCheckHandler)
    print(f"Servidor de salud ejecutándose en el puerto {PORT}")
    main()
