import urllib.parse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re
import locale

# Define o locale para Brasil (formato com vírgula e ponto)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # No Windows pode precisar ajustar

class Amazon():    
    def __init__(self, AMAZON_TAG: str):
        self.amazon_tag = AMAZON_TAG  

    def gerar_link_afiliado_amazon(self, link_produto: str) -> str:
        parsed = urllib.parse.urlparse(link_produto)
        query = urllib.parse.parse_qs(parsed.query)
        query["tag"] = [self.amazon_tag]
        new_query = urllib.parse.urlencode(query, doseq=True)
        new_url = parsed._replace(query=new_query)
        return urllib.parse.urlunparse(new_url)

    def extrair_dados_amazon_com_selenium(self, url: str):  # agora é de instância
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        driver = webdriver.Chrome(options=options)

        try:
            driver.get(url)
            time.sleep(10)

            try:
                title_elem = driver.find_element(By.ID, "productTitle")
                titulo = title_elem.text.strip()
            except:
                titulo = "Produto sem título"


            seletor = "span.a-price-whole"

            preco = "erro ao encontrar preço"
            try:
                preco_elem = driver.find_element(By.CSS_SELECTOR, seletor)
                texto = preco_elem.text.strip()
                print(f"\nTexto encontrado: {texto}\n")  # Debugging

                if texto:
                    # Remove tudo que não for número ou vírgula/ponto
                    texto_numerico = re.sub(r"[^\d,\.]", "", texto)

                    # Ajusta para formato decimal
                    if "," in texto_numerico and "." in texto_numerico:
                        # Corrige se veio no formato errado (ex: "1.299,99")
                        texto_numerico = texto_numerico.replace(".", "").replace(",", ".")
                    elif "," in texto_numerico:
                        texto_numerico = texto_numerico.replace(",", ".")  # ex: "1299,99" → "1299.99"

                    try:
                        valor_float = float(texto_numerico)
                        preco_formatado = locale.currency(valor_float, grouping=True)
                        preco = preco_formatado
                        print(f"\nPreço formatado: {preco}\n")  # Debugging
                    except ValueError:
                        preco = "Preço inválido"
                else:
                    preco = "Preço não encontrado"
            except:
                pass

            try:
                image_elem = driver.find_element(By.ID, "landingImage")
                imagem_url = image_elem.get_attribute("src")
            except:
                imagem_url = None

            return titulo, imagem_url, preco

        except Exception as e:
            print(f"[ERRO Selenium - Amazon] {e}")
            return "Produto sem título", None, "Preço não encontrado"

        finally:
            driver.quit()
