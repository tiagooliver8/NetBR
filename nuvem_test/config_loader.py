# nuvem_test/config_loader.py
import json
import os
import sys


def load_config():
    # Detecta se está rodando como executável PyInstaller
    if getattr(sys, 'frozen', False):
        # Executável: carrega de %userprofile%/.nuvem/conf.json
        user_dir = os.path.expandvars(r"%userprofile%/.nuvem")
        config_path = os.path.join(user_dir, "conf.json")
    else:
        # Desenvolvimento: carrega de ./config/conf.json
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'conf.json')
        config_path = os.path.abspath(config_path)
    with open(config_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao ler o JSON: {e}")

    # Validação dos testes TCP
    if "tests" not in data or not isinstance(data["tests"], list):
        raise ValueError("Configuração inválida: chave 'tests' ausente ou mal formatada.")
    for test in data["tests"]:
        if not all(k in test for k in ("host", "port", "required")):
            raise ValueError(f"Teste mal formatado: {test}")

    # Validação dos testes de velocidade
    if "speedtest" not in data or not isinstance(data["speedtest"], list):
        raise ValueError("Configuração inválida: chave 'speedtest' ausente ou mal formatada.")
    for st in data["speedtest"]:
        if not all(k in st for k in ("type", "description", "required")):
            raise ValueError(f"Speedtest mal formatado: {st}")

    return data


def get_speedtest_requirements():
    config = load_config()
    return config.get("speedtest", [])
