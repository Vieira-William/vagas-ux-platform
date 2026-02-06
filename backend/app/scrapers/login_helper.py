"""
Script para fazer login manual e salvar sessão em perfil persistente.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import os
import time

COOKIES_DIR = os.path.join(os.path.dirname(__file__), "cookies")
# Usa pasta no home do usuário para evitar problemas de permissão
PROFILE_DIR = os.path.expanduser("~/.vagas_ux_chrome_profile")


def salvar_cookies(driver, site: str):
    """Salva cookies do navegador em arquivo JSON."""
    os.makedirs(COOKIES_DIR, exist_ok=True)
    cookies = driver.get_cookies()
    filepath = os.path.join(COOKIES_DIR, f"{site}_cookies.json")
    with open(filepath, "w") as f:
        json.dump(cookies, f)
    print(f"Cookies salvos em: {filepath}")


def carregar_cookies(driver, site: str) -> bool:
    """Carrega cookies de arquivo JSON para o navegador."""
    filepath = os.path.join(COOKIES_DIR, f"{site}_cookies.json")
    if not os.path.exists(filepath):
        return False

    with open(filepath, "r") as f:
        cookies = json.load(f)

    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except:
            pass
    return True


def criar_driver_com_perfil(headless=False):
    """Cria driver do Chrome com perfil persistente."""
    os.makedirs(PROFILE_DIR, exist_ok=True)

    options = Options()
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--window-size=1200,800")
    options.add_argument("--lang=pt-BR")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    return driver


def login_linkedin():
    """Abre LinkedIn para login manual com perfil persistente."""
    print("\n=== LOGIN LINKEDIN ===")
    print("1. Uma janela do Chrome vai abrir")
    print("2. Faça login normalmente (pode usar chave de acesso)")
    print("3. Quando estiver logado, volte aqui e pressione ENTER")
    print("=" * 30)

    driver = criar_driver_com_perfil(headless=False)
    driver.get("https://www.linkedin.com/login")

    input("\nPressione ENTER quando terminar o login...")

    salvar_cookies(driver, "linkedin")
    driver.quit()
    print("Login LinkedIn salvo com sucesso!")


def login_indeed():
    """Abre Indeed para login manual."""
    print("\n=== LOGIN INDEED ===")
    print("1. Uma janela do Chrome vai abrir")
    print("2. Faça login normalmente (pode usar chave de acesso)")
    print("3. Quando estiver logado, volte aqui e pressione ENTER")
    print("=" * 30)

    driver = criar_driver_com_perfil(headless=False)
    driver.get("https://secure.indeed.com/auth")

    input("\nPressione ENTER quando terminar o login...")

    salvar_cookies(driver, "indeed")
    driver.quit()
    print("Login Indeed salvo com sucesso!")


if __name__ == "__main__":
    print("Qual site deseja fazer login?")
    print("1. LinkedIn")
    print("2. Indeed")
    print("3. Ambos")

    escolha = input("\nEscolha (1/2/3): ").strip()

    if escolha == "1":
        login_linkedin()
    elif escolha == "2":
        login_indeed()
    elif escolha == "3":
        login_linkedin()
        login_indeed()
    else:
        print("Opção inválida")
