from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
import re
import time

from .login_helper import criar_driver_com_perfil

TERMOS_PRODUTO = [
    "product designer", "product design", "product manager", "ux designer", "ui designer",
    "ux/ui", "ui/ux", "service designer", "head de produto", "product owner",
    "product operations", "design de produto", "designer de produto",
]

TERMOS_EXCLUIR = [
    "developer", "desenvolvedor", "engineer", "engenheiro", "qa", "tester",
    "analista de dados", "data analyst", "designer gráfico", "graphic designer",
    "marketing", "growth", "devops", "backend", "frontend", "fullstack",
]


def eh_vaga_produto(titulo: str) -> bool:
    titulo_lower = titulo.lower()
    for termo in TERMOS_EXCLUIR:
        if termo in titulo_lower:
            return False
    for termo in TERMOS_PRODUTO:
        if termo in titulo_lower:
            return True
    return False


def classificar_tipo_vaga(titulo: str) -> str:
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


def scroll_e_extrair_vagas(driver, max_scrolls=200):
    """Faz scroll lento na lista para carregar e extrair todas as vagas."""
    vagas = []
    links_vistos = set()

    try:
        lista = driver.find_element(By.CSS_SELECTOR, "div.scaffold-layout__list")

        for i in range(max_scrolls):
            # Pega todos os cards com job_id
            cards = driver.find_elements(By.CSS_SELECTOR, "li.scaffold-layout__list-item[data-occludable-job-id]")

            # Extrai vagas dos cards que têm conteúdo carregado
            for card in cards:
                try:
                    job_id = card.get_attribute("data-occludable-job-id")
                    if not job_id:
                        continue

                    link_vaga = f"https://www.linkedin.com/jobs/view/{job_id}"
                    if link_vaga in links_vistos:
                        continue

                    # Scrolla até o card para forçar renderização
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(0.15)

                    # Tenta extrair título
                    titulo = None
                    try:
                        titulo = card.find_element(By.CSS_SELECTOR, "a strong").text.strip()
                    except:
                        try:
                            titulo = card.find_element(By.CSS_SELECTOR, "strong").text.strip()
                        except:
                            pass

                    if not titulo:
                        continue

                    links_vistos.add(link_vaga)

                    # Extrai empresa e localização
                    empresa = None
                    localizacao = None
                    try:
                        empresa = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle").text.strip()
                    except:
                        pass
                    try:
                        localizacao = card.find_element(By.CSS_SELECTOR, ".job-card-container__metadata-wrapper li").text.strip()
                    except:
                        try:
                            localizacao = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__caption").text.strip()
                        except:
                            pass

                    vagas.append({
                        "titulo": titulo,
                        "empresa": empresa,
                        "link_vaga": link_vaga,
                        "localizacao": localizacao,
                    })
                except:
                    continue

            # Scroll para baixo na lista
            driver.execute_script("arguments[0].scrollTop += 300", lista)
            time.sleep(0.2)

            # Verifica se chegou ao fim
            scroll_pos = driver.execute_script("return arguments[0].scrollTop", lista)
            scroll_height = driver.execute_script("return arguments[0].scrollHeight", lista)
            client_height = driver.execute_script("return arguments[0].clientHeight", lista)

            if scroll_pos + client_height >= scroll_height - 50:
                # Chegou ao fim, espera um pouco por mais conteúdo
                time.sleep(0.5)
                new_height = driver.execute_script("return arguments[0].scrollHeight", lista)
                if new_height == scroll_height:
                    break

        return vagas
    except Exception as e:
        print(f"Erro no scroll: {e}")
        return vagas


def coletar_vagas_linkedin(max_paginas: int = 20, headless: bool = False) -> list[dict]:
    """Coleta vagas do LinkedIn com scroll e paginação."""

    base_url = "https://www.linkedin.com/jobs/search/?f_TPR=r86400&f_WT=2&keywords=ux&sortBy=R"
    todas_vagas = []
    links_vistos = set()
    driver = None

    try:
        driver = criar_driver_com_perfil(headless=headless)
        driver.get(base_url)
        time.sleep(4)

        if "Sign in" in driver.page_source or "Entrar" in driver.page_source:
            print("AVISO: Não está logado.")
            return []

        print("Login OK. Coletando vagas...")

        for pagina in range(1, max_paginas + 1):
            print(f"Página {pagina}...")

            # Scroll e extração na página atual
            vagas_pagina = scroll_e_extrair_vagas(driver)
            novas = 0

            for v in vagas_pagina:
                if v["link_vaga"] not in links_vistos:
                    links_vistos.add(v["link_vaga"])
                    todas_vagas.append(v)
                    novas += 1

            print(f"  -> {novas} novas (total: {len(todas_vagas)})")

            # Próxima página
            try:
                # Tenta diferentes seletores para botão de próxima página
                next_btn = None
                for selector in [
                    "button[aria-label='Ver próxima página']",
                    "button[aria-label='Avançar']",
                    "button[aria-label='Page forward']",
                    ".artdeco-pagination__button--next"
                ]:
                    try:
                        btns = driver.find_elements(By.CSS_SELECTOR, selector)
                        for btn in btns:
                            if not btn.get_attribute("disabled"):
                                next_btn = btn
                                break
                        if next_btn:
                            break
                    except:
                        continue

                if not next_btn:
                    print("Última página")
                    break

                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(3)
                # Scroll para topo da lista
                lista = driver.find_element(By.CSS_SELECTOR, "div.scaffold-layout__list")
                driver.execute_script("arguments[0].scrollTop = 0", lista)
                time.sleep(1)
            except Exception as e:
                print(f"Fim da paginação: {e}")
                break

        print(f"\nTotal coletado: {len(todas_vagas)} vagas")

        vagas_produto = []
        for v in todas_vagas:
            if eh_vaga_produto(v["titulo"]):
                vagas_produto.append({
                    "titulo": v["titulo"],
                    "empresa": v["empresa"],
                    "tipo_vaga": classificar_tipo_vaga(v["titulo"]),
                    "fonte": "linkedin_jobs",
                    "link_vaga": v["link_vaga"],
                    "localizacao": v["localizacao"],
                    "modalidade": "remoto",
                    "requisito_ingles": "nao_especificado",
                    "forma_contato": "link",
                    "data_coleta": date.today().isoformat(),
                })

        print(f"Vagas de produto: {len(vagas_produto)}")
        return vagas_produto

    except Exception as e:
        print(f"Erro: {e}")
        return []

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    vagas = coletar_vagas_linkedin()
    print(f"\nTotal: {len(vagas)}")
    for v in vagas[:10]:
        print(f"  - {v['titulo']} @ {v['empresa']}")
