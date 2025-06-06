import json
import os


def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "conf.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao ler o JSON: {e}")

    if "tests" not in data or not isinstance(data["tests"], list):
        raise ValueError("Configuração inválida: chave 'tests' ausente ou mal formatada.")

    # Validação básica de cada item
    for test in data["tests"]:
        if not all(k in test for k in ("host", "port", "required")):
            raise ValueError(f"Teste mal formatado: {test}")

    return data["tests"]
