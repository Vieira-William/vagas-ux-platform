"""
Abra este arquivo no terminal para fazer login.
Comando: python fazer_login.py
"""
import sys
sys.path.insert(0, '.')
from app.scrapers.login_helper import login_linkedin, login_indeed

print("\n" + "="*50)
print("FERRAMENTA DE LOGIN")
print("="*50)
print("\n1. LinkedIn")
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
