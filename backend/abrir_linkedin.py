#!/usr/bin/env python3
"""
Script para abrir LinkedIn e fazer login.
A janela ficará aberta por 5 minutos para você fazer login.
Feche a janela quando terminar.
"""
import sys
sys.path.insert(0, '.')

from app.scrapers.login_helper import criar_driver_com_perfil
import time

print("=" * 50)
print("ABRINDO LINKEDIN PARA LOGIN")
print("=" * 50)
print("\n1. Uma janela do Chrome vai abrir")
print("2. Faça login normalmente")
print("3. FECHE A JANELA quando terminar")
print("\nA janela ficará aberta por até 5 minutos...")
print("=" * 50)

driver = criar_driver_com_perfil(headless=False)
driver.get("https://www.linkedin.com/login")

# Mantém aberto por 5 minutos ou até fechar
start = time.time()
while time.time() - start < 300:  # 5 minutos
    try:
        _ = driver.current_url
        time.sleep(2)
    except:
        break

try:
    driver.quit()
except:
    pass

print("\n✅ Navegador fechado. Sessão salva!")
