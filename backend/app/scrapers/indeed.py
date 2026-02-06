from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
import os
import re
import time

from .login_helper import carregar_cookies

# Termos para filtrar vagas de produto (aceitar)
TERMOS_PRODUTO = [
    "product designer", "product manager", "ux designer", "ui designer",
    "ux/ui", "ui/ux", "service designer", "head de produto", "product owner",
    "product operations", "design de produto", "designer de produto",
]

# Termos para excluir (não são vagas de produto)
TERMOS_EXCLUIR = [
    "developer", "desenvolvedor", "engineer", "engenheiro", "qa", "tester",
    "analista de dados", "data analyst", "designer gráfico", "graphic designer",
    "marketing", "growth", "devops", "backend", "frontend", "fullstack",
]


def eh_vaga_produto(titulo: str) -> bool:
    """Verifica se o título é uma vaga de produto."""
    titulo_lower = titulo.lower()

    for termo in TERMOS_EXCLUIR:
        if termo in titulo_lower:
            return False

    for termo in TERMOS_PRODUTO:
        if termo in titulo_lower:
            return True

    return False


def classificar_tipo_vaga(titulo: str) -> str:
    """Classifica o tipo da vaga baseado no título."""
    titulo_lower = titulo.lower()

    if "product manager" in titulo_lower or "product owner" in titulo_lower:
        return "Product Manager"
    elif "head" in titulo_lower and "produto" in titulo_lower:
        return "Head de Produto"
    elif "service designer" in titulo_lower:
        return "Service Designer"
    elif "ui/ux" in titulo_lower or "ux/ui" in titulo_lower:
        return "UX/UI Designer"
    elif "ui designer" in titulo_lower:
        return "UI Designer"
    elif "ux designer" in titulo_lower or "ux" in titulo_lower:
        return "UX Designer"
    elif "product designer" in titulo_lower or "designer de produto" in titulo_lower:
        return "Product Designer"

    return "Product Designer"


def criar_driver():
    """Cria driver do Chrome com opções otimizadas."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=pt-BR")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    return driver


def coletar_vagas_indeed() -> list[dict]:
    """Coleta vagas do Indeed Brasil usando Selenium (sem login)."""

    # Filtros: UX, Brasil, Home Office, Português, Últimas 24h
    url = "https://br.indeed.com/empregos?q=UX&l=Brasil&sc=0kf%3Aattr%28DSQF7%29%3B&radius=25&fromage=1&lang=pt"

    vagas = []
    driver = None

    try:
        driver = criar_driver()

        # Primeiro acessa o domínio para poder adicionar cookies
        driver.get("https://br.indeed.com")
        time.sleep(1)

        # Tenta carregar cookies salvos (login)
        if carregar_cookies(driver, "indeed"):
            print("Cookies do Indeed carregados")

        # Agora acessa a URL de busca
        driver.get(url)

        # Aguardar carregamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.job_seen_beacon, td.resultContent"))
        )

        time.sleep(2)  # Extra wait para JS carregar

        # Encontrar cards de vagas
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon, td.resultContent")

        print(f"Encontrados {len(job_cards)} cards")

        for card in job_cards:
            try:
                # Título e link
                title_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a, a.jcs-JobTitle, h2 a")
                titulo = title_elem.text.strip()

                if not titulo or not eh_vaga_produto(titulo):
                    continue

                href = title_elem.get_attribute("href") or ""

                # Extrair vjk do link
                vjk_match = re.search(r"vjk=([^&]+)", href)
                if vjk_match:
                    link_vaga = f"https://br.indeed.com/viewjob?vjk={vjk_match.group(1)}"
                else:
                    link_vaga = href

                # Empresa
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='company-name'], .companyName")
                    empresa = company_elem.text.strip()
                except:
                    empresa = None

                # Localização
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='text-location'], .companyLocation")
                    localizacao = location_elem.text.strip()
                except:
                    localizacao = None

                vaga = {
                    "titulo": titulo,
                    "empresa": empresa,
                    "tipo_vaga": classificar_tipo_vaga(titulo),
                    "fonte": "indeed",
                    "link_vaga": link_vaga,
                    "localizacao": localizacao,
                    "modalidade": "remoto",
                    "requisito_ingles": "nao_especificado",
                    "forma_contato": "indeed",
                    "data_coleta": date.today().isoformat(),
                }

                # Evitar duplicatas pelo link
                if not any(v["link_vaga"] == link_vaga for v in vagas):
                    vagas.append(vaga)
                    print(f"  + {titulo} @ {empresa}")

            except Exception as e:
                continue

    except Exception as e:
        print(f"Erro: {e}")

    finally:
        if driver:
            driver.quit()

    return vagas


if __name__ == "__main__":
    print("Coletando vagas do Indeed...")
    vagas = coletar_vagas_indeed()
    print(f"\nTotal: {len(vagas)} vagas de produto")
