# imports gerais
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from lojas.aliexpress import Aliexpress
from lojas.amazon import Amazon
from lojas.magalu import Magalu
from config import Config

conf = Config()

# instâncias lojas
ali = Aliexpress(conf.AFFILIATE_PREFIX)
ama = Amazon(conf.AMAZON_TAG)
mgl = Magalu()

class Comandos:  
    def __init__(self):
        self.fila_postagens = []

    # === COMANDO /post ===
    async def post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        elif "magazinevoce" in url or "magazineluiza" in url:
            titulo, imagem, preco = mgl.extrair_dados_magalu(url)
            url_afiliado = url
        else:
            await update.message.reply_text("❌ Link não suportado. Envie um link da Amazon, Magalu ou AliExpress.")
            return

        mensagem = f"<b>💻🔥 {titulo}</b>\n\n💸 <b>{preco}</b>\n\n🔗 <a href=\"{url_afiliado}\">Compre aqui</a>"
        try:
            if imagem:
                await context.bot.send_photo(chat_id=conf.TELEGRAM_CHANNEL, photo=imagem, caption=mensagem, parse_mode='HTML')
            else:
                await context.bot.send_message(chat_id=conf.TELEGRAM_CHANNEL, text=mensagem, parse_mode='HTML')

            await update.message.reply_text("✅ Produto postado com sucesso no canal!")
        except Exception as e:
            print(f"[ERRO ao postar no canal] {e}")
            await update.message.reply_text("❌ Ocorreu um erro ao postar no canal.")

    # === LOOP DE POSTAGEM A CADA 30 MIN ===
    async def postar_da_fila(self, app):
        while True:
            if self.fila_postagens:
                url = self.fila_postagens.pop(0)

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
                        await app.bot.send_photo(chat_id=conf.TELEGRAM_CHANNEL, photo=imagem, caption=mensagem, parse_mode='HTML')
                    else:
                        await app.bot.send_message(chat_id=conf.TELEGRAM_CHANNEL, text=mensagem, parse_mode='HTML')
                    print(f"✅ Postado da fila: {url}")
                except Exception as e:
                    print(f"Erro ao postar: {e}")

            await asyncio.sleep(1800)

    # === COMANDO /post30 ===
    async def post30(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Uso: /post30 <link1> <link2> ...")
            return

        adicionados = 0
        for url in context.args:
            if any(x in url for x in ["aliexpress", "amazon", "magazinevoce", "magazineluiza"]):
                self.fila_postagens.append(url)
                adicionados += 1

        await update.message.reply_text(f"✅ {adicionados} produto(s) adicionados para postagem a cada 30 minutos.")
