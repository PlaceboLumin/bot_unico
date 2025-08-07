import asyncio
import os
import urllib.parse
import logging
import requests
import time
from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from lojas.aliexpress import Aliexpress
from lojas.amazon import Amazon
from lojas.magalu import Magalu


# === CONFIGURAÇÕES ===
TELEGRAM_TOKEN = "7480441409:AAEOUNKWWuB2Et3y3u4VR-mpJQR0abCzT88"
TELEGRAM_CHANNEL = "@Promos_Placebo"
AFFILIATE_PREFIX = "https://rzekl.com/g/1e8d1144948f503228bf16525dc3e8/?ulp="
AMAZON_TAG = "placebospromos-20"

logging.basicConfig(level=logging.INFO)

# Agora pode usar a classe
ali = Aliexpress(AFFILIATE_PREFIX)
ama = Amazon(AMAZON_TAG)
mgl = Magalu()

# === COMANDO /post ===
async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /post <link>")
        return

    url = context.args[0]

    if "aliexpress" in url:
        titulo, imagem, preco = ali.extrair_dados_aliexpress(url)
        url_afiliado = ali.gerar_link_afiliado_aliexpress(url)
    elif "amazon" in url:
        titulo, imagem, preco = ama.extrair_dados_amazon_com_selenium(url)
        url_afiliado = ama.gerar_link_afiliado_amazon(url)
    elif "magazinevoce" in url:
        titulo, imagem, preco = mgl.extrair_dados_magalu(url)  # Agora funciona
        url_afiliado = url  # Já é afiliado
    elif "magazineluiza" in url:
        titulo, imagem, preco = mgl.extrair_dados_magalu(url)
        url_afiliado = url  # Já é afiliado

    else:
        await update.message.reply_text("❌ Link não suportado. Envie um link da Amazon ou AliExpress.")
        return

    mensagem = f"<b>💻🔥 {titulo}</b>\n\n💸 <b>{preco}</b>\n\n🔗 <a href=\"{url_afiliado}\">Compre aqui</a>"
    try:
        if imagem:
            await context.bot.send_photo(chat_id=TELEGRAM_CHANNEL, photo=imagem, caption=mensagem, parse_mode='HTML')
        else:
            await context.bot.send_message(chat_id=TELEGRAM_CHANNEL, text=mensagem, parse_mode='HTML')

        # ✅ Mensagem de confirmação para o usuário
        await update.message.reply_text("✅ Produto postado com sucesso no canal!")
        
    except Exception as e:
        print(f"[ERRO ao postar no canal] {e}")
        await update.message.reply_text("❌ Ocorreu um erro ao postar no canal.")

# === GLOBAL ===
fila_postagens = []

# === LOOP DE POSTAGEM A CADA 30 MIN ===
async def postar_da_fila(app):
    while True:
        if fila_postagens:
            url = fila_postagens.pop(0)

            if "aliexpress" in url:
                titulo, imagem, preco = ali.extrair_dados_aliexpress(url)
                url_afiliado = ali.gerar_link_afiliado_aliexpress(url)
            elif "amazon" in url:
                titulo, imagem, preco = ama.extrair_dados_amazon_com_selenium(url)
                url_afiliado = ama.gerar_link_afiliado_amazon(url)
            elif "magazinevoce" in url or "magazineluiza" in url:
                titulo, imagem, preco = mgl.extrair_dados_magalu(url)
                url_afiliado = url
            else:
                print(f"❌ Link não suportado da fila: {url}")
                await asyncio.sleep(5)
                continue

            mensagem = f"<b>💻🔥 {titulo}</b>\n\n💸 <b>{preco}</b>\n\n🔗 <a href=\"{url_afiliado}\">Compre aqui</a>"

            try:
                if imagem:
                    await app.bot.send_photo(chat_id=TELEGRAM_CHANNEL, photo=imagem, caption=mensagem, parse_mode='HTML')
                else:
                    await app.bot.send_message(chat_id=TELEGRAM_CHANNEL, text=mensagem, parse_mode='HTML')
                print(f"✅ Postado da fila: {url}")
            except Exception as e:
                print(f"Erro ao postar: {e}")
        await asyncio.sleep(1800)

# === FUNÇÃO QUE RODA AO INICIAR O BOT ===
async def on_startup(app):
    print("✅ Bot rodando...")
    asyncio.create_task(postar_da_fila(app))

async def post30(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /post30 <link1> <link2> ...")
        return

    adicionados = 0
    for url in context.args:
        if any(x in url for x in ["aliexpress", "amazon", "magazinevoce", "magazineluiza"]):
            fila_postagens.append(url)
            adicionados += 1

    await update.message.reply_text(f"✅ {adicionados} produto(s) adicionados para postagem a cada 30 minutos.")

# === INICIALIZAÇÃO FINAL ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(on_startup).build()

    app.add_handler(CommandHandler("post", post))
    app.add_handler(CommandHandler("post30", post30))

    app.run_polling()

