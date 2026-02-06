#!/usr/bin/env python3
"""
Scheduler para coleta automática diária de vagas.
Roda em background e executa a coleta no horário configurado.
"""
import sys
import os
import time
import subprocess
from datetime import datetime, timedelta
import threading

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def log(msg: str):
    """Log com timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def executar_coleta():
    """Executa o script de coleta."""
    log("Iniciando coleta automática...")

    script_path = os.path.join(os.path.dirname(__file__), "coletar_tudo.py")
    venv_python = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "venv", "bin", "python")

    try:
        result = subprocess.run(
            [venv_python, script_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        print(result.stdout)
        if result.stderr:
            print("Erros:", result.stderr)
        log("Coleta concluída!")
    except Exception as e:
        log(f"Erro na coleta: {e}")


def agendar_proxima_coleta(hora: int = 9, minuto: int = 0):
    """
    Agenda a próxima coleta para o horário especificado.
    Se já passou do horário hoje, agenda para amanhã.
    """
    agora = datetime.now()
    proxima = agora.replace(hour=hora, minute=minuto, second=0, microsecond=0)

    if proxima <= agora:
        proxima += timedelta(days=1)

    segundos = (proxima - agora).total_seconds()
    return proxima, segundos


def rodar_scheduler(hora_coleta: int = 9, minuto_coleta: int = 0):
    """
    Roda o scheduler em loop infinito.

    Args:
        hora_coleta: Hora do dia para executar (0-23)
        minuto_coleta: Minuto da hora para executar (0-59)
    """
    log(f"Scheduler iniciado. Coleta programada para {hora_coleta:02d}:{minuto_coleta:02d} todos os dias.")

    while True:
        proxima, segundos = agendar_proxima_coleta(hora_coleta, minuto_coleta)
        log(f"Próxima coleta: {proxima.strftime('%d/%m/%Y %H:%M')} (em {segundos/3600:.1f} horas)")

        # Aguarda até o horário
        time.sleep(segundos)

        # Executa a coleta
        executar_coleta()

        # Pequena pausa antes de reagendar
        time.sleep(60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scheduler de coleta automática")
    parser.add_argument("--hora", type=int, default=9, help="Hora da coleta (0-23)")
    parser.add_argument("--minuto", type=int, default=0, help="Minuto da coleta (0-59)")
    parser.add_argument("--agora", action="store_true", help="Executar coleta imediatamente")

    args = parser.parse_args()

    if args.agora:
        executar_coleta()
    else:
        rodar_scheduler(args.hora, args.minuto)
