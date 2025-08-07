from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def extrair_preco_com_selenium(url):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # ajuste se necessário

    try:
        preco = driver.find_element(By.CSS_SELECTOR, "meta[property='og:price:amount']")
        valor = preco.get_attribute("content")
    except:
        valor = "Preço não encontrado"
    finally:
        driver.quit()

    return valor


# === Função auxiliar para extrair o preço com Selenium ===
def extrair_preco_com_selenium(url_produto):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url_produto)
        time.sleep(5)
        elementos_possiveis = [
            'span.product-price-value',
            'span[class*="price-default--current"]',
            'span[class*="uniform-banner-box-price"]'
        ]
        for seletor in elementos_possiveis:
            try:
                preco_elem = driver.find_element(By.CSS_SELECTOR, seletor)
                if preco_elem.text.strip():
                    return preco_elem.text.strip()
            except:
                continue
        return "Preço não encontrado"
    finally:
        driver.quit()
