import sys
import os
from datetime import datetime

# nuvem_test/logger.py

# Detecta se está rodando como executável PyInstaller
if getattr(sys, 'frozen', False):
    # Executável: salva em %userprofile%/.nuvem/logs
    USER_DIR = os.path.expandvars(r"%userprofile%/.nuvem")
    LOG_DIR = os.path.join(USER_DIR, "logs")
else:
    # Desenvolvimento: salva em ./logs
    LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
    LOG_DIR = os.path.abspath(LOG_DIR)

os.makedirs(LOG_DIR, exist_ok=True)

# Nome do arquivo: NuvemTest_[data e hora do teste].log
log_filename = "NuvemTest_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
log_path = os.path.join(LOG_DIR, log_filename)


def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"

    # Escreve no arquivo
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(full_message + "\n")

    # Também mostra no terminal
    print(full_message)
