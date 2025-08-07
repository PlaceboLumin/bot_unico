import urllib.parse
import requests
from bs4 import BeautifulSoup
from preco_utils import extrair_preco_com_selenium

class Aliexpress():
    def __init__(self, affiliate_prefix: str):
        self.affiliate_prefix = affiliate_prefix

    def gerar_link_afiliado_aliexpress(self, link_produto: str) -> str:
        encoded_link = urllib.parse.quote(link_produto, safe='')
        return f"{self.affiliate_prefix}{encoded_link}"

    def extrair_dados_aliexpress(self, url: str):
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "lxml")
        title_tag = soup.find("meta", property="og:title")
        image_tag = soup.find("meta", property="og:image")
        title = title_tag["content"] if title_tag else "Produto sem título"
        image_url = image_tag["content"] if image_tag else None
        preco = extrair_preco_com_selenium(url)  # Essa função precisa estar definida em outro lugar
        return title, image_url, preco
