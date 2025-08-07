import urllib.parse
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class Magalu():            

    # === EXTRAI DADOS MAGALU ===

    @staticmethod
    def extrair_dados_magalu(url: str):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=options)

        try:
            driver.get(url)
            time.sleep(5)

            # === Título ===
            try:
                title_elem = driver.find_element(By.CSS_SELECTOR, "h1[data-testid='heading-product-title']")
                titulo = title_elem.text.strip()
            except:
                titulo = "Produto sem título"

            # === Preço ===
            try:
                preco_elem = driver.find_element(By.CSS_SELECTOR, "p[data-testid='price-value']")
                preco = preco_elem.text.strip()

                # Remove "ou" do início, se houver (com ou sem espaço depois)
                if preco.lower().startswith("ou"):
                    preco = preco[2:].strip()  # Remove os dois primeiros caracteres ("ou") e espaços

                print(f"\nPreço formatado: {preco}\n")  # Debugging

            except:
                preco = "Preço indisponível"

            # === Imagem ===
            try:
                image_elem = driver.find_element(By.CSS_SELECTOR, "img[data-testid='image-selected-thumbnail']")
                imagem_url = image_elem.get_attribute("src")
            except:
                imagem_url = None

            return titulo, imagem_url, preco

        except Exception as e:
            print(f"[ERRO Selenium - Magalu] {e}")
            return "Produto sem título", None, "Preço indisponível"

        finally:
            driver.quit()
