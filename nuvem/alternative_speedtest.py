# nuvem/alternative_speedtest.py
import os
import json
import sys
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

def resource_path(relative_path):
    # Busca o caminho correto para recursos, tanto em ambiente empacotado quanto em desenvolvimento
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)

class AlternativeSpeedTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teste Alternativo de Velocidade")
        self.setGeometry(150, 150, 800, 600)

        # Busca o conf.json primeiro no diretório do usuário, depois no bundle
        user_dir = os.path.expandvars(r"%userprofile%/.nuvem")
        config_path = os.path.join(user_dir, "conf.json")
        if not os.path.exists(config_path):
            config_path = resource_path("config/conf.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            url = config.get("speedtest_fallback_url", "https://openspeedtest.com/speedtest")

        self.webview = QWebEngineView()
        self.webview.load(QUrl(url))

        layout = QVBoxLayout()
        layout.addWidget(self.webview)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
