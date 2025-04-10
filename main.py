from telegram.ext import ApplicationBuilder
from config import Config

application = ApplicationBuilder() \
    .token(Config.TELEGRAM_TOKEN) \
    .webhook_url(Config.WEBHOOK_URL) \
    .cert("ssl_cert.pem") \  # Путь к SSL-сертификату
    .build()
