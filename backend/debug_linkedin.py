import sys
sys.path.insert(0, '.')
from app.scrapers.login_helper import criar_driver_com_perfil
import time

driver = criar_driver_com_perfil(headless=False)
driver.get("https://www.linkedin.com/jobs/search/?f_TPR=r86400&f_WT=2&keywords=ux&sortBy=R")
time.sleep(5)

# Salvar HTML para debug
with open("linkedin_debug.html", "w") as f:
    f.write(driver.page_source)

print("HTML salvo em linkedin_debug.html")
print("Pressione ENTER para fechar...")
input()
driver.quit()
