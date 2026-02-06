#!/usr/bin/env python3
"""
Script principal de coleta automática.
Usa o Chrome do usuário (com sessões já logadas).
Executa coleta das 3 fontes e salva no banco.
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from app.database import SessionLocal, engine, Base
from app import crud, schemas
from app.scrapers.indeed import coletar_vagas_indeed
from app.scrapers.linkedin_jobs import coletar_vagas_linkedin
from app.scrapers.linkedin_posts import coletar_vagas_linkedin_posts


def salvar_vagas(db, vagas: list[dict], fonte: str) -> int:
    """Salva vagas no banco, retorna quantidade de novas."""
    novas = 0
    for vaga_dict in vagas:
        try:
            if not crud.check_duplicate(db, vaga_dict.get("titulo"), vaga_dict.get("empresa"), vaga_dict.get("link_vaga")):
                vaga = schemas.VagaCreate(**vaga_dict)
                crud.create_vaga(db, vaga)
                novas += 1
        except Exception as e:
            print(f"  Erro ao salvar: {e}")
    return novas


def coletar_tudo(mostrar_janela: bool = True):
    """
    Executa coleta de todas as fontes.

    Args:
        mostrar_janela: Se True, mostra o navegador (usa sessões do usuário).
                       Se False, roda headless (pode não ter login).
    """
    print("=" * 60)
    print(f"COLETA DE VAGAS - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)

    # Garante que as tabelas existem
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    resultados = {
        "indeed": {"coletadas": 0, "novas": 0, "erro": None},
        "linkedin_jobs": {"coletadas": 0, "novas": 0, "erro": None},
        "linkedin_posts": {"coletadas": 0, "novas": 0, "erro": None},
    }

    try:
        # 1. Indeed (não precisa de login)
        print("\n📋 INDEED")
        print("-" * 40)
        try:
            vagas_indeed = coletar_vagas_indeed()
            resultados["indeed"]["coletadas"] = len(vagas_indeed)
            resultados["indeed"]["novas"] = salvar_vagas(db, vagas_indeed, "indeed")
            print(f"✓ {resultados['indeed']['coletadas']} coletadas, {resultados['indeed']['novas']} novas")
        except Exception as e:
            resultados["indeed"]["erro"] = str(e)
            print(f"✗ Erro: {e}")

        # 2. LinkedIn Vagas
        print("\n💼 LINKEDIN VAGAS")
        print("-" * 40)
        try:
            vagas_linkedin = coletar_vagas_linkedin(headless=not mostrar_janela)
            resultados["linkedin_jobs"]["coletadas"] = len(vagas_linkedin)
            resultados["linkedin_jobs"]["novas"] = salvar_vagas(db, vagas_linkedin, "linkedin_jobs")
            print(f"✓ {resultados['linkedin_jobs']['coletadas']} coletadas, {resultados['linkedin_jobs']['novas']} novas")
        except Exception as e:
            resultados["linkedin_jobs"]["erro"] = str(e)
            print(f"✗ Erro: {e}")

        # 3. LinkedIn Publicações
        print("\n📝 LINKEDIN PUBLICAÇÕES")
        print("-" * 40)
        try:
            vagas_posts = coletar_vagas_linkedin_posts(headless=not mostrar_janela)
            resultados["linkedin_posts"]["coletadas"] = len(vagas_posts)
            resultados["linkedin_posts"]["novas"] = salvar_vagas(db, vagas_posts, "linkedin_posts")
            print(f"✓ {resultados['linkedin_posts']['coletadas']} coletadas, {resultados['linkedin_posts']['novas']} novas")
        except Exception as e:
            resultados["linkedin_posts"]["erro"] = str(e)
            print(f"✗ Erro: {e}")

        # Resumo
        total_novas = sum(r["novas"] for r in resultados.values())
        total_coletadas = sum(r["coletadas"] for r in resultados.values())

        print("\n" + "=" * 60)
        print("RESUMO")
        print("=" * 60)
        print(f"Total coletadas: {total_coletadas}")
        print(f"Novas salvas: {total_novas}")

        # Estatísticas do banco
        stats = crud.get_stats(db)
        print(f"\nNo banco de dados:")
        print(f"  Total de vagas: {stats['total_vagas']}")
        print(f"  Últimas 24h: {stats['ultimas_24h']}")

        if total_novas > 0:
            print(f"\n🎉 {total_novas} NOVAS VAGAS ENCONTRADAS!")
        else:
            print("\nNenhuma vaga nova encontrada.")

        return resultados

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Coleta vagas de todas as fontes")
    parser.add_argument("--headless", action="store_true", help="Rodar sem mostrar navegador")
    args = parser.parse_args()

    coletar_tudo(mostrar_janela=not args.headless)
