#!/usr/bin/env python3
"""
Script para fazer login e testar imediatamente.
"""
import sys
sys.path.insert(0, '.')

from app.scrapers.login_helper import criar_driver_com_perfil
from selenium.webdriver.common.by import By
import time

print("=" * 50)
print("LOGIN E TESTE DO LINKEDIN")
print("=" * 50)

driver = criar_driver_com_perfil(headless=False)
driver.get("https://www.linkedin.com/login")

print("\n1. Faça login no LinkedIn")
print("2. Quando estiver logado, pressione ENTER aqui")
print("=" * 50)

input("\nPressione ENTER quando terminar o login...")

# Testa se está logado
driver.get("https://www.linkedin.com/feed/")
time.sleep(3)

if "Sign in" in driver.page_source or "Entrar" in driver.page_source:
    print("\n❌ Login não detectado!")
else:
    print("\n✅ Login OK!")

    # Vai para busca de publicações
    print("\nTestando busca de publicações...")
    driver.get("https://www.linkedin.com/search/results/content/?keywords=ux%20vaga&datePosted=%22past-24h%22&sortBy=%22date_posted%22")
    time.sleep(5)

    # Scroll para carregar posts
    for i in range(15):
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(0.3)

    # Conta posts
    posts = driver.find_elements(By.CSS_SELECTOR, "div.feed-shared-update-v2")
    print(f"\n📊 Posts encontrados: {len(posts)}")

    if posts:
        print("\n--- Exemplo de post ---")
        print(posts[0].text[:500])
        print("---")

print("\nFechando navegador...")
driver.quit()
print("✅ Concluído!")
