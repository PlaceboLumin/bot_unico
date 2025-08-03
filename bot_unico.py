import asyncio
import os
import urllib.parse
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

TELEGRAM_TOKEN = os.getenv("7480441409:AAEOUNKWWuB2Et3y3u4VR-mpJQR0abCzT88")
TELEGRAM_CHANNEL = "@Promos_Placebo"
AFFILIATE_PREFIX = "https://rzekl.com/g/1e8d1144948f503228bf16525dc3e8/?ulp="
AMAZON_TAG = "placebospromos-20"

logging.basicConfig(level=logging.INFO)

# === Links afiliados ===
def gerar_link_afiliado_aliexpress(link: str):
    return f"{AFFILIATE_PREFIX}{urllib.parse.quote(link, safe='')}"

def gerar_link_afiliado_amazon(link: str):
    parsed = urllib.parse.urlparse(link)
    query = urllib.parse.parse_qs(parsed.query)
    query["tag"] = [AMAZON_TAG]
    new_query = urllib.parse.urlencode(query, doseq=True)
    return urllib.parse.urlunparse(parsed._replace(query=new_query))

# === Web scraping com Selenium ===
def configurar_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    return webdriver.Chrome(options=options)

def extrair_preco_com_selenium(url):
    driver = configurar_driver()
    try:
        driver.get(url)
        time.sleep(5)
        seletores = [
            'span.product-price-value',
            'span[class*="price-default--current"]',
            'span[class*="uniform-banner-box-price"]'
        ]
        for seletor in seletores:
            try:
                preco = driver.find_element(By.CSS_SELECTOR, seletor).text.strip()
                if preco:
                    return preco
            except:
                continue
        return "Preço não encontrado"
    finally:
        driver.quit()

def extrair_dados_amazon(url):
    driver = configurar_driver()
    try:
        driver.get(url)
        time.sleep(10)
        try:
            titulo = driver.find_element(By.ID, "productTitle").text.strip()
        except:
            titulo = "Produto sem título"

        preco = "Preço não encontrado"
        for seletor in ["span.a-price > span.a-offscreen", "span.a-offscreen", "span.a-price-whole"]:
            try:
                preco_elem = driver.find_element(By.CSS_SELECTOR, seletor).text.strip()
                if "R$" in preco_elem:
                    preco = preco_elem
                    break
            except:
                continue

        try:
            imagem_url = driver.find_element(By.ID, "landingImage").get_attribute("src")
        except:
            imagem_url = None

        return titulo, imagem_url, preco
    finally:
        driver.quit()

def extrair_dados_aliexpress(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "lxml")
    title_tag = soup.find("meta", property="og:title")
    image_tag = soup.find("meta", property="og:image")
    titulo = title_tag["content"] if title_tag else "Produto sem título"
    imagem_url = image_tag["content"] if image_tag else None
    preco = extrair_preco_com_selenium(url)
    return titulo, imagem_url, preco

def extrair_dados_magalu(url):
    driver = configurar_driver()
    try:
        driver.get(url)
        time.sleep(5)
        try:
            titulo = driver.find_element(By.CSS_SELECTOR, "h1[data-testid='heading-product-title']").text.strip()
        except:
            titulo = "Produto sem título"
        try:
            preco = driver.find_element(By.CSS_SELECTOR, "p[data-testid='price-value']").text.strip()
        except:
            preco = "Preço indisponível"
        try:
            imagem_url = driver.find_element(By.CSS_SELECTOR, "img[data-testid='image-selected-thumbnail']").get_attribute("src")
        except:
            imagem_url = None
        return titulo, imagem_url, preco
    finally:
        driver.quit()

# === Fila de postagens ===
fila_postagens = []

async def postar_da_fila(app):
    while True:
        if fila_postagens:
            url = fila_postagens.pop(0)

            if "aliexpress" in url:
                titulo, imagem, preco = extrair_dados_aliexpress(url)
                url_afiliado = gerar_link_afiliado_aliexpress(url)
            elif "amazon" in url:
                titulo, imagem, preco = extrair_dados_amazon(url)
                url_afiliado = gerar_link_afiliado_amazon(url)
            elif "magazinevoce" in url or "magazineluiza" in url:
                titulo, imagem, preco = extrair_dados_magalu(url)
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
                print(f"[Erro ao postar da fila] {e}")
        await asyncio.sleep(1800)

# === Comandos do Telegram ===
async def post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /post <link>")
        return

    url = context.args[0]

    if "aliexpress" in url:
        titulo, imagem, preco = extrair_dados_aliexpress(url)
        url_afiliado = gerar_link_afiliado_aliexpress(url)
    elif "amazon" in url:
        titulo, imagem, preco = extrair_dados_amazon(url)
        url_afiliado = gerar_link_afiliado_amazon(url)
    elif "magazinevoce" in url or "magazineluiza" in url:
        titulo, imagem, preco = extrair_dados_magalu(url)
        url_afiliado = url
    else:
        await update.message.reply_text("❌ Link não suportado. Envie um link da Amazon, Magalu ou AliExpress.")
        return

    mensagem = f"<b>💻🔥 {titulo}</b>\n\n💸 <b>{preco}</b>\n\n🔗 <a href=\"{url_afiliado}\">Compre aqui</a>"

    try:
        if imagem:
            await context.bot.send_photo(chat_id=TELEGRAM_CHANNEL, photo=imagem, caption=mensagem, parse_mode='HTML')
        else:
            await context.bot.send_message(chat_id=TELEGRAM_CHANNEL, text=mensagem, parse_mode='HTML')
        await update.message.reply_text("✅ Produto postado com sucesso no canal!")
    except Exception as e:
        print(f"[Erro ao postar] {e}")
        await update.message.reply_text("❌ Erro ao postar no canal.")

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

# === Inicialização do bot ===
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("post", post))
    app.add_handler(CommandHandler("post30", post30))
    asyncio.create_task(postar_da_fila(app))
    print("✅ Bot iniciado.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
