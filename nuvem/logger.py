import os
from datetime import datetime

# Cria diretório de logs se não existir
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(ROOT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Define nome do arquivo com data e hora
log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
log_path = os.path.join(LOG_DIR, log_filename)


def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"

    # Escreve no arquivo
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(full_message + "\n")

    # Também mostra no terminal
    print(full_message)
