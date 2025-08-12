import asyncio
import logging
from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO)

from config import Config
from comandos import Comandos

#instancias aqui
conf = Config()
comand = Comandos()

# === FUNÇÃO QUE RODA AO INICIAR O BOT ===
async def on_startup(app):
    print("✅ Bot rodando...")
    asyncio.create_task(comand.postar_da_fila(app))

# === INICIALIZAÇÃO FINAL ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(conf.TELEGRAM_TOKEN).post_init(on_startup).build()

    app.add_handler(CommandHandler("post", comand.post))
    app.add_handler(CommandHandler("post30", comand.post30))

    app.run_polling()

